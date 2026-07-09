"""
乐山公需课（LSGX）任务执行器

网站编码：LSGX
参考：selenium_demo/乐山市公需课/main.py
"""
import time
from typing import Any

from services.runners.selenium_runner import SeleniumTaskRunner
from services.task_runner import register_runner, update_task_fields

LSGX_HOME_URL = 'https://www.ls1018.com.cn/'
LSGX_DEFAULT_COURSE_URL = 'https://www.ls1018.com.cn/course/118.html'


@register_runner('LSGX')
class LsgxTaskRunner(SeleniumTaskRunner):
    """乐山公需课任务执行器。"""

    def __init__(self, task, website):
        super().__init__(task, website)
        self.current_course_url = LSGX_DEFAULT_COURSE_URL

    def run_main(self):
        self._log_info(
            '开始任务 id=%s user=%s class_id=%s enable_sms=%s headless=%s',
            self.task.id, self.task.username, self.task.class_id,
            self.website.enable_sms_code, self.task.is_head,
        )
        try:
            course_list = self._parse_course_list()
            self._build_context_log(course_list)
            self._init_browser(window_size=(1920, 1080))
            self._login()
            self._play_courses()
            if not self._stopped:
                update_task_fields(self.task, status='2')
            self._log_info('任务 id=%s 执行完成', self.task.id)
        except Exception:
            self._log_exception('任务 id=%s 执行失败', self.task.id)
            self._handle_run_exception()
            raise
        finally:
            self._finalize_run()

    def _parse_course_list(self) -> list[dict[str, Any]]:
        raw = self.task.courses
        if not raw:
            if self.task.class_id:
                return [{
                    'name': '默认课程',
                    'url': LSGX_DEFAULT_COURSE_URL,
                    'course_id': self.task.class_id,
                }]
            return []

        result = []
        for item in self._parse_course_items(raw):
            if isinstance(item, str):
                result.append({'name': item, 'url': item, 'course_id': self.task.class_id})
            elif isinstance(item, dict):
                result.append({
                    'name': item.get('name', ''),
                    'url': item.get('url', ''),
                    'course_id': item.get('course_id', self.task.class_id),
                })
        return result

    def _is_logged_in(self) -> bool:
        return bool(self.get_cookies_values('PHPSESSID'))

    def _login(self, max_rounds=100):
        try:
            self.driver.get(LSGX_HOME_URL)
            time.sleep(3)
            self._log_info('尝试登录 user=%s', self.task.username)
            self._auto_login()
        except Exception as exc:
            self._log_info("打开网站失败")
        for idx in range(max_rounds):
            if self._is_logged_in():
                self._log_info('已登录 user=%s', self.task.username)
                return
            self._log_info('第 %s 次尝试登录 user=%s', idx + 1, self.task.username)
            self._auto_login()
            time.sleep(3)
        if not self._is_logged_in():
            raise RuntimeError('登录失败，请检查账号密码')

    def _auto_login(self):
        from selenium.common import ElementNotInteractableException, TimeoutException
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.wait import WebDriverWait
        try:
            self._log_info('打开首页 %s', LSGX_HOME_URL)
            self.driver.get(LSGX_HOME_URL)
            time.sleep(5)
            self.driver.find_element(By.LINK_TEXT, '登录').click()

            username_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'log_username'))
            )
            username_input.clear()
            username_input.send_keys(self.task.username)

            password_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'log_pwd'))
            )
            password_input.clear()
            password_input.send_keys(self.task.password)

            if self.website.enable_sms_code == '1':
                self._log_info('需要手机验证码，等待处理...')
                time.sleep(30)

            self.driver.find_element(By.ID, 'logSub').click()
            time.sleep(10)
            self._log_info('登录完成 user=%s', self.task.username)
        except TimeoutException:
            self._log_error('超时未找到登录相关输入框')
        except ElementNotInteractableException:
            self._log_error('登录输入框不可交互')
        except Exception as exc:
            self._log_error('自动登录失败: %s', exc)

    def _play_courses(self):
        course_list = self._parse_course_list()
        if not course_list:
            self._log_warning('无课表数据，跳过播放')
            self._mark_course_complete()
            return

        first_course = course_list[0]
        self.current_course_url = first_course.get('url') or LSGX_DEFAULT_COURSE_URL
        self.is_complete = False
        self._open_course_home()
        self._start_monitor_thread(self._check_course_success)
        self._wait_until_complete()
        self._log_info('课表播放流程结束 user=%s', self.task.username)

    def _open_course_home(self):
        if self.is_complete:
            return

        self._log_info('打开课程页: %s', self.current_course_url)
        self.driver.get(self.current_course_url)
        time.sleep(5)

        if self.find_and_play_first_unfinished():
            self._log_info('已找到未完成课程并开始播放')
            return

        self._log_info('没有未完成课程，标记任务完成')
        self._mark_course_complete()

    def find_and_play_first_unfinished(self) -> bool:
        from selenium.webdriver.common.by import By

        try:
            ml_lists = self.driver.find_elements(By.CLASS_NAME, 'ml-list')
            if not ml_lists:
                self._log_warning('未找到课程列表 ml-list')
                return True

            for item in ml_lists:
                a_tag = item.find_element(By.CLASS_NAME, 'begin')
                href = a_tag.get_attribute('href')
                if not href:
                    continue

                flish_text = ''
                try:
                    flish_element = item.find_element(By.CLASS_NAME, 'flish')
                    flish_text = (flish_element.text or '').strip()
                except Exception:
                    self._log_info('列表项无 flish 标记，尝试直接打开: %s', href)
                    self._open_video_tab(href)
                    return True

                self._log_info('课程状态: %s', flish_text)
                if flish_text != '已学完':
                    self._open_video_tab(href)
                    return True
            return False
        except Exception:
            self._log_exception('查找未完成课程失败')
            return True

    def _check_course_success(self):
        from selenium.webdriver.common.by import By

        sleep_time = 10
        self._log_info('开始监听播放进度 user=%s', self.task.username)

        while not self.is_complete and self.is_running:
            if self.check_page_error():
                self._log_warning('页面异常，重新打开课程页')
                self._open_course_home()
                time.sleep(30)
                continue

            try:
                video = self.driver.find_element(By.ID, 'my-video')
                info = self.driver.execute_script("""
                    var video = arguments[0];
                    return {
                        paused: video.paused,
                        ended: video.ended,
                        currentTime: video.currentTime,
                        duration: video.duration
                    };
                """, video)

                progress = 0.0
                if info['duration'] and info['duration'] > 0:
                    progress = (info['currentTime'] / info['duration']) * 100
                self._log_info('播放进度: %.1f%%', progress)

                if info['ended']:
                    self._log_info('当前视频已播完，查找下一节')
                    self._open_course_home()
                    time.sleep(5)
                elif info['paused'] and info['currentTime'] > 0:
                    self._log_info('视频暂停，尝试继续播放')
                    video.click()
                    time.sleep(5)
                elif info['currentTime'] == 0:
                    self._log_info('视频未开始，点击播放')
                    video.click()
                    time.sleep(5)
            except Exception as exc:
                self._log_warning('获取视频进度失败: %s', exc)

            time.sleep(sleep_time)

        self._log_info('播放监控结束 user=%s', self.task.username)
