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
        self.current_course_class_id = ''
        self.is_must = True
        self._last_watch_times = None
        self._watch_times_stale_rounds = 0
        self._stale_reload_count = 0
        self._auth_expired = False
        self._auth_fail_rounds = 0
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
        self._driver_get(SCGB_HOME_URL)

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

                tip = self._wait_login_tip(timeout=5)
                if tip:
                    if tip == '验证码错误或已过期，请重新输入！':
                        self._log_warning('图形验证码错误，重试 %s/%s tip=%s', retry_count + 1, max_retry, tip)
                        self._close_modal()
                        continue
                    # 用户名/密码错误等，直接回传页面提示
                    self._log_error('登录失败: %s', tip)
                    return 'failed', tip

                self._log_info('图形验证码通过，等待手机验证码 user=%s', self.task.username)
                return 'waiting_sms'

            except ElementNotInteractableException:
                self._log_error('登录输入框不可交互')
                return 'failed', '登录输入框不可交互'
            except Exception:
                self._log_exception('登录异常 retry=%s', retry_count + 1)

        return 'failed', '图形验证码多次错误，登录失败'

    def _wait_login_tip(self, timeout: float = 5) -> str:
        """读取登录后弹窗/消息提示文案；无提示返回空串。"""
        from selenium.common import TimeoutException
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.wait import WebDriverWait

        # 弹窗标题（密码错误、验证码错误等）
        try:
            message = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((By.XPATH, '//div[@class="ivu-modal-header"]//p'))
            )
            text = (message.text or '').strip()
            if text:
                return text
        except TimeoutException:
            pass

        # 顶部 Message 提示兜底
        try:
            notices = self.driver.find_elements(
                By.XPATH,
                "//div[contains(@class,'ivu-message')]//span"
                " | //div[contains(@class,'ivu-notice-desc')]"
                " | //div[contains(@class,'ivu-notice-title')]",
            )
            for el in notices:
                text = (el.text or '').strip()
                if text and el.is_displayed():
                    return text
        except Exception:
            pass
        return ''

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
        """直接打开下一门未完成课程并播放，不经过个人中心。"""
        self._sync_api_headers()
        courses = self._parse_course_items(self.task.courses)
        if courses:
            self._sync_courses_progress(courses)
            course = self._get_current_course(courses)
            if not course:
                self._log_info('自定义课程已全部学完')
                self.is_complete = True
                return
            self._log_info('打开下一门自定义课程 id=%s', course.get('id'))
            self._open_custom_course(course)
        else:
            if not self.task.class_id:
                self._log_warning('未配置 class_id 且无课表，无法自动播放')
                return
            self._log_info('目标班级 class_id=%s，直接进入课程列表续播', self.task.class_id)
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
                if not self._is_browser_alive():
                    self._log_error('浏览器会话已断开，停止监控（请重新启动任务）')
                    self.is_running = False
                    break

                if self._auth_expired:
                    self._handle_login_expired()
                    break

                # SPA 源码常误含裸 "404"/"502"，基类 check_page_error 易误判并跳过切课逻辑
                if self._scgb_page_error():
                    self._log_warning('页面异常，先检查登录态再刷新')
                    if not self._ensure_login_valid():
                        self._handle_login_expired()
                        break
                    self._reload_current_course()
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

                # watchTimes 多轮不变：先强制刷新当前课续播，禁止误开「同一门未完成课」空转
                if self._watch_times_stale_rounds >= 2:
                    self._stale_reload_count += 1
                    if self._stale_reload_count >= 3:
                        self._log_warning(
                            '课程 %s 多次刷新仍无进度，跳过并切换下一门',
                            self.current_course_id,
                        )
                        self._skip_stuck_course(self.current_course_id)
                        sleep_time = 20
                    else:
                        self._log_warning(
                            '课程 %s 进度停滞，强制刷新当前课续播 (%s/3)',
                            self.current_course_id,
                            self._stale_reload_count,
                        )
                        self._reload_current_course()
                        sleep_time = 30
                    continue

                detail = self._fetch_course_detail(self.current_course_id)
                if self._auth_expired:
                    self._handle_login_expired()
                    break
                if not detail:
                    self._auth_fail_rounds += 1
                    self._sync_api_headers()
                    if self._auth_fail_rounds >= 3 and not self._ensure_login_valid():
                        self._handle_login_expired()
                        break
                    sleep_time = 15
                elif detail['totalPeriod'] <= detail['watchTimes']:
                    self._auth_fail_rounds = 0
                    self._log_info('课程 %s 已观看完成，立即续播下一门', self.current_course_id)
                    self._mark_custom_course_done(self.current_course_id)
                    self._reset_progress_tracker()
                    self._stale_reload_count = 0
                    self.current_course_id = ''
                    self.current_course_class_id = ''
                    if self._has_more_study_work():
                        self._open_course_and_play()
                        sleep_time = 20
                    else:
                        self._log_info('全部课程已学完')
                        self.is_complete = True
                        break
                else:
                    self._auth_fail_rounds = 0
                    watched = int(detail['watchTimes'])
                    remain = int(detail['totalPeriod']) - watched
                    # 上限 600s：接口常按整点上报，过长睡眠会误判停滞且难以及时点播放
                    sleep_time = max(30, min(remain, 600))
                    if self._last_watch_times == watched:
                        self._watch_times_stale_rounds += 1
                    else:
                        self._last_watch_times = watched
                        self._watch_times_stale_rounds = 0
                        self._stale_reload_count = 0
                    ended = self._ensure_video_playing()
                    video_info = self._read_video_progress()
                    if video_info:
                        cur = float(video_info.get('currentTime') or 0)
                        dur = float(video_info.get('duration') or 0)
                        pct = (cur / dur * 100) if dur > 0 else 0.0
                        self._log_info(
                            '课程 %s 视频进度 %.1f%% (%s/%s) paused=%s ended=%s '
                            'api_watched=%s/%s stale=%s 下次检测=%ss',
                            self.current_course_id,
                            pct,
                            self._format_seconds(cur),
                            self._format_seconds(dur) if dur > 0 else '?',
                            video_info.get('paused'),
                            video_info.get('ended'),
                            detail['watchTimes'],
                            detail['totalPeriod'],
                            self._watch_times_stale_rounds,
                            sleep_time,
                        )
                    else:
                        self._log_info(
                            '课程 %s 播放中（未读到 video） api_watched=%s/%s stale=%s 下次检测=%ss',
                            self.current_course_id,
                            detail['watchTimes'],
                            detail['totalPeriod'],
                            self._watch_times_stale_rounds,
                            sleep_time,
                        )
                    if ended:
                        sleep_time = min(sleep_time, 30)
                    elif self._watch_times_stale_rounds > 0:
                        # 已出现停滞迹象，缩短间隔以便尽快点播/刷新
                        sleep_time = min(sleep_time, 120)
            except Exception as exc:
                if self._is_session_dead_error(exc) or not self._is_browser_alive():
                    self._log_error(
                        '浏览器会话已断开（不是登录过期），停止监控。请重新启动任务: %s',
                        exc,
                    )
                    self.is_running = False
                    break
                self._log_warning('进度检测异常: %s', exc)
                # 异常时先判断登录是否过期
                if not self._ensure_login_valid():
                    self._handle_login_expired()
                    break
                sleep_time = 20

            time.sleep(sleep_time)

    def _get_current_course(self, courses):
        for course in courses:
            if not isinstance(course, dict):
                continue
            if str(course.get('status', '0')) != '1':
                return course
        return None

    def _sync_courses_progress(self, courses=None):
        """按任务课表统计：已完成数/总数，写入 progress。"""
        items = courses if courses is not None else self._parse_course_items(self.task.courses)
        if not items:
            return
        total = len(items)
        done = sum(
            1 for c in items
            if isinstance(c, dict) and str(c.get('status', '0')) == '1'
        )
        self._update_task_progress(f'{done}/{total}')

    def _goto_scgb_url(self, url: str, settle_seconds: float = 2):
        """打开 SCGB 的 hash 路由页。

        站点为 Vue hash 模式（#/course、#/myClass）。若当前已在同域，
        仅改 hash 时浏览器常不整页刷新，课程组件不会重新挂载，表现为
        「打开新课但不刷新、需手动 F5」。先离开再进入（对齐原版 scgb.py）。
        """
        try:
            current = self.driver.current_url or ''
        except Exception:
            current = ''
        if 'web.scgb.gov.cn' in current or current.startswith('about:'):
            self._log_info('hash 路由先离开当前页再进入，避免不刷新')
            try:
                self._driver_get('about:blank')
                time.sleep(0.5)
            except Exception:
                self._driver_get(SCGB_HOME_URL)
                time.sleep(1)
        self._driver_get(url)
        time.sleep(settle_seconds)
        # 再 refresh 一次，确保播放页真正重新挂载
        try:
            self.driver.refresh()
            time.sleep(max(1.0, settle_seconds))
        except Exception as exc:
            self._log_warning('打开后 refresh 失败: %s', exc)

    def _build_course_url(self, course_id: str, class_id: str = '') -> str:
        class_id = class_id or ''
        if class_id:
            return (
                f'https://web.scgb.gov.cn/#/course?id={course_id}'
                f'&className=&classId={class_id}'
            )
        return f'https://web.scgb.gov.cn/#/course?id={course_id}&className='

    def _reload_current_course(self):
        """进度停滞/页面异常：强制刷新当前课并续播，不切换到下一门。"""
        course_id = self.current_course_id
        class_id = self.current_course_class_id or (self.task.class_id or '')
        if not course_id:
            self._open_course_and_play()
            return
        if not self._is_browser_alive():
            return
        url = self._build_course_url(course_id, str(class_id))
        self._log_info('强制刷新当前课程播放页: %s', url)
        self._goto_scgb_url(url, settle_seconds=2)
        self._close_course_modal2()
        self._click_video_play_button()
        self._reset_progress_tracker()

    def _skip_stuck_course(self, course_id: str):
        """多次刷新仍无进度：记入跳过列表并尝试下一门。"""
        if not course_id:
            return
        skip = list(self.task.no_play_videos or [])
        if course_id not in skip:
            skip.append(course_id)
            update_task_fields(self.task, no_play_videos=skip)
            self._log_warning('已将课程加入不播放列表: %s', course_id)
        self._mark_custom_course_done(course_id)
        self._reset_progress_tracker()
        self._stale_reload_count = 0
        self.current_course_id = ''
        self.current_course_class_id = ''
        if self._has_more_study_work():
            self._open_course_and_play()
        else:
            self._log_info('无更多可学课程，结束任务')
            self.is_complete = True

    def _open_custom_course(self, course):
        course_id = course.get('id')
        if not course_id:
            self._log_warning('课表条目缺少 id，跳过: %s', course)
            return

        class_id = course.get('classId') or self.task.class_id
        course_url = self._build_course_url(course_id, str(class_id or ''))
        self._log_info('打开课程播放页: %s', course_url)
        self._goto_scgb_url(course_url, settle_seconds=2)
        self._close_course_modal2()
        self._click_video_play_button()
        self.current_course_id = course_id
        self.current_course_class_id = str(class_id or '')
        self._reset_progress_tracker()
        self._stale_reload_count = 0
        self._log_info('当前课程ID: %s classId=%s', self.current_course_id, self.current_course_class_id)

    def _open_class_course_detail(self, label: str):
        from selenium.common import TimeoutException
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.wait import WebDriverWait

        self._log_info('进行%s学习', label)
        self._goto_scgb_url(
            f'https://web.scgb.gov.cn/#/myClass?id={self.task.class_id}&collected=1',
            settle_seconds=1,
        )
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
                self.current_course_class_id = str(self.task.class_id or '')
                self._reset_progress_tracker()
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
        class_id = self.current_course_class_id or self.task.class_id or ''
        payload = {'courseId': course_id, 'classId': class_id}
        try:
            response = requests.post(url, headers=self.api_headers, json=payload, timeout=10)
            if response.status_code == 401:
                self._log_warning('课程详情接口 401，尝试从页面刷新 token')
                self._sync_api_headers()
                response = requests.post(url, headers=self.api_headers, json=payload, timeout=10)
                if response.status_code == 401:
                    self._log_warning('刷新 token 后仍 401，判定登录已过期')
                    self._auth_expired = True
                    return None
            response.raise_for_status()
            result = response.json().get('result')
            if result is not None:
                self._auth_expired = False
            return result
        except Exception:
            self._log_exception('查询课程详情失败 course_id=%s', course_id)
            return None

    def _ensure_login_valid(self) -> bool:
        """浏览器仍在时检查 localStorage token 是否有效。"""
        if not self._is_browser_alive():
            return False
        try:
            if self._is_logged_in():
                self._auth_expired = False
                return True
        except Exception as exc:
            if self._is_session_dead_error(exc):
                return False
            self._log_warning('检查登录态异常: %s', exc)
        self._sync_api_headers()
        try:
            ok = self._is_logged_in()
        except Exception:
            ok = False
        if not ok:
            self._auth_expired = True
        return ok

    def _handle_login_expired(self):
        """登录过期：停止任务，提示用户重新启动并完成短信验证。"""
        self._log_error('登录已过期或失效，停止任务。请重新启动任务并完成手机验证码登录')
        self._auth_expired = True
        self.is_running = False
        try:
            update_task_fields(self.task, status='1')
        except Exception:
            self._log_exception('登录过期后更新任务状态失败')

    def _reset_progress_tracker(self):
        self._last_watch_times = None
        self._watch_times_stale_rounds = 0

    @staticmethod
    def _is_session_dead_error(exc) -> bool:
        msg = str(exc or '').lower()
        return any(
            key in msg
            for key in (
                'invalid session',
                'session deleted',
                'disconnected',
                'not connected to devtools',
                'chrome not reachable',
                'no such window',
            )
        )

    def _is_browser_alive(self) -> bool:
        if not self.driver:
            return False
        try:
            _ = self.driver.current_url
            return True
        except Exception:
            return False

    def _scgb_page_error(self) -> bool:
        """仅匹配明确的网关/超时文案，避免裸 404/502 误伤 SPA 页面。"""
        try:
            page_source = (self.driver.page_source or '').lower()
        except Exception as exc:
            if self._is_session_dead_error(exc):
                raise
            self._log_error('检测页面错误异常: %s', exc)
            return True
        keywords = (
            '502 bad gateway',
            'bad gateway',
            '504 gateway timeout',
            '500 internal server error',
            '无法访问此网站',
            '连接已重置',
            '连接超时',
            '页面加载失败',
        )
        for keyword in keywords:
            if keyword in page_source:
                self._log_warning('检测到页面错误关键词: %s', keyword)
                return True
        return False

    def _read_video_progress(self) -> dict | None:
        """读取播放器进度（#videoPlayer_html5_api / video.vjs-tech）。"""
        try:
            info = self.driver.execute_script(
                """
                const v = document.querySelector(
                    'video#videoPlayer_html5_api, video.vjs-tech, video'
                );
                if (!v) return null;
                return {
                    currentTime: v.currentTime || 0,
                    duration: v.duration || 0,
                    paused: !!v.paused,
                    ended: !!v.ended
                };
                """
            )
            if not isinstance(info, dict):
                return None
            return info
        except Exception as exc:
            if self._is_session_dead_error(exc):
                raise
            return None

    @staticmethod
    def _format_seconds(seconds: float) -> str:
        total = max(int(seconds), 0)
        h, rem = divmod(total, 3600)
        m, s = divmod(rem, 60)
        if h:
            return f'{h:02d}:{m:02d}:{s:02d}'
        return f'{m:02d}:{s:02d}'

    def _ensure_video_playing(self) -> bool:
        """保证播放；若 video 已 ended 返回 True（调用方应加快切课检测）。"""
        try:
            info = self._read_video_progress()
            if info:
                if info.get('ended'):
                    self._log_info('当前视频元素已 ended，等待接口确认完成并切课')
                    return True
                if not info.get('paused') and float(info.get('currentTime') or 0) > 0:
                    return False
                # 暂停/未开播：优先 JS play
                self.driver.execute_script(
                    """
                    const v = document.querySelector(
                        'video#videoPlayer_html5_api, video.vjs-tech, video'
                    );
                    if (!v) return;
                    try { v.muted = false; } catch (e) {}
                    const p = v.play();
                    if (p && typeof p.catch === 'function') p.catch(function(){});
                    """
                )
                return False
        except Exception as exc:
            if self._is_session_dead_error(exc):
                raise
            self._log_warning('读取 video 状态失败: %s', exc)

        self._click_video_play_button()
        return False

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
            self._sync_courses_progress(updated)

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
