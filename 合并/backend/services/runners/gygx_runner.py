"""
广元公需课（GYGX）任务执行器

网站编码：GYGX
站点：https://www.gysjxjy.com:90/

会话在 sessionStorage（accessToken 等），播放由站点 window.open 新开页。
保留课程列表页窗口，通过 window handles 切换；禁止另起浏览器或无关直达重建会话。

任务 class_id 对应站点 planId。
"""
import re
import threading
import time

from services.runners.selenium_runner import SeleniumTaskRunner
from services.task_runner import register_runner

GYGX_HOME_URL = 'https://www.gysjxjy.com:90/'
GYGX_MY_URL = 'https://www.gysjxjy.com:90/my'


@register_runner('GYGX')
class GygxTaskRunner(SeleniumTaskRunner):
    """广元市继续教育网执行器。"""

    def __init__(self, task, website):
        super().__init__(task, website)
        self.list_window = None
        self.play_window = None
        self._play_done_event = threading.Event()

    def run_main(self):
        self._log_info(
            '开始任务 id=%s user=%s class_id=%s headless=%s',
            self.task.id, self.task.username, self.task.class_id, self.task.is_head,
        )
        try:
            if not self.task.class_id:
                raise RuntimeError('GYGX 任务缺少 class_id（对应站点 planId）')
            self._init_browser(window_size=(1920, 1080))
            self._ensure_logged_in(max_rounds=5)
            self._open_course_package()
            self._play_course_loop()
            self._sync_task_status()
        except Exception:
            self._log_exception('任务 id=%s 执行失败', self.task.id)
            self._handle_run_exception()
            raise
        finally:
            self._finalize_run()

    # ------------------------------------------------------------------ login
    def _is_logged_in(self) -> bool:
        token = self._get_session_storage('accessToken')
        return bool(token)

    def _auto_login(self):
        from selenium.common import ElementNotInteractableException, TimeoutException
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.wait import WebDriverWait

        self.driver.get(GYGX_HOME_URL)
        time.sleep(2)
        self._dismiss_notice_dialog()

        if self._is_logged_in():
            self._log_info('检测到已有登录态，跳过表单')
            return

        try:
            self._open_login_form()
            self._ensure_account_login_tab()

            inputs = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'input.el-input__inner'))
            )
            # 账号登录：账号、密码、验证码
            text_inputs = [el for el in inputs if (el.get_attribute('type') or 'text') != 'password']
            pwd_inputs = [el for el in inputs if (el.get_attribute('type') or '') == 'password']
            if len(text_inputs) < 2 or not pwd_inputs:
                raise RuntimeError('未找到登录输入框')

            account = text_inputs[0]
            captcha_input = text_inputs[1]
            password = pwd_inputs[0]

            account.clear()
            account.send_keys(self.task.username)
            password.clear()
            password.send_keys(self.task.password)

            captcha_input.clear()
            captcha_input.send_keys(self._recognize_image_captcha())

            login_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '.login-btn.cursor'))
            )
            login_btn.click()
            time.sleep(3)
            self._dismiss_message_box()
            self._log_info('登录表单已提交 user=%s', self.task.username)
        except (TimeoutException, ElementNotInteractableException):
            self._log_exception('登录失败')
            raise

    def _dismiss_notice_dialog(self):
        from selenium.webdriver.common.by import By

        try:
            btn = self.driver.find_element(By.CSS_SELECTOR, '.sure-btn.cursor')
            if btn.is_displayed():
                btn.click()
                time.sleep(0.5)
                self._log_info('已关闭特别提醒弹窗')
        except Exception:
            pass

    def _open_login_form(self):
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.wait import WebDriverWait

        # 已展开则跳过
        if self.driver.find_elements(By.CSS_SELECTOR, 'input.el-input__inner'):
            return

        login_entry = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//div[contains(@class,"my") and contains(@class,"cursor") and normalize-space()="登录"]'))
        )
        login_entry.click()
        time.sleep(1)

    def _ensure_account_login_tab(self):
        from selenium.webdriver.common.by import By

        try:
            tab = self.driver.find_element(
                By.XPATH,
                '//div[contains(@class,"type-item") and contains(normalize-space(),"账号登录")]',
            )
            if 'active' not in (tab.get_attribute('class') or ''):
                tab.click()
                time.sleep(0.5)
        except Exception:
            pass

    def _recognize_image_captcha(self) -> str:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.wait import WebDriverWait

        try:
            img = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.code-img-box img'))
            )
            return self._recognize_captcha_screenshot(img, f'gygx_{self.task.username}.png')
        except Exception:
            self._log_exception('验证码识别失败')
            return ''

    # -------------------------------------------------------- course package
    def _open_course_package(self):
        """通过 sessionStorage 注入 planId，进入「我的课程」课包列表。"""
        plan_id = str(self.task.class_id).strip()
        self._log_info('进入个人中心并打开课包 planId=%s', plan_id)

        # 同 tab 内跳转，sessionStorage 保持
        self.driver.get(GYGX_MY_URL)
        time.sleep(2)
        if not self._is_logged_in():
            raise RuntimeError('进入个人中心时登录态丢失')

        # 站点 my 页在切入「我的课程」时会读取 showCoursePackage + planId
        self.driver.execute_script(
            "sessionStorage.setItem('planId', arguments[0]);"
            "sessionStorage.setItem('showCoursePackage', 'true');",
            plan_id,
        )
        self._click_menu_my_course()
        time.sleep(3)
        self._dismiss_message_box()

        # 通过planId找到课程列表
        self._wait_course_table(plan_id=plan_id, timeout=12)

        self.list_window = self.driver.current_window_handle
        self._log_info('课包列表已打开 list_window=%s', self.list_window)

    def _click_plan_card_by_id(self, plan_id: str):
        from selenium.webdriver.common.by import By

        try:
            # 卡片/行上包含 planId，或「去学习」所在父节点
            candidates = self.driver.find_elements(
                By.XPATH,
                f'//*[contains(normalize-space(.), "{plan_id}")]',
            )
            for el in candidates:
                if not el.is_displayed():
                    continue
                try:
                    el.click()
                    self._log_info('已按 planId 点击课程入口: %s', plan_id)
                    return
                except Exception:
                    continue
            # 无精确 id 时点第一个「去学习」（外层课包入口）
            links = self.driver.find_elements(
                By.XPATH,
                '//*[contains(normalize-space(),"去学习")]',
            )
            for el in links:
                if el.is_displayed():
                    el.click()
                    self._log_info('已点击外层去学习入口')
                    return
        except Exception:
            self._log_exception('按 planId 点击课程失败')

    def _click_menu_my_course(self):
        from selenium.webdriver.common.by import By

        my_course = self.driver.find_element(By.XPATH, "//div[@class='box-item-text' and text()='我的课程']")
        my_course.click()

    def _wait_course_table(self, plan_id=None, timeout=15) -> bool:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//div[@class='course-item-title' and contains(text(), '" + plan_id + "')]/ancestor::div[@class='course-item']//span[text()='去学习']"
                ))
            )
            element.click()
            time.sleep(1)
        except Exception:
            pass


    # ----------------------------------------------------------- play loop
    def _play_course_loop(self):
        while self.is_running and not self.is_complete and not self._stopped:
            self._ensure_on_list_window()
            target = self._find_first_unfinished_study_link()
            if target is None:
                self._log_info('课包内视频均已完成')
                self._mark_course_complete()
                return

            course_name, progress, link = target
            self._log_info('准备播放: %s 当前进度=%s', course_name, progress)
            before_handles = set(self.driver.window_handles)
            try:
                link.click()
            except Exception:
                self.driver.execute_script('arguments[0].click();', link)

            play_handle = self._wait_new_window(before_handles, timeout=20)
            if not play_handle:
                self._log_warning('未检测到播放新窗口，重试刷新列表')
                self._refresh_course_list()
                continue

            self.play_window = play_handle
            self.driver.switch_to.window(play_handle)
            self._log_info('已切换到播放页')
            time.sleep(2)
            self._dismiss_message_box()

            self._play_done_event.clear()
            self._start_monitor_thread(self._monitor_play_progress, suffix='play')
            self._play_done_event.wait()

            self._close_play_window_and_return()
            self._refresh_course_list()
            time.sleep(2)

        if self.is_running and not self._stopped and not self.is_complete:
            # 循环异常退出时保持未完成
            self._log_warning('播放循环结束但未标记完成')

    def _ensure_on_list_window(self):
        if self.list_window and self.list_window in self.driver.window_handles:
            self.driver.switch_to.window(self.list_window)
        else:
            # 列表页丢失时重新打开课包（同 tab 恢复）
            self._log_warning('列表窗口丢失，重新打开课包')
            self._open_course_package()

    def _find_first_unfinished_study_link(self):
        """返回 (课程名, 进度文本, 去学习元素) 或 None。"""
        from selenium.webdriver.common.by import By

        try:
            rows = self.driver.find_elements(By.CSS_SELECTOR, '.el-table__body tr')
            for row in rows:
                text = (row.text or '').strip()
                if not text:
                    continue
                progress = self._extract_progress_percent(text)
                self._log_info('课表行: %s | 解析进度=%s', text.replace('\n', ' / '), progress)
                if progress is not None and progress >= 100:
                    continue
                links = row.find_elements(
                    By.XPATH,
                    './/span[contains(@class,"study-text") and contains(normalize-space(),"去学习")]',
                )
                if not links:
                    continue
                name = text.split('\n')[0].strip() if text else ''
                return name, progress, links[0]
        except Exception:
            self._log_exception('查找未完成课件失败')
        return None

    def _extract_progress_percent(self, text: str):
        # 匹配 100% / 35.5% / 进度相关数字
        matches = re.findall(r'(\d+(?:\.\d+)?)\s*%', text or '')
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

                self._dismiss_message_box()
                self._try_resume_video()

                percent = self._read_play_percent()
                if percent is not None:
                    self._log_info('播放进度: %.1f%%', percent)
                    if percent >= 100:
                        self._log_info('当前课件播放完成')
                        break

                time.sleep(8)
        finally:
            self._play_done_event.set()

    def _read_play_percent(self):
        from selenium.webdriver.common.by import By

        # 1) 页面 progress-info 文案
        try:
            infos = self.driver.find_elements(By.CSS_SELECTOR, '.progress-info')
            for el in infos:
                if not el.is_displayed():
                    continue
                p = self._extract_progress_percent(el.text or '')
                if p is not None:
                    return p
        except Exception:
            pass

        # 2) video 元素计算
        try:
            result = self.driver.execute_script(
                """
                const v = document.querySelector('video.course-video') || document.querySelector('video');
                if (!v || !v.duration) return null;
                return (v.currentTime / v.duration) * 100;
                """
            )
            if result is not None:
                return float(result)
        except Exception:
            pass

        # 3) iframe 内 video
        try:
            iframes = self.driver.find_elements(By.CSS_SELECTOR, 'iframe, #video-container iframe')
            for iframe in iframes:
                try:
                    self.driver.switch_to.frame(iframe)
                    result = self.driver.execute_script(
                        """
                        const v = document.querySelector('video');
                        if (!v || !v.duration) return null;
                        return (v.currentTime / v.duration) * 100;
                        """
                    )
                    self.driver.switch_to.default_content()
                    if result is not None:
                        return float(result)
                except Exception:
                    try:
                        self.driver.switch_to.default_content()
                    except Exception:
                        pass
        except Exception:
            pass
        return None

    def _try_resume_video(self):
        try:
            self.driver.execute_script(
                """
                const tryPlay = (v) => {
                  if (!v) return;
                  if (v.paused) { v.play().catch(() => {}); }
                };
                tryPlay(document.querySelector('video.course-video') || document.querySelector('video'));
                const iframes = document.querySelectorAll('iframe');
                for (const f of iframes) {
                  try {
                    const doc = f.contentDocument || f.contentWindow.document;
                    tryPlay(doc.querySelector('video'));
                  } catch (e) {}
                }
                """
            )
        except Exception:
            pass

        # 点击可能的确认弹窗继续
        self._dismiss_message_box()

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
        """点击「查询」刷新课包进度。"""
        from selenium.webdriver.common.by import By

        self._ensure_on_list_window()
        self._dismiss_message_box()
        for xpath in (
                '//span[contains(@class,"get-code") and contains(normalize-space(),"查询")]',
                '//div[contains(@class,"search-icon") and contains(@class,"cursor")]',
                '//*[contains(@class,"cursor") and normalize-space()="查询"]',
                '//button[contains(.,"查询")]',
        ):
            try:
                els = self.driver.find_elements(By.XPATH, xpath)
                for el in els:
                    if el.is_displayed():
                        el.click()
                        self._log_info('已点击查询刷新进度')
                        time.sleep(2)
                        return
            except Exception:
                continue
        self._log_warning('未找到查询按钮，尝试重新打开课包')
        self._open_course_package()

    def _dismiss_message_box(self):
        from selenium.webdriver.common.by import By

        for xpath in (
                '//div[contains(@class,"el-message-box")]//button[contains(.,"确认") or contains(.,"确定")]',
                '//button[contains(@class,"el-button") and (contains(.,"确认") or contains(.,"确定"))]',
                '//div[contains(@class,"sure-btn")]',
        ):
            try:
                btns = self.driver.find_elements(By.XPATH, xpath)
                for btn in btns:
                    if btn.is_displayed():
                        btn.click()
                        time.sleep(0.3)
            except Exception:
                continue
        try:
            self._dismiss_confirm_dialog()
        except Exception:
            pass
