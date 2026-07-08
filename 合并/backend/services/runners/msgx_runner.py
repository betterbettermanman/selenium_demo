"""
眉山公需课（MSGX）任务执行器

网站编码：MSGX
参考：selenium_demo/眉山市专业技术人员网络培训网/main.py
"""
import logging
import os
import re
import threading
import time
from urllib.parse import unquote

from models import db
from services.task_runner import BaseTaskRunner, register_runner, update_task_fields

logger = logging.getLogger(__name__)

MSGX_LOGIN_URL = 'http://meishan.scjxjypx.com/'
CHINAHRT_TRAIN_LIST = 'https://gp.chinahrt.com/index.html#/v_trainplan_list'
CHINAHRT_USER_SET = 'https://gp.chinahrt.com/index.html#/v_user_set'
CHINAHRT_COURSE_DETAIL_API = 'https://gp.chinahrt.com/gp6/lms/stu/course/courseDetail?'


@register_runner('MSGX')
class MsgxTaskRunner(BaseTaskRunner):
    """眉山市专业技术人员网络培训网执行器。"""

    def __init__(self, task, website):
        super().__init__(task, website)
        self.is_complete = False
        self.is_running = True
        self.current_course_id = ''
        self.trainplan_id = ''
        self.platform_id = ''
        self.jwt_token = ''
        self.headers = {
            'User-Agent': 'Mozilla/5.0',
            'Accept': '*/*',
            'Host': 'gp.chinahrt.com',
        }
        self._monitor_thread = None
        self._play_status_thread = None

    def run_main(self):
        logger.info(
            '[MSGX] 开始任务 id=%s user=%s course=%s headless=%s',
            self.task.id,
            self.task.username,
            self._get_target_course_name(),
            self.task.is_head,
        )
        try:
            self._init_browser()
            self._ensure_logged_in()
            result = self._open_home()
            if result == 'course':
                self._start_monitors()
                while self.is_running and not self.is_complete:
                    time.sleep(1)
            elif result == 'complete':
                self.is_complete = True

            if self.is_complete and not self._stopped:
                update_task_fields(self.task, status='2')
                logger.info('[MSGX] 任务 id=%s 执行完成', self.task.id)
            elif not self._stopped:
                update_task_fields(self.task, status='1')
        except Exception:
            logger.exception('[MSGX] 任务 id=%s 执行失败', self.task.id)
            db.session.rollback()
            update_task_fields(self.task, status='1')
            raise
        finally:
            self.is_running = False
            self._cleanup()

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

    def _init_browser(self):
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
        except ImportError as exc:
            raise RuntimeError('请先安装 selenium: pip install selenium') from exc

        user_data_dir = os.path.join(
            os.getcwd(), 'browser_data', 'MSGX', str(self.task.id), self.task.username
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
        logger.info('[MSGX] 浏览器已启动')

    def _get_session_storage(self, key: str):
        try:
            return self.driver.execute_script(f"return window.sessionStorage.getItem('{key}');")
        except Exception:
            return None

    def _is_logged_in(self) -> bool:
        token = self._get_session_storage('jwtToken')
        if token:
            self.jwt_token = token
            self.headers['hrttoken'] = token
            return True
        return False

    def _ensure_logged_in(self, max_rounds=5):
        for idx in range(max_rounds):
            self._auto_login()
            time.sleep(3)
            self.driver.get(CHINAHRT_USER_SET)
            time.sleep(2)
            if self._is_logged_in():
                real_name = self._get_session_storage('realName') or ''
                organ_name = self._get_session_storage('orgName') or ''
                update_task_fields(self.task, nick_name=real_name, organ_name=organ_name)
                logger.info('[MSGX] 已登录 %s【%s】', real_name, organ_name)
                return
            logger.warning('[MSGX] 第 %s 次登录未成功', idx + 1)
        raise RuntimeError('登录失败，请检查账号密码或验证码')

    def _auto_login(self):
        from selenium.common import ElementNotInteractableException, TimeoutException
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.wait import WebDriverWait

        self.driver.get(MSGX_LOGIN_URL)
        time.sleep(3)

        try:
            iframe = self.driver.find_element(By.XPATH, '//div[@class="login-box"]/iframe')
            self.driver.switch_to.frame(iframe)

            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="账号"]'))
            ).send_keys(self.task.username)

            pwd = self.driver.find_element(By.XPATH, '//input[@placeholder="密码"]')
            pwd.clear()
            pwd.send_keys(self.task.password)

            captcha_input = self.driver.find_element(By.XPATH, '//input[@placeholder="验证码"]')
            captcha_input.clear()
            captcha_input.send_keys(self._recognize_image_captcha())

            self.driver.find_element(
                By.XPATH,
                '//button[@class="el-button logbtn cb mt5 el-button--default el-button--small"]',
            ).click()
            logger.info('[MSGX] 登录表单已提交')
        except (TimeoutException, ElementNotInteractableException):
            logger.exception('[MSGX] 登录失败')
            raise
        finally:
            self.driver.switch_to.default_content()

    def _recognize_image_captcha(self) -> str:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.wait import WebDriverWait

        try:
            img = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//img[@alt="验证码"]'))
            )
            os.makedirs('png', exist_ok=True)
            save_path = os.path.join('png', f'msgx_{self.task.username}.png')
            if not img.screenshot(save_path):
                return ''
            try:
                import ddddocr
                ocr = ddddocr.DdddOcr()
                with open(save_path, 'rb') as f:
                    return ocr.classification(f.read())
            except ImportError:
                logger.warning('[MSGX] 未安装 ddddocr')
                return ''
        except Exception:
            logger.exception('[MSGX] 验证码识别失败')
            return ''

    def _open_home(self) -> str:
        """打开培训计划列表，处理激活/学习/考试。返回 course / exam / complete。"""
        from selenium.common import NoSuchElementException
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.wait import WebDriverWait

        if self.is_complete:
            return 'complete'

        logger.info('[MSGX] 打开培训计划列表')
        self.driver.get(CHINAHRT_TRAIN_LIST)
        time.sleep(5)

        parents = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.fl.ml30'))
        )
        target_name = self._get_target_course_name()
        current_course = None

        for parent in parents:
            course_div = parent.find_element(By.CLASS_NAME, 'course-title')
            span_values = [s.text for s in course_div.find_elements(By.TAG_NAME, 'span')]
            logger.info('[MSGX] 课程列表项: %s', span_values)
            if not target_name or target_name in span_values or any(target_name in v for v in span_values):
                current_course = parent
                break

        if current_course is None and parents:
            current_course = parents[0]
            logger.info('[MSGX] 未匹配到指定课程名，使用第一项')

        if current_course is None:
            logger.warning('[MSGX] 未找到课程')
            self.is_running = False
            return 'complete'

        column_wrap = current_course.find_element(By.CLASS_NAME, 'column-wrap')
        course_title = current_course.find_element(By.CLASS_NAME, 'course-title')

        try:
            img_src = course_title.find_element(By.TAG_NAME, 'img').get_attribute('src') or ''
            if 'static/images/icon-label3.png' in img_src:
                logger.info('[MSGX] 课程已完成标记')
                self.is_running = False
                self.is_complete = True
                return 'complete'
        except NoSuchElementException:
            pass

        video_process = column_wrap.find_elements(By.CLASS_NAME, 'el-progress__text')
        if video_process and video_process[0].text != '已学100%':
            try:
                column_wrap.find_element(By.XPATH, ".//button[contains(text(), '去激活')]").click()
                logger.info('[MSGX] 点击去激活')
                time.sleep(5)
                return self._open_home()
            except NoSuchElementException:
                pass
            try:
                column_wrap.find_element(
                    By.XPATH,
                    ".//button[contains(text(), '去学习') or contains(text(), '继续学习')]",
                ).click()
                logger.info('[MSGX] 进入课程学习')
                self._open_course()
                return 'course'
            except NoSuchElementException:
                logger.warning('[MSGX] 未找到学习按钮')

        if len(video_process) > 1 and video_process[1].text != '已考100%':
            try:
                column_wrap.find_element(By.XPATH, ".//button[contains(text(), '去考试')]").click()
                logger.info('[MSGX] 进入考试（需人工或后续扩展自动答题）')
                return 'exam'
            except NoSuchElementException:
                pass

        logger.info('[MSGX] 当前培养计划项已处理完毕')
        self.is_running = False
        self.is_complete = True
        return 'complete'

    def _open_course(self):
        """打开课程目录并进入第一个未完成小节播放。"""
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.wait import WebDriverWait

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.course-list.cb'))
        )
        time.sleep(3)

        course_list_div = self.driver.find_element(By.CSS_SELECTOR, 'div.course-list.cb')
        ul_element = course_list_div.find_element(By.TAG_NAME, 'ul')
        all_li = ul_element.find_elements(By.TAG_NAME, 'li')

        for li in all_li:
            progress = li.find_element(By.CSS_SELECTOR, 'div.progress-line').find_element(By.TAG_NAME, 'span').text
            if progress == '100%':
                continue
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(li.find_element(By.CSS_SELECTOR, 'div'))).click()
            break

        original_window = self.driver.current_window_handle
        WebDriverWait(self.driver, 10).until(lambda d: len(d.window_handles) > 1)
        for handle in self.driver.window_handles:
            if handle != original_window:
                self.driver.switch_to.window(handle)
                break

        time.sleep(3)
        catalog = self.driver.find_element(By.CSS_SELECTOR, 'div.course-catalog.m0')
        for li in catalog.find_elements(By.TAG_NAME, 'li'):
            links = li.find_elements(By.TAG_NAME, 'a')
            if len(links) < 2:
                continue
            if '已学完' in links[1].text:
                continue
            links[1].click()
            break

        time.sleep(5)
        first_new = self.driver.current_window_handle
        second_new = None
        for handle in self.driver.window_handles:
            if handle not in (original_window, first_new):
                second_new = handle
                self.driver.switch_to.window(handle)
                break

        if first_new and second_new:
            self.driver.switch_to.window(first_new)
            self.driver.close()
            self.driver.switch_to.window(second_new)

        iframe = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="video-container"]/iframe'))
        )
        self.driver.switch_to.frame(iframe)
        pause = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//div[starts-with(@class, "pausecenter")]'))
        )
        pause.click()

        self.current_course_id = self._extract_hash_param(self.driver.current_url, 'courseId') or ''
        self.trainplan_id = self._extract_hash_param(self.driver.current_url, 'trainplanId') or ''
        self.platform_id = self._extract_hash_param(self.driver.current_url, 'platformId') or ''
        logger.info('[MSGX] 开始播放 courseId=%s', self.current_course_id)

    def _extract_hash_param(self, url: str, param_name: str) -> str:
        match = re.search(rf'{param_name}=([^&]+)', url)
        return unquote(match.group(1)) if match else ''

    def _start_monitors(self):
        self._monitor_thread = threading.Thread(
            target=self._check_course_success,
            daemon=True,
            name=f'msgx-monitor-{self.task.id}',
        )
        self._play_status_thread = threading.Thread(
            target=self._check_course_play_status,
            daemon=True,
            name=f'msgx-play-{self.task.id}',
        )
        self._monitor_thread.start()
        self._play_status_thread.start()

    def _check_course_success(self):
        import requests

        sleep_time = 30
        while self.is_running:
            if self.current_course_id and self.jwt_token:
                try:
                    resp = requests.get(
                        CHINAHRT_COURSE_DETAIL_API,
                        headers=self.headers,
                        params={
                            'courseId': self.current_course_id,
                            'trainplanId': self.trainplan_id,
                            'platformId': self.platform_id,
                        },
                        timeout=30,
                    )
                    detail = resp.json().get('data', {})
                    percent = detail.get('learnPercent', 0)
                    logger.info('[MSGX] 课程 %s 学习进度: %s%%', self.current_course_id, percent)
                    if percent == 100:
                        if len(self.driver.window_handles) > 1:
                            self.driver.close()
                            self.driver.switch_to.window(self.driver.window_handles[0])
                        self.current_course_id = ''
                        threading.Thread(target=self._open_home, daemon=True).start()
                        sleep_time = 60
                except Exception as exc:
                    logger.warning('[MSGX] 查询课程进度失败: %s', exc)
                    sleep_time = 20
            time.sleep(sleep_time)

    def _check_course_play_status(self):
        from selenium.common import NoSuchElementException, TimeoutException
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.wait import WebDriverWait

        while self.is_running:
            time.sleep(10)
            try:
                element = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, '//span[text()="课程评价"]'))
                )
                # 判断是否可见（Selenium 内置方法）
                is_displayed = element.is_displayed()
                print(f"元素是否可见: {is_displayed}")
                if is_displayed:
                    logger.info('[MSGX] 检测到课程评价，当前小节完成')
                    if len(self.driver.window_handles) > 1:
                        self.driver.close()
                        self.driver.switch_to.window(self.driver.window_handles[0])
                    time.sleep(5)
                    continue
            except TimeoutException:
                pass

            try:
                pause = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, '//div[starts-with(@class, "pausecenter")]'))
                )
                if pause.value_of_css_property('display') != 'none':
                    pause.click()
            except (TimeoutException, NoSuchElementException):
                pass
            except Exception as exc:
                logger.debug('[MSGX] 播放状态检测: %s', exc)

    def _cleanup(self):
        if self.driver:
            try:
                self.driver.quit()
                logger.info('[MSGX] 浏览器已关闭')
            except Exception:
                logger.exception('[MSGX] 关闭浏览器失败')
            finally:
                self.driver = None
