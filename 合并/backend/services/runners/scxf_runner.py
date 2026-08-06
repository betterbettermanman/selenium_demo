"""
四川学法平台（SCXF）任务执行器

网站编码：SCXF
站点：https://www.scxfks.com
参考：selenium_demo/四川省学法用法平台/main.py

范围：自动登录 + 日常学法播放；学分累计 >= 100 后标记完成（暂不进测评）。
"""
import random
import re
import threading
import time

from services.runners.selenium_runner import SeleniumTaskRunner
from services.task_runner import register_runner, update_task_fields

SCXF_HOME_URL = 'https://www.scxfks.com/study/index'
SCXF_LOGIN_URL = 'https://www.scxfks.com/study/login'
SCXF_COURSES_YEAR = 'https://www.scxfks.com/study/courses/year'
SCXF_COURSES_ALL = 'https://www.scxfks.com/study/courses/all'
SCXF_CREDIT_TARGET = 100


@register_runner('SCXF')
class ScxfTaskRunner(SeleniumTaskRunner):
    """四川省国家工作人员学法用法平台执行器。"""

    def __init__(self, task, website):
        super().__init__(task, website)
        self.current_course_id = ''
        self._opening_home = False
        self._opening_lock = threading.Lock()

    def run_main(self):
        self._log_info(
            '开始任务 id=%s user=%s headless=%s',
            self.task.id, self.task.username, self.task.is_head,
        )
        try:
            self._init_browser(window_size=(1920, 1080))
            self._ensure_logged_in(max_rounds=8)
            self._open_home()
            if not self.is_complete:
                self._start_monitor_thread(self._check_course_success)
                self._wait_until_complete()
            self._sync_task_status()
        except Exception:
            self._log_exception('任务 id=%s 执行失败', self.task.id)
            self._handle_run_exception()
            raise
        finally:
            self._finalize_run()

    # ------------------------------------------------------------------ login
    def _is_logged_in(self) -> bool:
        """
        登录态判定（勿仅依赖首页 .userbox）：
        - 明确在登录页 → 未登录
        - 已在 /study/ 业务页（首页/课程/章节等）→ 视为已登录
        - 否则再查 .userbox /「退出登录」
        """
        from selenium.common import NoSuchElementException
        from selenium.webdriver.common.by import By

        try:
            url = self.driver.current_url or ''
        except Exception:
            return False

        if '/study/login' in url:
            return False

        # 课程列表、章节页等通常没有首页 userbox，不能据此误判掉线
        if 'scxfks.com/study/' in url and '/study/login' not in url:
            return True

        try:
            self.driver.find_element(By.CLASS_NAME, 'userbox')
            return True
        except NoSuchElementException:
            pass
        try:
            self.driver.find_element(By.LINK_TEXT, '退出登录')
            return True
        except NoSuchElementException:
            pass
        return False

    def _auto_login(self):
        from selenium.common import ElementNotInteractableException, TimeoutException
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.wait import WebDriverWait

        self._log_info('打开登录页 %s', SCXF_LOGIN_URL)
        self._driver_get(SCXF_LOGIN_URL)
        time.sleep(2)

        try:
            try:
                account_tab = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.LINK_TEXT, '使用账号登录'))
                )
                account_tab.click()
                time.sleep(1)
            except TimeoutException:
                pass

            username_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='mobile']"))
            )
            username_input.clear()
            username_input.send_keys(self.task.username)

            password_input = self.driver.find_element(By.CSS_SELECTOR, "input[name='password']")
            password_input.clear()
            password_input.send_keys(self.task.password)

            captcha = self._recognize_image_captcha()
            if not captcha:
                self._refresh_captcha()
                captcha = self._recognize_image_captcha()
            captcha_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='captcha']"))
            )
            captcha_input.clear()
            captcha_input.send_keys(captcha or '')

            # 点登录会先弹出须知弹框，勾选确认后才会真正提交
            submit_btn = None
            for selector in (
                (By.CSS_SELECTOR, "button[name='submit']"),
                (By.CSS_SELECTOR, "button[type='submit']"),
                (By.CLASS_NAME, 'button'),
            ):
                try:
                    submit_btn = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable(selector)
                    )
                    break
                except TimeoutException:
                    continue
            if submit_btn is None:
                raise TimeoutException('未找到登录按钮')
            submit_btn.click()
            time.sleep(1)

            if not self._handle_login_notice():
                self._log_warning('登录须知弹框未处理成功，可能导致登录失败')
            time.sleep(3)

            tip = self._get_login_tip()
            if tip and not self._is_logged_in():
                self._log_warning('登录提示: %s', tip)
                self._refresh_captcha()
        except (TimeoutException, ElementNotInteractableException):
            self._log_exception('登录失败')
            raise

    def _recognize_image_captcha(self) -> str:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.wait import WebDriverWait

        try:
            captcha_el = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'captcha'))
            )
            return self._recognize_captcha_screenshot(captcha_el, f'scxf_{self.task.username}.png')
        except Exception:
            self._log_exception('验证码识别失败')
            return ''

    def _refresh_captcha(self):
        from selenium.common import NoSuchElementException
        from selenium.webdriver.common.by import By

        try:
            self.driver.find_element(By.CLASS_NAME, 'captcha').click()
            time.sleep(1)
        except NoSuchElementException:
            pass

    def _handle_login_notice(self) -> bool:
        """处理登录后的须知弹框（#myModal）：勾选已知晓并点确定。"""
        from selenium.common import TimeoutException
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.wait import WebDriverWait

        try:
            # 等待弹框出现（点登录后由页面脚本唤起）
            WebDriverWait(self.driver, 8).until(
                EC.visibility_of_element_located((By.ID, 'myModal'))
            )
            self._log_info('检测到登录须知弹框，开始处理')

            know = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, 'know'))
            )
            if not know.is_selected():
                try:
                    know.click()
                except Exception:
                    self.driver.execute_script('arguments[0].click();', know)
                time.sleep(0.3)

            yes_btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.ID, 'yes'))
            )
            try:
                yes_btn.click()
            except Exception:
                self.driver.execute_script('arguments[0].click();', yes_btn)

            # 等弹框关闭，避免遮挡后续元素
            try:
                WebDriverWait(self.driver, 8).until(
                    EC.invisibility_of_element_located((By.ID, 'myModal'))
                )
            except TimeoutException:
                # 兜底隐藏，防止残留遮罩挡点击
                self.driver.execute_script(
                    "var m=document.getElementById('myModal');"
                    "if(m){m.classList.remove('show'); m.style.display='none';}"
                    "document.querySelectorAll('.modal-backdrop').forEach(function(e){e.remove();});"
                    "document.body.classList.remove('modal-open');"
                )
            self._log_info('登录须知弹框已关闭')
            time.sleep(1)
            return True
        except TimeoutException:
            self._log_warning('未检测到登录须知弹框')
            return False

    def _get_login_tip(self) -> str:
        from selenium.common import NoSuchElementException
        from selenium.webdriver.common.by import By

        try:
            return (self.driver.find_element(By.CSS_SELECTOR, 'div.tip').text or '').strip()
        except NoSuchElementException:
            return ''

    # --------------------------------------------------------------- study
    def _dismiss_popups(self):
        from selenium.common import NoSuchElementException, TimeoutException
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.wait import WebDriverWait

        try:
            cancel_button = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.ID, 'noWx'))
            )
            cancel_button.click()
            self._log_info('已关闭微信绑定提示')
        except (TimeoutException, NoSuchElementException):
            pass

    @staticmethod
    def _parse_score_value(text) -> float:
        match = re.search(r'(\d+(?:\.\d+)?)', text or '')
        return float(match.group(1)) if match else 0.0

    def _get_user_info(self) -> dict:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.wait import WebDriverWait

        card = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'userbox'))
        )
        user_info = {}
        for p in card.find_elements(By.TAG_NAME, 'p'):
            text = p.text or ''
            if '：' in text:
                key, value = text.split('：', 1)
                user_info[key.strip()] = value.strip()
        self._log_info('用户信息: %s', user_info)
        return user_info

    def _sync_profile(self, user_info: dict):
        nick = user_info.get('姓名') or user_info.get('用户名') or ''
        organ = user_info.get('单位') or user_info.get('所在单位') or ''
        fields = {}
        if nick:
            fields['nick_name'] = nick
        if organ:
            fields['organ_name'] = organ
        if fields:
            update_task_fields(self.task, **fields)

    def _open_home(self):
        if self.is_complete or self._stopped or not self.is_running:
            return

        self._log_info('打开首页检测学习情况')
        self._driver_get(SCXF_HOME_URL)
        time.sleep(3)
        self._dismiss_popups()

        if not self._is_logged_in():
            self._log_warning('首页检测未登录，重新登录')
            self._ensure_logged_in(max_rounds=5)
            self._driver_get(SCXF_HOME_URL)
            time.sleep(3)
            self._dismiss_popups()

        user_info = self._get_user_info()
        self._sync_profile(user_info)
        credit_score = self._parse_score_value(user_info.get('学分累计', '0'))
        self._log_info('学分累计: %s / %s', credit_score, SCXF_CREDIT_TARGET)
        self._update_task_progress(f'{credit_score:g}/{SCXF_CREDIT_TARGET}')

        if credit_score >= SCXF_CREDIT_TARGET:
            self._log_info('学分已达标，标记任务完成（暂不进测评）')
            self._mark_course_complete()
            return

        self._open_daily_study()

    def _refresh_credit_progress(self) -> float | None:
        """回首页读取学分并写到任务 progress，返回学分值。"""
        try:
            self._driver_get(SCXF_HOME_URL)
            time.sleep(3)
            self._dismiss_popups()
            user_info = self._get_user_info()
            self._sync_profile(user_info)
            credit_score = self._parse_score_value(user_info.get('学分累计', '0'))
            progress = f'{credit_score:g}/{SCXF_CREDIT_TARGET}'
            self._update_task_progress(progress)
            self._log_info('当前学分进度: %s', progress)
            return credit_score
        except Exception as exc:
            self._log_warning('回写学分进度失败: %s', exc)
            return None

    def _finish_for_daily_limit(self):
        """今日上限：回写学分、结束本次执行（不标记任务完成，便于次日/调度续跑）。"""
        self._log_info('已到达今日上限，回写学分并结束本次执行')
        credit_score = self._refresh_credit_progress()
        if credit_score is not None and credit_score >= SCXF_CREDIT_TARGET:
            self._log_info('学分已达标，标记任务完成（暂不进测评）')
            self._mark_course_complete()
            return
        # 未达总目标：停跑并关浏览器，任务保持未完成 status=1
        self.is_running = False

    def _start_course_chapter(self) -> bool:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.wait import WebDriverWait

        if '/chapter/' in (self.driver.current_url or ''):
            self.current_course_id = self.driver.current_url.rsplit('/chapter/', 1)[-1]
            self._log_info('开始学习章节: %s', self.current_course_id)
            return True

        chapters = self.driver.find_elements(By.XPATH, "//li[@chapter-type='0' and @class='c_item']")

        for index, li in enumerate(chapters, 1):
            title_elem = li.find_element(By.XPATH, ".//a")
            title = title_elem.text.strip() if title_elem else f"章节{index}"

            # 有学分标记的视为已学过，跳过；无学分标记则点击学习
            try:
                li.find_element(By.XPATH, ".//div[contains(text(), '学分')]")
                continue
            except Exception:
                pass

            li.click()
            self._log_info('点击未学章节: %s', (title or '').strip()[:40])
            try:
                WebDriverWait(self.driver, 15).until(
                    lambda d: '/chapter/' in (d.current_url or '')
                )
                self.current_course_id = self.driver.current_url.rsplit('/chapter/', 1)[-1]
                self._log_info('已进入章节页: %s', self.current_course_id)
            except Exception:
                self._log_warning(
                    '点击章节后未进入 /chapter/ 页，当前 url=%s',
                    self.driver.current_url,
                )
            return True
        return False

    def _open_daily_study(self):
        from selenium.webdriver.common.by import By

        self._log_info('打开日常学法')
        self._driver_get(SCXF_COURSES_YEAR)
        time.sleep(3)

        study_links = self.driver.find_elements(By.LINK_TEXT, '进入学习')
        for index in range(len(study_links)):
            if self.is_complete or self._stopped or not self.is_running:
                return
            study_links = self.driver.find_elements(By.LINK_TEXT, '进入学习')
            if index >= len(study_links):
                break
            study_links[index].click()
            time.sleep(3)
            if self._start_course_chapter():
                return
            self._driver_get(SCXF_COURSES_YEAR)
            time.sleep(2)

        self._driver_get(SCXF_COURSES_ALL)
        time.sleep(3)
        for link_text in ('继续学习', '开始学习', '进入学习'):
            for study_link in self.driver.find_elements(By.LINK_TEXT, link_text):
                if self.is_complete or self._stopped or not self.is_running:
                    return
                study_link.click()
                time.sleep(3)
                if self._start_course_chapter():
                    return

        self._log_warning('未找到可学习的课程，稍后重试')

    def _spawn_open_home(self):
        """在子线程中打开首页；需带上 Flask app context，否则更新任务会报错。"""
        with self._opening_lock:
            if self._opening_home:
                self._log_info('已有打开首页流程在执行，跳过')
                return
            self._opening_home = True

        def _target():
            try:
                self._run_with_context(self._open_home)
            finally:
                with self._opening_lock:
                    self._opening_home = False

        threading.Thread(
            target=_target,
            daemon=True,
            name=f'scxf-open-home-{self.task.id}',
        ).start()

    def _check_course_success(self):
        from selenium.common import NoSuchElementException
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.wait import WebDriverWait

        while not self.is_complete and self.is_running and not self._stopped:
            sleep_time = 10
            try:
                if '/chapter/' in (self.driver.current_url or ''):
                    try:
                        limit_div = self.driver.find_element(By.CSS_SELECTOR, 'div.limit')
                        if '已到达今日上限' in (limit_div.text or ''):
                            self._finish_for_daily_limit()
                            return
                    except NoSuchElementException:
                        pass

                    wait_time = random.randint(10, 15)
                    self._log_info('章节 %s 学习中，等待 %s 秒', self.current_course_id, wait_time)
                    time.sleep(wait_time)

                    back_btn = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'返回目录')]"))
                    )
                    back_btn.click()
                    self._log_info('章节学习完成，返回目录')
                    time.sleep(3)
                    self._spawn_open_home()
                    sleep_time = 30
                else:
                    # 打开首页/选课线程正在跑时，勿抢 driver，也勿误判登录失效
                    with self._opening_lock:
                        opening = self._opening_home
                    if opening:
                        self._log_info('打开学习流程进行中，本轮跳过检测')
                        sleep_time = 15
                    elif not self._is_logged_in():
                        self._log_warning(
                            '登录失效，重新登录（url=%s）',
                            (self.driver.current_url or '')[:120],
                        )
                        self._ensure_logged_in(max_rounds=5)
                        self._log_info('重新登录完成，重新打开学习')
                        self._spawn_open_home()
                        sleep_time = 30
                    else:
                        self._log_info(
                            '当前不在章节页 url=%s，重新打开学习',
                            (self.driver.current_url or '')[:120],
                        )
                        self._spawn_open_home()
                        sleep_time = 30
            except Exception as exc:
                self._log_error('检测学习状态失败: %s', exc)
                with self._opening_lock:
                    opening = self._opening_home
                if opening:
                    sleep_time = 15
                elif self._is_logged_in():
                    self._spawn_open_home()
                    sleep_time = 20
                else:
                    self._ensure_logged_in(max_rounds=5)
                    self._spawn_open_home()
                    sleep_time = 20

            self._log_info('间隔 %s 秒继续检测', sleep_time)
            time.sleep(sleep_time)
