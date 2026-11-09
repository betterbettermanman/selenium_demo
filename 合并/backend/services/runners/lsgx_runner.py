"""
乐山公需课（LSGX）任务执行器

网站编码：LSGX
站点：http://lssjjw.63ym.cn/
学习页：http://lssjjw.63ym.cn/study.aspx?id=118
登录：login.aspx，账号 + 密码 + 图形验证码（canvas / Validate.aspx，ddddocr）
播课：同一页目录 .lesson-item + video.js（#my-video）。未报名的免费课先点「立即报名」。
课程 ID 可从 class_id、课表 URL 解析；兼容旧站 /course/118.html。
"""
from __future__ import annotations

import re
import time
from typing import Any
from urllib.parse import parse_qs, urlparse

from services.runners.selenium_runner import SeleniumTaskRunner
from services.task_runner import register_runner, update_task_fields

LSGX_ORIGIN = 'http://lssjjw.63ym.cn'
LSGX_HOME_URL = f'{LSGX_ORIGIN}/'
LSGX_LOGIN_URL = f'{LSGX_ORIGIN}/login.aspx'
LSGX_DEFAULT_COURSE_ID = '118'
# 旧站课程页、新站详情页 / 学习页都从这里取数字 ID
_COURSE_ID_RE = re.compile(r'(?:(?:[?&]id=)|(?:/course/))(\d+)', re.IGNORECASE)
_DONE_MARK = '已学完'
_UNFINISHED_MARKS = ('未学习', '已学至')


def resolve_lsgx_course_id(*candidates: str) -> str:
    """从课程 ID、旧站 /course/{id}.html 或新站 ?id= 中解析课程 ID。"""
    for raw in candidates:
        text = (raw or '').strip()
        if not text or text.lower() == 'null':
            continue
        if text.isdigit():
            return text
        match = _COURSE_ID_RE.search(text)
        if match:
            return match.group(1)
        query = parse_qs(urlparse(text).query)
        if query.get('id') and str(query['id'][0]).isdigit():
            return str(query['id'][0])
    return LSGX_DEFAULT_COURSE_ID


def lsgx_detail_url(course_id: str) -> str:
    return f'{LSGX_ORIGIN}/coursedetail.aspx?id={course_id}'


def lsgx_study_url(course_id: str) -> str:
    return f'{LSGX_ORIGIN}/study.aspx?id={course_id}'


def normalize_captcha_code(raw: str) -> str:
    """验证码为 4 位字母或数字。识别结果里的空格、杂点符号丢掉。"""
    code = re.sub(r'[^0-9A-Za-z]', '', raw or '')
    return code[:4]


def lesson_is_finished(status_text: str) -> bool:
    text = (status_text or '').strip()
    if any(mark in text for mark in _UNFINISHED_MARKS):
        return False
    return _DONE_MARK in text


def summarize_lesson_status(statuses: list[str]) -> tuple[int, int]:
    done = 0
    total = 0
    for status in statuses:
        text = (status or '').strip()
        if not text:
            continue
        total += 1
        if lesson_is_finished(text):
            done += 1
    return done, total


@register_runner('LSGX')
class LsgxTaskRunner(SeleniumTaskRunner):
    """乐山公需课任务执行器。"""

    def __init__(self, task, website):
        super().__init__(task, website)
        self.course_id = LSGX_DEFAULT_COURSE_ID
        self.current_course_url = lsgx_study_url(self.course_id)

    def run_main(self):
        self._log_info(
            '开始任务 id=%s user=%s class_id=%s enable_sms=%s headless=%s',
            self.task.id, self.task.username, self.task.class_id,
            self.website.enable_sms_code, self.task.is_head,
        )
        try:
            self._prepare_course()
            self._build_context_log(self._parse_course_list())
            self._init_browser(window_size=(1920, 1080))
            self._login()
            if self._stopped or not self.is_running:
                return
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

    def _prepare_course(self):
        sources: list[str] = []
        raw = self.task.courses
        for item in self._parse_course_items(raw):
            if isinstance(item, str):
                sources.append(item)
            elif isinstance(item, dict):
                sources.append(str(item.get('url') or ''))
                sources.append(str(item.get('course_id') or ''))
        sources.append(self.task.class_id or '')
        self.course_id = resolve_lsgx_course_id(*sources)
        self.current_course_url = lsgx_study_url(self.course_id)
        self._log_info('课程 course_id=%s study=%s', self.course_id, self.current_course_url)

    def _parse_course_list(self) -> list[dict[str, Any]]:
        course_id = self.course_id or resolve_lsgx_course_id(self.task.class_id or '')
        study_url = lsgx_study_url(course_id)
        raw = self.task.courses
        if not raw:
            return [{
                'name': '默认课程',
                'url': study_url,
                'course_id': course_id,
            }]

        result = []
        for item in self._parse_course_items(raw):
            if isinstance(item, str):
                item_id = resolve_lsgx_course_id(item, course_id)
                result.append({
                    'name': item,
                    'url': lsgx_study_url(item_id),
                    'course_id': item_id,
                })
            elif isinstance(item, dict):
                item_id = resolve_lsgx_course_id(
                    str(item.get('course_id') or ''),
                    str(item.get('url') or ''),
                    course_id,
                )
                result.append({
                    'name': item.get('name', ''),
                    'url': lsgx_study_url(item_id),
                    'course_id': item_id,
                })
        return result or [{
            'name': '默认课程',
            'url': study_url,
            'course_id': course_id,
        }]

    def _is_logged_in(self) -> bool:
        try:
            return bool(self.driver.execute_script(
                """
                var url = location.href || '';
                if (/login\\.aspx/i.test(url) && document.getElementById('uname')) return false;
                if (document.querySelector('a[href*="loginout.aspx"]')) return true;
                var text = document.body ? (document.body.innerText || '') : '';
                if (text.indexOf('欢迎您') >= 0 && text.indexOf('退出') >= 0) return true;
                if (/\\/Person\\//i.test(url)) return true;
                if (/study\\.aspx/i.test(url) && document.querySelector('#catalogList .lesson-item')) return true;
                return false;
                """
            ))
        except Exception:
            return False

    def _login(self, max_rounds=5):
        try:
            self._log_info('打开登录页检查登录态 %s', LSGX_LOGIN_URL)
            self._driver_get(LSGX_LOGIN_URL)
            time.sleep(2)
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
            time.sleep(2)

        if not self._is_logged_in():
            raise RuntimeError('登录失败，请检查账号密码或验证码')

    def _auto_login(self):
        from selenium.common import ElementNotInteractableException, TimeoutException
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.wait import WebDriverWait

        try:
            if 'login.aspx' not in (self.driver.current_url or '').lower() or self._is_logged_in():
                self._driver_get(LSGX_LOGIN_URL)
                time.sleep(1)
            if self._is_logged_in():
                self._log_info('自动登录前检测到已登录，跳过表单')
                return

            self._dismiss_login_layers()
            username_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'uname'))
            )
            username_input.clear()
            username_input.send_keys(self.task.username)

            password_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'pwd'))
            )
            password_input.clear()
            password_input.send_keys(self.task.password)

            if not self._fill_captcha():
                self._log_warning('验证码未写入输入框，取消本次登录提交')
                return

            login_btn = self.driver.find_element(By.ID, 'loginBtn')
            # 验证码错误时的 layer 遮罩会挡住原生点击，直接触发按钮自己的提交事件
            self.driver.execute_script('arguments[0].click();', login_btn)
            try:
                WebDriverWait(self.driver, 15).until(EC.staleness_of(login_btn))
            except TimeoutException:
                self._log_warning('登录提交后页面未跳转')
            time.sleep(1)
            if not self._is_logged_in():
                tip = self._read_login_error()
                if tip:
                    self._log_warning('登录未成功: %s', tip)
            else:
                self._log_info('登录完成 user=%s', self.task.username)
        except TimeoutException:
            self._log_error('超时未找到登录相关输入框')
        except ElementNotInteractableException:
            self._log_error('登录输入框不可交互')
        except Exception as exc:
            self._log_error('自动登录失败: %s', exc)

    def _dismiss_login_layers(self):
        try:
            self.driver.execute_script(
                """
                document.querySelectorAll('.layui-layer-btn a, .layui-layer-close').forEach(function (el) {
                    try { el.click(); } catch (e) {}
                });
                if (window.layer && layer.closeAll) {
                    try { layer.closeAll(); } catch (e) {}
                }
                """
            )
        except Exception:
            pass

    def _read_login_error(self) -> str:
        try:
            text = self.driver.execute_script(
                """
                var layer = document.querySelector('.layui-layer-content');
                if (layer && (layer.innerText || '').trim()) return layer.innerText.trim();
                var toast = document.getElementById('toast');
                if (toast && toast.classList.contains('show')) return (toast.innerText || '').trim();
                return (document.body && document.body.innerText || '').slice(0, 400);
                """
            ) or ''
        except Exception:
            return ''
        for hint in (
            '请输入验证码', '验证码不能为空', '验证码错误', '验证码不正确',
            '密码错误', '账号或密码', '用户不存在', '账号不存在',
        ):
            if hint in text:
                return hint
        return ''

    def _fill_captcha(self) -> bool:
        """识别图形验证码并写入 #captcha。空结果不提交。"""
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.wait import WebDriverWait

        for attempt in range(3):
            code = self._recognize_image_captcha()
            if len(code) < 4:
                self._log_warning('验证码识别不足 4 位，换一张重试 %s/3', attempt + 1)
                self._refresh_captcha()
                continue

            captcha_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'captcha'))
            )
            self._set_input_value(captcha_input, code)
            actual = self.driver.execute_script(
                "var el = document.getElementById('captcha'); return el ? (el.value || '') : '';"
            ) or ''
            if actual:
                self._log_info('已输入验证码 len=%s', len(actual))
                return True
            self._log_warning('验证码未能写入输入框，换一张重试 %s/3', attempt + 1)
            self._refresh_captcha()
        return False

    def _set_input_value(self, element, value: str):
        """先键盘输入，写不进去再用脚本赋值，保证表单能提交到该字段。"""
        try:
            element.click()
        except Exception:
            pass
        try:
            element.clear()
        except Exception:
            pass
        element.send_keys(value)
        current = element.get_attribute('value') or ''
        if current == value:
            return
        self.driver.execute_script(
            """
            var el = arguments[0];
            var value = arguments[1];
            el.focus();
            el.value = value;
            el.dispatchEvent(new Event('input', {bubbles: true}));
            el.dispatchEvent(new Event('change', {bubbles: true}));
            """,
            element,
            value,
        )

    def _refresh_captcha(self):
        try:
            self.driver.execute_script(
                """
                var link = document.getElementById('refreshCaptcha');
                if (link) { link.click(); return; }
                var btn = document.getElementById('captchaImg');
                if (btn) btn.click();
                """
            )
        except Exception:
            self._log_exception('刷新验证码失败')
        time.sleep(0.6)

    def _recognize_image_captcha(self) -> str:
        """从 canvas 像素识别验证码。元素截图经常是空白，不能用来提交。"""
        try:
            self._wait_captcha_painted()
            code = normalize_captcha_code(self._ocr_captcha_png())
            self._log_info('图形验证码识别结果 len=%s', len(code))
            return code
        except Exception:
            self._log_exception('验证码识别失败')
            return ''

    def _wait_captcha_painted(self, timeout: float = 8):
        from selenium.webdriver.support.wait import WebDriverWait

        WebDriverWait(self.driver, timeout).until(
            lambda d: d.execute_script(
                """
                var canvas = document.getElementById('captchaCanvas');
                if (!canvas) return false;
                var ctx = canvas.getContext('2d');
                var data = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
                var n = 0;
                for (var i = 0; i < data.length; i += 16) {
                    if (data[i + 3] > 20 && (data[i] < 245 || data[i + 1] < 245 || data[i + 2] < 245)) n++;
                }
                return n > 20;
                """
            )
        )

    def _ocr_captcha_png(self) -> str:
        import base64
        import os

        data_url = self.driver.execute_script(
            """
            var canvas = document.getElementById('captchaCanvas');
            if (!canvas) return '';
            try { return canvas.toDataURL('image/png'); }
            catch (e) { return ''; }
            """
        ) or ''
        png = b''
        if isinstance(data_url, str) and data_url.startswith('data:image'):
            png = base64.b64decode(data_url.split(',', 1)[1])
        if not png:
            from selenium.webdriver.common.by import By

            canvas = self.driver.find_element(By.ID, 'captchaCanvas')
            return self._recognize_captcha_screenshot(canvas, f'lsgx_{self.task.username}.png')

        os.makedirs('png', exist_ok=True)
        save_path = os.path.join('png', f'lsgx_{self.task.username}.png')
        with open(save_path, 'wb') as handle:
            handle.write(png)
        try:
            return self._new_ddddocr().classification(png) or ''
        except ImportError:
            self._log_warning('未安装 ddddocr，无法识别验证码')
            return ''
        except Exception:
            self._log_exception('验证码识别失败')
            return ''

    def _play_courses(self):
        self.is_complete = False
        self._open_study_page()
        if self._stopped or not self.is_running:
            return
        if self._course_finished_dialog() or self._all_lessons_finished():
            self._pause_video()
            self._log_info('课程已全部学完')
            self._mark_course_complete()
            return

        self._log_info('站点会自动点开第一节未学完课件，开始监听播放')
        self._start_monitor_thread(self._check_course_success)
        self._wait_until_complete()
        self._log_info('课表播放流程结束 user=%s', self.task.username)

    def _open_study_page(self):
        if self.is_complete:
            return

        url = lsgx_study_url(self.course_id)
        self.current_course_url = url
        self._log_info('打开学习页: %s', url)
        self._driver_get(url)
        time.sleep(2)

        if not self._is_logged_in():
            self._log_warning('学习页未登录，重新登录')
            self._login()
            self._driver_get(url)
            time.sleep(2)

        if self._catalog_ready():
            self._log_lesson_progress()
            return

        self._enroll_if_needed()
        if not self._wait_catalog():
            raise RuntimeError(
                f'未进入学习页 course_id={self.course_id} url={self.driver.current_url}'
            )
        self._log_lesson_progress()

    def _catalog_ready(self) -> bool:
        try:
            return bool(self.driver.execute_script(
                "return document.querySelectorAll('#catalogList .lesson-item').length > 0;"
            ))
        except Exception:
            return False

    def _wait_catalog(self, timeout=20) -> bool:
        from selenium.webdriver.support.wait import WebDriverWait

        try:
            WebDriverWait(self.driver, timeout).until(lambda d: self._catalog_ready())
            return True
        except Exception:
            self._log_warning('等待课程目录超时 url=%s', getattr(self.driver, 'current_url', ''))
            return False

    def _enroll_if_needed(self):
        detail = lsgx_detail_url(self.course_id)
        if 'coursedetail.aspx' not in (self.driver.current_url or '').lower():
            self._log_info('打开课程详情准备报名 %s', detail)
            self._driver_get(detail)
            time.sleep(2)

        info = self.driver.execute_script(
            """
            var btn = document.getElementById('btnAction');
            if (!btn) return null;
            return {
                text: (btn.innerText || '').replace(/\\s+/g, ''),
                purchased: String(btn.getAttribute('data-purchased') || ''),
                free: String(btn.getAttribute('data-free') || '')
            };
            """
        )
        if not info:
            self._log_warning('课程详情没有报名/学习按钮')
            return

        self._log_info(
            '课程按钮 text=%s purchased=%s free=%s',
            info.get('text'), info.get('purchased'), info.get('free'),
        )
        if info.get('purchased') != '1' and info.get('free') != '1':
            raise RuntimeError('课程未报名且不是免费课，无法自动进入学习')

        self.driver.execute_script("document.getElementById('btnAction').click();")
        if info.get('purchased') != '1':
            if not self._click_layer_button('立即报名', '确定'):
                self._log_warning('未出现免费报名确认框')
        self._wait_catalog(timeout=20)

    def _click_layer_button(self, *labels: str, timeout: float = 8) -> bool:
        deadline = time.time() + timeout
        wanted = [label.replace(' ', '') for label in labels]
        while time.time() < deadline:
            if self._stopped:
                return False
            clicked = self.driver.execute_script(
                """
                var labels = arguments[0];
                var nodes = document.querySelectorAll('.layui-layer-btn a');
                for (var i = 0; i < nodes.length; i++) {
                    var text = (nodes[i].innerText || '').replace(/\\s/g, '');
                    for (var j = 0; j < labels.length; j++) {
                        if (text.indexOf(labels[j]) >= 0) {
                            nodes[i].click();
                            return text;
                        }
                    }
                }
                return '';
                """,
                wanted,
            )
            if clicked:
                self._log_info('已点击弹窗按钮 %s', clicked)
                return True
            time.sleep(0.4)
        return False

    def _lesson_snapshot(self) -> list[dict[str, Any]]:
        try:
            rows = self.driver.execute_script(
                """
                return Array.from(document.querySelectorAll('#catalogList .lesson-item')).map(function (el) {
                    return {
                        sid: el.getAttribute('data-sid') || '',
                        status: ((el.querySelector('.lesson-time') || {}).innerText || '').trim(),
                        locked: el.classList.contains('locked'),
                        playing: el.classList.contains('playing')
                    };
                });
                """
            )
            return rows or []
        except Exception:
            self._log_exception('读取课程目录失败')
            return []

    def _log_lesson_progress(self) -> tuple[int, int]:
        rows = self._lesson_snapshot()
        done, total = summarize_lesson_status([row.get('status', '') for row in rows])
        if total:
            self._update_task_progress(f'{done}/{total}')
            self._log_info('课表进度 已完成=%s/%s', done, total)
        return done, total

    def _all_lessons_finished(self) -> bool:
        done, total = self._log_lesson_progress()
        return total > 0 and done == total

    def _course_finished_dialog(self) -> bool:
        try:
            text = self.driver.execute_script(
                """
                var parts = [];
                document.querySelectorAll('.layui-layer-content').forEach(function (el) {
                    parts.push(el.innerText || '');
                });
                return parts.join('\\n');
                """
            ) or ''
        except Exception:
            return False
        return '已完成本课程' in text or '学时证明已生成' in text

    def _click_lesson(self, sid: str) -> bool:
        if not sid:
            return False
        try:
            clicked = self.driver.execute_script(
                """
                var sid = arguments[0];
                var nodes = document.querySelectorAll('#catalogList .lesson-item');
                for (var i = 0; i < nodes.length; i++) {
                    if ((nodes[i].getAttribute('data-sid') || '') === sid) {
                        nodes[i].click();
                        return true;
                    }
                }
                return false;
                """,
                sid,
            )
            if clicked:
                self._log_info('打开小节 sid=%s', sid)
            return bool(clicked)
        except Exception:
            self._log_exception('点击小节失败 sid=%s', sid)
            return False

    def _click_first_unfinished(self) -> bool:
        for row in self._lesson_snapshot():
            if row.get('locked'):
                continue
            if lesson_is_finished(row.get('status', '')):
                continue
            if not row.get('status'):
                continue
            return self._click_lesson(str(row.get('sid') or ''))
        return False

    def _click_after_ended(self) -> bool:
        """当前节已结束时点下一节；站点自动连播失败时由这里补点。"""
        try:
            sid = self.driver.execute_script(
                """
                var items = Array.from(document.querySelectorAll('#catalogList .lesson-item'));
                var start = 0;
                items.forEach(function (el, idx) {
                    if (el.classList.contains('playing')) start = idx + 1;
                });
                function unfinished(el) {
                    var status = ((el.querySelector('.lesson-time') || {}).innerText || '');
                    if (el.classList.contains('locked')) return false;
                    if (status.indexOf('已学完') >= 0) return false;
                    return status.indexOf('未学习') >= 0 || status.indexOf('已学至') >= 0 || !status;
                }
                for (var i = start; i < items.length; i++) {
                    if (unfinished(items[i])) return items[i].getAttribute('data-sid') || '';
                }
                for (var j = 0; j < items.length; j++) {
                    if (unfinished(items[j])) return items[j].getAttribute('data-sid') || '';
                }
                return '';
                """
            )
        except Exception:
            self._log_exception('查找下一节失败')
            return False
        return self._click_lesson(str(sid or ''))

    def _find_video(self):
        from selenium.webdriver.common.by import By

        try:
            selector = self.driver.execute_script(
                """
                var video = document.querySelector('#my-video_html5_api, video.vjs-tech, video');
                if (!video) return '';
                if (video.id) return '#' + video.id;
                return 'video';
                """
            )
        except Exception:
            return None
        if not selector:
            return None
        try:
            element = self.driver.find_element(By.CSS_SELECTOR, selector)
        except Exception:
            return None
        if (element.tag_name or '').lower() != 'video':
            return None
        return element

    def _pause_video(self):
        try:
            self.driver.execute_script(
                """
                var video = document.querySelector('#my-video_html5_api, video.vjs-tech, video');
                if (video && !video.paused) video.pause();
                """
            )
        except Exception:
            pass

    def _study_page_broken(self) -> bool:
        """目录还在就不是错误页。video.js 源码里有裸「404」，整页搜索会误判。"""
        if self._catalog_ready():
            return False
        try:
            text = (self.driver.execute_script(
                "return (document.body && document.body.innerText) || '';"
            ) or '').lower()
        except Exception:
            return True
        keywords = (
            '502 bad gateway',
            'bad gateway',
            '504 gateway timeout',
            '500 internal server error',
            '无法访问此网站',
            '无法访问',
            '连接已重置',
            '连接超时',
            '页面加载失败',
            'page not found',
        )
        return any(keyword in text for keyword in keywords)

    def _check_course_success(self):
        sleep_time = 60
        self._log_info('开始监听播放进度 user=%s interval=%ss', self.task.username, sleep_time)

        while not self.is_complete and self.is_running and not self._stopped:
            if self._course_finished_dialog() or self._all_lessons_finished():
                self._pause_video()
                self._log_info('课程已全部学完')
                self._mark_course_complete()
                break

            if self._study_page_broken():
                self._log_warning('页面异常，重新打开学习页')
                try:
                    self._open_study_page()
                except Exception:
                    self._log_exception('重新打开学习页失败')
                time.sleep(15)
                continue

            video = self._find_video()
            if video is None:
                self._log_warning('未找到播放器，尝试点开未完成小节')
                if not self._click_first_unfinished():
                    try:
                        self._open_study_page()
                    except Exception:
                        self._log_exception('重新打开学习页失败')
                time.sleep(15)
                continue

            try:
                info = self.driver.execute_script(
                    """
                    var video = arguments[0];
                    return {
                        paused: !!video.paused,
                        ended: !!video.ended,
                        currentTime: video.currentTime || 0,
                        duration: video.duration || 0
                    };
                    """,
                    video,
                )
            except Exception as exc:
                self._log_warning('获取视频进度失败: %s', self._short_exc(exc))
                time.sleep(15)
                continue

            try:
                progress = 0.0
                if info['duration'] and info['duration'] > 0:
                    progress = (info['currentTime'] / info['duration']) * 100
                self._log_info('播放进度: %.1f%%', progress)

                if info['ended']:
                    self._log_info('当前视频已播完，查找下一节')
                    if not self._click_after_ended():
                        self._open_study_page()
                    time.sleep(5)
                elif info['paused'] or info['currentTime'] == 0:
                    reason = '暂停' if info['paused'] and info['currentTime'] > 0 else '未开始'
                    self._log_info('视频%s，尝试继续播放', reason)
                    if not self._resume_video(video):
                        self._log_warning(
                            '继续播放失败，稍后重试 currentTime=%.1f', info['currentTime'],
                        )
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
                root.querySelectorAll(
                    '[class*="pausecenter"], .vjs-modal-dialog, .vjs-loading-spinner, .vjs-big-play-button'
                ).forEach(function (el) {
                    try {
                        if (el.classList && el.classList.contains('vjs-big-play-button')) return;
                        el.style.pointerEvents = 'none';
                    } catch (e) {}
                });
                var rect = video.getBoundingClientRect();
                document.querySelectorAll('h2, .vjs-title-bar, .vjs-title-bar-title, [class*="title"]').forEach(function (el) {
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

        if self._try_js_play(video):
            return True

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
