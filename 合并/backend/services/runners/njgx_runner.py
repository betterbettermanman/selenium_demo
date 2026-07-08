"""
内江公需课（NJGX）任务执行器

网站编码：NJGX
参考：selenium_demo/内江公需课/main.py
"""
import logging
import os
import threading
import time
from typing import Any

from models import db
from services.task_runner import BaseTaskRunner, register_runner, update_task_fields

logger = logging.getLogger(__name__)

NJGX_BASE_URL = 'https://www.njsjxjy.cn'
NJGX_DEFAULT_COURSE_ID = '1166058'


@register_runner('NJGX')
class NjgxTaskRunner(BaseTaskRunner):
    """内江公需课任务执行器。"""

    def __init__(self, task, website):
        super().__init__(task, website)
        self.is_complete = False
        self.is_running = True
        self.current_course_url = self._build_course_url()
        self._monitor_thread = None

    def run_main(self):
        logger.info(
            '[NJGX] 开始任务 id=%s user=%s class_id=%s headless=%s',
            self.task.id,
            self.task.username,
            self.task.class_id,
            self.task.is_head,
        )
        try:
            self._build_context_log()
            self._init_browser()
            self._ensure_logged_in()
            self._play_courses()
            if self.is_complete and not self._stopped:
                update_task_fields(self.task, status='2')
                logger.info('[NJGX] 任务 id=%s 执行完成', self.task.id)
            else:
                update_task_fields(self.task, status='1')
                logger.warning('[NJGX] 任务 id=%s 未完成', self.task.id)
        except Exception:
            logger.exception('[NJGX] 任务 id=%s 执行失败', self.task.id)
            db.session.rollback()
            update_task_fields(self.task, status='1')
            raise
        finally:
            self.is_running = False
            self._cleanup()

    def _build_course_url(self, course_id=None) -> str:
        cid = course_id or self.task.class_id or NJGX_DEFAULT_COURSE_ID
        return f'{NJGX_BASE_URL}/play/play.aspx?course_id={cid}&try='

    def _build_login_url(self) -> str:
        return (
            f'{NJGX_BASE_URL}/login.aspx?ReturnUrl=/play/play.aspx'
            f'?course_id={self.task.class_id or NJGX_DEFAULT_COURSE_ID}&try='
        )

    def _build_context_log(self):
        course_list = self._parse_course_list()
        logger.info('[NJGX] 课表条目数=%s 跳过视频=%s', len(course_list), self.task.no_play_videos or [])

    def _parse_course_list(self) -> list[dict[str, Any]]:
        raw = self.task.courses
        if not raw:
            return [{
                'name': '默认课程',
                'url': self._build_course_url(),
                'course_id': self.task.class_id or NJGX_DEFAULT_COURSE_ID,
            }]
        if isinstance(raw, list):
            result = []
            for item in raw:
                if isinstance(item, str):
                    result.append({
                        'name': item,
                        'url': self._build_course_url(item) if item.isdigit() else item,
                        'course_id': item if item.isdigit() else self.task.class_id,
                    })
                elif isinstance(item, dict):
                    cid = item.get('course_id', self.task.class_id)
                    result.append({
                        'name': item.get('name', ''),
                        'url': item.get('url') or self._build_course_url(cid),
                        'course_id': cid,
                    })
            return result
        if isinstance(raw, dict):
            cid = raw.get('course_id', self.task.class_id)
            return [{
                'name': raw.get('name', ''),
                'url': raw.get('url') or self._build_course_url(cid),
                'course_id': cid,
            }]
        return []

    def _init_browser(self):
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
        except ImportError as exc:
            raise RuntimeError('请先安装 selenium: pip install selenium') from exc

        user_data_dir = os.path.join(
            os.getcwd(), 'browser_data', 'NJGX', str(self.task.id), self.task.username
        )
        os.makedirs(user_data_dir, exist_ok=True)

        options = Options()
        if self.task.is_head == '1':
            options.add_argument('--headless=new')
        options.add_argument(f'--user-data-dir={user_data_dir}')
        options.add_argument('--disable-gpu')
        options.add_argument('--start-maximized')
        options.add_argument('--no-sandbox')

        chromedriver_path = os.getenv('CHROMEDRIVER_PATH', '../driver/chromedriver.exe')
        service = Service(chromedriver_path) if os.path.exists(chromedriver_path) else Service()

        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.maximize_window()
        self.driver.implicitly_wait(10)
        logger.info('[NJGX] 浏览器已启动 headless=%s', self.task.is_head == '1')

    def _is_logged_in(self) -> bool:
        try:
            cookies = self.driver.get_cookies()
            return any(c.get('name') == 'ASP.NET_SessionId' and c.get('value') for c in cookies)
        except Exception:
            return False

    def _ensure_logged_in(self, max_rounds=5):
        for round_idx in range(max_rounds):
            if self._is_logged_in():
                logger.info('[NJGX] 已登录 user=%s', self.task.username)
                return
            logger.info('[NJGX] 第 %s 次尝试登录', round_idx + 1)
            self._auto_login()
            time.sleep(3)
        if not self._is_logged_in():
            raise RuntimeError('登录失败，请检查账号密码或验证码')

    def _auto_login(self):
        from selenium.common import ElementNotInteractableException, TimeoutException
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.wait import WebDriverWait

        self.driver.get(self._build_login_url())
        time.sleep(2)

        try:
            username_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'ctl10_UserName'))
            )
            username_input.clear()
            username_input.send_keys(self.task.username)

            password_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'ctl10_Password'))
            )
            password_input.clear()
            password_input.send_keys(self.task.password)

            capture_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'ctl10_code_op'))
            )
            capture_input.clear()
            capture_input.send_keys(self._recognize_image_captcha())

            self.driver.find_element(By.ID, 'ctl10_ImageButton1').click()
            time.sleep(5)
            self._dismiss_confirm_dialog()
            logger.info('[NJGX] 登录表单已提交 user=%s', self.task.username)
        except TimeoutException:
            logger.error('[NJGX] 超时未找到登录输入框')
            raise
        except ElementNotInteractableException:
            logger.error('[NJGX] 登录输入框不可交互')
            raise

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

    def _recognize_image_captcha(self) -> str:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.wait import WebDriverWait

        try:
            formdata_div = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'UserImageCheck'))
            )
            os.makedirs('png', exist_ok=True)
            save_path = os.path.join('png', f'njgx_{self.task.username}.png')
            if not formdata_div.screenshot(save_path):
                return ''

            try:
                import ddddocr
                ocr = ddddocr.DdddOcr()
                with open(save_path, 'rb') as f:
                    return ocr.classification(f.read())
            except ImportError:
                logger.warning('[NJGX] 未安装 ddddocr，验证码识别跳过')
                return ''
        except Exception:
            logger.exception('[NJGX] 识别图形验证码失败')
            return ''

    def _play_courses(self):
        course_list = self._parse_course_list()
        if not course_list:
            logger.warning('[NJGX] 无课表数据')
            self._mark_course_complete()
            return

        first = course_list[0]
        self.current_course_url = first.get('url') or self._build_course_url(first.get('course_id'))
        self.is_complete = False

        self._open_course_home()

        self._monitor_thread = threading.Thread(
            target=self._check_course_success,
            daemon=True,
            name=f'njgx-monitor-{self.task.id}',
        )
        self._monitor_thread.start()

        while not self.is_complete and self.is_running:
            time.sleep(1)

        logger.info('[NJGX] 播放流程结束 user=%s', self.task.username)

    def _open_course_home(self):
        if self.is_complete:
            return

        self.driver.switch_to.default_content()
        logger.info('[NJGX] 打开课程页: %s', self.current_course_url)
        self.driver.get(self.current_course_url)
        time.sleep(5)

        if self._find_and_play_first_unfinished():
            logger.info('[NJGX] 已开始播放未完成课程')
            return

        logger.info('[NJGX] 无未完成课程，任务完成')
        self._mark_course_complete()

    def _switch_to_playframe(self) -> bool:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.wait import WebDriverWait

        try:
            self.driver.switch_to.default_content()
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'playframeNew'))
            )
            self.driver.switch_to.frame('playframeNew')
            logger.info('[NJGX] 已切换到 playframeNew iframe')
            return True
        except Exception:
            logger.exception('[NJGX] 切换 playframeNew 失败')
            return False

    def _find_and_play_first_unfinished(self) -> bool:
        if not self._switch_to_playframe():
            return False
        return self._click_first_unfinished_in_form()

    def _click_first_unfinished_in_form(self) -> bool:
        """在 form1 第三个 div 的课程列表中点击第一个未完成课程。"""
        from selenium.webdriver.common.by import By

        try:
            form1 = self.driver.find_element(By.ID, 'form1')
            divs = form1.find_elements(By.XPATH, './div')
            if len(divs) < 3:
                logger.warning('[NJGX] form1 下 div 不足 3 个')
                return False

            scroll_div = divs[2].find_element(
                By.XPATH,
                ".//div[@style='overflow: scroll; overflow-x: hidden; height: 200;']",
            )
            links = scroll_div.find_elements(By.TAG_NAME, 'a')
            if not links:
                logger.warning('[NJGX] 未找到课程链接')
                return False

            for link in links:
                status = (link.text or '').strip()
                course_name = self.driver.execute_script(
                    "return arguments[0].previousSibling ? arguments[0].previousSibling.textContent.trim() : '';",
                    link,
                )
                course_name = (course_name or '').replace('&lt;', '').strip()
                logger.info('[NJGX] 课程: %s 状态: %s', course_name, status)

                if status != '已完成':
                    logger.info('[NJGX] 点击播放: %s', course_name)
                    link.click()
                    time.sleep(2)
                    return True

            return False
        except Exception:
            logger.exception('[NJGX] 查找未完成课程失败')
            return False
        finally:
            self.driver.switch_to.default_content()

    def _mark_course_complete(self):
        self.is_complete = True
        if not self._stopped and update_task_fields(self.task, status='2'):
            logger.info('[NJGX] 任务 id=%s 已标记完成', self.task.id)

    def _check_course_success(self):
        """监听 spanThisProgress 进度，100% 时继续下一节。"""
        from selenium.webdriver.common.by import By

        sleep_time = 10
        logger.info('[NJGX] 开始监听播放进度 user=%s', self.task.username)

        while not self.is_complete and self.is_running:
            if self._check_page_error():
                logger.warning('[NJGX] 页面异常，重新打开课程页')
                self._open_course_home()
                time.sleep(10)
                continue

            try:
                progress_el = self.driver.find_element(By.ID, 'spanThisProgress')
                progress_value = float((progress_el.text or '0').strip())
                logger.info('[NJGX] 播放进度: %.1f%%', progress_value)

                if progress_value >= 100:
                    logger.info('[NJGX] 当前小节已完成，查找下一节')
                    self._open_course_home()
                    time.sleep(5)
            except Exception as exc:
                logger.debug('[NJGX] 获取进度失败: %s', exc)

            time.sleep(sleep_time)

        logger.info('[NJGX] 播放监控结束 user=%s', self.task.username)

    def _check_page_error(self) -> bool:
        try:
            page_source = (self.driver.page_source or '').lower()
            keywords = ['502', '无法访问', '404', '500 internal server error', 'bad gateway']
            return any(k in page_source for k in keywords)
        except Exception:
            return True

    def _cleanup(self):
        if self.driver:
            try:
                self.driver.quit()
                logger.info('[NJGX] 浏览器已关闭')
            except Exception:
                logger.exception('[NJGX] 关闭浏览器失败')
            finally:
                self.driver = None
