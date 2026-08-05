"""
四川公需课程学习（SCGX）任务执行器

网站编码：SCGX
站点：https://www.sedu.net/student/#/login
参考：selenium_demo/四川省继续教育网/main.py

范围：自动登录 + 按 task.courses 配置播放目标课；暂不处理考试。
登录态：localStorage STUDENT-TOKEN。

课表配置示例（task.courses）：
[
  {"targetId": "xxx", "name": "构建“1+4+N”培育体系，助力教师成长", "status": "0"},
  {"targetId": "yyy", "name": "另一门课", "status": "1"}
]
status: "1"=已完成，其它=未完成。只播放未完成项，播完回写 status=1 并更新 progress。
"""
import base64
import os
import re
import threading
import time

from services.runners.selenium_runner import SeleniumTaskRunner
from services.task_runner import register_runner, update_task_fields

SCGX_LOGIN_URL = 'https://www.sedu.net/student/#/login'
SCGX_CENTER_URL = 'https://www.sedu.net/student/#/center'
SCGX_OUR_COURSE_URL = 'https://www.sedu.net/student/#/our-course'
SCGX_BASE_URL = 'https://www.sedu.net/student/'


@register_runner('SCGX')
class ScgxTaskRunner(SeleniumTaskRunner):
    """四川省继续教育网（sedu.net）学员端执行器。"""

    def __init__(self, task, website):
        super().__init__(task, website)
        self.list_window = None
        self._open_home_lock = threading.Lock()
        self._last_list_refresh = 0
        self._spa_booted = False
        self.current_target_id = ''
        self.current_target_name = ''

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
        登录态以学员端（sedu.net/student）窗口的 localStorage.STUDENT-TOKEN 为准。
        学习页常是新开窗口/不同域名，当前窗口读不到 token，不能据此判失效。
        """
        return bool(self._get_student_token())

    def _get_student_token(self) -> str | None:
        if not self.driver:
            return None

        current = None
        try:
            current = self.driver.current_window_handle
        except Exception:
            pass

        try:
            # 优先当前页（若已在学员端）
            try:
                if 'sedu.net/student' in (self.driver.current_url or ''):
                    token = self._get_local_storage('STUDENT-TOKEN')
                    if token:
                        return token
            except Exception:
                pass

            # 再查列表页窗口
            handles = list(self.driver.window_handles)
            ordered = []
            if self.list_window and self.list_window in handles:
                ordered.append(self.list_window)
            ordered.extend(h for h in handles if h not in ordered)

            for handle in ordered:
                try:
                    self.driver.switch_to.window(handle)
                    if 'sedu.net/student' not in (self.driver.current_url or ''):
                        continue
                    token = self._get_local_storage('STUDENT-TOKEN')
                    if token:
                        return token
                except Exception:
                    continue
            return None
        finally:
            if current:
                try:
                    if current in self.driver.window_handles:
                        self.driver.switch_to.window(current)
                except Exception:
                    pass

    def _boot_spa(self):
        """先加载学员端壳页面，避免直接打开 #/xxx 出现白屏。"""
        if self._spa_booted:
            return
        self._log_info('预加载 SPA 壳页 %s', SCGX_BASE_URL)
        self._driver_get(SCGX_BASE_URL, label='SPA壳页')
        time.sleep(3)
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.support.wait import WebDriverWait

            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#app, body'))
            )
        except Exception:
            self._log_warning('等待 SPA 根节点超时，继续尝试')
        self._spa_booted = True

    def _open_spa_route(self, hash_url: str, *, label: str = 'SPA页面', refresh_on_blank: bool = True):
        """
        打开 hash 路由页面。
        sedu 学员端直接 get #/login 经常白屏，需先 boot 再切 hash；仍白屏则 refresh。
        """
        self._boot_spa()

        # 已在同 origin 时用改 hash，比再次完整 get 更稳
        try:
            current = self.driver.current_url or ''
            if 'sedu.net/student' in current:
                hash_part = ''
                if '#' in hash_url:
                    hash_part = hash_url.split('#', 1)[1]
                    if not hash_part.startswith('/'):
                        hash_part = '/' + hash_part
                    hash_part = '#' + hash_part
                else:
                    hash_part = '#/'
                self._log_info('切换 SPA 路由 %s -> %s', label, hash_part)
                self.driver.execute_script('window.location.hash = arguments[0];', hash_part)
                time.sleep(2)
            else:
                self._driver_get(hash_url, label=label)
                time.sleep(2)
        except Exception:
            self._driver_get(hash_url, label=label)
            time.sleep(2)

        if refresh_on_blank and self._is_spa_blank():
            self._log_warning('%s 疑似白屏，执行刷新', label)
            try:
                self.driver.refresh()
            except Exception:
                self._driver_get(hash_url, label=f'{label}-刷新')
            time.sleep(3)

    def _is_spa_blank(self) -> bool:
        """粗判 SPA 是否白屏（几乎无可见交互元素）。"""
        try:
            from selenium.webdriver.common.by import By

            body = self.driver.find_element(By.TAG_NAME, 'body')
            text = (body.text or '').strip()
            inputs = self.driver.find_elements(By.CSS_SELECTOR, 'input, button, .el-button, .el-table')
            # 白屏时通常几乎没有文本，也没有表单/表格
            if len(text) < 8 and len(inputs) == 0:
                return True
            # app 根节点存在但子节点为空
            apps = self.driver.find_elements(By.ID, 'app')
            if apps:
                html = (apps[0].get_attribute('innerHTML') or '').strip()
                if len(html) < 20:
                    return True
            return False
        except Exception:
            return True

    def _ensure_logged_in(self, max_rounds: int = 8, *, before_check=None, on_success=None):
        """已登录则直接返回，避免从学习页误跳回个人中心。"""
        if not self._spa_booted:
            try:
                self._boot_spa()
            except Exception:
                pass

        if self._is_logged_in():
            self._log_info('学员端已登录，跳过登录流程')
            if on_success:
                on_success()
            return

        super()._ensure_logged_in(
            max_rounds=max_rounds,
            before_check=before_check,
            on_success=on_success,
        )

    def _wait_login_form(self, timeout: int = 20):
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.wait import WebDriverWait

        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//input[@placeholder='请输入身份证号/手机号/单位账号']")
            )
        )

    def _auto_login(self):
        from selenium.common import ElementNotInteractableException, TimeoutException
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.wait import WebDriverWait

        self._log_info('打开登录页 %s', SCGX_LOGIN_URL)
        self._open_spa_route(SCGX_LOGIN_URL, label='登录页')

        try:
            try:
                username_input = self._wait_login_form(timeout=12)
            except TimeoutException:
                self._log_warning('登录表单未出现，刷新后重试')
                self.driver.refresh()
                time.sleep(3)
                if self._is_spa_blank():
                    self._spa_booted = False
                    self._open_spa_route(SCGX_LOGIN_URL, label='登录页-重建')
                username_input = self._wait_login_form(timeout=20)

            username_input.clear()
            username_input.send_keys(self.task.username)

            password_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='请输入密码']"))
            )
            password_input.clear()
            password_input.send_keys(self.task.password)

            captcha_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="请输入验证码"]'))
            )
            captcha_input.clear()
            captcha_input.send_keys(self._recognize_image_captcha())

            login_buttons = self.driver.find_elements(By.XPATH, "//button[span='登录']")
            if not login_buttons:
                login_buttons = self.driver.find_elements(
                    By.XPATH, "//button[.//span[normalize-space()='登录'] or normalize-space()='登录']"
                )
            if not login_buttons:
                raise TimeoutException('未找到登录按钮')
            # 参考脚本取第 2 个「登录」按钮；不足则点最后一个
            btn = login_buttons[1] if len(login_buttons) > 1 else login_buttons[-1]
            btn.click()
            time.sleep(3)
            self._log_info('登录表单已提交 user=%s', self.task.username)
        except (TimeoutException, ElementNotInteractableException):
            self._log_exception('登录失败')
            raise

    def _recognize_image_captcha(self) -> str:
        """识别登录页 base64 验证码图片。"""
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.wait import WebDriverWait

        try:
            img = None
            for xpath in (
                '//input[@placeholder="请输入验证码"]/ancestor::div[contains(@class,"el-input")]/following::img[1]',
                '//img[contains(@src,"data:image")]',
                '//img[@alt="验证码"]',
            ):
                els = self.driver.find_elements(By.XPATH, xpath)
                for el in els:
                    src = el.get_attribute('src') or ''
                    if src.startswith('data:image') or '验证码' in (el.get_attribute('alt') or ''):
                        img = el
                        break
                if img is not None:
                    break
            if img is None:
                img = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, 'img'))
                )

            src = img.get_attribute('src') or ''
            if src.startswith('data:image'):
                match = re.match(r'data:(image/.+?);base64,(.*)', src)
                if not match:
                    return ''
                os.makedirs('png', exist_ok=True)
                save_path = os.path.join('png', f'scgx_{self.task.username}.png')
                with open(save_path, 'wb') as f:
                    f.write(base64.b64decode(match.group(2)))
                try:
                    import ddddocr
                    ocr = ddddocr.DdddOcr()
                    with open(save_path, 'rb') as f:
                        return ocr.classification(f.read())
                except ImportError:
                    self._log_warning('未安装 ddddocr，跳过验证码识别')
                    return ''
                except Exception:
                    self._log_exception('验证码识别失败')
                    return ''

            return self._recognize_captcha_screenshot(img, f'scgx_{self.task.username}.png')
        except Exception:
            self._log_exception('获取验证码失败')
            return ''

    # --------------------------------------------------------------- courses
    def _get_course_configs(self) -> list[dict]:
        """从 task.courses 读取目标课：targetId / name / status。"""
        result = []
        for item in self._parse_course_items(self.task.courses):
            if isinstance(item, dict):
                target_id = str(item.get('targetId') or item.get('id') or '').strip()
                name = str(item.get('name') or item.get('title') or '').strip()
                if not target_id and not name:
                    continue
                result.append({
                    'targetId': target_id,
                    'name': name,
                    'status': str(item.get('status', '0')),
                })
            elif isinstance(item, str) and item.strip():
                result.append({
                    'targetId': '',
                    'name': item.strip(),
                    'status': '0',
                })
        return result

    def _get_current_target(self) -> dict | None:
        """返回下一门未完成目标课（status != '1'）。"""
        for course in self._get_course_configs():
            if course.get('status') != '1':
                return course
        return None

    def _sync_courses_progress(self, courses=None):
        items = courses if courses is not None else self._get_course_configs()
        if not items:
            return
        total = len(items)
        done = sum(1 for c in items if str(c.get('status', '0')) == '1')
        self._update_task_progress(f'{done}/{total}')

    def _mark_target_done(self, target_id: str = '', name: str = ''):
        """将课表中对应 targetId/name 的 status 置为 1，并刷新 progress。"""
        raw_items = self._parse_course_items(self.task.courses)
        if not raw_items:
            return

        target_id = (target_id or self.current_target_id or '').strip()
        name = (name or self.current_target_name or '').strip()
        updated = []
        changed = False
        for item in raw_items:
            if not isinstance(item, dict):
                updated.append(item)
                continue
            item_id = str(item.get('targetId') or item.get('id') or '').strip()
            item_name = str(item.get('name') or item.get('title') or '').strip()
            matched = False
            if target_id and item_id and item_id == target_id:
                matched = True
            elif name and item_name and (name in item_name or item_name in name):
                matched = True
            if matched and str(item.get('status', '0')) != '1':
                item = {**item, 'status': '1'}
                changed = True
                self._log_info('已更新课表播放状态 targetId=%s name=%s -> 1', item_id, item_name)
            updated.append(item)

        if changed:
            update_task_fields(self.task, courses=updated)
            self._sync_courses_progress(self._get_course_configs())

    def _row_matches_target(self, row_name: str, target: dict | None) -> bool:
        if not target:
            return True
        row_name = (row_name or '').replace('\n', ' ').strip()
        name = (target.get('name') or '').strip()
        target_id = (target.get('targetId') or '').strip()
        if name and (name in row_name or row_name in name):
            return True
        if target_id and target_id in row_name:
            return True
        return False

    def _open_our_course_page(self):
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.wait import WebDriverWait

        self._open_spa_route(SCGX_OUR_COURSE_URL, label='我的课程')
        time.sleep(1)
        try:
            menu = self.driver.find_element(By.XPATH, "//div//*[@*='/our-course']")
            menu.click()
            time.sleep(1)
        except Exception:
            pass

        try:
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'el-table__body-wrapper'))
            )
        except Exception:
            self._log_warning('课表未出现，刷新我的课程页')
            self.driver.refresh()
            time.sleep(3)
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'el-table__body-wrapper'))
            )
        self.list_window = self.driver.current_window_handle

    def _find_pending_study_link(self, target: dict | None = None):
        """
        返回 (课程名, 链接, 站点进度, 站点状态) 或 None。
        若传入 target，只匹配 targetId/name 对应行。
        """
        from selenium.webdriver.common.by import By

        table = self.driver.find_element(By.CLASS_NAME, 'el-table__body-wrapper')
        for tr in table.find_elements(By.TAG_NAME, 'tr'):
            tds = tr.find_elements(By.TAG_NAME, 'td')
            if len(tds) < 8:
                continue
            name = ''
            status = ''
            process = ''
            try:
                name = (tds[1].find_element(By.TAG_NAME, 'div').text or '').strip()
                status = (tds[6].find_element(By.TAG_NAME, 'div').text or '').strip()
                process = (tds[4].find_element(By.TAG_NAME, 'div').text or '').strip()
            except Exception:
                try:
                    status = (tds[6].text or '').strip()
                    name = (tds[1].text or '').strip() if len(tds) > 1 else ''
                except Exception:
                    continue

            self._log_info('课表行: %s | 进度=%s | 状态=%s', name.replace('\n', ' / '), process, status)

            if not self._row_matches_target(name, target):
                continue

            # 站点已学完：同步课表状态，不点进去
            if process == '100.00%' or status in ('待考试', '待发证', '已完成'):
                self._log_info('目标课站点已完成: %s', name.replace('\n', ' / '))
                if target:
                    self._mark_target_done(target.get('targetId', ''), target.get('name', ''))
                return None

            if status == '待考试':
                self._log_info('跳过待考试课程: %s', name.replace('\n', ' / '))
                if target:
                    self._mark_target_done(target.get('targetId', ''), target.get('name', ''))
                return None

            a_tags = tds[7].find_elements(By.TAG_NAME, 'a')
            if not a_tags:
                continue
            return name, a_tags[0], process, status
        return None

    def _open_home(self):
        if self.is_complete or self._stopped:
            return
        if not self._open_home_lock.acquire(blocking=False):
            self._log_info('已有打开课程流程在执行，跳过')
            return
        try:
            self._open_home_locked()
        finally:
            self._open_home_lock.release()

    def _open_home_locked(self):
        self._log_info('打开我的课程')
        if not self._is_logged_in():
            self._ensure_logged_in(max_rounds=5)

        try:
            handles = list(self.driver.window_handles)
            if self.list_window and self.list_window in handles:
                for h in handles:
                    if h != self.list_window:
                        self.driver.switch_to.window(h)
                        self.driver.close()
                self.driver.switch_to.window(self.list_window)
        except Exception:
            pass

        self._open_our_course_page()
        self._sync_courses_progress()

        configs = self._get_course_configs()
        course_name = link = process = status = None
        target = None

        # 可能连续遇到「站点已学完」的目标课，需循环标记并找下一门
        for _ in range(30):
            configs = self._get_course_configs()
            target = self._get_current_target() if configs else None

            if configs and target is None:
                self._log_info('配置课表已全部完成，标记任务完成')
                self._mark_course_complete()
                return

            if target:
                self._log_info(
                    '当前目标课 targetId=%s name=%s',
                    target.get('targetId'), target.get('name'),
                )

            found = self._find_pending_study_link(target)
            if found is not None:
                course_name, link, process, status = found
                break

            if not configs:
                self._log_info('无待学习课程，标记任务完成（考试不处理）')
                self._mark_course_complete()
                return

            nxt = self._get_current_target()
            if nxt is None:
                self._log_info('配置课表已全部完成，标记任务完成')
                self._mark_course_complete()
                return
            # 刚把当前目标标完成，继续找下一门
            if target and (
                nxt.get('targetId') != target.get('targetId')
                or nxt.get('name') != target.get('name')
            ):
                continue
            self._log_warning(
                '未在课表中找到可播放的目标课 targetId=%s name=%s',
                nxt.get('targetId'), nxt.get('name'),
            )
            return
        else:
            return

        self.current_target_id = (target or {}).get('targetId', '') if target else ''
        self.current_target_name = (target or {}).get('name', '') if target else course_name
        self._log_info(
            '进入课程: %s | 进度=%s | 状态=%s | targetId=%s',
            course_name.replace('\n', ' / '), process, status, self.current_target_id,
        )
        before = set(self.driver.window_handles)
        try:
            link.click()
        except Exception:
            self.driver.execute_script('arguments[0].click();', link)
        time.sleep(3)

        after = set(self.driver.window_handles)
        new_ones = after - before
        if new_ones:
            self.driver.switch_to.window(next(iter(new_ones)))
            self._log_info('已切换到学习页')

        self._last_list_refresh = time.time()
        self._try_start_video()

    def _try_start_video(self):
        try:
            self.driver.execute_script(
                """
                const tryPlay = (v) => {
                  if (!v) return;
                  if (v.paused) { v.play().catch(() => {}); }
                };
                document.querySelectorAll('video').forEach(tryPlay);
                const btns = [...document.querySelectorAll('button, div, span, i')]
                  .filter(el => {
                    const t = (el.innerText || el.textContent || '').trim();
                    return /^(播放|继续学习|开始学习)$/.test(t);
                  });
                if (btns[0]) btns[0].click();
                """
            )
        except Exception:
            pass

    def _spawn_open_home(self):
        threading.Thread(
            target=lambda: self._run_with_context(self._open_home),
            daemon=True,
            name=f'scgx-open-home-{self.task.id}',
        ).start()

    def _on_current_course_finished(self):
        """当前课播放完成：回写 status，再打开下一门。"""
        self._mark_target_done(self.current_target_id, self.current_target_name)
        self.current_target_id = ''
        self.current_target_name = ''
        if self._get_course_configs() and self._get_current_target() is None:
            self._log_info('全部目标课已完成')
            self._mark_course_complete()
            return
        self._spawn_open_home()

    def _check_course_success(self):
        from selenium.webdriver.common.by import By

        while not self.is_complete and self.is_running and not self._stopped:
            try:
                if not self._is_logged_in():
                    self._log_warning(
                        '学员端窗口未检测到 STUDENT-TOKEN，判定登录失效并重新登录'
                    )
                    self._ensure_logged_in(max_rounds=5)
                    self._spawn_open_home()
                    time.sleep(20)
                    continue

                self._try_start_video()

                page_text = ''
                try:
                    page_text = self.driver.find_element(By.TAG_NAME, 'body').text or ''
                except Exception:
                    pass

                if any(k in page_text for k in ('已学完', '学习完成', '已完成学习')):
                    self._log_info('检测到课程完成标记，更新播放状态')
                    self._on_current_course_finished()
                    time.sleep(30)
                    continue

                if time.time() - self._last_list_refresh >= 180:
                    self._log_info('定时刷新课表')
                    self._spawn_open_home()
            except Exception as exc:
                self._log_error('监控异常: %s', exc)
                self._spawn_open_home()

            time.sleep(30)
