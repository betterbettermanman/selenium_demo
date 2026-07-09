"""网站预览浏览器：有头模式打开网站 URL。"""
import logging
import os
import threading
import time

logger = logging.getLogger(__name__)

_browsers = {}
_lock = threading.Lock()


def is_website_browser_open(website_id: int) -> bool:
    with _lock:
        driver = _browsers.get(website_id)
    if not driver:
        return False
    try:
        _ = driver.window_handles
        return True
    except Exception:
        with _lock:
            _browsers.pop(website_id, None)
        return False


def open_website_browser(website) -> tuple[bool, str]:
    url = (website.url or '').strip()
    if not url:
        return False, '请先配置网站 URL'
    if not url.startswith(('http://', 'https://')):
        return False, '网站 URL 须以 http:// 或 https:// 开头'

    website_id = website.id
    with _lock:
        driver = _browsers.get(website_id)
        if driver:
            try:
                _ = driver.window_handles
                driver.get(url)
                return True, f'浏览器已打开，已跳转: {url}'
            except Exception:
                _browsers.pop(website_id, None)

    try:
        driver = _create_headed_driver(website)
        driver.get(url)
    except Exception as exc:
        logger.exception('打开网站浏览器失败 website_id=%s', website_id)
        return False, f'打开浏览器失败: {exc}'

    with _lock:
        _browsers[website_id] = driver

    threading.Thread(
        target=_watch_browser,
        args=(website_id, driver),
        daemon=True,
        name=f'website-browser-{website_id}',
    ).start()
    return True, f'已打开有头浏览器: {url}'


def close_website_browser(website_id: int) -> tuple[bool, str]:
    with _lock:
        driver = _browsers.pop(website_id, None)
    if not driver:
        return False, '该网站浏览器未打开'
    try:
        driver.quit()
    except Exception:
        logger.exception('关闭网站浏览器失败 website_id=%s', website_id)
    return True, '浏览器已关闭'


def _create_headed_driver(website):
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service

    from utils.chromedriver_manager import get_chromedriver_path

    code = website.code or f'web{website.id}'
    user_data_dir = os.path.join(
        os.getcwd(), 'browser_data', 'WEBSITE_PREVIEW', code,
    )
    os.makedirs(user_data_dir, exist_ok=True)

    options = Options()
    options.add_argument(f'--user-data-dir={user_data_dir}')
    options.add_argument('--disable-gpu')
    options.add_argument('--start-maximized')
    options.add_argument('--no-sandbox')

    service = Service(get_chromedriver_path())
    driver = webdriver.Chrome(service=service, options=options)
    driver.maximize_window()
    driver.implicitly_wait(10)
    return driver


def _watch_browser(website_id: int, driver):
    while True:
        time.sleep(2)
        try:
            _ = driver.window_handles
        except Exception:
            with _lock:
                if _browsers.get(website_id) is driver:
                    _browsers.pop(website_id, None)
            logger.info('网站预览浏览器已关闭 website_id=%s', website_id)
            break
