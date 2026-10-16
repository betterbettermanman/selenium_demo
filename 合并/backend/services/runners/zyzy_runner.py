"""
张掖专业课（ZYZY）任务执行器

网站编码：ZYZY
公需登录：https://jxjy.zygbxxpt.com/login_toLogin
专业课站点：https://zjjy-zy.ceivs.cn/
单点入口：https://jxjy.zygbxxpt.com/cas/ceinet

专业课站点账号密码可能未初始化，登录走公需站图形验证码，再单点进入。
任务 class_id 为培训班 trainingId，或带 trainingId 的课程 URL。
播课：培训详情页点「详情」→「播放」，新开 /studycourseware，iframe 内 ckplayer 正常播放，不拖动进度。
"""
from __future__ import annotations

import re
import time
from urllib.parse import unquote

from services.runners.selenium_runner import SeleniumTaskRunner
from services.task_runner import register_runner, update_task_fields

LOGIN_URL = 'https://jxjy.zygbxxpt.com/login_toLogin'
CAS_URL = 'https://jxjy.zygbxxpt.com/cas/ceinet'
TRAINING_URL_TMPL = 'https://zjjy-zy.ceivs.cn/training-detail?trainingId={training_id}'
TRAINING_ID_PATTERN = re.compile(r'trainingId=(\d+)')
PERCENT_PATTERN = re.compile(r'(\d+(?:\.\d+)?)\s*%')
HOURS_LEFT_PATTERN = re.compile(r'还需要完成\s*([\d.]+)\s*学时')
COURSE_ITEM_SELECTOR = '.elective-course-item, .required-course-item'


def parse_training_id(raw) -> str:
    """从任务 class_id 解析培训班 trainingId。"""
    text = unquote((raw or '').strip())
    if not text:
        raise RuntimeError('ZYZY 任务缺少 class_id（培训班 trainingId）')
    if text.isdigit():
        return text
    match = TRAINING_ID_PATTERN.search(text)
    if match:
        return match.group(1)
    raise RuntimeError('ZYZY class_id 须为培训班 ID，或包含 trainingId 的课程 URL')


@register_runner('ZYZY')
class ZyzyTaskRunner(SeleniumTaskRunner):
    """张掖专技专业课：公需站登录 + 单点进入培训班，播放未完成课件。"""

    def __init__(self, task, website):
        super().__init__(task, website)
        self.training_id = ''
        self.list_window = None
        self.play_window = None
        self._failed_titles: dict[str, int] = {}
        self._done_courseware_ids: set[str] = set()
        self._list_skip = 0

    def run_main(self):
        self._log_info(
            '开始任务 id=%s user=%s class_id=%s headless=%s',
            self.task.id, self.task.username, self.task.class_id, self.task.is_head,
        )
        try:
            self._prepare_config()
            self._init_browser(window_size=(1920, 1080))
            self._ensure_logged_in(max_rounds=6)
            self._sync_user_profile()
            self._open_training()
            self._play_course_loop()
            self._sync_task_status()
        except Exception:
            self._log_exception('任务 id=%s 执行失败', self.task.id)
            self._handle_run_exception()
            raise
        finally:
            self._finalize_run()

    def _prepare_config(self):
        self.training_id = parse_training_id(self.task.class_id)
        self._log_info('培训班 trainingId=%s', self.training_id)

    # ------------------------------------------------------------------ login
    def _is_logged_in(self) -> bool:
        from selenium.webdriver.common.by import By

        try:
            url = self.driver.current_url or ''
            if 'zjjy-zy.ceivs.cn' in url and 're_path=' not in url:
                passwords = self.driver.find_elements(By.CSS_SELECTOR, 'input[name="password"]')
                if not any(el.is_displayed() for el in passwords):
                    body = self.driver.find_element(By.TAG_NAME, 'body').text or ''
                    if '请输入密码' not in body and '欢迎登录' not in body:
                        return True
            logout = self.driver.find_elements(
                By.CSS_SELECTOR, '.header-logout, .manage-logout-box'
            )
            if any(el.is_displayed() for el in logout):
                return True
            body_head = (self.driver.find_element(By.TAG_NAME, 'body').text or '')[:80]
            if '退出' in body_head and '未登录' not in body_head:
                return True
        except Exception:
            self._log_exception('检测登录态失败')
        return False

    def _auto_login(self):
        from selenium.common import ElementNotInteractableException, TimeoutException
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.wait import WebDriverWait

        self._driver_get(LOGIN_URL, label='登录页')
        time.sleep(2)
        self._hide_notice_overlays()

        if self._is_logged_in():
            self._log_info('检测到已有登录态，跳过表单')
            return

        try:
            username = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'loginname'))
            )
            username.clear()
            username.send_keys(self.task.username)

            password = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'password'))
            )
            password.clear()
            password.send_keys(self.task.password)

            captcha = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'code'))
            )
            captcha.clear()
            captcha.send_keys(self._recognize_image_captcha())

            login_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'user_login'))
            )
            login_btn.click()
            time.sleep(3)
            self._log_info('登录表单已提交 user=%s', self.task.username)
        except (TimeoutException, ElementNotInteractableException):
            self._log_exception('登录失败')
            raise

    def _recognize_image_captcha(self) -> str:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.wait import WebDriverWait

        try:
            img = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'codeImg'))
            )
            return self._recognize_captcha_screenshot(img, f'zyzy_{self.task.username}.png')
        except Exception:
            self._log_exception('验证码识别失败')
            return ''

    def _hide_notice_overlays(self):
        try:
            self.driver.execute_script(
                """
                document.querySelectorAll(
                  '.honesty-contact-logout, .honesty-contact-login, .page-modal-bg'
                ).forEach(el => { el.style.display = 'none'; });
                """
            )
        except Exception:
            pass

    def _sync_user_profile(self):
        from selenium.webdriver.common.by import By

        try:
            body = (self.driver.find_element(By.TAG_NAME, 'body').text or '')
            for line in body.splitlines():
                text = line.strip()
                if text and '退出' in text and len(text) <= 20:
                    name = text.replace('退出', '').strip()
                    if name and name != '未登录':
                        update_task_fields(self.task, nick_name=name)
                        self._log_info('已登录 %s', name)
                        return
        except Exception:
            self._log_exception('同步学员资料失败')

    # ------------------------------------------------------------- course list
    def _training_url(self) -> str:
        return TRAINING_URL_TMPL.format(training_id=self.training_id)

    def _open_training(self):
        self._log_info('单点进入专业课 %s', CAS_URL)
        self._driver_get(CAS_URL, label='单点登录')
        time.sleep(3)
        if not self._is_logged_in():
            raise RuntimeError('单点登录后未进入专业课站点')

        url = self._training_url()
        self._log_info('打开培训班 %s', url)
        self._driver_get(url, label='培训详情')
        time.sleep(3)
        if not self._wait_course_list(timeout=20):
            raise RuntimeError(f'未打开培训班课程列表 trainingId={self.training_id}')
        self.list_window = self.driver.current_window_handle
        self._select_unfinished_tab()
        self._wait_course_items()
        self._update_hours_progress()
        self._log_info('培训班已打开 list_window=%s', self.list_window)

    def _wait_course_list(self, timeout=20) -> bool:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.wait import WebDriverWait

        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, '//*[contains(.,"培训任务")]'))
            )
            return True
        except Exception:
            self._log_warning('等待培训任务超时')
            return False

    def _wait_course_items(self, timeout=20) -> bool:
        from selenium.webdriver.common.by import By

        self.driver.implicitly_wait(0)
        try:
            end = time.time() + timeout
            while time.time() < end and self.is_running:
                items = self.driver.find_elements(By.CSS_SELECTOR, COURSE_ITEM_SELECTOR)
                if items:
                    self._log_info('课程列表已出现 count=%s', len(items))
                    return True
                time.sleep(0.5)
            self._log_warning('等待课程条目超时')
            return False
        finally:
            self.driver.implicitly_wait(10)

    def _select_unfinished_tab(self):
        from selenium.webdriver.common.by import By

        self.driver.implicitly_wait(0)
        try:
            for xpath in (
                "//div[contains(@class,'course-status-nav')]//*[normalize-space()='未完成']",
                "//*[contains(@class,'status-nav')]//*[normalize-space()='未完成']",
            ):
                try:
                    tabs = self.driver.find_elements(By.XPATH, xpath)
                    for tab in tabs:
                        if tab.is_displayed():
                            tab.click()
                            time.sleep(0.5)
                except Exception:
                    continue
        finally:
            self.driver.implicitly_wait(10)

    def _ensure_on_list_window(self):
        if self.list_window and self.list_window in self.driver.window_handles:
            self.driver.switch_to.window(self.list_window)
            self.driver.switch_to.default_content()
            return
        self._log_warning('列表窗口丢失，重新打开培训班')
        self._open_training()

    def _refresh_course_list(self):
        self._ensure_on_list_window()
        try:
            self.driver.refresh()
            time.sleep(3)
            self._wait_course_list(timeout=20)
            self._select_unfinished_tab()
            self._go_first_page()
            self._update_hours_progress()
        except Exception:
            self._log_warning('刷新失败，重新打开培训班')
            self._open_training()

    def _go_first_page(self):
        from selenium.webdriver.common.by import By

        try:
            pages = self.driver.find_elements(By.CSS_SELECTOR, '.el-pager li.number')
            if not pages:
                return
            first = pages[0]
            classes = first.get_attribute('class') or ''
            if 'active' not in classes and first.is_displayed():
                first.click()
                time.sleep(1)
        except Exception:
            pass

    def _update_hours_progress(self):
        from selenium.webdriver.common.by import By

        try:
            text = self.driver.find_element(By.TAG_NAME, 'body').text or ''
        except Exception:
            return
        done_n = len(self._done_courseware_ids)
        prefix = f'已播{done_n}节 ' if done_n else ''
        hours = HOURS_LEFT_PATTERN.search(text)
        if hours:
            self._update_task_progress(f'{prefix}还需{hours.group(1)}学时')
            return
        percents = PERCENT_PATTERN.findall(text)
        if percents:
            self._update_task_progress(f'{prefix}{percents[0]}%')

    # --------------------------------------------------------------- play loop
    def _play_course_loop(self):
        while self.is_running and not self.is_complete and not self._stopped:
            self._ensure_on_list_window()
            self._select_unfinished_tab()
            target = self._find_next_play_target(skip=self._list_skip)
            if target is None:
                if self._list_skip:
                    self._list_skip = 0
                    if self._goto_next_page():
                        continue
                    self._log_info('列表中的课件本轮都已播过')
                    self._mark_course_complete()
                    return
                if self._goto_next_page():
                    continue
                if self._has_unfinished_items():
                    raise RuntimeError('仍有未完成课件，但连续播放失败，请检查播放页')
                self._log_info('未完成课件已播完')
                self._mark_course_complete()
                return

            title, play_el = target
            self._log_info('准备播放: %s', title)
            before_handles = set(self.driver.window_handles)
            try:
                self.driver.execute_script('arguments[0].click();', play_el)
            except Exception:
                self._log_exception('点击播放失败 title=%s', title)
                self._note_play_failure(title)
                continue

            play_handle = self._wait_new_window(before_handles, timeout=20)
            if not play_handle:
                self._log_warning('未打开播放页 title=%s', title)
                self._note_play_failure(title)
                self._refresh_course_list()
                continue

            self.play_window = play_handle
            self.driver.switch_to.window(play_handle)
            play_url = self.driver.current_url or ''
            courseware_id = self._courseware_id(play_url)
            self._log_info('已切换到播放页 url=%s', play_url)
            if courseware_id and courseware_id in self._done_courseware_ids:
                self._log_info('该课件本轮已播完，改播下一节 coursewareId=%s', courseware_id)
                self._close_play_window_and_return()
                self._list_skip += 1
                continue
            self._start_player()
            finished = self._watch_until_done()
            self._close_play_window_and_return()
            if finished:
                self._failed_titles.pop(title, None)
                if courseware_id:
                    self._done_courseware_ids.add(courseware_id)
                self._log_info('本节已完成，已播课件数=%s', len(self._done_courseware_ids))
            else:
                self._note_play_failure(title)
            self._list_skip = 0
            self._refresh_course_list()

        if self.is_running and not self._stopped and not self.is_complete:
            self._log_warning('播放循环结束但未标记完成')

    def _note_play_failure(self, title: str):
        count = self._failed_titles.get(title, 0) + 1
        self._failed_titles[title] = count
        self._log_warning('课件播放未完成 title=%s 连续失败=%s', title, count)

    def _find_next_play_target(self, skip=0):
        from selenium.webdriver.common.by import By

        self._log_info('查找未完成课件 skip=%s', skip)
        self.driver.implicitly_wait(0)
        try:
            items = self.driver.find_elements(By.CSS_SELECTOR, COURSE_ITEM_SELECTOR)
            self._log_info('课程条目数=%s', len(items))
            found = 0
            for item in items:
                title = self._item_title(item)
                if not title:
                    continue
                if self._failed_titles.get(title, 0) >= 3:
                    continue
                status_els = item.find_elements(
                    By.CSS_SELECTOR,
                    '.elective-course-status-tip, .required-course-status-tip',
                )
                status = (status_els[0].text if status_els else '').strip()
                if '已完成' in status and '未完成' not in status:
                    continue
                plays = self._unfinished_play_buttons(item)
                if not plays and self._expand_item(item):
                    plays = self._unfinished_play_buttons(item)
                for play in plays:
                    if found == skip:
                        self._log_info('命中课件 title=%s', title)
                        return title, play
                    found += 1
            return None
        except Exception:
            self._log_exception('读取课程列表失败')
            return None
        finally:
            self.driver.implicitly_wait(10)

    @staticmethod
    def _courseware_id(url: str) -> str:
        match = re.search(r'coursewareId=(\d+)', url or '')
        return match.group(1) if match else ''

    def _item_title(self, item) -> str:
        from selenium.webdriver.common.by import By

        for el in item.find_elements(By.CSS_SELECTOR, '.title'):
            text = (el.get_attribute('title') or el.text or '').strip()
            if text:
                return text
        return ''

    def _expand_item(self, item) -> bool:
        from selenium.webdriver.common.by import By

        try:
            details = item.find_elements(By.CSS_SELECTOR, '.known p, .known')
            for detail in details:
                if detail.is_displayed() and '详情' in (detail.text or ''):
                    self.driver.execute_script('arguments[0].click();', detail)
                    time.sleep(1.5)
                    return True
        except Exception:
            self._log_exception('展开课程详情失败')
        return False

    def _unfinished_play_buttons(self, item):
        from selenium.webdriver.common.by import By

        buttons = []
        boxes = item.find_elements(By.CSS_SELECTOR, '.required-course-play')
        for box in boxes:
            try:
                if not box.is_displayed():
                    continue
            except Exception:
                continue
            percent = self._play_box_percent(box)
            if percent is not None and percent >= 99.5:
                continue
            spans = box.find_elements(By.XPATH, './/span[normalize-space()="播放"]')
            if spans:
                buttons.append(spans[0])
        return buttons

    def _play_box_percent(self, box):
        from selenium.webdriver.common.by import By

        try:
            row = box.find_element(By.XPATH, './ancestor::li[1]')
            nums = row.find_elements(By.CSS_SELECTOR, '.learned-section-num')
            if nums:
                return self._extract_percent(nums[0].text or '')
        except Exception:
            pass
        return None

    @staticmethod
    def _extract_percent(text: str):
        matches = PERCENT_PATTERN.findall(text or '')
        if not matches:
            return None
        try:
            return float(matches[-1])
        except ValueError:
            return None

    def _has_unfinished_items(self) -> bool:
        from selenium.webdriver.common.by import By

        self.driver.implicitly_wait(0)
        try:
            items = self.driver.find_elements(By.CSS_SELECTOR, COURSE_ITEM_SELECTOR)
            for item in items:
                tips = item.find_elements(
                    By.CSS_SELECTOR, '.elective-course-status-tip, .required-course-status-tip'
                )
                status = (tips[0].text if tips else '').strip()
                if '未完成' in status:
                    return True
            return False
        except Exception:
            return False
        finally:
            self.driver.implicitly_wait(10)

    def _goto_next_page(self) -> bool:
        from selenium.webdriver.common.by import By

        try:
            buttons = self.driver.find_elements(By.CSS_SELECTOR, '.el-pagination .btn-next')
            for btn in buttons:
                classes = btn.get_attribute('class') or ''
                disabled = btn.get_attribute('disabled')
                if not btn.is_displayed() or 'disabled' in classes or disabled:
                    continue
                btn.click()
                time.sleep(2)
                self._log_info('已翻到下一页')
                return True
        except Exception:
            self._log_exception('翻页失败')
        return False

    def _wait_new_window(self, before_handles: set, timeout=20):
        end = time.time() + timeout
        while time.time() < end and self.is_running:
            handles = set(self.driver.window_handles)
            new_ones = handles - before_handles
            if new_ones:
                return next(iter(new_ones))
            time.sleep(0.5)
        return None

    def _watch_until_done(self, timeout=3 * 60 * 60) -> bool:
        end = time.time() + timeout
        last_time = -1.0
        high_water = 0.0
        stuck = 0
        while time.time() < end and self.is_running and not self._stopped:
            if self.play_window not in self.driver.window_handles:
                self._log_warning('播放窗口已关闭')
                return False
            state = self._read_player_state()
            if state is None:
                stuck += 1
            else:
                current = float(state['current'])
                duration = float(state['duration'])
                self._log_info(
                    '播放进度 current=%.0fs duration=%.0fs percent=%.1f paused=%s',
                    current, duration, state['percent'], state['paused'],
                )
                if self._playback_reached_end(state, high_water):
                    time.sleep(5)
                    self._log_info('当前课件播放完成')
                    return True
                if state['paused'] or current - last_time < 1:
                    stuck += 1
                    self._resume_video()
                else:
                    stuck = 0
                high_water = max(high_water, current)
                last_time = current
            if stuck >= 18:
                self._log_warning('播放进度长时间无变化')
                return False
            remaining = 0.0
            if state and float(state.get('duration') or 0) > 1:
                remaining = float(state['duration']) - float(state['current'])
            time.sleep(2 if 0 < remaining <= 30 else 10)
        return False

    @staticmethod
    def _playback_reached_end(state, high_water: float) -> bool:
        """播完、贴着结尾，或播完后播放器把进度打回开头。"""
        current = float(state.get('current') or 0)
        duration = float(state.get('duration') or 0)
        if state.get('ended'):
            return True
        if duration > 1 and current >= duration - 3:
            return True
        if duration > 1 and high_water >= duration - 20 and current + 15 < high_water:
            return True
        return False

    def _read_player_state(self):
        try:
            self.driver.switch_to.window(self.play_window)
            self.driver.switch_to.default_content()
            page_percent = self._page_learn_percent()
            from selenium.webdriver.common.by import By

            iframe = self.driver.find_elements(By.CSS_SELECTOR, 'iframe')
            if not iframe:
                if page_percent is None:
                    return None
                return {
                    'current': 0.0,
                    'duration': 0.0,
                    'percent': page_percent,
                    'paused': False,
                    'ended': page_percent >= 99.5,
                }
            self.driver.switch_to.frame(iframe[0])
            result = self.driver.execute_script(
                """
                const v = document.querySelector('video');
                if (!v) return null;
                const duration = v.duration || 0;
                const current = v.currentTime || 0;
                const percent = duration > 1 ? (current / duration) * 100 : 0;
                return {
                  current: current,
                  duration: duration,
                  percent: percent,
                  paused: !!v.paused,
                  ended: !!v.ended
                };
                """
            )
            self.driver.switch_to.default_content()
            if not result:
                return None
            if page_percent is not None:
                result['percent'] = max(float(result['percent']), page_percent)
            return result
        except Exception:
            try:
                self.driver.switch_to.default_content()
            except Exception:
                pass
            return None

    def _page_learn_percent(self):
        from selenium.webdriver.common.by import By

        try:
            text = self.driver.find_element(By.TAG_NAME, 'body').text or ''
        except Exception:
            return None
        marker = '本节课程您学习了'
        idx = text.find(marker)
        if idx < 0:
            return None
        return self._extract_percent(text[idx:idx + 40])

    def _start_player(self):
        """课件播放器 autoplay=false，需点 iframe 内 #playButton 才会 videoPlay。"""
        end = time.time() + 25
        while time.time() < end and self.is_running and not self._stopped:
            if self._resume_video():
                return
            time.sleep(1)
        self._log_warning('播放器未能开始播放')

    def _resume_video(self) -> bool:
        from selenium.webdriver.common.by import By

        try:
            self.driver.switch_to.window(self.play_window)
            self.driver.switch_to.default_content()
            frames = self.driver.find_elements(By.CSS_SELECTOR, 'iframe')
            if not frames:
                return False
            self.driver.switch_to.frame(frames[0])
            for selector in ('#maskCloseButton', '#adClose', '#playButton'):
                for el in self.driver.find_elements(By.CSS_SELECTOR, selector):
                    try:
                        if not el.is_displayed():
                            continue
                        el.click()
                        self._log_info('已点击播放器 %s', selector)
                        time.sleep(0.4)
                    except Exception:
                        try:
                            self.driver.execute_script('arguments[0].click();', el)
                        except Exception:
                            pass
            state = self.driver.execute_script(
                """
                const v = document.querySelector('video');
                if (window.player && typeof player.videoPlay === 'function' && (!v || v.paused)) {
                    try { player.videoPlay(); } catch (e) {}
                }
                if (!v) return {ready: false, paused: true, reason: 'no-video'};
                if (!v.paused) return {ready: true, paused: false, reason: 'playing'};
                const play = v.play();
                if (play && play.catch) {
                    play.catch(() => {
                        v.muted = true;
                        const again = v.play();
                        if (again && again.catch) again.catch(() => {});
                    });
                }
                return {
                    ready: (v.duration || 0) > 1,
                    paused: !!v.paused,
                    reason: v.paused ? 'still-paused' : 'started'
                };
                """
            )
            paused = bool(state and state.get('paused', True))
            if paused:
                self._log_info('播放器仍暂停 state=%s', state)
            else:
                self._log_info('播放器已开始 state=%s', state)
            return bool(state and state.get('ready') and not paused)
        except Exception:
            self._log_exception('恢复播放失败')
            return False
        finally:
            try:
                self.driver.switch_to.default_content()
            except Exception:
                pass

    def _close_play_window_and_return(self):
        try:
            if self.play_window and self.play_window in self.driver.window_handles:
                self.driver.switch_to.window(self.play_window)
                self.driver.close()
                self._log_info('已关闭播放页')
        except Exception:
            self._log_exception('关闭播放页失败')
        finally:
            self.play_window = None
        self._ensure_on_list_window()
