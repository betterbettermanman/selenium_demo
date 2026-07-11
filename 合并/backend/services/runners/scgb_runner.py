"""
四川干部网络学院（SCGB）任务执行器

网站编码：SCGB
参考：selenium_demo/四川干部网络学院/scgb.py
"""
import json
import re
import time
from urllib.parse import parse_qs, urlparse

import requests

from models import db
from services.runners.selenium_runner import SeleniumTaskRunner
from services.task_runner import register_runner, update_task_fields

SCGB_HOME_URL = 'https://web.scgb.gov.cn/#/index'
SCGB_API_BASE = 'https://api.scgb.gov.cn/api/services/app'


@register_runner('SCGB')
class ScgbTaskRunner(SeleniumTaskRunner):
    """四川干部网络学院执行器，支持图形验证码登录 + 手机短信验证码。"""

    def __init__(self, task, website):
        super().__init__(task, website)
        self.nick_name = ''
        self.organ_name = ''
        self.current_course_id = ''
        self.is_must = True
        self.api_headers = {
            'User-Agent': 'Mozilla/5.0',
            'Accept': '*/*',
        }

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
        """参考 scgb.py open_home：获取当前课程并打开播放页。"""
        self._sync_api_headers()
        self._log_info('打开个人中心检查学习进度')
        self.driver.get('https://web.scgb.gov.cn/#/personal')
        time.sleep(3)

        courses = self._parse_course_items(self.task.courses)
        if courses:
            course = self._get_current_course(courses)
            if not course:
                self._log_info('自定义课程已全部学完')
                self.is_complete = True
                return
            self._open_custom_course(course)
        else:
            if not self.task.class_id:
                self._log_warning('未配置 class_id 且无课表，无法自动播放')
                return
            self._log_info('目标班级 class_id=%s', self.task.class_id)
            if not self._check_study_time():
                return
            label = '必修' if self.is_must else '选修'
            self._open_class_course_detail(label)

        self.is_complete = False

    def _monitor_play_progress(self):
        sleep_time = 30
        null_course_rounds = 0

        while not self.is_complete and self.is_running:
            try:
                if self.check_page_error():
                    self._log_warning('页面异常，重新打开课程')
                    self._open_course_and_play()
                    time.sleep(10)
                    continue

                if not self.current_course_id:
                    null_course_rounds += 1
                    if null_course_rounds >= 10:
                        self._log_warning('连续未获取到课程ID，停止监控')
                        break
                    time.sleep(10)
                    continue
                null_course_rounds = 0

                detail = self._fetch_course_detail(self.current_course_id)
                if not detail:
                    sleep_time = 15
                elif detail['totalPeriod'] <= detail['watchTimes']:
                    self._log_info('课程 %s 已观看完成', self.current_course_id)
                    self._mark_custom_course_done(self.current_course_id)
                    if self._has_more_study_work():
                        self.current_course_id = ''
                        self._open_course_and_play()
                        sleep_time = 40
                    else:
                        self._log_info('全部课程已学完')
                        self.is_complete = True
                        break
                else:
                    remain = int(detail['totalPeriod']) - int(detail['watchTimes'])
                    sleep_time = max(30, min(remain, 1200))
                    self._log_info(
                        '课程 %s 播放中 total=%s watched=%s 下次检测间隔=%ss',
                        self.current_course_id,
                        detail['totalPeriod'],
                        detail['watchTimes'],
                        sleep_time,
                    )
                    self._click_video_play_button()
            except Exception as exc:
                self._log_warning('进度检测异常: %s', exc)
                sleep_time = 20

            time.sleep(sleep_time)

    def _get_current_course(self, courses):
        for course in courses:
            if not isinstance(course, dict):
                continue
            if str(course.get('status', '0')) != '1':
                return course
        return None

    def _open_custom_course(self, course):
        course_id = course.get('id')
        if not course_id:
            self._log_warning('课表条目缺少 id，跳过: %s', course)
            return

        self.driver.get(SCGB_HOME_URL)
        time.sleep(2)
        class_id = course.get('classId') or self.task.class_id
        if class_id:
            course_url = (
                f'https://web.scgb.gov.cn/#/course?id={course_id}'
                f'&className=&classId={class_id}'
            )
        else:
            course_url = f'https://web.scgb.gov.cn/#/course?id={course_id}&className='
        self._log_info('打开课程页面: %s', course_url)
        self.driver.get(course_url)
        time.sleep(2)
        self._close_course_modal2()
        self._click_video_play_button()
        self.current_course_id = course_id
        self._log_info('当前课程ID: %s', self.current_course_id)

    def _open_class_course_detail(self, label: str):
        from selenium.common import TimeoutException
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.wait import WebDriverWait

        self._log_info('进行%s学习', label)
        self.driver.get(f'https://web.scgb.gov.cn/#/myClass?id={self.task.class_id}&collected=1')
        time.sleep(1)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, 'el-loading-spinner'))
            )
            self._close_class_confirm_modal()
        except TimeoutException:
            pass

        required_div = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//div[text()=' {label} ']"))
        )
        WebDriverWait(self.driver, 20).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, 'el-loading-spinner'))
        )
        required_div.click()
        time.sleep(1)

        has_next_page = self._play_first_unfinished_in_course_list()
        while has_next_page:
            try:
                next_btn = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'ivu-page-next'))
                )
                WebDriverWait(self.driver, 20).until(
                    EC.invisibility_of_element_located((By.CLASS_NAME, 'el-loading-spinner'))
                )
                next_btn.click()
                time.sleep(2)
                has_next_page = self._play_first_unfinished_in_course_list()
            except TimeoutException:
                self._log_warning('未找到下一页按钮，结束翻页')
                break

    def _play_first_unfinished_in_course_list(self) -> bool:
        """在当前课程列表页查找未完成视频并打开，返回 True 表示需要翻页。"""
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.wait import WebDriverWait

        skip_videos = set(self.task.no_play_videos or [])
        required_div = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'course-list'))
        )
        child_divs = required_div.find_elements(By.XPATH, './div')
        for child_div in child_divs:
            try:
                span_elements = child_div.find_elements(By.TAG_NAME, 'span')
                if len(span_elements) < 4:
                    continue
                if self._compare_hours_str(span_elements[3].text.strip()):
                    continue

                WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(child_div))
                handles_before = self.driver.window_handles
                WebDriverWait(self.driver, 20).until(
                    EC.invisibility_of_element_located((By.CSS_SELECTOR, 'div.el-loading-mask.is-fullscreen'))
                )
                child_div.click()
                WebDriverWait(self.driver, 10).until(
                    EC.number_of_windows_to_be(len(handles_before) + 1)
                )
                all_handles = self.driver.window_handles
                new_handle = [h for h in all_handles if h not in handles_before][0]
                self.driver.switch_to.window(new_handle)
                new_page_url = self.driver.current_url
                course_id = self._extract_id_from_url(new_page_url)
                if course_id in skip_videos:
                    self.driver.close()
                    self.driver.switch_to.window(handles_before[0])
                    continue

                for handle in all_handles:
                    if handle != new_handle:
                        self.driver.switch_to.window(handle)
                        self.driver.close()
                self.driver.switch_to.window(new_handle)
                self.current_course_id = course_id or ''
                self._log_info('当前课程ID: %s', self.current_course_id)
                self._close_course_modal2()
                self._click_video_play_button()
                return False
            except Exception as exc:
                self._log_warning('处理课程列表项失败: %s', exc)
        return True

    def _check_study_time(self) -> bool:
        """检查班级必修/选修学时是否完成，并设置 is_must。"""
        if not self.task.class_id:
            return False

        url = f'{SCGB_API_BASE}/class/app/getClassDetailByUserId?classId={self.task.class_id}'
        try:
            response = requests.get(url=url, headers=self.api_headers, timeout=10)
            response.raise_for_status()
            result = response.json().get('result', {})
            required_hours = round(int(result.get('requiredPeriod', 0)) / 3600, 2)
            elective_hours = round(int(result.get('electivePeriod', 0)) / 3600, 2)
            self._log_info('学习进度 必修=%s 选修=%s', required_hours, elective_hours)
            if int(result.get('electivePeriod', 0)) < int(result.get('classElectiveTimes', 0)) * 3600:
                self.is_must = False
                return True
            if int(result.get('requiredPeriod', 0)) < int(result.get('classTimes', 0)) * 3600:
                self.is_must = True
                return True
            self._log_info('必修和选修已全部学完')
            self.is_complete = True
            return False
        except Exception:
            self._log_exception('查询班级学时失败 class_id=%s', self.task.class_id)
            return False

    def _has_more_study_work(self) -> bool:
        courses = self._parse_course_items(self.task.courses)
        if courses:
            return self._get_current_course(courses) is not None
        return self._check_study_time()

    def _fetch_course_detail(self, course_id: str):
        url = f'{SCGB_API_BASE}/course/app/getCourseDetailByUserId?'
        payload = {'courseId': course_id, 'classId': self.task.class_id or ''}
        try:
            response = requests.post(url, headers=self.api_headers, json=payload, timeout=10)
            if response.status_code == 401:
                self._log_warning('登录已过期')
                return None
            response.raise_for_status()
            return response.json().get('result')
        except Exception:
            self._log_exception('查询课程详情失败 course_id=%s', course_id)
            return None

    def _mark_custom_course_done(self, course_id: str):
        courses = self._parse_course_items(self.task.courses)
        if not courses:
            return
        updated = []
        changed = False
        for course in courses:
            if isinstance(course, dict) and course.get('id') == course_id:
                course = {**course, 'status': '1'}
                changed = True
            updated.append(course)
        if changed:
            update_task_fields(self.task, courses=updated)

    def _sync_api_headers(self):
        store = self._get_local_storage('store')
        if not store:
            return
        try:
            session = json.loads(store).get('session', {})
            token = session.get('accessToken')
            if token:
                self.api_headers['Authorization'] = f'Bearer {token}'
        except json.JSONDecodeError:
            self._log_error('localStorage store 格式错误')

    def _click_video_play_button(self):
        from selenium.common import TimeoutException
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.wait import WebDriverWait

        try:
            play_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'vjs-big-play-button'))
            )
            play_button.click()
        except TimeoutException:
            pass
        except Exception:
            self._log_warning('点击播放按钮失败，可能已在播放中')

    def _close_course_modal2(self):
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.wait import WebDriverWait

        modals = self.driver.find_elements(By.XPATH, '//div[@class="ivu-modal"]')
        for modal in modals:
            if modal.is_displayed():
                buttons = modal.find_elements(By.XPATH, './/div[@class="ivu-modal-footer"]//button')
                if len(buttons) > 1:
                    buttons[1].click()
                    WebDriverWait(self.driver, 5).until(EC.invisibility_of_element(modal))
                break

    def _close_class_confirm_modal(self):
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.wait import WebDriverWait

        modals = self.driver.find_elements(By.XPATH, '//div[@class="ivu-modal"]')
        for modal in modals:
            if modal.is_displayed():
                confirm_btn = modal.find_element(
                    By.XPATH,
                    './/div[@class="ivu-modal-confirm-footer"]//button[.//span[text()="确定"]]',
                )
                confirm_btn.click()
                WebDriverWait(self.driver, 5).until(EC.invisibility_of_element(modal))
                break

    @staticmethod
    def _extract_id_from_url(url: str):
        parsed_url = urlparse(url)
        hash_part = parsed_url.fragment
        query_start = hash_part.find('?')
        if query_start == -1:
            return None
        query_params = parse_qs(hash_part[query_start + 1:])
        return query_params.get('id', [None])[0]

    @staticmethod
    def _extract_number_from_string(value: str):
        match = re.search(r'\d+\.?\d*', value or '')
        return float(match.group()) if match else None

    def _compare_hours_str(self, hours_str: str) -> bool:
        parts = (hours_str or '').split('/')
        if len(parts) != 2:
            return False
        left = self._extract_number_from_string(parts[0].strip())
        right = self._extract_number_from_string(parts[1].strip())
        return left is not None and right is not None and left == right

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
                self._sync_api_headers()
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
