"""任务预览浏览器：有头模式打开任务关联网站，复用任务专属 user-data-dir。"""
import logging
import os
import threading
import time

from services.task_runner import is_task_running

logger = logging.getLogger(__name__)

_browsers = {}
_lock = threading.Lock()


def _task_user_data_dir(task, website) -> str:
    """与 SeleniumTaskRunner._browser_user_data_dir 保持一致，便于复用登录态。"""
    code = (website.code if website else None) or 'RUNNER'
    return os.path.join(
        os.getcwd(), 'browser_data', code, str(task.id), task.username or 'user'
    )


def is_task_browser_open(task_id: int) -> bool:
    with _lock:
        driver = _browsers.get(task_id)
    if not driver:
        return False
    try:
        _ = driver.window_handles
        return True
    except Exception:
        with _lock:
            _browsers.pop(task_id, None)
        return False


def open_task_browser(task, website) -> tuple[bool, str]:
    url = (website.url or '').strip() if website else ''
    if not url:
        return False, '请先配置网站 URL'
    if not url.startswith(('http://', 'https://')):
        return False, '网站 URL 须以 http:// 或 https:// 开头'
    if not task.website_code:
        return False, '任务未关联网站'
    if is_task_running(task.id):
        return False, '任务正在执行中，请先关闭任务再打开预览浏览器（避免占用同一用户目录）'

    task_id = task.id
    with _lock:
        driver = _browsers.get(task_id)
        if driver:
            try:
                _ = driver.window_handles
                msg = _navigate(driver, url)
                return True, msg
            except Exception:
                _browsers.pop(task_id, None)

    try:
        driver = _create_headed_driver(task, website)
        msg = _navigate(driver, url)
    except Exception as exc:
        logger.exception('打开任务浏览器失败 task_id=%s', task_id)
        return False, f'打开浏览器失败: {exc}'

    with _lock:
        _browsers[task_id] = driver

    threading.Thread(
        target=_watch_browser,
        args=(task_id, driver),
        daemon=True,
        name=f'task-browser-{task_id}',
    ).start()
    return True, msg


def close_task_browser(task_id: int) -> tuple[bool, str]:
    with _lock:
        driver = _browsers.pop(task_id, None)
    if not driver:
        return False, '该任务预览浏览器未打开'
    try:
        driver.quit()
    except Exception:
        logger.exception('关闭任务预览浏览器失败 task_id=%s', task_id)
    return True, '浏览器已关闭'


def _create_headed_driver(task, website):
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service

    from utils.chromedriver_manager import get_chromedriver_path

    user_data_dir = _task_user_data_dir(task, website)
    os.makedirs(user_data_dir, exist_ok=True)

    options = Options()
    options.add_argument(f'--user-data-dir={user_data_dir}')
    options.add_argument('--disable-gpu')
    options.add_argument('--start-maximized')
    options.add_argument('--no-sandbox')
    # 不等待整页资源加载完，避免学习站拖慢「打开浏览器」接口
    options.page_load_strategy = 'eager'

    t0 = time.perf_counter()
    service = Service(get_chromedriver_path())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(15)
    driver.maximize_window()
    driver.implicitly_wait(3)
    logger.info('任务预览浏览器启动耗时 %.1fms task_id=%s', (time.perf_counter() - t0) * 1000, task.id)
    return driver


def _navigate(driver, url: str) -> str:
    """跳转目标页；超时也视为已打开（窗口已在，页面可能仍在加载）。"""
    from selenium.common.exceptions import TimeoutException

    t0 = time.perf_counter()
    try:
        driver.get(url)
        logger.info('任务预览跳转完成 %.1fms url=%s', (time.perf_counter() - t0) * 1000, url)
        return f'已打开有头浏览器: {url}'
    except TimeoutException:
        logger.warning('任务预览页面加载超时（已打开窗口）url=%s', url)
        return f'浏览器已打开，页面仍在加载: {url}'


def _watch_browser(task_id: int, driver):
    while True:
        time.sleep(2)
        try:
            _ = driver.window_handles
        except Exception:
            with _lock:
                if _browsers.get(task_id) is driver:
                    _browsers.pop(task_id, None)
            logger.info('任务预览浏览器已关闭 task_id=%s', task_id)
            break
