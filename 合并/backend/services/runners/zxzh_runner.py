"""
国家中小学智慧教育平台（ZXZH）任务执行器

网站编码：ZXZH
站点：https://basic.smartedu.cn/
登录：https://auth.smartedu.cn/uias/login
验证码：腾讯防水墙滑块（iframe #tcaptcha_iframe_dy / drag_ele.html）

流程：检测已有登录态 →（必要时）滑块登录 → 打开专题页（task.class_id）→ 按 task.courses 播课
完成条件：专题页累计学时达到 CREDIT_TARGET（默认 10）。
单课优化：专题页「已学习 > 认定」即跳过换下一门（实际学时通常略高于认定）；「已认定 >= 认定」亦跳过。
"""
from __future__ import annotations

import os
import random
import re
import time
from urllib.request import urlopen

from services.runners.selenium_runner import SeleniumTaskRunner
from services.task_runner import register_runner

ZXZH_HOME_URL = 'https://basic.smartedu.cn/'
ZXZH_LOGIN_URL = 'https://auth.smartedu.cn/uias/login'
SLIDER_MAX_RETRY = 8
CREDIT_TARGET = 10
VIDEO_POLL_SECONDS = 30
VIDEO_MAX_WAIT_SECONDS = 3 * 60 * 60  # 单节最长等待 3 小时
# 专题页单课进度：已学习 2.15 / 已认定 2.00 / 认定 2 学时
COURSE_LEARNED_PATTERN = re.compile(r'已学习\s*([\d.]+)')
COURSE_CREDIT_PATTERN = re.compile(
    r'已认定\s*([\d.]+)\s*/\s*认定\s*([\d.]+)\s*学时'
)
COURSE_CREDIT_SCAN_CHARS = 800
COURSE_CREDIT_EPS = 1e-6
# 专题页「总进度」：已认定 / 要求认定（class 带 hash，用 contains 匹配）
TOTAL_PROGRESS_BLOCK_XPATH = (
    "//*[contains(@class,'topprocess') and contains(.,'要求认定')]"
)
TOTAL_ACCREDITED_PATTERN = re.compile(
    r'已认定\s*/\s*要求认定\s*([\d.]+)\s*/\s*([\d.]+)',
    re.S,
)
TOTAL_ACCREDITED_LOOSE_PATTERN = re.compile(
    r'要求认定\s*([\d.]+)\s*/\s*([\d.]+)',
    re.S,
)


@register_runner('ZXZH')
class ZxzhTaskRunner(SeleniumTaskRunner):
    """国家中小学智慧教育平台：登录 + 教师研修播课。"""

    def __init__(self, task, website):
        super().__init__(task, website)
        self.list_window = None
        self.play_window = None
        self.training_url = ''
        self.course_list: list[dict] = []

    def run_main(self):
        self._log_info(
            '开始任务 id=%s user=%s headless=%s class_id=%s',
            self.task.id, self.task.username, self.task.is_head, self.task.class_id,
        )
        try:
            self._prepare_config()
            self._init_browser(window_size=(1920, 1080))
            if self._check_already_logged_in():
                self._log_info('系统已登录，跳过登录，直接进入专题学习')
            else:
                self._ensure_logged_in(max_rounds=2)
            self._play_training_loop()
            self._sync_task_status()
        except Exception:
            self._log_exception('任务 id=%s 执行失败', self.task.id)
            self._handle_run_exception()
            raise
        finally:
            self._finalize_run()

    def _prepare_config(self):
        self.training_url = (self.task.class_id or '').strip()
        if not self.training_url.startswith('http'):
            raise RuntimeError('ZXZH 任务缺少 class_id（专题页 URL）')
        self.course_list = self._parse_course_configs()
        if not self.course_list:
            raise RuntimeError('ZXZH 任务缺少 courses（需含 title/url 的 JSON 数组）')
        self._log_info('专题页=%s 课程数=%s 目标学时=%s', self.training_url, len(self.course_list), CREDIT_TARGET)
        for idx, item in enumerate(self.course_list, 1):
            self._log_info('课表[%s] %s | %s', idx, item.get('title'), item.get('url'))

    def _parse_course_configs(self) -> list[dict]:
        raw = self._parse_course_items(self.task.courses)
        result = []
        for item in raw:
            if not isinstance(item, dict):
                continue
            title = str(item.get('title') or '').strip()
            url = str(item.get('url') or '').strip()
            if title and url.startswith('http'):
                result.append({'title': title, 'url': url})
        return result

    def _init_browser(self, *, window_size: tuple[int, int] | None = None):
        """启动浏览器并降低 webdriver 特征（腾讯滑块对自动化较敏感）。"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
        except ImportError as exc:
            raise RuntimeError('请先安装 selenium: pip install selenium') from exc

        user_data_dir = self._browser_user_data_dir()
        os.makedirs(user_data_dir, exist_ok=True)

        options = Options()
        if self.task.is_head == '1':
            options.add_argument('--headless=new')
        options.add_argument(f'--user-data-dir={user_data_dir}')
        options.add_argument('--disable-gpu')
        if window_size:
            options.add_argument(f'--window-size={window_size[0]},{window_size[1]}')
        options.add_argument('--start-maximized')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)

        from utils.chromedriver_manager import get_chromedriver_path

        chromedriver_path = get_chromedriver_path()
        service = Service(chromedriver_path)
        self._log_info('使用 chromedriver: %s', chromedriver_path)

        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.maximize_window()
        self.driver.implicitly_wait(10)
        try:
            self.driver.execute_cdp_cmd(
                'Page.addScriptToEvaluateOnNewDocument',
                {'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined});'},
            )
        except Exception:
            self._log_warning('注入 anti-webdriver 脚本失败，继续尝试登录')
        self._log_info('浏览器已启动 headless=%s', self.task.is_head == '1')

    # ------------------------------------------------------------------ login
    def _check_already_logged_in(self) -> bool:
        """先打开专题页/首页，用头像判断是否已登录（对齐寒暑假期教师研修 check_login）。"""
        probe_url = self.training_url or ZXZH_HOME_URL
        self._log_info('登录前检测会话，打开 %s', probe_url)
        try:
            self.driver.get(probe_url)
            time.sleep(5)
        except Exception:
            self._log_warning('打开探测页失败，将走登录流程')
            return False

        # 被踢到登录页 → 未登录
        url = (self.driver.current_url or '').lower()
        if 'auth.smartedu.cn' in url and 'login' in url:
            self._log_info('探测页跳转到登录，判定未登录')
            return False

        if self._has_user_avatar(timeout=8):
            self._log_info('检测到用户头像，判定已登录')
            return True

        if self._is_logged_in():
            self._log_info('检测到登录 cookie/storage，判定已登录')
            return True

        self._log_info('未检测到登录态，需要重新登录')
        return False

    def _has_user_avatar(self, timeout: float = 8) -> bool:
        """参考实现：div.index-module_avatar* 可点击即视为已登录。"""
        try:
            from selenium.webdriver.common.by import By

            xpath = ".//div[starts-with(@class,'index-module_avatar')]"
            if timeout <= 0:
                els = self.driver.find_elements(By.XPATH, xpath)
                return any(el.is_displayed() for el in els)

            from selenium.common import TimeoutException
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.support.wait import WebDriverWait

            WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            return True
        except Exception:
            return False

    def _is_logged_in(self) -> bool:
        try:
            url = (self.driver.current_url or '').lower()
        except Exception:
            return False

        # 仍在登录页则未登录
        if 'auth.smartedu.cn' in url and '/uias/login' in url:
            return False

        # 业务站：优先用头像（与参考脚本一致，瞬时检测避免拖慢循环）
        if 'smartedu.cn' in url and 'auth.smartedu.cn' not in url:
            if self._has_user_avatar(timeout=0):
                return True
            for key in (
                'ND_UC_AUTH', 'UC_TOKEN', 'token', 'access_token', 'TGC',
                'CASTGC', 'SESSION', 'JSESSIONID',
            ):
                if self.get_cookies_values(key):
                    return True
                if self._get_local_storage(key) or self._get_session_storage(key):
                    return True
            # 业务站且无「登录」入口
            try:
                from selenium.webdriver.common.by import By

                login_entries = self.driver.find_elements(
                    By.XPATH,
                    '//a[contains(@class,"user-un-login") or normalize-space()="登录"]',
                )
                visible_login = [el for el in login_entries if el.is_displayed()]
                if not visible_login:
                    return True
            except Exception:
                return True

        for key in (
            'ND_UC_AUTH', 'UC_TOKEN', 'token', 'access_token', 'TGC',
            'CASTGC', 'SESSION', 'JSESSIONID',
        ):
            if self.get_cookies_values(key):
                return True
            if self._get_local_storage(key) or self._get_session_storage(key):
                return True
        return False

    def _auto_login(self):
        from selenium.common import ElementNotInteractableException, TimeoutException
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.wait import WebDriverWait

        self._log_info('打开登录页 %s', ZXZH_LOGIN_URL)
        self.driver.get(ZXZH_LOGIN_URL)
        time.sleep(2)

        if self._is_logged_in() or self._has_user_avatar(timeout=3):
            self._log_info('检测到已有登录态，跳过表单')
            return

        try:
            wait = WebDriverWait(self.driver, 15)
            # 等待 Xuser SDK 初始化验证码类型
            for _ in range(30):
                captcha_type = self.driver.execute_script('return window.currentCaptchaType || "";')
                if captcha_type:
                    self._log_info('验证码类型: %s', captcha_type)
                    break
                time.sleep(0.3)

            username = wait.until(EC.presence_of_element_located((By.ID, 'username')))
            username.clear()
            username.send_keys(self.task.username)

            password = self.driver.find_element(By.ID, 'tmpPassword')
            password.clear()
            password.send_keys(self.task.password)

            agree = self.driver.find_element(By.ID, 'agreementCheckbox')
            if not agree.is_selected():
                self.driver.execute_script('arguments[0].click();', agree)
                time.sleep(0.3)

            login_btn = wait.until(EC.element_to_be_clickable((By.ID, 'loginBtn')))
            login_btn.click()
            self._log_info('已点击登录，等待滑块 user=%s', self.task.username)

            if not self._solve_tencent_slider(max_retry=SLIDER_MAX_RETRY):
                tip = self._get_login_error_tip()
                raise RuntimeError(f'滑块验证失败{(": " + tip) if tip else ""}')

            # 滑块成功后 SDK 会写入 captchaCode 并调用 check() 登录
            for _ in range(30):
                if self._is_logged_in():
                    break
                tip = self._get_login_error_tip()
                if tip:
                    self._log_warning('登录提示: %s', tip)
                    break
                time.sleep(0.5)

            if not self._is_logged_in():
                self.driver.get(ZXZH_HOME_URL)
                time.sleep(2)

            self._log_info('登录流程结束 logged_in=%s url=%s', self._is_logged_in(), self.driver.current_url)
        except (TimeoutException, ElementNotInteractableException):
            self._log_exception('登录失败')
            raise

    def _get_login_error_tip(self) -> str:
        try:
            from selenium.webdriver.common.by import By

            for sel in ('#loginFormError', '.flxerror_tip'):
                els = self.driver.find_elements(By.CSS_SELECTOR, sel)
                for el in els:
                    text = (el.text or '').strip()
                    if text and el.is_displayed():
                        return text
        except Exception:
            pass
        return ''

    # ----------------------------------------------------------- training
    def _play_training_loop(self):
        """登录后：打开专题页，循环播课直到学时达标。"""
        self._open_training_home()
        self.list_window = self.driver.current_window_handle

        if self._hours_reached():
            self._log_info('学时已达标，直接完成')
            self._mark_course_complete()
            return

        empty_rounds = 0
        while self.is_running and not self._stopped and not self.is_complete:
            if not self._is_logged_in():
                self._log_warning('检测到登录失效，尝试重新登录')
                self._ensure_logged_in(max_rounds=2)
                self._open_training_home()
                self.list_window = self.driver.current_window_handle

            if self._hours_reached():
                self._mark_course_complete()
                return

            played = False
            all_credit_done = True
            for course in self.course_list:
                if self._stopped or not self.is_running or self.is_complete:
                    break
                if self._is_course_credit_done(course['title']):
                    self._log_info('课程认定已满，跳过: %s', course['title'])
                    continue
                all_credit_done = False
                self._log_info('尝试播放课程: %s', course['title'])
                if self._play_one_unfinished_section(course):
                    played = True
                    self._switch_to_list_window()
                    self._open_training_home()
                    hours = self._read_training_hours()
                    self._log_info('回专题页刷新学时 current=%s target=%s', hours[0], hours[1])
                    progress = self._read_course_progress(course['title'])
                    if progress:
                        self._log_info(
                            '回专题页课程进度 %s: 已学习=%s 已认定=%s / 认定=%s',
                            course['title'],
                            progress['learned'],
                            progress['accredited'],
                            progress['required'],
                        )
                    if self._hours_reached(hours):
                        self._mark_course_complete()
                        return
                    break
                if self._stopped or not self.is_running:
                    break

            if not played:
                if self._stopped or not self.is_running:
                    break
                empty_rounds += 1
                if all_credit_done:
                    self._log_warning(
                        '配置课程认定均已满但仍未达总学时目标 empty_rounds=%s', empty_rounds
                    )
                else:
                    self._log_warning('本轮未找到可播小节 empty_rounds=%s', empty_rounds)
                if empty_rounds >= 2:
                    raise RuntimeError(
                        f'学时未满（目标 {CREDIT_TARGET}）且 courses 已无未完成小节，请补充 courses 或人工检查'
                    )
                self._open_training_home()
                time.sleep(3)
            else:
                empty_rounds = 0

        if not self.is_complete and not self._stopped:
            self._log_warning('播课循环结束但未标记完成')

    def _open_training_home(self):
        self._log_info('打开专题页 %s', self.training_url)
        self.driver.get(self.training_url)
        time.sleep(5)
        # 未登录会被踢到登录页
        if 'auth.smartedu.cn' in (self.driver.current_url or ''):
            self._log_warning('打开专题页时跳到登录，重新登录')
            self._ensure_logged_in(max_rounds=2)
            self.driver.get(self.training_url)
            time.sleep(5)
        self.list_window = self.driver.current_window_handle

    def _read_training_hours(self) -> tuple[float, float]:
        """从专题页解析 (当前已认定学时, 要求认定学时)。

        页面结构（总进度）：
          已学习 2.80 学时
          已认定 / 要求认定  2.00 / 10 学时
        完成条件应对齐「已认定 / 要求认定」，不能用单课卡片的「已认定/认定」。
        """
        for attempt in range(3):
            hours = self._read_training_hours_from_dom()
            if hours is not None:
                return hours
            hours = self._read_training_hours_from_text()
            if hours is not None:
                return hours
            if attempt < 2:
                time.sleep(1.5)

        self._log_warning('未能解析总进度学时，默认 0/%s', CREDIT_TARGET)
        return 0.0, float(CREDIT_TARGET)

    def _read_training_hours_from_dom(self) -> tuple[float, float] | None:
        """优先用总进度 DOM（class 含 topprocess + 文案含要求认定）。"""
        try:
            from selenium.webdriver.common.by import By

            blocks = self.driver.find_elements(By.XPATH, TOTAL_PROGRESS_BLOCK_XPATH)
        except Exception:
            return None
        if not blocks:
            return None

        # 取文本最长的一块，避免点到过小的子节点
        block = max(blocks, key=lambda el: len((el.text or '').strip()))
        text = (block.text or '').strip()
        if not text:
            return None

        parsed = self._parse_total_accredited_text(text)
        if parsed is not None:
            self._log_info(
                '总进度 DOM 解析 accredited=%s required=%s text=%s',
                parsed[0], parsed[1], re.sub(r'\s+', ' ', text)[:120],
            )
        return parsed

    def _read_training_hours_from_text(self) -> tuple[float, float] | None:
        """文本兜底：只认「要求认定」，避免误匹配单课「已认定/认定」。"""
        body = self._training_page_text()
        if not body:
            return None

        # 先截取「总进度」附近，缩小误匹配范围
        window = body
        idx = body.find('总进度')
        if idx >= 0:
            window = body[idx:idx + 400]
        elif '要求认定' in body:
            idx = body.find('要求认定')
            window = body[max(0, idx - 40):idx + 120]

        parsed = self._parse_total_accredited_text(window)
        if parsed is not None:
            self._log_info(
                '总进度文本解析 accredited=%s required=%s',
                parsed[0], parsed[1],
            )
            return parsed

        # 兼容旧文案：已获学时 2 / 10
        legacy = re.search(
            r'已获(?:得)?学时\s*([\d.]+)\s*/\s*([\d.]+)',
            body,
        )
        if legacy:
            try:
                return float(legacy.group(1)), float(legacy.group(2))
            except (TypeError, ValueError):
                pass
        return None

    @staticmethod
    def _parse_total_accredited_text(text: str) -> tuple[float, float] | None:
        if not text or '要求认定' not in text:
            return None
        for pat in (TOTAL_ACCREDITED_PATTERN, TOTAL_ACCREDITED_LOOSE_PATTERN):
            m = pat.search(text)
            if not m:
                continue
            try:
                current = float(m.group(1))
                target = float(m.group(2))
                if target <= 0:
                    continue
                return current, target
            except (TypeError, ValueError):
                continue

        # DOM text 常被拆成多行：已认定 / 要求认定 \n 2.00 \n / \n 10 \n 学时
        if '要求认定' in text:
            nums = re.findall(r'\d+\.\d+|\d+', text[text.find('要求认定'):])
            if len(nums) >= 2:
                try:
                    current = float(nums[0])
                    target = float(nums[1])
                    if target > 0:
                        return current, target
                except ValueError:
                    pass
        return None

    def _hours_reached(self, hours: tuple[float, float] | None = None) -> bool:
        current, target = hours if hours is not None else self._read_training_hours()
        reached = current >= CREDIT_TARGET or (target > 0 and current >= target)
        self._log_info('学时检测 current=%s target=%s credit_target=%s reached=%s', current, target, CREDIT_TARGET, reached)
        return reached

    def _training_page_text(self) -> str:
        try:
            from selenium.webdriver.common.by import By

            return self.driver.find_element(By.TAG_NAME, 'body').text or ''
        except Exception:
            return self.driver.page_source or ''

    def _read_course_progress(self, title: str) -> dict[str, float] | None:
        """从专题页解析某门课进度：已学习 / 已认定 / 认定。匹配失败返回 None。"""
        title = (title or '').strip()
        if not title:
            return None
        body = self._training_page_text()
        idx = body.find(title)
        if idx < 0:
            self._log_warning('专题页未找到课程标题，无法读学时进度: %s', title)
            return None
        window = body[idx:idx + COURSE_CREDIT_SCAN_CHARS]
        credit_m = COURSE_CREDIT_PATTERN.search(window)
        if not credit_m:
            self._log_warning('课程卡片未解析到认定学时: %s', title)
            return None
        try:
            accredited = float(credit_m.group(1))
            required = float(credit_m.group(2))
        except (TypeError, ValueError):
            return None

        learned = accredited
        learned_m = COURSE_LEARNED_PATTERN.search(window)
        if learned_m:
            try:
                learned = float(learned_m.group(1))
            except (TypeError, ValueError):
                pass

        return {
            'learned': learned,
            'accredited': accredited,
            'required': required,
        }

    def _read_course_credit(self, title: str) -> tuple[float, float] | None:
        """兼容旧调用：返回 (已认定, 认定)。"""
        progress = self._read_course_progress(title)
        if not progress:
            return None
        return progress['accredited'], progress['required']

    def _is_course_credit_done(self, title: str) -> bool:
        """实际学时已超过认定，或已认定已满 → 可换下一章。"""
        progress = self._read_course_progress(title)
        if not progress:
            return False
        learned = progress['learned']
        accredited = progress['accredited']
        required = progress['required']
        # 实际学时通常略高于认定：已学习 > 认定 即可换课
        by_learned = learned > required + COURSE_CREDIT_EPS
        by_accredited = accredited + COURSE_CREDIT_EPS >= required
        done = by_learned or by_accredited
        self._log_info(
            '课程进度检测 %s: 已学习=%s 已认定=%s / 认定=%s '
            'by_learned=%s by_accredited=%s done=%s',
            title, learned, accredited, required, by_learned, by_accredited, done,
        )
        return done

    def _session_alive(self) -> bool:
        """浏览器会话是否仍可用（手动停止会 quit driver）。"""
        if self._stopped or not self.is_running:
            return False
        if not self.driver:
            return False
        try:
            _ = self.driver.window_handles
            return True
        except Exception:
            return False

    def _switch_to_list_window(self):
        if not self._session_alive():
            return
        try:
            handles = self.driver.window_handles
            if self.list_window and self.list_window in handles:
                self.driver.switch_to.window(self.list_window)
                return
            if handles:
                self.driver.switch_to.window(handles[0])
                self.list_window = self.driver.current_window_handle
        except Exception:
            self._log_warning('切换专题页窗口失败（会话可能已关闭）')

    def _close_play_window(self):
        if not self.driver:
            self.play_window = None
            return
        try:
            if not self._session_alive():
                return
            handles = self.driver.window_handles
            if self.play_window and self.play_window in handles:
                self.driver.switch_to.window(self.play_window)
                self.driver.close()
        except Exception:
            if not self._stopped:
                self._log_warning('关闭播放页失败')
        finally:
            self.play_window = None
            try:
                self._switch_to_list_window()
            except Exception:
                pass

    def _play_one_unfinished_section(self, course: dict) -> bool:
        """打开一门课，播放一节未完成视频；成功播完一节返回 True。"""
        if not self._session_alive():
            return False
        self._switch_to_list_window()
        if not self._session_alive():
            return False
        before = set(self.driver.window_handles)
        self.driver.execute_script('window.open(arguments[0]);', course['url'])
        time.sleep(2)
        if not self._session_alive():
            return False
        new_handles = [h for h in self.driver.window_handles if h not in before]
        if not new_handles:
            self._log_warning('未能打开课程新标签: %s', course['title'])
            return False
        self.play_window = new_handles[-1]
        self.driver.switch_to.window(self.play_window)
        self._log_info('已打开课程页: %s url=%s', course['title'], self.driver.current_url)
        time.sleep(5)

        try:
            if not self._session_alive():
                return False
            self._expand_course_catalog()
            clicked = self._click_first_unfinished_resource()
            if not clicked:
                self._log_info('课程无未完成小节: %s', course['title'])
                self._close_play_window()
                return False

            self._start_video_playback()
            done = self._wait_video_finished()
            if not done:
                if self._stopped:
                    self._log_info('任务已停止，结束本节: %s', course['title'])
                else:
                    self._log_warning('等待「再学一遍」超时/中断: %s', course['title'])
                self._close_play_window()
                return False

            self._log_info('本节播放完成: %s', course['title'])
            self._close_play_window()
            return True
        except Exception:
            if self._stopped or not self.driver:
                self._log_info('任务已停止或浏览器已关闭，忽略播放异常: %s', course['title'])
                self.play_window = None
                return False
            self._log_exception('播放课程异常: %s', course['title'])
            self._close_play_window()
            return False

    def _expand_course_catalog(self):
        from selenium.webdriver.common.by import By

        try:
            headers = self.driver.find_elements(By.CLASS_NAME, 'fish-collapse-header')
            for header in headers:
                try:
                    parent = header.find_element(By.XPATH, '..')
                    children = parent.find_elements(By.XPATH, './div')
                    if len(children) == 1 and header.is_displayed():
                        header.click()
                        time.sleep(0.3)
                except Exception:
                    continue
            self._log_info('目录折叠项已展开 count=%s', len(headers))
        except Exception:
            self._log_warning('展开目录失败（可能已展开）')

    def _click_first_unfinished_resource(self) -> bool:
        from selenium.webdriver.common.by import By

        items = self.driver.find_elements(
            By.CSS_SELECTOR,
            'div.resource-item.resource-item-train, div[class*="resource-item-train"]',
        )
        self._log_info('资源条目数=%s', len(items))
        for item in items:
            try:
                status = ''
                icons = item.find_elements(By.CSS_SELECTOR, '.status-icon i, i[title]')
                for icon in icons:
                    status = (icon.get_attribute('title') or '').strip()
                    if status:
                        break
                text = (item.text or '').strip().replace('\n', ' ')[:80]
                self._log_info('资源 status=%s text=%s', status, text)
                if status in ('未开始', '进行中'):
                    item.click()
                    time.sleep(2)
                    return True
            except Exception:
                continue
        return False

    def _start_video_playback(self):
        from selenium.common import TimeoutException
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.wait import WebDriverWait

        wait = WebDriverWait(self.driver, 10)
        wait_short = WebDriverWait(self.driver, 3)

        # 大播放按钮
        try:
            btn = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'vjs-big-play-button')))
            btn.click()
            self._log_info('已点击大播放按钮')
        except TimeoutException:
            self._log_warning('未找到大播放按钮，可能已在播放')

        # 我知道了
        try:
            know = wait_short.until(
                EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='我知道了'] or normalize-space()='我知道了']"))
            )
            know.click()
            self._log_info('已点击「我知道了」')
        except TimeoutException:
            pass

        # 控制条播放
        try:
            bar = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'vjs-control-bar')))
            play_btns = bar.find_elements(By.CSS_SELECTOR, 'button.vjs-play-control, button')
            if play_btns:
                play_btns[0].click()
                self._log_info('已点击控制条播放')
        except TimeoutException:
            self._log_warning('未找到控制条')

        self._set_playback_rate_2x()

    def _set_playback_rate_2x(self):
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.wait import WebDriverWait

        try:
            # 参考脚本：连续点击 Playback Rate 切到 2x
            rate_btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@title='Playback Rate']"))
            )
            for _ in range(3):
                rate_btn.click()
                time.sleep(0.2)
            self._log_info('已尝试设置 2 倍速')
            return
        except Exception:
            pass

        # 兜底：JS 直接设 playbackRate
        try:
            ok = self.driver.execute_script(
                """
                const v = document.querySelector('video');
                if (v) { v.playbackRate = 2; v.play(); return true; }
                return false;
                """
            )
            if ok:
                self._log_info('已通过 JS 设置 video.playbackRate=2')
        except Exception:
            self._log_warning('设置倍速失败')

    def _wait_video_finished(self) -> bool:
        """轮询等待「再学一遍」出现。"""
        from selenium.webdriver.common.by import By

        elapsed = 0
        while elapsed < VIDEO_MAX_WAIT_SECONDS and self.is_running and not self._stopped:
            try:
                els = self.driver.find_elements(
                    By.XPATH,
                    "//div[normalize-space()='再学一遍'] | //span[normalize-space()='再学一遍'] | //*[normalize-space()='再学一遍']",
                )
                if any(el.is_displayed() for el in els):
                    self._log_info('检测到「再学一遍」')
                    return True
            except Exception:
                pass

            # 暂停则尝试继续播
            try:
                self.driver.execute_script(
                    """
                    const v = document.querySelector('video');
                    if (v && v.paused) v.play();
                    """
                )
            except Exception:
                pass

            time.sleep(VIDEO_POLL_SECONDS)
            elapsed += VIDEO_POLL_SECONDS
            if elapsed % 300 == 0:
                self._log_info('播放中… 已等待 %s 秒', elapsed)

        return False

    # ----------------------------------------------------------- slider
    def _solve_tencent_slider(self, max_retry: int = SLIDER_MAX_RETRY) -> bool:
        from selenium.common import TimeoutException
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.wait import WebDriverWait

        for attempt in range(1, max_retry + 1):
            self._log_info('滑块尝试 %s/%s', attempt, max_retry)
            try:
                self.driver.switch_to.default_content()
                # 若滑块未出现，尝试再次点击登录唤起
                if not self.driver.find_elements(By.ID, 'tcaptcha_iframe_dy'):
                    try:
                        btn = self.driver.find_element(By.ID, 'loginBtn')
                        text = (btn.text or '').strip()
                        if '登录中' not in text:
                            btn.click()
                        else:
                            # 卡在登录中则整页重进
                            self.driver.get(ZXZH_LOGIN_URL)
                            time.sleep(2)
                            self._refill_login_form()
                            self.driver.find_element(By.ID, 'loginBtn').click()
                    except Exception:
                        pass

                WebDriverWait(self.driver, 12).until(
                    EC.presence_of_element_located((By.ID, 'tcaptcha_iframe_dy'))
                )
                self.driver.switch_to.frame(self.driver.find_element(By.ID, 'tcaptcha_iframe_dy'))
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, 'slideBg'))
                )
                self._wait_slider_ready()

                distance = self._calc_slider_distance()
                if distance <= 0:
                    self._log_warning('缺口距离无效 distance=%s，刷新重试', distance)
                    self._refresh_slider()
                    continue

                self._drag_slider_cdp(distance)
                time.sleep(2.0)

                self.driver.switch_to.default_content()
                if self._slider_passed():
                    self._log_info('滑块通过 url=%s', self.driver.current_url)
                    return True

                self._log_warning('滑块未通过，刷新重试')
                try:
                    if self.driver.find_elements(By.ID, 'tcaptcha_iframe_dy'):
                        self.driver.switch_to.frame(self.driver.find_element(By.ID, 'tcaptcha_iframe_dy'))
                        self._refresh_slider()
                except Exception:
                    self.driver.switch_to.default_content()
            except TimeoutException:
                self._log_warning('等待滑块超时，准备重开登录页')
                self.driver.switch_to.default_content()
                try:
                    self.driver.get(ZXZH_LOGIN_URL)
                    time.sleep(2)
                    self._refill_login_form()
                    self.driver.find_element(By.ID, 'loginBtn').click()
                    time.sleep(1)
                except Exception:
                    pass
            except Exception:
                self._log_exception('滑块处理异常')
                try:
                    self.driver.switch_to.default_content()
                except Exception:
                    pass
        return False

    def _refill_login_form(self):
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.wait import WebDriverWait

        wait = WebDriverWait(self.driver, 10)
        for _ in range(20):
            if self.driver.execute_script('return window.currentCaptchaType || "";'):
                break
            time.sleep(0.3)
        user = wait.until(EC.presence_of_element_located((By.ID, 'username')))
        user.clear()
        user.send_keys(self.task.username)
        pwd = self.driver.find_element(By.ID, 'tmpPassword')
        pwd.clear()
        pwd.send_keys(self.task.password)
        agree = self.driver.find_element(By.ID, 'agreementCheckbox')
        if not agree.is_selected():
            self.driver.execute_script('arguments[0].click();', agree)

    def _slider_passed(self) -> bool:
        """滑块成功：必须拿到 identifyCode，或已确认登录态。"""
        try:
            code = self.driver.execute_script(
                "return (document.querySelector(\"input[name='captchaCode']\")||{}).value||'';"
            )
            if code:
                self._log_info('检测到 captchaCode 已写入 len=%s', len(code))
                return True
        except Exception:
            pass

        # 仅当明确已登录才放行（避免 URL 抖动误判）
        return self._is_logged_in()

    def _wait_slider_ready(self):
        for _ in range(20):
            if self._find_puzzle_piece() is not None and self._find_drag_button() is not None:
                return
            time.sleep(0.3)

    def _refresh_slider(self):
        from selenium.webdriver.common.by import By

        try:
            btn = self.driver.find_element(By.CSS_SELECTOR, '#e_reload, #reload')
            self.driver.execute_script('arguments[0].click();', btn)
            time.sleep(1.5)
        except Exception:
            self._log_warning('刷新滑块失败')

    def _calc_slider_distance(self) -> int:
        """在 iframe 内计算拖拽距离（显示像素）。"""
        from selenium.webdriver.common.by import By

        os.makedirs('png', exist_ok=True)
        prefix = f'zxzh_{self.task.username}_{int(time.time())}'
        bg_path = os.path.join('png', f'{prefix}_bg.png')
        piece_path = os.path.join('png', f'{prefix}_piece.png')

        bg_el = self.driver.find_element(By.ID, 'slideBg')
        piece_el = self._find_puzzle_piece()
        if piece_el is None:
            self._log_warning('未找到拼图块元素')
            return 0

        # 隐藏前景，避免截背景时叠上拼图块
        self.driver.execute_script(
            "document.querySelectorAll('.tc-fg-item,.tc-watermark-area')"
            ".forEach(e => e.style.visibility = 'hidden');"
        )
        time.sleep(0.1)
        bg_el.screenshot(bg_path)
        self.driver.execute_script(
            "document.querySelectorAll('.tc-fg-item,.tc-watermark-area')"
            ".forEach(e => e.style.visibility = 'visible');"
        )
        piece_el.screenshot(piece_path)

        with open(bg_path, 'rb') as f:
            bg_bytes = f.read()
        with open(piece_path, 'rb') as f:
            piece_bytes = f.read()

        try:
            left_css = (piece_el.value_of_css_property('left') or '0').replace('px', '')
            relative_left = float(left_css or 0)
        except Exception:
            relative_left = 20.0

        ocr_offset, ocr_conf = self._distance_by_ddddocr_with_conf(piece_bytes, bg_bytes)
        cv_offset = self._distance_by_opencv_template(piece_path, bg_path)
        contour_offset = self._distance_by_opencv_gap_file(bg_path)

        # 实测：opencv 暗色缺口轮廓对腾讯滑块更稳；高置信 ddddocr 次之
        if contour_offset > relative_left + 30:
            offset = contour_offset
            method = 'opencv-contour'
        elif ocr_conf >= 0.72 and ocr_offset > relative_left + 30:
            offset = ocr_offset
            method = f'ddddocr(conf={ocr_conf:.2f})'
        elif cv_offset > relative_left + 30:
            offset = cv_offset
            method = 'opencv-template'
        elif ocr_offset > 0:
            offset = ocr_offset
            method = f'ddddocr-fallback(conf={ocr_conf:.2f})'
        else:
            offset = max(contour_offset, cv_offset, ocr_offset)
            method = 'best-effort'

        distance = max(int(offset - relative_left), 1)
        self._log_info(
            '滑块距离 method=%s offset=%s left=%s distance=%s ocr=%s/%s cv=%s contour=%s',
            method, offset, relative_left, distance,
            ocr_offset, f'{ocr_conf:.2f}', cv_offset, contour_offset,
        )
        return distance

    def _find_puzzle_piece(self):
        from selenium.webdriver.common.by import By

        for el in self.driver.find_elements(By.CSS_SELECTOR, '.tc-fg-item'):
            cls = el.get_attribute('class') or ''
            if 'tc-slider-normal' in cls:
                continue
            size = el.size or {}
            w, h = size.get('width', 0), size.get('height', 0)
            if 30 <= w <= 90 and 30 <= h <= 90:
                return el
        return None

    def _find_drag_button(self):
        from selenium.webdriver.common.by import By

        for el in self.driver.find_elements(By.CSS_SELECTOR, '.tc-slider-normal'):
            if el.is_displayed():
                return el
        return None

    def _drag_slider_cdp(self, distance: int):
        """通过 CDP 派发真实鼠标事件拖动（跨域 iframe 下 ActionChains 无效）。"""
        from selenium.webdriver.common.by import By

        self.driver.switch_to.default_content()
        iframe = self.driver.find_element(By.ID, 'tcaptcha_iframe_dy')
        iframe_box = self.driver.execute_script(
            'const r = arguments[0].getBoundingClientRect(); return {x: r.x, y: r.y};',
            iframe,
        )
        self.driver.switch_to.frame(iframe)
        btn = self._find_drag_button()
        if btn is None:
            raise RuntimeError('未找到滑块拖动按钮')
        btn_box = self.driver.execute_script(
            'const r = arguments[0].getBoundingClientRect();'
            'return {x: r.x, y: r.y, w: r.width, h: r.height};',
            btn,
        )
        start_x = iframe_box['x'] + btn_box['x'] + btn_box['w'] / 2
        start_y = iframe_box['y'] + btn_box['y'] + btn_box['h'] / 2
        tracks = self._build_tracks(distance)
        self._log_info(
            'CDP 拖拽 start=(%.1f,%.1f) distance=%s steps=%s',
            start_x, start_y, distance, len(tracks),
        )

        self.driver.switch_to.default_content()
        self.driver.execute_cdp_cmd('Input.dispatchMouseEvent', {
            'type': 'mouseMoved', 'x': start_x, 'y': start_y,
            'buttons': 0, 'pointerType': 'mouse',
        })
        time.sleep(0.05)
        self.driver.execute_cdp_cmd('Input.dispatchMouseEvent', {
            'type': 'mousePressed', 'x': start_x, 'y': start_y,
            'button': 'left', 'buttons': 1, 'clickCount': 1, 'pointerType': 'mouse',
        })
        time.sleep(0.15)

        cur_x = start_x
        cur_y = start_y
        for dx in tracks:
            cur_x += dx
            cur_y = start_y + random.uniform(-1, 1)
            self.driver.execute_cdp_cmd('Input.dispatchMouseEvent', {
                'type': 'mouseMoved', 'x': cur_x, 'y': cur_y,
                'button': 'left', 'buttons': 1, 'pointerType': 'mouse',
            })
            time.sleep(random.uniform(0.008, 0.02))

        time.sleep(0.12)
        self.driver.execute_cdp_cmd('Input.dispatchMouseEvent', {
            'type': 'mouseReleased', 'x': cur_x, 'y': cur_y,
            'button': 'left', 'buttons': 0, 'clickCount': 1, 'pointerType': 'mouse',
        })

    @staticmethod
    def _build_tracks(distance: int) -> list[int]:
        """拟人轨迹：先加速后减速。"""
        tracks: list[int] = []
        current = 0
        mid = distance * 0.72
        t = 0.2
        v = 0.0
        while current < distance:
            a = random.uniform(2.2, 3.2) if current < mid else -random.uniform(2.5, 3.8)
            v0 = v
            v = v0 + a * t
            move = max(int(v0 * t + 0.5 * a * t * t), 1)
            if current + move > distance:
                move = distance - current
            tracks.append(move)
            current += move
        return tracks

    def _distance_by_ddddocr(self, piece_bytes: bytes, bg_bytes: bytes) -> int:
        offset, _ = self._distance_by_ddddocr_with_conf(piece_bytes, bg_bytes)
        return offset

    def _distance_by_ddddocr_with_conf(self, piece_bytes: bytes, bg_bytes: bytes) -> tuple[int, float]:
        try:
            import ddddocr

            det = ddddocr.DdddOcr(det=False, ocr=False, show_ad=False)
            res = det.slide_match(piece_bytes, bg_bytes, simple_target=True)
            target = res.get('target') if isinstance(res, dict) else None
            conf = float(res.get('confidence') or 0) if isinstance(res, dict) else 0.0
            if isinstance(target, (list, tuple)) and target:
                return int(target[0]), conf
            if isinstance(res, dict) and 'target_x' in res:
                return int(res['target_x']), conf
            self._log_warning('ddddocr 返回异常: %s', res)
        except ImportError:
            self._log_warning('未安装 ddddocr')
        except Exception:
            self._log_exception('ddddocr 缺口识别失败')
        return 0, 0.0

    def _distance_by_opencv(self, piece_path: str, bg_path: str) -> int:
        return self._distance_by_opencv_template(piece_path, bg_path)

    def _distance_by_opencv_template(self, piece_path: str, bg_path: str) -> int:
        try:
            import cv2

            bg = cv2.imread(bg_path)
            piece = cv2.imread(piece_path)
            if bg is None or piece is None:
                return 0
            bg_gray = cv2.cvtColor(bg, cv2.COLOR_BGR2GRAY)
            piece_gray = cv2.cvtColor(piece, cv2.COLOR_BGR2GRAY)
            bg_edge = cv2.Canny(bg_gray, 100, 200)
            piece_edge = cv2.Canny(piece_gray, 100, 200)
            res = cv2.matchTemplate(bg_edge, piece_edge, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)
            self._log_info('OpenCV 模板匹配 max_val=%.3f loc=%s', max_val, max_loc)
            if max_val < 0.28:
                return 0
            return int(max_loc[0])
        except ImportError:
            self._log_warning('未安装 opencv-python')
        except Exception:
            self._log_exception('OpenCV 模板匹配失败')
        return 0

    def _distance_by_opencv_gap_file(self, bg_path: str) -> int:
        try:
            import cv2

            bg_gray = cv2.imread(bg_path, cv2.IMREAD_GRAYSCALE)
            if bg_gray is None:
                return 0
            return self._distance_by_opencv_gap(bg_gray)
        except Exception:
            self._log_exception('读取背景图失败')
            return 0

    def _distance_by_opencv_gap(self, bg_gray) -> int:
        try:
            import cv2

            blur = cv2.GaussianBlur(bg_gray, (5, 5), 0)
            thr = cv2.adaptiveThreshold(
                blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 21, 8
            )
            contours, _ = cv2.findContours(thr, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            best = None
            for cnt in contours:
                x, y, w, h = cv2.boundingRect(cnt)
                if 35 <= w <= 75 and 35 <= h <= 75 and x > 40:
                    area = cv2.contourArea(cnt)
                    if best is None or area > best[0]:
                        best = (area, x)
            if best:
                self._log_info('OpenCV 轮廓缺口 x=%s area=%s', best[1], best[0])
                return int(best[1])
            return 0
        except Exception:
            self._log_exception('OpenCV 缺口轮廓识别失败')
            return 0

    @staticmethod
    def _css_bg_url(element) -> str:
        try:
            style = element.get_attribute('style') or ''
            m = re.search(r'background-image:\s*url\(["\']?(.*?)["\']?\)', style)
            if m:
                return m.group(1).replace('&amp;', '&')
            bg = element.value_of_css_property('background-image') or ''
            m2 = re.search(r'url\(["\']?(.*?)["\']?\)', bg)
            return (m2.group(1) if m2 else '').replace('&amp;', '&')
        except Exception:
            return ''

    @staticmethod
    def _download(url: str, path: str):
        if not url or not url.startswith('http'):
            return
        with urlopen(url, timeout=15) as resp:
            data = resp.read()
        with open(path, 'wb') as f:
            f.write(data)
