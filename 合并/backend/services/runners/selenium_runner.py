"""
Selenium 任务执行器基类

抽取各网站 runner 的浏览器初始化、状态管理、验证码识别、页面检测等通用逻辑。
子类按需重写 _is_logged_in、_auto_login、run_main 等方法。
"""
import logging
import os
import threading
import time
from typing import Any, Callable

from services.task_runner import BaseTaskRunner, update_task_fields

logger = logging.getLogger(__name__)

DEFAULT_PAGE_ERROR_KEYWORDS = [
    '502 bad gateway',
    'bad gateway',
    '504 gateway timeout',
    '500 internal server error',
    '无法访问此网站',
    '无法访问',
    '连接已重置',
    '连接超时',
    '页面加载失败',
    'page not found',
    '404',
    '502',
]

# ChromeDriver 超时/假死时，driver.get 统一重试
DRIVER_GET_RETRY = 3
DRIVER_GET_RETRY_INTERVAL = 5


class SeleniumTaskRunner(BaseTaskRunner):
    """基于 Selenium 的任务执行器基类。"""

    def __init__(self, task, website):
        super().__init__(task, website)
        self.is_complete = False
        self.is_running = True
        self.current_course_url = ''
        self._monitor_thread = None

    @property
    def log_tag(self) -> str:
        return self.website.code or 'RUNNER'

    @property
    def log_task_id(self):
        return getattr(self.task, 'id', None) or '?'

    def _log_info(self, msg: str, *args):
        logger.info(
            '[%s][taskId=%s][%s] ' + msg,
            self.log_tag, self.log_task_id, self.log_user_label, *args,
        )

    def _log_warning(self, msg: str, *args):
        logger.warning(
            '[%s][taskId=%s][%s] ' + msg,
            self.log_tag, self.log_task_id, self.log_user_label, *args,
        )

    def _log_error(self, msg: str, *args):
        logger.error(
            '[%s][taskId=%s][%s] ' + msg,
            self.log_tag, self.log_task_id, self.log_user_label, *args,
        )

    def _log_exception(self, msg: str, *args):
        logger.exception(
            '[%s][taskId=%s][%s] ' + msg,
            self.log_tag, self.log_task_id, self.log_user_label, *args,
        )

    def _driver_get(self, url: str, *, retries: int = DRIVER_GET_RETRY, label: str = '页面') -> None:
        """打开 URL，对 ChromeDriver 超时/假死做有限次重试（各站点共用）。"""
        last_exc: Exception | None = None
        for attempt in range(1, retries + 1):
            if self._stopped or not self.driver:
                return
            try:
                self._log_info('打开%s attempt=%s/%s url=%s', label, attempt, retries, url)
                self.driver.get(url)
                return
            except Exception as exc:
                last_exc = exc
                err_name = type(exc).__name__
                err_msg = str(exc).split('\n', 1)[0].strip()
                if len(err_msg) > 200:
                    err_msg = err_msg[:200] + '...'
                retryable = self._is_driver_get_retryable(exc)
                self._log_warning(
                    '打开%s失败 attempt=%s/%s retryable=%s err=%s: %s',
                    label, attempt, retries, retryable, err_name, err_msg,
                )
                if not retryable or attempt >= retries:
                    break
                try:
                    self.driver.execute_script('window.stop();')
                except Exception:
                    pass
                time.sleep(DRIVER_GET_RETRY_INTERVAL)

        if last_exc is not None:
            raise last_exc

    @staticmethod
    def _is_driver_get_retryable(exc: Exception) -> bool:
        name = type(exc).__name__.lower()
        msg = str(exc).lower()
        keywords = (
            'timeout', 'timed out', 'readtimeout', 'connection',
            'disconnected', 'chrome not reachable', 'invalid session',
            'session deleted', 'no such window', 'browsing context',
        )
        return any(k in name or k in msg for k in keywords)

    def _browser_user_data_dir(self) -> str:
        return os.path.join(
            os.getcwd(), 'browser_data', self.log_tag, str(self.task.id), self.task.username
        )

    def _init_browser(self, *, window_size: tuple[int, int] | None = None):
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
        except ImportError as exc:
            raise RuntimeError('请先安装 selenium: pip install selenium') from exc

        user_data_dir = self._browser_user_data_dir()
        os.makedirs(user_data_dir, exist_ok=True)

        options = Options()
        if self.task.is_head == '1':
            options.add_argument('--headless=new')
        options.add_argument(f'--user-data-dir={user_data_dir}')
        options.add_argument('--disable-gpu')
        if window_size:
            options.add_argument(f'--window-size={window_size[0]},{window_size[1]}')
        options.add_argument('--start-maximized')
        options.add_argument('--no-sandbox')

        from utils.chromedriver_manager import get_chromedriver_path

        chromedriver_path = get_chromedriver_path()
        service = Service(chromedriver_path)
        self._log_info('使用 chromedriver: %s', chromedriver_path)

        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.maximize_window()
        self.driver.implicitly_wait(10)
        self._log_info('浏览器已启动 headless=%s', self.task.is_head == '1')

    def _cleanup(self):
        if self.driver:
            try:
                self.driver.quit()
                self._log_info('浏览器已关闭')
            except Exception:
                self._log_exception('关闭浏览器失败')
            finally:
                self.driver = None

    def _mark_course_complete(self):
        self.is_complete = True
        if not self._stopped and update_task_fields(self.task, status='2'):
            self._log_info('任务 id=%s 已标记完成', self.task.id)

    def _update_task_progress(self, progress: str) -> bool:
        """回写任务进度字段；值未变化时跳过，避免频繁写库。"""
        text = (progress or '').strip()
        if not text:
            return False
        if (getattr(self.task, 'progress', None) or '') == text:
            return True
        if self._stopped:
            return False
        ok = update_task_fields(self.task, progress=text)
        if ok:
            self._log_info('任务进度已更新 progress=%s', text)
        else:
            self._log_warning('任务进度更新失败 progress=%s', text)
        return ok

    def check_page_error(self, extra_keywords: list[str] | None = None) -> bool:
        try:
            page_source = (self.driver.page_source or '').lower()
            keywords = DEFAULT_PAGE_ERROR_KEYWORDS + (extra_keywords or [])
            for keyword in keywords:
                if keyword.lower() in page_source:
                    self._log_warning('检测到页面错误关键词: %s', keyword)
                    return True
            return False
        except Exception as exc:
            self._log_error('检测页面错误异常: %s', exc)
            return True

    def _recognize_captcha_screenshot(self, element, filename: str) -> str:
        os.makedirs('png', exist_ok=True)
        save_path = os.path.join('png', filename)
        if not element.screenshot(save_path):
            return ''
        try:
            import ddddocr
            ocr = ddddocr.DdddOcr()
            with open(save_path, 'rb') as f:
                return ocr.classification(f.read())
        except ImportError:
            self._log_warning('未安装 ddddocr，跳过验证码识别')
            return ''
        except Exception:
            self._log_exception('验证码识别失败')
            return ''

    def _open_video_tab(self, href: str):
        self.driver.execute_script('window.open(arguments[0])', href)
        self.driver.switch_to.window(self.driver.window_handles[-1])
        self._log_info('已切换到播放页: %s', self.driver.current_url)

    def _get_target_course_name(self) -> str:
        raw = self.task.courses
        if isinstance(raw, dict) and raw.get('name'):
            return str(raw['name']).strip()
        if isinstance(raw, list):
            for item in raw:
                if isinstance(item, dict) and item.get('name'):
                    return str(item['name']).strip()
                if isinstance(item, str) and item.strip():
                    return item.strip()
        if self.task.remark:
            return self.task.remark.strip()
        return ''

    def _parse_course_items(self, raw: Any) -> list[Any]:
        if not raw:
            return []
        if isinstance(raw, list):
            return raw
        if isinstance(raw, dict):
            return [raw]
        return []

    def _build_context_log(self, course_list: list):
        skip_videos = self.task.no_play_videos or []
        self._log_info('课表条目数=%s 跳过视频=%s', len(course_list), skip_videos)
        for idx, item in enumerate(course_list, start=1):
            self._log_info('课表[%s] %s', idx, item)

    def _wait_until_complete(self):
        while not self.is_complete and self.is_running:
            time.sleep(1)

    def _start_monitor_thread(self, target: Callable, suffix: str = 'monitor'):
        # 监控线程独立于主线程，必须自带 Flask app_context，
        # 否则 update_task_fields / db 操作会抛 Working outside of application context，
        # 进而导致「播完后无法切下一集」等逻辑被 except 吞掉。
        self._monitor_thread = threading.Thread(
            target=lambda: self._run_with_context(target),
            daemon=True,
            name=f'{self.log_tag.lower()}-{suffix}-{self.task.id}',
        )
        self._monitor_thread.start()

    def _handle_run_exception(self):
        from models import db
        db.session.rollback()
        update_task_fields(self.task, status='1')

    def _finalize_run(self):
        self.is_running = False
        self._cleanup()

    def _sync_task_status(self):
        if self.is_complete and not self._stopped:
            update_task_fields(self.task, status='2')
            self._log_info('任务 id=%s 执行完成', self.task.id)
        elif not self._stopped:
            update_task_fields(self.task, status='1')

    def _ensure_logged_in(
        self,
        max_rounds: int = 5,
        *,
        before_check=None,
        on_success=None,
    ):
        """登录重试：子类实现 _is_logged_in / _auto_login。"""
        for idx in range(max_rounds):
            if before_check:
                before_check()
            if self._is_logged_in():
                if on_success:
                    on_success()
                return
            self._log_info('第 %s 次尝试登录', idx + 1)
            self._auto_login()
            time.sleep(3)
        if not self._is_logged_in():
            raise RuntimeError('登录失败，请检查账号密码或验证码')

    def _is_logged_in(self) -> bool:
        return False

    def _auto_login(self):
        raise NotImplementedError(f'{self.log_tag} 未实现 _auto_login')

    def _get_session_storage(self, key: str):
        try:
            return self.driver.execute_script(f"return window.sessionStorage.getItem('{key}');")
        except Exception:
            return None

    def _get_local_storage(self, key: str):
        try:
            return self.driver.execute_script(f"return window.localStorage.getItem('{key}');")
        except Exception:
            return None

    def get_cookies_values(self, key: str):
        """从浏览器 cookie 中按名称取值。"""
        if not self.driver:
            return None
        try:
            for cookie in self.driver.get_cookies():
                if cookie.get('name') == key:
                    return cookie.get('value')
        except Exception:
            self._log_exception('读取 cookie 失败 key=%s', key)
        return None

    def _dismiss_confirm_dialog(self):
        from selenium.webdriver.common.by import By

        try:
            confirm = self.driver.find_element(By.XPATH, "//button[contains(text(), '确定')]")
            confirm.click()
        except Exception:
            try:
                alert = self.driver.switch_to.alert
                alert.accept()
            except Exception:
                pass
