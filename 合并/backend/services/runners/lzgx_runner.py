"""
泸州公需课（LZGX）任务执行器

网站编码：LZGX
站点：https://jxjy.lzy.edu.cn/

登录：首页身份证 + 密码 + 图形验证码（ddddocr）
播课：保留 /reg/userStudy 列表窗，站点 videoStudy 新开播放页；句柄切换。
任务 class_id 对应站点 courseId。
"""
from __future__ import annotations

import re
import threading
import time

from services.runners.selenium_runner import SeleniumTaskRunner
from services.task_runner import register_runner, update_task_fields

LZGX_HOME_URL = 'https://jxjy.lzy.edu.cn/'
LZGX_INDEX_URL = 'https://jxjy.lzy.edu.cn/reg/index'
LZGX_STUDY_URL_TMPL = 'https://jxjy.lzy.edu.cn/reg/userStudy?courseId={course_id}'
PERCENT_PATTERN = re.compile(r'(\d+(?:\.\d+)?)\s*%')
DONE_MARKERS = ('已完成',)


@register_runner('LZGX')
class LzgxTaskRunner(SeleniumTaskRunner):
    """泸州职业技术学院继续教育网：登录 + 按 courseId 播未完成课件。"""

    def __init__(self, task, website):
        super().__init__(task, website)
        self.course_id = ''
        self.list_window = None
        self.play_window = None
        self._play_done_event = threading.Event()

    def run_main(self):
        self._log_info(
            '开始任务 id=%s user=%s class_id=%s headless=%s',
            self.task.id, self.task.username, self.task.class_id, self.task.is_head,
        )
        try:
            self._prepare_config()
            self._init_browser(window_size=(1920, 1080))
            self._ensure_logged_in(max_rounds=5)
            self._sync_user_profile()
            self._open_course_list()
            self._play_course_loop()
            self._sync_task_status()
        except Exception:
            self._log_exception('任务 id=%s 执行失败', self.task.id)
            self._handle_run_exception()
            raise
        finally:
            self._finalize_run()

    def _prepare_config(self):
        self.course_id = (self.task.class_id or '').strip()
        if not self.course_id:
            raise RuntimeError('LZGX 任务缺少 class_id（课程 courseId）')
        if self.course_id.startswith('http'):
            raise RuntimeError('LZGX class_id 须为课程 ID，不要填完整 URL')
        self._log_info('课程 courseId=%s', self.course_id)

    # ------------------------------------------------------------------ login
    def _is_logged_in(self) -> bool:
        from selenium.webdriver.common.by import By

        try:
            url = (self.driver.current_url or '').lower()
            if '/reg/' in url:
                logout = self.driver.find_elements(
                    By.XPATH, '//a[contains(@href,"/logout") or contains(normalize-space(),"注销登录")]'
                )
                if any(el.is_displayed() for el in logout):
                    return True
            # cookie 存在时再探学员中心
            if self.get_cookies_values('lzrspx_front'):
                if '/reg/' in url and 'login' not in url:
                    return True
        except Exception:
            self._log_exception('检测登录态失败')
        return False

    def _auto_login(self):
        from selenium.common import ElementNotInteractableException, TimeoutException
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.wait import WebDriverWait

        self._driver_get(LZGX_HOME_URL)
        time.sleep(2)
        self._dismiss_layer_dialogs()

        if self._is_logged_in():
            self._log_info('检测到已有登录态，跳过表单')
            return

        try:
            username = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'username'))
            )
            username.clear()
            username.send_keys(self.task.username)

            password = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'password'))
            )
            password.clear()
            password.send_keys(self.task.password)

            captcha = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'captcha'))
            )
            captcha.clear()
            captcha.send_keys(self._recognize_image_captcha())

            login_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'input.btn_dl, .btn_dl'))
            )
            login_btn.click()
            time.sleep(3)
            self._dismiss_layer_dialogs()
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
                EC.presence_of_element_located((By.ID, 'imgcode'))
            )
            return self._recognize_captcha_screenshot(img, f'lzgx_{self.task.username}.png')
        except Exception:
            self._log_exception('验证码识别失败')
            return ''

    def _sync_user_profile(self):
        from selenium.webdriver.common.by import By

        try:
            if '/reg/' not in (self.driver.current_url or ''):
                self._driver_get(LZGX_INDEX_URL)
                time.sleep(2)
            self._dismiss_layer_dialogs()
            headings = self.driver.find_elements(By.XPATH, '//h2[contains(.,"姓名")]')
            for h in headings:
                text = (h.text or '').strip()
                if '姓名' in text:
                    name = text.split('：', 1)[-1].split(':', 1)[-1].strip()
                    if name:
                        update_task_fields(self.task, nick_name=name)
                        self._log_info('已登录 %s', name)
                    return
        except Exception:
            self._log_exception('同步学员资料失败')

    # ------------------------------------------------------------- course list
    def _study_list_url(self) -> str:
        return LZGX_STUDY_URL_TMPL.format(course_id=self.course_id)

    def _open_course_list(self):
        url = self._study_list_url()
        self._log_info('打开课程学习列表 %s', url)
        self._driver_get(url)
        time.sleep(2)
        self._dismiss_layer_dialogs()

        if 'login' in (self.driver.current_url or '').lower() and '/reg/' not in (
            self.driver.current_url or ''
        ):
            raise RuntimeError('打开学习列表时未登录，被重定向到登录页')

        if not self._wait_study_table(timeout=15):
            raise RuntimeError(f'未找到课程列表表格 courseId={self.course_id}')

        self.list_window = self.driver.current_window_handle
        hours = self._read_course_hours_summary()
        if hours:
            self._update_task_progress(hours)
        self._log_info('课程列表已打开 list_window=%s hours=%s', self.list_window, hours or '-')

    def _wait_study_table(self, timeout=15) -> bool:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.wait import WebDriverWait

        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//table//th[contains(.,"课件标题") or contains(.,"学习进度")]')
                )
            )
            return True
        except Exception:
            self._log_warning('等待课件表格超时')
            return False

    def _read_course_hours_summary(self) -> str:
        from selenium.webdriver.common.by import By

        try:
            paras = self.driver.find_elements(By.TAG_NAME, 'p')
            for p in paras:
                text = (p.text or '').strip()
                if '学时' in text:
                    return text.replace('课程学时：', '').strip()
        except Exception:
            pass
        return ''

    # --------------------------------------------------------------- play loop
    def _play_course_loop(self):
        while self.is_running and not self.is_complete and not self._stopped:
            self._ensure_on_list_window()
            target = self._find_first_unfinished_study_link()
            if target is None:
                self._log_info('本课视频均已完成')
                self._mark_course_complete()
                return

            title, progress, link = target
            self._log_info('准备播放: %s 当前进度=%s', title, progress)
            before_handles = set(self.driver.window_handles)
            try:
                link.click()
            except Exception:
                self.driver.execute_script('arguments[0].click();', link)

            play_handle = self._wait_new_window(before_handles, timeout=20)
            if not play_handle:
                self._log_warning('未检测到播放新窗口，刷新列表后重试')
                self._refresh_course_list()
                continue

            self.play_window = play_handle
            self.driver.switch_to.window(play_handle)
            self._log_info('已切换到播放页 url=%s', self.driver.current_url)
            time.sleep(2)
            self._dismiss_layer_dialogs()
            self._try_resume_video()

            self._play_done_event.clear()
            self._start_monitor_thread(self._monitor_play_progress, suffix='play')
            self._play_done_event.wait()

            self._close_play_window_and_return()
            self._refresh_course_list()
            time.sleep(2)

        if self.is_running and not self._stopped and not self.is_complete:
            self._log_warning('播放循环结束但未标记完成')

    def _ensure_on_list_window(self):
        if self.list_window and self.list_window in self.driver.window_handles:
            self.driver.switch_to.window(self.list_window)
        else:
            self._log_warning('列表窗口丢失，重新打开课程列表')
            self._open_course_list()

    def _find_first_unfinished_study_link(self):
        """返回 (课件标题, 进度文本, 学习链接元素) 或 None。"""
        from selenium.webdriver.common.by import By

        try:
            rows = self.driver.find_elements(By.CSS_SELECTOR, 'table tr')
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, 'td')
                if len(cells) < 7:
                    continue
                title = (cells[0].text or '').strip()
                progress_text = (cells[5].text or '').strip()
                if self._is_lesson_done(progress_text):
                    continue
                links = cells[6].find_elements(
                    By.XPATH, './/a[contains(normalize-space(),"学习")]'
                )
                if not links:
                    continue
                return title, progress_text, links[0]
        except Exception:
            self._log_exception('查找未完成课件失败')
        return None

    def _is_lesson_done(self, progress_text: str) -> bool:
        text = progress_text or ''
        if any(m in text for m in DONE_MARKERS):
            return True
        percent = self._extract_progress_percent(text)
        return percent is not None and percent >= 100

    @staticmethod
    def _extract_progress_percent(text: str):
        matches = PERCENT_PATTERN.findall(text or '')
        if not matches:
            return None
        try:
            return float(matches[-1])
        except ValueError:
            return None

    def _wait_new_window(self, before_handles: set, timeout=20):
        end = time.time() + timeout
        while time.time() < end and self.is_running:
            handles = set(self.driver.window_handles)
            new_ones = handles - before_handles
            if new_ones:
                return next(iter(new_ones))
            time.sleep(0.5)
        return None

    def _monitor_play_progress(self):
        self._log_info('开始监控播放进度')
        stuck_rounds = 0
        last_percent = -1.0
        try:
            while self.is_running and not self._stopped:
                if self.play_window and self.play_window not in self.driver.window_handles:
                    self._log_warning('播放窗口已关闭')
                    break

                try:
                    if self.play_window:
                        self.driver.switch_to.window(self.play_window)
                except Exception:
                    break

                self._dismiss_layer_dialogs()
                self._try_resume_video()

                if self._read_daily_limit_alert():
                    self._log_warning('触发单日学时上限或站点停止计时，结束当前课件监控')
                    break

                percent = self._read_play_percent()
                if percent is not None:
                    self._log_info('播放进度: %.1f%%', percent)
                    if percent >= 99.5:
                        self._log_info('当前课件播放完成')
                        break
                    if abs(percent - last_percent) < 0.1:
                        stuck_rounds += 1
                    else:
                        stuck_rounds = 0
                        last_percent = percent
                    if stuck_rounds >= 40:
                        self._log_warning('播放进度长时间无变化，结束当前课件监控')
                        break

                time.sleep(8)
        finally:
            self._play_done_event.set()

    def _read_play_percent(self):
        from selenium.webdriver.common.by import By

        # 1) 页面提示文案「学习进度:xx%」
        try:
            for el in self.driver.find_elements(By.ID, 'ts_msg'):
                p = self._extract_progress_percent(el.text or '')
                if p is not None:
                    return p
            body = self.driver.find_element(By.TAG_NAME, 'body').text or ''
            p = self._extract_progress_percent(body)
            if p is not None and '学习进度' in body:
                return p
        except Exception:
            pass

        # 2) video.currentTime / duration（仅作辅助；不 seek）
        try:
            result = self.driver.execute_script(
                """
                const v = document.getElementById('video') || document.querySelector('video');
                if (!v || !v.duration || v.duration < 1) return null;
                if (v.ended) return 100;
                return (v.currentTime / v.duration) * 100;
                """
            )
            if result is not None:
                return float(result)
        except Exception:
            pass
        return None

    def _read_daily_limit_alert(self) -> bool:
        from selenium.webdriver.common.by import By

        try:
            text = (self.driver.find_element(By.TAG_NAME, 'body').text or '')
            keywords = ('当日累计有效学时已达上限', '不再计入学时', '停止记录学时')
            return any(k in text for k in keywords)
        except Exception:
            return False

    def _try_resume_video(self):
        from selenium.webdriver.common.by import By

        # layer「继续学习」
        for xpath in (
            '//a[contains(@class,"layui-layer-btn") and contains(.,"继续学习")]',
            '//div[contains(@class,"layui-layer-btn")]//a[contains(.,"继续学习")]',
            '//a[contains(normalize-space(),"继续学习")]',
            '//button[contains(normalize-space(),"继续学习")]',
        ):
            try:
                btns = self.driver.find_elements(By.XPATH, xpath)
                for btn in btns:
                    if btn.is_displayed():
                        btn.click()
                        time.sleep(0.3)
                        self._log_info('已点击继续学习')
            except Exception:
                continue

        try:
            self.driver.execute_script(
                """
                const v = document.getElementById('video') || document.querySelector('video');
                if (v && v.paused) { v.play().catch(() => {}); }
                """
            )
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

    def _refresh_course_list(self):
        self._ensure_on_list_window()
        self._dismiss_layer_dialogs()
        try:
            self.driver.refresh()
            time.sleep(2)
            self._dismiss_layer_dialogs()
            self._wait_study_table(timeout=15)
            hours = self._read_course_hours_summary()
            if hours:
                self._update_task_progress(hours)
            self._log_info('已刷新课程列表 progress=%s', hours or '-')
        except Exception:
            self._log_warning('刷新失败，重新打开课程列表')
            self._open_course_list()

    def _dismiss_layer_dialogs(self):
        from selenium.webdriver.common.by import By

        # 优先点「继续学习 / 确定 / 确认」
        for xpath in (
            '//a[contains(@class,"layui-layer-btn") and (contains(.,"继续学习") or contains(.,"确定") or contains(.,"确认"))]',
            '//div[contains(@class,"layui-layer-btn")]//a[contains(.,"继续学习") or contains(.,"确定") or contains(.,"确认")]',
            '//a[contains(@class,"layui-layer-close")]',
            '//*[contains(@class,"layui-layer-ico")]',
        ):
            try:
                els = self.driver.find_elements(By.XPATH, xpath)
                for el in els:
                    if el.is_displayed():
                        el.click()
                        time.sleep(0.3)
            except Exception:
                continue
        try:
            self._dismiss_confirm_dialog()
        except Exception:
            pass
