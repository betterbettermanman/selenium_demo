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
        """有会话 cookie，且首页不再显示「登录」入口，视为已登录。"""
        if not self.get_cookies_values('PHPSESSID'):
            return False
        try:
            from selenium.webdriver.common.by import By

            login_els = self.driver.find_elements(By.LINK_TEXT, '登录')
            if any(el.is_displayed() for el in login_els):
                return False
            return True
        except Exception:
            # cookie 在但无法判断页面时，保守认为可能已登录
            return True

    def _login(self, max_rounds=5):
        try:
            self._log_info('打开首页检查登录态 %s', LSGX_HOME_URL)
            self._driver_get(LSGX_HOME_URL)
            time.sleep(3)
        except Exception:
            self._log_warning('打开网站失败')
            raise

        if self._is_logged_in():
            self._log_info('已登录，跳过自动登录 user=%s', self.task.username)
            return

        self._log_info('未登录，开始自动登录 user=%s', self.task.username)
        for idx in range(max_rounds):
            if self._stopped or not self.is_running:
                return
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
            self._log_info('打开首页准备登录 %s', LSGX_HOME_URL)
            self._driver_get(LSGX_HOME_URL)
            time.sleep(5)

            # 再次确认：若已登录则不再点登录
            if self._is_logged_in():
                self._log_info('自动登录前检测到已登录，跳过表单')
                return

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
        self._driver_get(self.current_course_url)
        time.sleep(5)

        if self.find_and_play_first_unfinished():
            self._log_info('已找到未完成课程并开始播放')
            return

        self._log_info('没有未完成课程，标记任务完成')
        self._mark_course_complete()

    def find_and_play_first_unfinished(self) -> bool:
        """找第一个未学完小节并打开；全部已学完则返回 False。"""
        from selenium.webdriver.common.by import By

        try:
            ml_lists = self.driver.find_elements(By.CLASS_NAME, 'ml-list')
            if not ml_lists:
                self._log_warning('未找到课程列表 ml-list')
                return True

            total = len(ml_lists)
            done = 0
            play_href = None
            for item in ml_lists:
                try:
                    href = item.find_element(By.CLASS_NAME, 'begin').get_attribute('href')
                except Exception:
                    continue
                if not href:
                    continue

                try:
                    status = (item.find_element(By.CLASS_NAME, 'flish').text or '').strip()
                except Exception:
                    status = ''

                if status == '已学完':
                    done += 1
                    continue
                if play_href is None:
                    play_href = href

            self._update_task_progress(f'{done}/{total}')
            self._log_info('课表进度 已完成=%s/%s', done, total)

            if play_href:
                self._log_info('打开未完成小节: %s', play_href)
                self._open_video_tab(play_href)
                return True

            self._log_info('列表小节已全部学完')
            return False
        except Exception:
            self._log_exception('查找未完成课程失败')
            return True

    def _check_course_success(self):
        from selenium.webdriver.common.by import By

        sleep_time = 60
        self._log_info('开始监听播放进度 user=%s interval=%ss', self.task.username, sleep_time)

        while not self.is_complete and self.is_running and not self._stopped:
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
                        currentTime: video.currentTime || 0,
                        duration: video.duration || 0
                    };
                """, video)
            except Exception as exc:
                self._log_warning('获取视频进度失败: %s', self._short_exc(exc))
                self._log_warning('未找到播放器，重新打开播放页面')
                self._open_course_home()
                time.sleep(30)
                continue

            try:
                progress = 0.0
                if info['duration'] and info['duration'] > 0:
                    progress = (info['currentTime'] / info['duration']) * 100
                self._log_info('播放进度: %.1f%%', progress)

                if info['ended']:
                    self._log_info('当前视频已播完，查找下一节')
                    self._open_course_home()
                    time.sleep(5)
                elif info['paused'] or info['currentTime'] == 0:
                    reason = '暂停' if info['paused'] and info['currentTime'] > 0 else '未开始'
                    self._log_info('视频%s，尝试继续播放', reason)
                    if not self._resume_video(video):
                        self._log_warning('继续播放失败，稍后重试 currentTime=%.1f', info['currentTime'])
                    time.sleep(5)
            except Exception as exc:
                self._log_warning('处理播放状态失败: %s', self._short_exc(exc))

            time.sleep(sleep_time)

        self._log_info('播放监控结束 user=%s', self.task.username)

    def _video_still_paused(self, video) -> bool:
        try:
            return bool(self.driver.execute_script(
                'var v = arguments[0]; return !v || !!v.paused;', video
            ))
        except Exception:
            return True

    @staticmethod
    def _short_exc(exc: BaseException) -> str:
        """压缩 Selenium 异常，避免把整段 Stacktrace 打进日志。"""
        first = str(exc).split('\n', 1)[0].strip()
        # element click intercepted 常带很长 Element 描述，截断即可
        if len(first) > 180:
            first = first[:180] + '...'
        return f'{type(exc).__name__}: {first}'

    def _dismiss_player_overlays(self, video) -> None:
        """尝试关掉挡住播放器的遮罩/标题层，避免 click intercepted。"""
        from selenium.webdriver.common.by import By

        try:
            self.driver.execute_script(
                """
                var video = arguments[0];
                var root = video && (video.closest('.video-js, .vjs-tech, #my-video') || video.parentElement);
                if (!root) root = document;
                // 常见暂停/提示遮罩
                root.querySelectorAll(
                    '[class*="pausecenter"], .vjs-modal-dialog, .vjs-loading-spinner, .vjs-big-play-button'
                ).forEach(function (el) {
                    try {
                        if (el.classList && el.classList.contains('vjs-big-play-button')) return;
                        el.style.pointerEvents = 'none';
                    } catch (e) {}
                });
                // 盖在 video 上的标题 h2 等，禁止拦截点击
                var rect = video.getBoundingClientRect();
                document.querySelectorAll('h2, .title, [class*="title"]').forEach(function (el) {
                    try {
                        var r = el.getBoundingClientRect();
                        var overlap = !(r.right < rect.left || r.left > rect.right
                            || r.bottom < rect.top || r.top > rect.bottom);
                        if (overlap) el.style.pointerEvents = 'none';
                    } catch (e) {}
                });
                """,
                video,
            )
        except Exception:
            pass

        try:
            overlays = self.driver.find_elements(
                By.XPATH, '//div[starts-with(@class, "pausecenter")]'
            )
            for el in overlays:
                if not el.is_displayed():
                    continue
                try:
                    el.click()
                except Exception:
                    try:
                        self.driver.execute_script('arguments[0].click();', el)
                    except Exception:
                        pass
                self._log_info('已点击 pausecenter 遮罩')
                time.sleep(0.5)
        except Exception:
            pass

    def _resume_video(self, video) -> bool:
        """恢复播放：遮罩 → 控制条 → JS play（中途暂停优先）→ 点击 video。"""
        from selenium.common import ElementClickInterceptedException, ElementNotInteractableException
        from selenium.webdriver.common.action_chains import ActionChains
        from selenium.webdriver.common.by import By

        self._dismiss_player_overlays(video)
        if not self._video_still_paused(video):
            return True

        # 1) 控制条 / 大播放按钮
        for selector in (
            'button.vjs-play-control',
            '.vjs-big-play-button',
            '.vjs-play-control',
            'button.vjs-big-play-button',
        ):
            try:
                for btn in self.driver.find_elements(By.CSS_SELECTOR, selector):
                    if not btn.is_displayed():
                        continue
                    try:
                        btn.click()
                    except (ElementClickInterceptedException, ElementNotInteractableException):
                        self.driver.execute_script('arguments[0].click();', btn)
                    except Exception:
                        try:
                            self.driver.execute_script('arguments[0].click();', btn)
                        except Exception:
                            continue
                    time.sleep(0.8)
                    if not self._video_still_paused(video):
                        self._log_info('通过 %s 恢复播放', selector)
                        return True
            except Exception:
                continue

        # 2) 中途暂停：优先 JS play()（比点 video 更稳，且不受 h2 遮挡影响）
        if self._try_js_play(video):
            return True

        # 3) 再尝试点击 video（过自动播放策略）；被遮挡时静默改用 JS click
        click_attempts = (
            ('native', lambda: video.click()),
            ('actions', lambda: ActionChains(self.driver).move_to_element(video).click().perform()),
            ('js', lambda: self.driver.execute_script('arguments[0].click();', video)),
        )
        for name, clicker in click_attempts:
            try:
                clicker()
                time.sleep(0.8)
                if not self._video_still_paused(video):
                    self._log_info('通过点击 video(%s) 恢复播放', name)
                    return True
            except (ElementClickInterceptedException, ElementNotInteractableException) as exc:
                self._log_info('点击 video(%s) 被拦截，继续下一种方式: %s', name, self._short_exc(exc))
            except Exception as exc:
                self._log_info('点击 video(%s) 失败: %s', name, self._short_exc(exc))

        # 4) 最后再试一次 JS play
        if self._try_js_play(video):
            return True
        return not self._video_still_paused(video)

    def _try_js_play(self, video) -> bool:
        """通过 video.play() 恢复；有声失败则静音重试。"""
        try:
            ok = self.driver.execute_async_script(
                """
                var video = arguments[0];
                var done = arguments[arguments.length - 1];
                function tryPlay(muted) {
                    try { video.muted = !!muted; } catch (e) {}
                    var p = video.play();
                    if (!p || typeof p.then !== 'function') {
                        done(!video.paused);
                        return;
                    }
                    p.then(function () { done(true); })
                     .catch(function () {
                        if (!muted) {
                            tryPlay(true);
                        } else {
                            done(false);
                        }
                     });
                }
                tryPlay(false);
                """,
                video,
            )
            time.sleep(0.5)
            if ok and not self._video_still_paused(video):
                self._log_info('通过 JS play() 恢复播放')
                return True
            self._log_info('JS play() 未恢复 ok=%s paused=%s', ok, self._video_still_paused(video))
        except Exception as exc:
            self._log_info('JS play() 失败: %s', self._short_exc(exc))
        return False
