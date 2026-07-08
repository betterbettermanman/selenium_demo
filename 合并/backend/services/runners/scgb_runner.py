"""
四川干部网络学院（SCGB）任务执行器

网站编码：SCGB
参考：selenium_demo/四川干部网络学院/scgb.py
"""
import json
import logging
import os
import time

from models import db
from services.task_runner import BaseTaskRunner, register_runner, update_task_fields

logger = logging.getLogger(__name__)

SCGB_HOME_URL = 'https://web.scgb.gov.cn/#/index'


@register_runner('SCGB')
class ScgbTaskRunner(BaseTaskRunner):
    """四川干部网络学院执行器，支持图形验证码登录 + 手机短信验证码。"""

    def __init__(self, task, website):
        super().__init__(task, website)
        self.is_complete = False
        self.nick_name = ''
        self.organ_name = ''

    # ------------------------------------------------------------------
    # 登录阶段（同步，供 start_task 调用）
    # ------------------------------------------------------------------
    def prepare_login(self):
        from selenium.common import ElementNotInteractableException, TimeoutException
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.wait import WebDriverWait

        self._init_browser()
        self.driver.get(SCGB_HOME_URL)

        try:
            notice = WebDriverWait(self.driver, 2).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'close'))
            )
            if notice and notice.is_displayed():
                notice.click()
            time.sleep(1)
        except TimeoutException:
            pass

        if self._is_logged_in():
            logger.info('[SCGB] 已登录，跳过登录流程 user=%s', self.task.username)
            return 'ready'

        logger.info('[SCGB] 开始自动登录 user=%s', self.task.username)
        max_retry = 3
        for retry_count in range(max_retry):
            try:
                username_input = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="请输入您的用户名"]'))
                )
                username_input.clear()
                username_input.send_keys(self.task.username)

                password_input = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="请输入您的密码"]'))
                )
                password_input.clear()
                password_input.send_keys(self.task.password)

                capture_input = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="请输入验证码"]'))
                )
                capture_input.clear()
                captcha = self._recognize_image_captcha()
                capture_input.send_keys(captcha or '1234')

                login_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//div[@class="ivu-form-item-content"]//button'))
                )
                login_button.click()

                try:
                    message = WebDriverWait(self.driver, 5).until(
                        EC.visibility_of_element_located((By.XPATH, '//div[@class="ivu-modal-header"]//p'))
                    )
                    if message.text == '验证码错误或已过期，请重新输入！':
                        logger.warning('[SCGB] 图形验证码错误，重试 %s/%s', retry_count + 1, max_retry)
                        self._close_modal()
                        continue
                    logger.error('[SCGB] 登录失败: %s', message.text)
                    return 'failed'
                except TimeoutException:
                    logger.info('[SCGB] 图形验证码通过，等待手机验证码 user=%s', self.task.username)
                    return 'waiting_sms'

            except ElementNotInteractableException:
                logger.error('[SCGB] 登录输入框不可交互')
                return 'failed'
            except Exception:
                logger.exception('[SCGB] 登录异常 retry=%s', retry_count + 1)

        return 'failed'

    def submit_sms_code(self, code: str):
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.wait import WebDriverWait

        if not self.driver:
            return False, '浏览器未初始化'

        try:
            phone_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="请输入验证码"]'))
            )
            phone_input.clear()
            phone_input.send_keys(code)

            login_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//div[@class="ivu-form-item-content"]//button'))
            )
            login_button.click()
            time.sleep(3)

            if self._is_logged_in():
                update_task_fields(
                    self.task,
                    nick_name=self.nick_name,
                    organ_name=self.organ_name,
                )
                logger.info('[SCGB] 手机验证码验证成功 user=%s', self.task.username)
                return True, '验证成功，开始学习'

            self._close_modal()
            phone_input.clear()
            return False, '验证码错误或已过期'
        except Exception as exc:
            logger.exception('[SCGB] 提交手机验证码失败')
            return False, str(exc)

    def resend_sms_code(self):
        from selenium.common import NoSuchElementException, TimeoutException
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.wait import WebDriverWait

        if not self.driver:
            return False, '浏览器未初始化'

        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'tips'))
            )
            direct_span = element.find_element(By.TAG_NAME, 'span')
            span_text = direct_span.text.strip()
            if span_text == '重发验证码':
                direct_span.click()
                return True, '验证码已重发'
            return False, span_text or '暂时无法重发'
        except (TimeoutException, NoSuchElementException):
            return False, '未找到重发验证码按钮'
        except Exception as exc:
            return False, str(exc)

    # ------------------------------------------------------------------
    # 主流程（验证码通过后异步执行）
    # ------------------------------------------------------------------
    def run_main(self):
        import threading

        logger.info('[SCGB] 开始主流程 task=%s user=%s', self.task.id, self.task.username)
        try:
            self._open_course_and_play()
            monitor = threading.Thread(
                target=self._monitor_play_progress,
                daemon=True,
                name=f'scgb-monitor-{self.task.id}',
            )
            monitor.start()

            while not self.is_complete and monitor.is_alive():
                time.sleep(1)

            if self.is_complete:
                update_task_fields(self.task, status='2')
                logger.info('[SCGB] 任务完成 id=%s', self.task.id)
            else:
                update_task_fields(self.task, status='1')
                logger.warning('[SCGB] 任务未完成 id=%s', self.task.id)
        except Exception:
            db.session.rollback()
            update_task_fields(self.task, status='1')
            raise

    def _open_course_and_play(self):
        """打开课程页面（可按 task.class_id / courses 扩展）。"""
        from selenium.webdriver.common.by import By

        logger.info('[SCGB] 打开个人中心检查学习进度')
        self.driver.get('https://web.scgb.gov.cn/#/personal')
        time.sleep(5)

        if self.task.class_id:
            logger.info('[SCGB] 目标课程 class_id=%s', self.task.class_id)
            # TODO: 根据 class_id 跳转到具体课程页，参考 scgb.py exec_main3

        self.is_complete = False

    def _monitor_play_progress(self):
        """监听学习进度（示例骨架，可对接 scgb.py check_course_success）。"""
        sleep_time = 15
        max_idle_rounds = 20
        idle_rounds = 0

        while not self.is_complete and idle_rounds < max_idle_rounds:
            try:
                if self._check_page_error():
                    logger.warning('[SCGB] 页面异常，刷新个人中心')
                    self.driver.get('https://web.scgb.gov.cn/#/personal')
                    time.sleep(10)
                    continue

                # TODO: 对接真实进度检测逻辑
                logger.info('[SCGB] 检测学习进度中...')
                idle_rounds += 1
            except Exception as exc:
                logger.warning('[SCGB] 进度检测异常: %s', exc)

            time.sleep(sleep_time)

        # 示例：检测完成后标记（实际应按课时是否达标判断）
        # self.is_complete = True

    # ------------------------------------------------------------------
    # 工具方法
    # ------------------------------------------------------------------
    def _init_browser(self):
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
        except ImportError as exc:
            raise RuntimeError('请先安装 selenium: pip install selenium') from exc

        user_data_dir = os.path.join(
            os.getcwd(), 'browser_data', 'SCGB', str(self.task.id), self.task.username
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
        logger.info('[SCGB] 浏览器已启动')

    def _is_logged_in(self) -> bool:
        store = self._get_local_storage('store')
        if not store:
            return False
        try:
            store_json = json.loads(store)
            session = store_json.get('session', {})
            if 'accessToken' in session:
                self.nick_name = session.get('nickName', '')
                self.organ_name = session.get('organName', '')
                return True
        except json.JSONDecodeError:
            logger.error('[SCGB] localStorage store 格式错误')
        return False

    def _get_local_storage(self, key: str):
        try:
            return self.driver.execute_script(f"return window.localStorage.getItem('{key}');")
        except Exception:
            return None

    def _recognize_image_captcha(self) -> str:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.wait import WebDriverWait

        try:
            formdata_div = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'validate-form-img'))
            )
            os.makedirs('png', exist_ok=True)
            save_path = os.path.join('png', f'{self.task.username}.png')
            if not formdata_div.screenshot(save_path):
                return ''

            try:
                import ddddocr
                ocr = ddddocr.DdddOcr()
                with open(save_path, 'rb') as f:
                    return ocr.classification(f.read())
            except ImportError:
                logger.warning('[SCGB] 未安装 ddddocr，使用占位验证码')
                return ''
        except Exception:
            logger.exception('[SCGB] 识别图形验证码失败')
            return ''

    def _close_modal(self):
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.wait import WebDriverWait

        modals = self.driver.find_elements(By.XPATH, '//div[@class="ivu-modal"]')
        for modal in modals:
            if modal.is_displayed():
                try:
                    confirm_btn = modal.find_element(
                        By.XPATH, './/div[@class="ivu-modal-footer"]//button[.//span[text()="确定"]]'
                    )
                    confirm_btn.click()
                    WebDriverWait(self.driver, 5).until(EC.invisibility_of_element(modal))
                except Exception:
                    pass
                break

    def _check_page_error(self) -> bool:
        try:
            page_source = (self.driver.page_source or '').lower()
            keywords = ['502', '无法访问', '404', '500 internal server error']
            return any(k in page_source for k in keywords)
        except Exception:
            return True

    def _cleanup(self):
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                logger.exception('[SCGB] 关闭浏览器失败')
            finally:
                self.driver = None
