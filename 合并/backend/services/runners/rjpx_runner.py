"""
人教教师服务培训平台（RJPX）任务执行器

网站编码：RJPX
站点：https://wp.pep.com.cn/

登录：密码登录（用户名/手机号 + 密码 + 图形验证码 captcha.php）
学习：进入培训后打开「学习数据」，播放其中全部未完成的必修/必学内容。
回放播放页多为展视互动 Gensee（bjpep.gensee.com/webcast/site/vod/）。

任务 class_id 对应培训项目 pxid（如 2026 秋季新教材培训为 196）。
为空时默认 196。
"""
from __future__ import annotations

import re
import threading
import time
from urllib.parse import unquote

from services.runners.selenium_runner import SeleniumTaskRunner
from services.task_runner import register_runner, update_task_fields

RJPX_BASE = 'https://wp.pep.com.cn/web/index.php'
DEFAULT_PXID = '196'
PERCENT_PATTERN = re.compile(r'(\d+(?:\.\d+)?)\s*%')
PXID_IN_URL = re.compile(r'(?:login/index|px/index|pxcom/index)/(\d+)', re.I)
DONE_MARKERS = ('已完成', '已学完', '已学', '达标')
REQUIRED_MARKERS = ('必修', '必学')
ELECTIVE_MARKERS = ('选修',)
PLAY_BUTTON_TEXTS = ('观看回放', '进入学习', '开始学习', '继续学习', '进入培训', '学习')
NAV_STUDY_DATA = '学习数据'
NAV_COURSE = '培训课程'
SKIP_TAB_TEXTS = (
    '学习数据', '我的证书', '培训课程', '报名信息', '个人中心', '退出',
    '首页', '资讯', '帮助', '通知', '公告', '证书',
)


def parse_pxid(raw) -> str:
    """从任务 class_id 解析培训项目 pxid。"""
    text = (raw or '').strip()
    if not text:
        return DEFAULT_PXID
    if text.startswith('http'):
        decoded = unquote(text)
        match = PXID_IN_URL.search(decoded)
        if match:
            return match.group(1)
        return DEFAULT_PXID
    if text.isdigit():
        return text
    match = PXID_IN_URL.search(text)
    if match:
        return match.group(1)
    raise RuntimeError('RJPX class_id 须为培训项目 ID（pxid），例如 196')


@register_runner('RJPX')
class RjpxTaskRunner(SeleniumTaskRunner):
    """人教教师服务培训平台：密码登录 + 学习数据中全部必修回放。"""

    def __init__(self, task, website):
        super().__init__(task, website)
        self.pxid = DEFAULT_PXID
        self.list_window = None
        self.play_window = None
        self._play_done_event = threading.Event()
        self._played_titles: set[str] = set()

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
            self._open_training_home()
            self._learn_required_loop()
            self._sync_task_status()
        except Exception:
            self._log_exception('任务 id=%s 执行失败', self.task.id)
            self._handle_run_exception()
            raise
        finally:
            self._finalize_run()

    def _prepare_config(self):
        self.pxid = parse_pxid(self.task.class_id)
        self._log_info('培训项目 pxid=%s', self.pxid)

    # ------------------------------------------------------------------ urls
    def _login_url(self) -> str:
        return f'{RJPX_BASE}?/login/index/{self.pxid}/1'

    def _home_url(self) -> str:
        if self.pxid == '0':
            return f'{RJPX_BASE}?/pxcom/index/0'
        return f'{RJPX_BASE}?/px/index/{self.pxid}'

    # ------------------------------------------------------------------ login
    def _is_logged_in(self) -> bool:
        from selenium.webdriver.common.by import By

        try:
            url = (self.driver.current_url or '').lower()
            if '/login/' in url:
                return False
            body = ''
            try:
                body = (self.driver.find_element(By.TAG_NAME, 'body').text or '')
            except Exception:
                pass
            if '请您先登录' in body:
                return False
            if '/px/' in url or '/pxcom/' in url:
                logout = self.driver.find_elements(
                    By.XPATH,
                    '//a[contains(normalize-space(),"退出") or contains(normalize-space(),"注销")]',
                )
                if logout:
                    return True
                if any(k in body for k in ('学习数据', '培训课程', '个人空间', '我的证书', '进入培训')):
                    return True
            cookies = {c.get('name') for c in (self.driver.get_cookies() or [])}
            if cookies & {'PEPUser', 'pepuser', 'uid', 'userid', 'PHPSESSID'} and '/login/' not in url:
                if '请您先登录' not in body and '用户名/手机号' not in body:
                    if '/px/' in url or '/pxcom/' in url:
                        return True
        except Exception:
            self._log_exception('检测登录态失败')
        return False

    def _auto_login(self):
        from selenium.common import ElementNotInteractableException, TimeoutException
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.wait import WebDriverWait

        self._driver_get(self._login_url(), label='登录页')
        time.sleep(2)
        self._dismiss_popups()

        if self._is_logged_in():
            self._log_info('检测到已有登录态，跳过表单')
            return

        try:
            self._switch_password_login_tab()
            username = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'regName'))
            )
            username.clear()
            username.send_keys(self.task.username)

            password = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'passwd'))
            )
            password.clear()
            password.send_keys(self.task.password)

            self._check_agree_box()

            captcha = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'validcode2'))
            )
            captcha.clear()
            captcha.send_keys(self._recognize_image_captcha())

            self._click_password_login_button()
            time.sleep(3)
            self._dismiss_popups()
            err = self._read_login_error()
            if err:
                self._log_warning('登录页提示: %s', err)
            self._log_info('登录表单已提交 user=%s', self.task.username)
        except (TimeoutException, ElementNotInteractableException):
            self._log_exception('登录失败')
            raise

    def _switch_password_login_tab(self):
        from selenium.webdriver.common.by import By

        for xpath in (
            '//li[contains(@id,"login1")]',
            '//li[.//h5[contains(normalize-space(),"密码登录")] or contains(normalize-space(),"密码登录")]',
            '//*[contains(normalize-space(),"密码登录")]',
        ):
            try:
                tabs = self.driver.find_elements(By.XPATH, xpath)
                for tab in tabs:
                    if tab.is_displayed():
                        tab.click()
                        time.sleep(0.4)
                        return
            except Exception:
                continue

    def _check_agree_box(self):
        from selenium.webdriver.common.by import By

        try:
            box = self.driver.find_element(By.ID, 'agree1')
            if not box.is_selected():
                self.driver.execute_script('arguments[0].click();', box)
                time.sleep(0.2)
        except Exception:
            self._log_warning('勾选用户协议失败，继续尝试登录')

    def _click_password_login_button(self):
        from selenium.webdriver.common.by import By

        # 密码表单内的登录图，避免点到短信登录按钮
        for selector in (
            'form[name="loginForm"] img#imgLogin',
            'form[name="loginForm"] img[src*="btn_login"]',
            '#imgLogin',
        ):
            try:
                btns = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for btn in btns:
                    if btn.is_displayed():
                        btn.click()
                        return
            except Exception:
                continue
        self.driver.execute_script('if (typeof doLogin === "function") { doLogin(); }')

    def _recognize_image_captcha(self) -> str:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.wait import WebDriverWait

        try:
            img = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'imgValidCode'))
            )
            code = self._recognize_captcha_screenshot(img, f'rjpx_{self.task.username}.png')
            self._log_info('图形验证码识别结果 len=%s', len(code or ''))
            return code
        except Exception:
            self._log_exception('验证码识别失败')
            return ''

    def _read_login_error(self) -> str:
        from selenium.webdriver.common.by import By

        for eid in ('errmsg1', 'msgValidCode', 'msgRegName', 'msgPwd', 'msgAgree1'):
            try:
                el = self.driver.find_element(By.ID, eid)
                text = (el.text or '').strip().replace('\xa0', '').strip()
                if text and text != '&nbsp;':
                    return text
            except Exception:
                continue
        return ''

    def _sync_user_profile(self):
        from selenium.webdriver.common.by import By

        try:
            if not self._is_logged_in():
                return
            name = ''
            for xpath in (
                '//*[contains(@class,"user") or contains(@class,"name")][contains(.,"老师") or contains(.,"姓名")]',
                '//span[contains(@class,"name") or contains(@class,"user")]',
            ):
                els = self.driver.find_elements(By.XPATH, xpath)
                for el in els:
                    text = (el.text or '').strip()
                    if not text or len(text) > 20:
                        continue
                    name = text.replace('老师', '').replace('欢迎', '').strip(' ，,:：')
                    if 1 < len(name) <= 12:
                        break
                if name:
                    break
            if name:
                update_task_fields(self.task, nick_name=name)
                self._log_info('已登录 %s', name)
        except Exception:
            self._log_exception('同步学员资料失败')

    # ------------------------------------------------------------- navigation
    def _open_training_home(self):
        url = self._home_url()
        self._log_info('打开培训首页 %s', url)
        self._driver_get(url, label='培训首页')
        time.sleep(2)
        self._dismiss_popups()
        if not self._is_logged_in():
            raise RuntimeError('打开培训首页时未登录，被重定向到登录页')
        self._enter_training_if_needed()
        self.list_window = self.driver.current_window_handle
        self._log_info('培训首页已打开 list_window=%s url=%s', self.list_window, self.driver.current_url)

    def _enter_training_if_needed(self):
        from selenium.webdriver.common.by import By

        if self._has_left_nav(NAV_STUDY_DATA):
            return
        for xpath in (
            '//a[contains(normalize-space(),"进入培训")]',
            '//button[contains(normalize-space(),"进入培训")]',
            '//a[contains(normalize-space(),"进入学习")]',
        ):
            try:
                btns = self.driver.find_elements(By.XPATH, xpath)
                for btn in btns:
                    if btn.is_displayed():
                        btn.click()
                        time.sleep(2)
                        self._dismiss_popups()
                        if self._has_left_nav(NAV_STUDY_DATA):
                            return
            except Exception:
                continue

    def _has_left_nav(self, text: str) -> bool:
        from selenium.webdriver.common.by import By

        try:
            els = self.driver.find_elements(
                By.XPATH, f'//a[contains(normalize-space(),"{text}")] | //*[self::li or self::span][contains(normalize-space(),"{text}")]'
            )
            return any(el.is_displayed() for el in els)
        except Exception:
            return False

    def _click_left_nav(self, text: str) -> bool:
        from selenium.webdriver.common.by import By

        for xpath in (
            f'//a[contains(normalize-space(),"{text}")]',
            f'//li[contains(normalize-space(),"{text}")]',
            f'//*[contains(normalize-space(),"{text}") and (self::a or self::span or self::div)]',
        ):
            try:
                els = self.driver.find_elements(By.XPATH, xpath)
                for el in els:
                    if not el.is_displayed():
                        continue
                    label = (el.text or '').strip()
                    if text not in label:
                        continue
                    self.driver.execute_script('arguments[0].click();', el)
                    time.sleep(2)
                    self._dismiss_popups()
                    self._log_info('已点击导航「%s」 url=%s', text, self.driver.current_url)
                    return True
            except Exception:
                continue
        return False

    def _open_study_data(self):
        self._ensure_on_list_window()
        if not self._click_left_nav(NAV_STUDY_DATA):
            # 部分项目用独立路由
            self._driver_get(
                f'{RJPX_BASE}?/px/xxsj/{self.pxid}',
                label='学习数据',
            )
            time.sleep(2)
            self._dismiss_popups()
        if '请您先登录' in (self.driver.page_source or ''):
            raise RuntimeError('打开学习数据时登录已失效')

    # ---------------------------------------------------------- required list
    def _learn_required_loop(self):
        idle_rounds = 0
        while self.is_running and not self.is_complete and not self._stopped:
            self._ensure_on_list_window()
            self._open_study_data()
            required = self._collect_required_lessons()
            unfinished = [item for item in required if not item.get('done')]
            done_count = len(required) - len(unfinished)
            if required:
                self._update_task_progress(f'必修 {done_count}/{len(required)}')
            self._log_info(
                '学习数据必修合计=%s 未完成=%s',
                len(required), len(unfinished),
            )

            if required and not unfinished:
                self._log_info('学习数据中全部必修已完成')
                self._mark_course_complete()
                return

            target = self._pick_next_unfinished(required)
            played = False
            if target:
                played = self._play_required_item(target)
            if not played:
                played = self._play_from_course_menu(unfinished)

            if not played:
                idle_rounds += 1
                self._log_warning('本轮未找到可播放的必修回放 idle=%s', idle_rounds)
                if idle_rounds >= 3:
                    if required and not unfinished:
                        self._mark_course_complete()
                        return
                    raise RuntimeError('未能打开学习数据中的必修回放，请检查账号是否已报名或页面结构是否变化')
                self._try_switch_next_subject()
                time.sleep(2)
                continue

            idle_rounds = 0
            self._close_play_window_and_return()
            time.sleep(2)

        if self.is_running and not self._stopped and not self.is_complete:
            self._log_warning('学习循环结束但未标记完成')

    def _collect_required_lessons(self) -> list[dict]:
        """从当前页（含学科页签）收集必修条目。"""
        items: list[dict] = []
        seen: set[str] = set()

        def _merge(batch):
            for item in batch or []:
                title = (item.get('title') or '').strip()
                if not title or title in seen:
                    continue
                seen.add(title)
                items.append(item)

        _merge(self._extract_required_from_page())
        for tab in self._subject_tabs():
            if self._stopped:
                break
            try:
                self.driver.execute_script('arguments[0].click();', tab)
                time.sleep(1.2)
                self._dismiss_popups()
                _merge(self._extract_required_from_page())
            except Exception:
                continue
        return items

    def _extract_required_from_page(self) -> list[dict]:
        try:
            result = self.driver.execute_script(
                """
                const doneRe = /已完成|已学完|已学\\b|达标|100\\s*%/;
                const requiredRe = /必修|必学/;
                const electiveRe = /选修/;
                const playRe = /观看回放|进入学习|开始学习|继续学习|进入培训/;
                const items = [];
                const seen = new Set();
                const push = (title, meta, done) => {
                    const t = (title || '').replace(/\\s+/g, ' ').trim();
                    if (!t || t.length < 2 || t.length > 80 || seen.has(t)) return;
                    if (!requiredRe.test(meta) && !requiredRe.test(t)) return;
                    if (electiveRe.test(t) && !requiredRe.test(t)) return;
                    seen.add(t);
                    items.push({title: t, done: !!done, meta: (meta || '').slice(0, 160)});
                };
                document.querySelectorAll('tr').forEach(row => {
                    if (row.querySelector('th')) return;
                    const text = (row.innerText || '').replace(/\\s+/g, ' ').trim();
                    if (!text || !requiredRe.test(text) || electiveRe.test(text)) return;
                    const cells = [...row.querySelectorAll('td')].map(td => (td.innerText || '').trim()).filter(Boolean);
                    let title = cells.find(c => c && !requiredRe.test(c) && !doneRe.test(c) && c.length > 1) || cells[0] || '';
                    title = title.replace(/必修|必学/g, '').trim() || cells[0];
                    push(title, text, doneRe.test(text));
                });
                document.querySelectorAll('li, .item, .course, [class*="kc"], [class*="course"]').forEach(el => {
                    const text = (el.innerText || '').replace(/\\s+/g, ' ').trim();
                    if (!text || text.length > 80 || !requiredRe.test(text)) return;
                    if (el.querySelector('li, tr')) return;
                    const title = text.replace(/必修|必学|选修/g, ' ').replace(/\\s+/g, ' ').trim();
                    push(title, text, doneRe.test(text));
                });
                return items;
                """
            )
            if isinstance(result, list):
                cleaned = []
                for item in result:
                    if not isinstance(item, dict):
                        continue
                    title = (item.get('title') or '').strip()
                    if not title:
                        continue
                    items_done = bool(item.get('done'))
                    meta = item.get('meta') or ''
                    if any(m in title for m in ELECTIVE_MARKERS) and not any(
                        m in title for m in REQUIRED_MARKERS
                    ):
                        continue
                    cleaned.append({'title': title, 'done': items_done, 'meta': meta})
                return cleaned
        except Exception:
            self._log_exception('解析学习数据失败')
        return []

    def _subject_tabs(self):
        from selenium.webdriver.common.by import By

        tabs = []
        xpaths = (
            '//div[contains(@class,"tab") or contains(@class,"xk") or contains(@class,"subject")]//a',
            '//ul[contains(@class,"tab")]//li',
            '//*[contains(normalize-space(),"学段") or contains(normalize-space(),"学科")]/following-sibling::*//a',
        )
        try:
            for xpath in xpaths:
                for el in self.driver.find_elements(By.XPATH, xpath):
                    if not el.is_displayed():
                        continue
                    text = (el.text or '').strip()
                    if not text or len(text) > 12:
                        continue
                    if any(k in text for k in SKIP_TAB_TEXTS):
                        continue
                    tabs.append(el)
            # 去重（同一元素可能被多个 xpath 命中）
            uniq = []
            seen_id = set()
            for el in tabs:
                key = el.id
                if key in seen_id:
                    continue
                seen_id.add(key)
                uniq.append(el)
            return uniq[:30]
        except Exception:
            return []

    def _pick_next_unfinished(self, required: list[dict]) -> dict | None:
        for item in required:
            title = item.get('title') or ''
            if item.get('done'):
                continue
            if title in self._played_titles:
                continue
            return item
        for item in required:
            if not item.get('done'):
                return item
        return None

    def _play_required_item(self, item: dict) -> bool:
        title = item.get('title') or ''
        self._log_info('准备播放必修: %s', title)
        self._ensure_on_list_window()
        before = set(self.driver.window_handles)
        clicked = self._click_play_near_title(title)
        if not clicked:
            return False
        return self._wait_and_monitor_player(before, title)

    def _click_play_near_title(self, title: str) -> bool:
        from selenium.webdriver.common.by import By

        short = title[:18]
        if not short:
            return False
        row_xpaths = (
            f'//tr[contains(., "{short}")]',
            f'//li[contains(normalize-space(), "{short}")]',
            f'//*[contains(normalize-space(), "{short}")]',
        )
        for row_xpath in row_xpaths:
            try:
                rows = self.driver.find_elements(By.XPATH, row_xpath)
            except Exception:
                continue
            for row in rows[:8]:
                if not row.is_displayed():
                    continue
                for text in PLAY_BUTTON_TEXTS:
                    try:
                        btns = row.find_elements(
                            By.XPATH, f'.//a[contains(normalize-space(),"{text}")] | .//button[contains(normalize-space(),"{text}")]'
                        )
                    except Exception:
                        continue
                    for btn in btns:
                        if btn.is_displayed():
                            self.driver.execute_script('arguments[0].click();', btn)
                            time.sleep(1.5)
                            self._dismiss_popups()
                            return True
                # 行本身可点
                try:
                    href = row.get_attribute('href') or ''
                    if 'javascript' not in href.lower() and (href or row.tag_name.lower() in ('a', 'button')):
                        row.click()
                        time.sleep(1.5)
                        return True
                except Exception:
                    continue
        return False

    def _play_from_course_menu(self, unfinished: list[dict]) -> bool:
        """学习数据上点不开时，转到培训课程页按标题找「观看回放」。"""
        self._ensure_on_list_window()
        if not self._click_left_nav(NAV_COURSE):
            self._log_warning('未找到培训课程导航')
            return False
        titles = [item.get('title') for item in unfinished if item.get('title')]
        if not titles:
            # 没有解析到标题时，直接点第一节带「观看回放」且含必修的课
            return self._click_first_required_replay()

        for title in titles:
            if self._stopped:
                return False
            if title in self._played_titles:
                continue
            before = set(self.driver.window_handles)
            if self._click_play_near_title(title):
                return self._wait_and_monitor_player(before, title)
        return self._click_first_required_replay()

    def _click_first_required_replay(self) -> bool:
        from selenium.webdriver.common.by import By

        before = set(self.driver.window_handles)
        try:
            rows = self.driver.find_elements(By.XPATH, '//tr | //li')
            for row in rows:
                text = (row.text or '')
                if not any(m in text for m in REQUIRED_MARKERS):
                    continue
                if any(m in text for m in ELECTIVE_MARKERS):
                    continue
                if any(m in text for m in DONE_MARKERS):
                    continue
                btns = row.find_elements(
                    By.XPATH, './/a[contains(normalize-space(),"观看回放")] | .//a[contains(normalize-space(),"学习")]'
                )
                for btn in btns:
                    if btn.is_displayed():
                        title = text.replace('\n', ' ').strip()[:40]
                        self.driver.execute_script('arguments[0].click();', btn)
                        time.sleep(1.5)
                        return self._wait_and_monitor_player(before, title)
        except Exception:
            self._log_exception('培训课程页查找回放失败')
        return False

    def _try_switch_next_subject(self):
        tabs = self._subject_tabs()
        for tab in tabs:
            try:
                cls = tab.get_attribute('class') or ''
                if 'active' in cls or 'cur' in cls or 'on' in cls:
                    continue
                tab.click()
                time.sleep(1)
                self._log_info('已切换学科页签: %s', (tab.text or '').strip())
                return
            except Exception:
                continue

    # --------------------------------------------------------------- player
    def _wait_and_monitor_player(self, before_handles: set, title: str) -> bool:
        play_handle = self._wait_new_window(before_handles, timeout=12)
        if play_handle:
            self.play_window = play_handle
            self.driver.switch_to.window(play_handle)
        else:
            # 可能同页跳转 / iframe
            self.play_window = self.driver.current_window_handle

        time.sleep(2)
        self._dismiss_popups()
        url = self.driver.current_url or ''
        self._log_info('播放页 url=%s title=%s', url, title)
        if not self._looks_like_player():
            if play_handle:
                return True  # 已点开，交给监控判断
            return False

        self._play_done_event.clear()
        self._start_monitor_thread(self._monitor_play_progress, suffix='play')
        self._play_done_event.wait()
        if title:
            self._played_titles.add(title)
        return True

    def _looks_like_player(self) -> bool:
        url = (self.driver.current_url or '').lower()
        if 'gensee.com' in url or '/webcast/' in url or 'vod' in url:
            return True
        try:
            if self.driver.find_elements('css selector', 'video'):
                return True
            if self.driver.find_elements('css selector', 'iframe'):
                return True
        except Exception:
            pass
        return False

    def _wait_new_window(self, before_handles: set, timeout=12):
        end = time.time() + timeout
        while time.time() < end and self.is_running:
            handles = set(self.driver.window_handles)
            new_ones = handles - before_handles
            if new_ones:
                return next(iter(new_ones))
            time.sleep(0.4)
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

                self._dismiss_popups()
                self._try_resume_video()

                percent = self._read_play_percent()
                if percent is not None:
                    self._log_info('播放进度: %.1f%%', percent)
                    if percent >= 99.0:
                        self._log_info('当前课件播放完成')
                        break
                    if abs(percent - last_percent) < 0.2:
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
        try:
            result = self.driver.execute_script(
                """
                const videos = [];
                const collect = (doc) => {
                    if (!doc) return;
                    doc.querySelectorAll('video').forEach(v => videos.push(v));
                };
                collect(document);
                document.querySelectorAll('iframe').forEach(f => {
                    try { collect(f.contentDocument); } catch (e) {}
                });
                for (const v of videos) {
                    if (!v || !v.duration || v.duration < 1) continue;
                    if (v.ended) return 100;
                    return (v.currentTime / v.duration) * 100;
                }
                return null;
                """
            )
            if result is not None:
                return float(result)
        except Exception:
            pass
        try:
            body = self.driver.find_element('tag name', 'body').text or ''
            matches = PERCENT_PATTERN.findall(body)
            if matches:
                return float(matches[-1])
        except Exception:
            pass
        return None

    def _try_resume_video(self):
        from selenium.webdriver.common.by import By

        for xpath in (
            '//button[contains(@class,"play") or contains(@aria-label,"播放")]',
            '//div[contains(@class,"play") and not(contains(@class,"pause"))]',
            '//a[contains(normalize-space(),"继续学习") or contains(normalize-space(),"继续播放")]',
            '//*[contains(normalize-space(),"点击播放") or contains(normalize-space(),"立即播放")]',
        ):
            try:
                els = self.driver.find_elements(By.XPATH, xpath)
                for el in els:
                    if el.is_displayed():
                        el.click()
                        time.sleep(0.3)
            except Exception:
                continue

        # Gensee / 通用 video
        try:
            self.driver.execute_script(
                """
                const playAll = (doc) => {
                    if (!doc) return;
                    doc.querySelectorAll('video').forEach(v => {
                        try { v.muted = false; v.play().catch(() => {}); } catch (e) {}
                    });
                };
                playAll(document);
                document.querySelectorAll('iframe').forEach(f => {
                    try { playAll(f.contentDocument); } catch (e) {}
                });
                """
            )
        except Exception:
            pass

        # 尝试进入 Gensee iframe
        try:
            frames = self.driver.find_elements(By.TAG_NAME, 'iframe')
            for frame in frames[:4]:
                try:
                    self.driver.switch_to.frame(frame)
                    self.driver.execute_script(
                        """
                        const v = document.querySelector('video');
                        if (v && v.paused) { v.play().catch(() => {}); }
                        """
                    )
                except Exception:
                    pass
                finally:
                    try:
                        self.driver.switch_to.default_content()
                    except Exception:
                        pass
        except Exception:
            pass

    def _close_play_window_and_return(self):
        try:
            if (
                self.play_window
                and self.list_window
                and self.play_window != self.list_window
                and self.play_window in self.driver.window_handles
            ):
                self.driver.switch_to.window(self.play_window)
                self.driver.close()
                self._log_info('已关闭播放页')
        except Exception:
            self._log_exception('关闭播放页失败')
        finally:
            self.play_window = None
        self._ensure_on_list_window()

    def _ensure_on_list_window(self):
        if self.list_window and self.list_window in self.driver.window_handles:
            self.driver.switch_to.window(self.list_window)
        else:
            self._log_warning('列表窗口丢失，重新打开培训首页')
            self._open_training_home()

    def _dismiss_popups(self):
        from selenium.webdriver.common.by import By

        for xpath in (
            '//a[contains(@class,"btn_close") or contains(@class,"close")]',
            '//*[contains(@class,"btn_close_tzgg")]',
            '//button[contains(normalize-space(),"确定") or contains(normalize-space(),"我知道了") or contains(normalize-space(),"关闭")]',
            '//a[contains(normalize-space(),"确定") or contains(normalize-space(),"关闭")]',
        ):
            try:
                els = self.driver.find_elements(By.XPATH, xpath)
                for el in els:
                    if el.is_displayed():
                        el.click()
                        time.sleep(0.2)
            except Exception:
                continue
        try:
            self._dismiss_confirm_dialog()
        except Exception:
            pass
