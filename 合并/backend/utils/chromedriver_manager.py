"""
ChromeDriver 自动下载与缓存（国内 npmmirror 镜像）

根据本机 Chrome 版本匹配最接近的 chromedriver，下载后缓存到本地目录。
"""
import json
import logging
import os
import platform
import re
import shutil
import subprocess
import threading
import time
import zipfile
from pathlib import Path
from typing import Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)

_lock = threading.Lock()

# 国内镜像（registry.npmmirror.com 二进制同步）
NPMMIRROR_CFT_BASE = 'https://registry.npmmirror.com/-/binary/chrome-for-testing'
NPMMIRROR_LEGACY_BASE = 'https://registry.npmmirror.com/-/binary/chromedriver'

# 可选备用（非国内）
GOOGLE_CFT_JSON = (
    'https://googlechromelabs.github.io/chrome-for-testing/'
    'last-known-good-versions-with-downloads.json'
)

VERSION_INDEX_TTL = 6 * 3600  # 版本列表缓存 6 小时


def get_chromedriver_path(force_refresh: bool = False) -> str:
    """
    获取 chromedriver 可执行文件路径。
    优先级：CHROMEDRIVER_PATH 环境变量 > 本地缓存 > 自动下载。
    """
    env_path = os.getenv('CHROMEDRIVER_PATH', '').strip()
    if env_path and os.path.isfile(env_path):
        return env_path

    chrome_version = detect_chrome_version()
    if not chrome_version:
        raise RuntimeError(
            '未检测到本机 Google Chrome，请先安装 Chrome 或手动设置 CHROMEDRIVER_PATH'
        )

    cache_dir = _get_cache_dir()
    meta_path = cache_dir / 'meta.json'
    meta = _read_json(meta_path, default={})

    if (
        not force_refresh
        and meta.get('chrome_version') == chrome_version
        and meta.get('path')
        and os.path.isfile(meta['path'])
    ):
        logger.debug('使用缓存 chromedriver: %s', meta['path'])
        return meta['path']

    with _lock:
        meta = _read_json(meta_path, default={})
        if (
            not force_refresh
            and meta.get('chrome_version') == chrome_version
            and meta.get('path')
            and os.path.isfile(meta['path'])
        ):
            return meta['path']

        driver_version, download_url, exe_name = resolve_download(chrome_version)
        target_dir = cache_dir / driver_version
        driver_exe = target_dir / exe_name

        if not driver_exe.is_file() or force_refresh:
            _download_and_extract(download_url, target_dir, exe_name)

        meta = {
            'chrome_version': chrome_version,
            'driver_version': driver_version,
            'path': str(driver_exe),
            'download_url': download_url,
            'updated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        }
        _write_json(meta_path, meta)
        logger.info(
            'chromedriver 就绪 Chrome=%s Driver=%s Path=%s',
            chrome_version, driver_version, driver_exe,
        )
        return str(driver_exe)


def detect_chrome_version() -> Optional[str]:
    system = platform.system()

    if system == 'Windows':
        version = _detect_chrome_version_windows()
        if version:
            return version
    elif system == 'Darwin':
        version = _detect_chrome_version_mac()
        if version:
            return version
    elif system == 'Linux':
        version = _detect_chrome_version_linux()
        if version:
            return version

    for cmd in (
        'google-chrome --version',
        'google-chrome-stable --version',
        'chromium --version',
        'chromium-browser --version',
    ):
        version = _parse_version_from_command(cmd)
        if version:
            return version
    return None


def resolve_download(chrome_version: str) -> tuple[str, str, str]:
    major = int(chrome_version.split('.')[0])
    platform_key, zip_name, exe_name = _platform_assets()

    if major >= 115:
        versions = _list_mirror_versions(NPMMIRROR_CFT_BASE)
        driver_version = _find_best_version(chrome_version, versions)
        download_url = f'{NPMMIRROR_CFT_BASE}/{driver_version}/{platform_key}/{zip_name}'
        return driver_version, download_url, exe_name

    versions = _list_mirror_versions(NPMMIRROR_LEGACY_BASE)
    driver_version = _find_best_version(chrome_version, versions)
    legacy_zip = 'chromedriver_win32.zip' if platform_key == 'win32' else f'chromedriver_{platform_key}.zip'
    download_url = f'{NPMMIRROR_LEGACY_BASE}/{driver_version}/{legacy_zip}'
    return driver_version, download_url, 'chromedriver.exe'


def _get_cache_dir() -> Path:
    custom = os.getenv('CHROMEDRIVER_CACHE_DIR', '').strip()
    if custom:
        cache_dir = Path(custom)
    else:
        cache_dir = Path(os.getcwd()) / 'driver_cache' / 'chromedriver'
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def _platform_assets() -> tuple[str, str, str]:
    system = platform.system()
    machine = platform.machine().lower()

    if system == 'Windows':
        if machine in ('amd64', 'x86_64', 'arm64'):
            return 'win64', 'chromedriver-win64.zip', 'chromedriver.exe'
        return 'win32', 'chromedriver-win32.zip', 'chromedriver.exe'

    if system == 'Darwin':
        if machine == 'arm64':
            return 'mac-arm64', 'chromedriver-mac-arm64.zip', 'chromedriver'
        return 'mac-x64', 'chromedriver-mac-x64.zip', 'chromedriver'

    return 'linux64', 'chromedriver-linux64.zip', 'chromedriver'


def _detect_chrome_version_windows() -> Optional[str]:
    try:
        import winreg
    except ImportError:
        winreg = None

    if winreg:
        reg_paths = (
            (winreg.HKEY_CURRENT_USER, r'Software\Google\Chrome\BLBeacon'),
            (winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Google\Chrome\BLBeacon'),
            (winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Wow6432Node\Google\Chrome\BLBeacon'),
        )
        for root, subkey in reg_paths:
            try:
                key = winreg.OpenKey(root, subkey)
                version, _ = winreg.QueryValueEx(key, 'version')
                if version:
                    return str(version)
            except OSError:
                continue

    chrome_paths = [
        os.path.expandvars(r'%ProgramFiles%\Google\Chrome\Application\chrome.exe'),
        os.path.expandvars(r'%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe'),
        os.path.expandvars(r'%LocalAppData%\Google\Chrome\Application\chrome.exe'),
    ]
    for path in chrome_paths:
        if os.path.isfile(path):
            version = _parse_version_from_command(f'"{path}" --version')
            if version:
                return version
    return None


def _detect_chrome_version_mac() -> Optional[str]:
    paths = [
        '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        os.path.expanduser('~/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'),
    ]
    for path in paths:
        if os.path.isfile(path):
            version = _parse_version_from_command(f'"{path}" --version')
            if version:
                return version
    return None


def _detect_chrome_version_linux() -> Optional[str]:
    paths = [
        '/usr/bin/google-chrome',
        '/usr/bin/google-chrome-stable',
        '/usr/bin/chromium',
        '/usr/bin/chromium-browser',
    ]
    for path in paths:
        if os.path.isfile(path):
            version = _parse_version_from_command(f'"{path}" --version')
            if version:
                return version
    return None


def _parse_version_from_command(command: str) -> Optional[str]:
    try:
        output = subprocess.check_output(
            command, shell=True, stderr=subprocess.STDOUT, text=True, timeout=10,
        )
        match = re.search(r'(\d+\.\d+\.\d+\.\d+)', output)
        return match.group(1) if match else None
    except Exception:
        return None


def _version_tuple(version: str) -> tuple[int, ...]:
    return tuple(int(x) for x in version.split('.'))


def _find_best_version(chrome_version: str, available: list[str]) -> str:
    if not available:
        raise RuntimeError('镜像站未返回可用 chromedriver 版本列表')

    if chrome_version in available:
        return chrome_version

    chrome_parts = chrome_version.split('.')
    chrome_major = chrome_parts[0]
    chrome_t = _version_tuple(chrome_version)

    same_major = [v for v in available if v.split('.')[0] == chrome_major]
    if not same_major:
        raise RuntimeError(
            f'未找到与 Chrome {chrome_version} 主版本匹配的 chromedriver，'
            f'请手动设置 CHROMEDRIVER_PATH'
        )

    # 优先同 major.minor.build 前缀
    for prefix_len in (4, 3, 2):
        if len(chrome_parts) < prefix_len:
            continue
        prefix = '.'.join(chrome_parts[:prefix_len])
        candidates = [v for v in same_major if v.startswith(prefix + '.') or v == prefix]
        if candidates:
            candidates.sort(key=_version_tuple)
            le = [v for v in candidates if _version_tuple(v) <= chrome_t]
            return le[-1] if le else candidates[0]

    same_major.sort(key=_version_tuple)
    le = [v for v in same_major if _version_tuple(v) <= chrome_t]
    return le[-1] if le else same_major[-1]


def _list_mirror_versions(base_url: str) -> list[str]:
    cache_dir = _get_cache_dir()
    index_name = 'cft_versions.json' if 'chrome-for-testing' in base_url else 'legacy_versions.json'
    index_path = cache_dir / index_name
    index_meta_path = cache_dir / f'{index_name}.meta'

    if index_path.is_file() and index_meta_path.is_file():
        try:
            meta = _read_json(index_meta_path, default={})
            if time.time() - meta.get('ts', 0) < VERSION_INDEX_TTL:
                return _read_json(index_path, default=[])
        except Exception:
            pass

    versions = _fetch_mirror_versions(base_url)
    _write_json(index_path, versions)
    _write_json(index_meta_path, {'ts': time.time(), 'count': len(versions)})
    return versions


def _fetch_mirror_versions(base_url: str) -> list[str]:
    try:
        payload = _http_get_json(f'{base_url}/')
        versions = sorted(
            {item['name'].strip('/') for item in payload if item.get('type') == 'dir'},
            key=_version_tuple,
        )
        if versions:
            logger.info('从 npmmirror 获取 %s 个 chromedriver 版本', len(versions))
            return versions
    except Exception as exc:
        logger.warning('从 npmmirror 获取版本列表失败: %s', exc)

    if 'chrome-for-testing' in base_url:
        return _fetch_google_cft_versions()
    raise RuntimeError('无法获取 chromedriver 版本列表')


def _fetch_google_cft_versions() -> list[str]:
    logger.info('尝试从 Google 官方 JSON 获取版本列表（备用）')
    data = _http_get_json(GOOGLE_CFT_JSON)
    versions = [item['version'] for item in data.get('versions', []) if item.get('version')]
    versions.sort(key=_version_tuple)
    return versions


def _download_and_extract(download_url: str, target_dir: Path, exe_name: str):
    target_dir.mkdir(parents=True, exist_ok=True)
    zip_path = target_dir / 'download.zip'
    logger.info('正在下载 chromedriver: %s', download_url)

    try:
        _http_download(download_url, zip_path)
    except Exception as primary_exc:
        fallback_url = _to_cdn_url(download_url)
        if fallback_url != download_url:
            logger.warning('registry 下载失败，尝试 CDN: %s', fallback_url)
            _http_download(fallback_url, zip_path)
        else:
            raise RuntimeError(f'chromedriver 下载失败: {primary_exc}') from primary_exc

    if target_dir.exists():
        for item in target_dir.iterdir():
            if item.name != 'download.zip':
                if item.is_dir():
                    shutil.rmtree(item, ignore_errors=True)
                else:
                    item.unlink(missing_ok=True)

    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(target_dir)
    zip_path.unlink(missing_ok=True)

    found = _find_file(target_dir, exe_name)
    if not found:
        raise RuntimeError(f'解压后未找到 {exe_name}')

    final_path = target_dir / exe_name
    if found.resolve() != final_path.resolve():
        shutil.copy2(found, final_path)
        if found.name != exe_name:
            found.unlink(missing_ok=True)

    if platform.system() != 'Windows':
        final_path.chmod(final_path.stat().st_mode | 0o111)


def _to_cdn_url(url: str) -> str:
    return url.replace(
        'https://registry.npmmirror.com/-/binary/',
        'https://cdn.npmmirror.com/binaries/',
    )


def _find_file(root: Path, filename: str) -> Optional[Path]:
    direct = root / filename
    if direct.is_file():
        return direct
    for path in root.rglob(filename):
        if path.is_file():
            return path
    return None


def _http_get_json(url: str):
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0 task-manager/chromedriver-manager'})
    with urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode('utf-8'))


def _http_download(url: str, dest: Path):
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0 task-manager/chromedriver-manager'})
    with urlopen(req, timeout=120) as resp, open(dest, 'wb') as f:
        shutil.copyfileobj(resp, f)


def _read_json(path: Path, default=None):
    if not path.is_file():
        return default if default is not None else {}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def _write_json(path: Path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
