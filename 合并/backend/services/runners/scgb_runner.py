"""
四川干部网络学院（SCGB）任务执行器

网站编码：SCGB
参考：selenium_demo/四川干部网络学院/scgb.py
"""
import json
import time

from models import db
from services.task_runner import register_runner, update_task_fields
from services.runners.selenium_runner import SeleniumTaskRunner

SCGB_HOME_URL = 'https://web.scgb.gov.cn/#/index'


@register_runner('SCGB')
class ScgbTaskRunner(SeleniumTaskRunner):
    """四川干部网络学院执行器，支持图形验证码登录 + 手机短信验证码。"""

    def __init__(self, task, website):
        super().__init__(task, website)
        self.nick_name = ''
        self.organ_name = ''

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
            self._log_info('已登录，跳过登录流程 user=%s', self.task.username)
            return 'ready'

        self._log_info('开始自动登录 user=%s', self.task.username)
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
                        self._log_warning('图形验证码错误，重试 %s/%s', retry_count + 1, max_retry)
                        self._close_modal()
                        continue
                    self._log_error('登录失败: %s', message.text)
                    return 'failed'
                except TimeoutException:
                    self._log_info('图形验证码通过，等待手机验证码 user=%s', self.task.username)
                    return 'waiting_sms'

            except ElementNotInteractableException:
                self._log_error('登录输入框不可交互')
                return 'failed'
            except Exception:
                self._log_exception('登录异常 retry=%s', retry_count + 1)

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
                self._log_info('手机验证码验证成功 user=%s', self.task.username)
                return True, '验证成功，开始学习'

            self._close_modal()
            phone_input.clear()
            return False, '验证码错误或已过期'
        except Exception as exc:
            self._log_exception('提交手机验证码失败')
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

    def run_main(self):
        self._log_info('开始主流程 task=%s user=%s', self.task.id, self.task.username)
        try:
            self._open_course_and_play()
            self._start_monitor_thread(self._monitor_play_progress)
            self._wait_until_complete()
            self._sync_task_status()
        except Exception:
            db.session.rollback()
            update_task_fields(self.task, status='1')
            raise

    def _open_course_and_play(self):
        self._log_info('打开个人中心检查学习进度')
        self.driver.get('https://web.scgb.gov.cn/#/personal')
        time.sleep(5)

        if self.task.class_id:
            self._log_info('目标课程 class_id=%s', self.task.class_id)

        self.is_complete = False

    def _monitor_play_progress(self):
        sleep_time = 15
        max_idle_rounds = 20
        idle_rounds = 0

        while not self.is_complete and idle_rounds < max_idle_rounds:
            try:
                if self.check_page_error():
                    self._log_warning('页面异常，刷新个人中心')
                    self.driver.get('https://web.scgb.gov.cn/#/personal')
                    time.sleep(10)
                    continue

                self._log_info('检测学习进度中...')
                idle_rounds += 1
            except Exception as exc:
                self._log_warning('进度检测异常: %s', exc)

            time.sleep(sleep_time)

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
            self._log_error('localStorage store 格式错误')
        return False

    def _recognize_image_captcha(self) -> str:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.wait import WebDriverWait

        try:
            formdata_div = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'validate-form-img'))
            )
            return self._recognize_captcha_screenshot(formdata_div, f'{self.task.username}.png')
        except Exception:
            self._log_exception('识别图形验证码失败')
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
