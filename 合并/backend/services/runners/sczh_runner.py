"""
四川智慧中小学平台（SCZH）任务执行器

网站编码：SCZH
站点：https://basic.sc.smartedu.cn/
登录：ThirdPortalService otherlogin（账号密码）
参考：selenium_demo/四川智慧教育平台2/main.py

两步流程：
1) 打开 class_id 课程详情列表页（coursedatail），点击 .course-list-cell 未学小节，进入视频播放页
2) 在播放页使用 #chapter 播放列表检测进度（重新学习/100% = 完成），播完切下一节

完成条件：
- 课程「特定课表」配置 {"sum": 16}（创建任务时写入 task.courses）
- 进度 = 页面已学列表数量 / sum；仅当已学 >= sum 才标记任务完成
- 当前课程列表学完但未达 sum：只结束本次执行，定时任务可续跑
"""
from __future__ import annotations

import random
import re
import threading
import time

from services.runners.selenium_runner import SeleniumTaskRunner
from services.task_runner import register_runner

SCZH_LOGIN_URL = (
    'https://basic.sc.smartedu.cn/ThirdPortalService/user/otherlogin!login.ac'
    '?appkey=C56DA16ECBC56FBEEC908DA09E45C72C917A80118F057FA1F0B5BAE41CC9CC9DECD5BDB7133FE17C328C5D37B37CA8E7'
    '&pkey=5D79CA42E45C5273DF8532D09E1F158B15E25919CDB958940F84D5E63F5F53A1ECD5BDB7133FE17C328C5D37B37CA8E7'
    '&params=718F83A5347CBFDB7D1A9065FA090FE949D92330BB9A3351FE0715C5B8A3E86F37916C1004E835C7C7F964E3F301477F7D37F04485FA8707845DAAA23356236ED1D326CF5A5E3C263470516EE9B4A2ED'
)
TOKEN_COOKIE = 'Teaching_Autonomic_Learning_Token'

# 列表页（coursedatail）状态
LIST_DONE_STATUSES = ('已学习',)
# 播放页（#chapter）状态：重新学习 = 已完成
PLAY_DONE_STATUSES = ('重新学习', '已学习', '已学完')
PERCENT_PATTERN = re.compile(r'(\d+(?:\.\d+)?)\s*%')
STUCK_SLEEP_LIMIT = 100
PLAY_PAGE_WAIT_SECONDS = 15
LIST_PAGE_WAIT_SECONDS = 15


@register_runner('SCZH')
class SczhTaskRunner(SeleniumTaskRunner):
    """四川智慧中小学平台：登录 + 列表进播放页 + 按 sum 目标回写进度。"""

    def __init__(self, task, website):
        super().__init__(task, website)
        self.course_url = ''
        self.sum_target = 0
        self.current_subsection_title = ''
        self._on_play_page = False
        self._sleep_time = 10
        self._sleep_time_num = 0

    def run_main(self):
        self._log_info(
            '开始任务 id=%s user=%s headless=%s class_id=%s',
            self.task.id, self.task.username, self.task.is_head, self.task.class_id,
        )
        try:
            self._prepare_config()
            self._init_browser(window_size=(1920, 1080))
            self._ensure_logged_in(max_rounds=5)
            self._open_course()
            if not self.is_complete and self.is_running:
                self._start_monitor_thread(self._check_course_success)
                self._wait_until_complete()
            self._sync_task_status()
        except Exception:
            self._log_exception('任务 id=%s 执行失败', self.task.id)
            self._handle_run_exception()
            raise
        finally:
            self._finalize_run()

    def _prepare_config(self):
        self.course_url = (self.task.class_id or '').strip()
        if not self.course_url.startswith('http'):
            raise RuntimeError('SCZH 任务缺少 class_id（课程详情页 URL）')
        self.sum_target = self._parse_sum_target()
        self._log_info('课程页=%s sum目标=%s', self.course_url, self.sum_target)

    def _parse_sum_target(self) -> int:
        """从课程/任务特定课表读取 sum，示例：{"sum": 16}"""
        for item in self._parse_course_items(self.task.courses):
            if not isinstance(item, dict) or item.get('sum') is None:
                continue
            try:
                value = int(item.get('sum'))
            except (TypeError, ValueError) as exc:
                raise RuntimeError('SCZH 课程配置 sum 须为整数，示例: {"sum": 16}') from exc
            if value <= 0:
                raise RuntimeError('SCZH 课程配置 sum 须为正整数')
            return value
        raise RuntimeError('SCZH 课程配置缺少 sum，请在特定课表填写 {"sum": 16}')

    def _apply_learned_progress(self, learned: int) -> bool:
        """回写进度 learned/sum；返回是否已达总目标（应标记任务完成）。"""
        learned = max(0, int(learned or 0))
        self._update_task_progress(f'{learned}/{self.sum_target}')
        self._log_info('任务进度 %s/%s', learned, self.sum_target)
        return learned >= self.sum_target

    def _finish_session(self, reason: str):
        """当前课暂无可学内容但未达 sum：结束本次执行，不标记任务完成。"""
        self._log_info(
            '%s，结束本次执行（未达 sum=%s，定时可续跑）',
            reason, self.sum_target,
        )
        self.is_running = False

    def _handle_learned_count(self, learned: int, *, exhausted: bool = False) -> bool:
        """
        根据已学数量更新进度。
        返回 True 表示应停止继续点课（已完成或结束本次）。
        exhausted=True 表示当前课程列表已无未学项。
        """
        if self._apply_learned_progress(learned):
            self._log_info('已达 sum 目标，标记任务完成')
            self._mark_course_complete()
            return True
        if exhausted:
            self._finish_session('当前课程列表已学完')
            return True
        return False

    # ------------------------------------------------------------------ login
    def _is_logged_in(self) -> bool:
        return bool(self.get_cookies_values(TOKEN_COOKIE))

    def _auto_login(self):
        from selenium.common import ElementNotInteractableException, TimeoutException
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.wait import WebDriverWait

        self._log_info('打开登录页')
        self._driver_get(SCZH_LOGIN_URL, label='登录页')
        time.sleep(2)

        try:
            username_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'loginName'))
            )
            username_input.clear()
            username_input.send_keys(self.task.username)

            password_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'password'))
            )
            password_input.clear()
            password_input.send_keys(self.task.password)

            login_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'submit-btn'))
            )
            login_button.click()
            time.sleep(2)

            try:
                cancel_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), '取消')]"))
                )
                cancel_button.click()
                self._log_info('已点击取消弹层')
            except TimeoutException:
                self._log_info('未出现取消按钮，跳过')
        except (TimeoutException, ElementNotInteractableException):
            self._log_exception('自动登录失败')
            raise

    # --------------------------------------------------------------- helpers
    @staticmethod
    def _parse_play_status(text: str) -> tuple[bool, int]:
        status = (text or '').strip()
        if not status:
            return False, 0
        if any(t in status for t in PLAY_DONE_STATUSES):
            return True, 100
        match = PERCENT_PATTERN.search(status)
        if match:
            percent = int(float(match.group(1)))
            return percent >= 100, min(percent, 100)
        return False, 0

    @staticmethod
    def _is_list_done(status_text: str) -> bool:
        text = (status_text or '').strip()
        return text in LIST_DONE_STATUSES or any(t in text for t in LIST_DONE_STATUSES)

    def _is_play_page(self) -> bool:
        from selenium.webdriver.common.by import By

        try:
            if self.driver.find_elements(By.CSS_SELECTOR, '#chapter .subsectionNameContent'):
                return True
            if self.driver.find_elements(By.ID, 'video'):
                return True
            url = self.driver.current_url or ''
            if 'subsectionId=' in url:
                return True
        except Exception:
            return False
        return False

    def _wait_play_page(self) -> bool:
        from selenium.common import TimeoutException
        from selenium.webdriver.support.wait import WebDriverWait

        try:
            WebDriverWait(self.driver, PLAY_PAGE_WAIT_SECONDS).until(
                lambda d: self._is_play_page()
            )
            self._on_play_page = True
            self._log_info('已进入视频播放页 url=%s', self.driver.current_url)
            return True
        except TimeoutException:
            self._on_play_page = False
            self._log_warning('等待视频播放页超时 url=%s', getattr(self.driver, 'current_url', ''))
            return False

    # --------------------------------------------------------------- list page
    def _list_course_cells(self) -> list[dict]:
        """课程详情列表页 .course-list-cell。"""
        from selenium.common import TimeoutException
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.wait import WebDriverWait

        try:
            WebDriverWait(self.driver, LIST_PAGE_WAIT_SECONDS).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'course-list-cell'))
            )
        except TimeoutException:
            return []

        cells = self.driver.find_elements(By.CLASS_NAME, 'course-list-cell')
        result = []
        for index, cell in enumerate(cells, 1):
            status_text = ''
            try:
                status = cell.find_element(By.XPATH, ".//div[@class='status']")
                status_text = (status.text or '').strip()
            except Exception:
                status_text = ''
            result.append({
                'index': index,
                'status_text': status_text,
                'done': self._is_list_done(status_text),
                'element': cell,
            })
        return result

    def _enter_play_from_list(self) -> bool:
        """在列表页点击未学小节，进入播放页。"""
        items = self._list_course_cells()
        if not items:
            self._log_warning('列表页未找到 course-list-cell')
            return False

        learned = sum(1 for item in items if item['done'])
        self._log_info('列表页已学 %s / 本课 %s（目标 sum=%s）', learned, len(items), self.sum_target)
        if self._handle_learned_count(learned, exhausted=(learned >= len(items))):
            return False

        for item in items:
            if self._stopped or self.is_complete or not self.is_running:
                return False
            if item['done']:
                continue
            self._log_info(
                '点击列表未学小节 index=%s status=%s',
                item['index'], item['status_text'] or '(空)',
            )
            try:
                item['element'].click()
            except Exception:
                self.driver.execute_script('arguments[0].click();', item['element'])
            time.sleep(3)
            if not self._wait_play_page():
                return False
            self._play_video_element()
            self._sync_current_from_playlist()
            return True
        return False

    # --------------------------------------------------------------- play page
    def _list_playlist_items(self) -> list[dict]:
        """播放页 #chapter 列表（标题去重）。"""
        from selenium.webdriver.common.by import By

        if not self._is_play_page():
            return []

        nodes = self.driver.find_elements(
            By.CSS_SELECTOR, '#chapter .subsectionNameContent'
        )
        result: list[dict] = []
        seen: set[str] = set()
        for node in nodes:
            try:
                title_el = node.find_element(By.CSS_SELECTOR, '.subsectionName')
                title = (title_el.text or '').strip()
            except Exception:
                title = ''
            if not title or title in seen:
                continue
            seen.add(title)

            status_text = ''
            try:
                status_el = node.find_element(By.CSS_SELECTOR, '.subsectionStudy span')
                status_text = (status_el.text or '').strip()
            except Exception:
                status_text = ''

            done, percent = self._parse_play_status(status_text)
            click_target = node
            try:
                click_target = node.find_element(By.CSS_SELECTOR, '.subsectionNameContent_fir')
            except Exception:
                pass

            result.append({
                'title': title,
                'status_text': status_text,
                'done': done,
                'percent': percent,
                'element': click_target,
            })
        return result

    def _sync_current_from_playlist(self):
        from selenium.webdriver.common.by import By

        items = self._list_playlist_items()
        if not items:
            return
        try:
            studying = self.driver.find_elements(
                By.CSS_SELECTOR, '#chapter .subsectionNameContent_fir.studying'
            )
            if studying:
                title_el = studying[0].find_element(By.CSS_SELECTOR, '.subsectionName')
                self.current_subsection_title = (title_el.text or '').strip()
                return
        except Exception:
            pass
        for item in items:
            if not item['done']:
                self.current_subsection_title = item['title']
                return

    def _click_playlist_unfinished(self) -> bool:
        items = self._list_playlist_items()
        if not items:
            self._log_warning('播放页未找到章节列表')
            return False

        learned = sum(1 for item in items if item['done'])
        self._log_info('播放列表已学 %s / 本页 %s（目标 sum=%s）', learned, len(items), self.sum_target)
        if self._handle_learned_count(learned, exhausted=(learned >= len(items))):
            return False

        for index, item in enumerate(items, 1):
            if self._stopped or self.is_complete or not self.is_running:
                return False
            if item['done']:
                continue
            self._log_info(
                '点击播放列表未完成小节 [%s/%s] %s status=%s',
                index, len(items), item['title'], item['status_text'] or '(空)',
            )
            try:
                item['element'].click()
            except Exception:
                self.driver.execute_script('arguments[0].click();', item['element'])
            time.sleep(3)
            self._play_video_element()
            self.current_subsection_title = item['title']
            self._apply_learned_progress(learned)
            return True
        return False

    def _play_video_element(self) -> bool:
        from selenium.common import TimeoutException
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.wait import WebDriverWait

        try:
            video = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'video'))
            )
            self.driver.execute_script(
                'var v=arguments[0]; try{v.muted=true; v.play();}catch(e){}',
                video,
            )
            time.sleep(1)
            self._log_info('已触发 video.play()')
            return True
        except TimeoutException:
            self._log_warning('未找到 video 元素')
            return False

    def _read_play_progress(self) -> tuple[int, int, int, str]:
        items = self._list_playlist_items()
        total = len(items)
        learned = sum(1 for item in items if item['done'])
        current_percent = 0
        current_title = self.current_subsection_title

        if self.current_subsection_title:
            for item in items:
                if item['title'] == self.current_subsection_title:
                    current_title = item['title']
                    current_percent = 100 if item['done'] else item['percent']
                    break
        else:
            self._sync_current_from_playlist()
            current_title = self.current_subsection_title
            for item in items:
                if item['title'] == current_title:
                    current_percent = 100 if item['done'] else item['percent']
                    break

        return learned, total, current_percent, current_title

    # --------------------------------------------------------------- main flow
    def _open_course(self):
        if self.is_complete or self._stopped or not self.is_running:
            return

        self._on_play_page = False
        self.current_subsection_title = ''
        self._log_info('打开课程列表页')
        self._driver_get(self.course_url, label='课程页')
        time.sleep(5)

        if not self._is_logged_in():
            self._log_warning('课程页检测未登录，重新登录')
            self._ensure_logged_in(max_rounds=3)
            self._driver_get(self.course_url, label='课程页')
            time.sleep(5)

        if self._is_play_page():
            self._on_play_page = True
            self._log_info('当前已在播放页，直接使用播放列表')
            if not self._click_playlist_unfinished():
                if not self.is_complete and self.is_running:
                    self._log_warning('播放列表无可播小节')
            return

        if not self._enter_play_from_list():
            if not self.is_complete and self.is_running:
                self._log_warning('未能从列表页进入播放页，稍后重试')

    def _spawn_open_course(self):
        threading.Thread(
            target=lambda: self._run_with_context(self._open_course),
            daemon=True,
            name=f'sczh-open-course-{self.task.id}',
        ).start()

    def _check_course_success(self):
        while not self.is_complete and self.is_running and not self._stopped:
            sleep_time = 30

            if self._sleep_time_num >= STUCK_SLEEP_LIMIT:
                self._log_warning('进度检测疑似卡住，重新进入课程')
                try:
                    self._ensure_logged_in(max_rounds=3)
                except Exception:
                    self._log_exception('卡住恢复时登录失败')
                self.current_subsection_title = ''
                self._on_play_page = False
                self._sleep_time_num = 0
                self._spawn_open_course()
                time.sleep(10)
                continue

            try:
                if not self._is_play_page():
                    self._log_info('不在播放页，重新从列表进入')
                    self._on_play_page = False
                    self._spawn_open_course()
                    sleep_time = 20
                else:
                    self._on_play_page = True
                    self._play_video_element()

                    learned, page_total, current_percent, current_title = self._read_play_progress()
                    if page_total > 0:
                        self._apply_learned_progress(learned)
                        self._log_info(
                            '播放列表已学 %s/%s（目标 sum=%s）当前=%s %s%%',
                            learned, page_total, self.sum_target,
                            current_title or '-', current_percent,
                        )

                    if page_total > 0 and learned >= self.sum_target:
                        self._log_info('已达 sum 目标，标记任务完成')
                        self._mark_course_complete()
                        return

                    if page_total > 0 and learned >= page_total:
                        # 本课播放列表学完，但未达 sum：结束本次，不标完成
                        self._handle_learned_count(learned, exhausted=True)
                        return

                    if current_title and current_percent >= 100:
                        self._log_info('当前小节已完成，切换下一节: %s', current_title)
                        self.current_subsection_title = ''
                        if not self._click_playlist_unfinished():
                            if not self.is_running or self.is_complete:
                                return
                            self._spawn_open_course()
                        sleep_time = 15
                    elif page_total > 0 and learned < page_total and not current_title:
                        self._log_info('播放页无当前小节，点下一未完成项')
                        if not self._click_playlist_unfinished():
                            if not self.is_running or self.is_complete:
                                return
                            self._spawn_open_course()
                        sleep_time = 15
                    else:
                        sleep_time = random.randint(60, 120)

                if not self.is_running or self.is_complete:
                    return

                if not self._is_logged_in():
                    self._log_warning('登录失效，重新登录')
                    self._ensure_logged_in(max_rounds=3)
                    self._spawn_open_course()
                    sleep_time = 20
            except Exception as exc:
                self._log_error('检测进度失败: %s', exc)
                if not self.is_running or self.is_complete:
                    return
                if not self._is_logged_in():
                    try:
                        self._ensure_logged_in(max_rounds=3)
                    except Exception:
                        self._log_exception('进度失败后重新登录失败')
                self._spawn_open_course()
                sleep_time = 20

            if self._sleep_time == sleep_time:
                self._sleep_time_num += 1
            else:
                self._sleep_time = sleep_time
                self._sleep_time_num = 0

            self._log_info('间隔 %s 秒继续检测', sleep_time)
            end_ts = time.time() + sleep_time
            while time.time() < end_ts:
                if self._stopped or self.is_complete or not self.is_running:
                    return
                time.sleep(min(5, max(end_ts - time.time(), 0)))