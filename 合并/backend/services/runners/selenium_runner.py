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

    def _log_info(self, msg: str, *args):
        logger.info('[%s] ' + msg, self.log_tag, *args)

    def _log_warning(self, msg: str, *args):
        logger.warning('[%s] ' + msg, self.log_tag, *args)

    def _log_error(self, msg: str, *args):
        logger.error('[%s] ' + msg, self.log_tag, *args)

    def _log_exception(self, msg: str, *args):
        logger.exception('[%s] ' + msg, self.log_tag, *args)

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
        self._monitor_thread = threading.Thread(
            target=target,
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
