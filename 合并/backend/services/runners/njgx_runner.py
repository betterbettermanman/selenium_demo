"""
内江公需课（NJGX）任务执行器

网站编码：NJGX
参考：selenium_demo/内江公需课/main.py
"""
import time
from typing import Any

from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from services.runners.selenium_runner import SeleniumTaskRunner
from services.task_runner import register_runner

NJGX_BASE_URL = 'https://www.njsjxjy.cn'
NJGX_DEFAULT_COURSE_ID = '1166058'


@register_runner('NJGX')
class NjgxTaskRunner(SeleniumTaskRunner):
    """内江公需课任务执行器。"""

    def __init__(self, task, website):
        super().__init__(task, website)
        self.current_course_url = self._build_course_url()

    def run_main(self):
        self._log_info(
            '开始任务 id=%s user=%s class_id=%s headless=%s',
            self.task.id, self.task.username, self.task.class_id, self.task.is_head,
        )
        try:
            self._build_context_log(self._parse_course_list())
            self._init_browser()
            self._ensure_logged_in()
            self._play_courses()
            self._sync_task_status()
        except Exception:
            self._log_exception('任务 id=%s 执行失败', self.task.id)
            self._handle_run_exception()
            raise
        finally:
            self._finalize_run()

    def _build_course_url(self, course_id=None) -> str:
        cid = course_id or self.task.class_id or NJGX_DEFAULT_COURSE_ID
        return f'{NJGX_BASE_URL}/play/play.aspx?course_id={cid}&try='

    def _build_login_url(self) -> str:
        return (
            f'{NJGX_BASE_URL}/login.aspx?ReturnUrl=/play/play.aspx'
            f'?course_id={self.task.class_id or NJGX_DEFAULT_COURSE_ID}&try='
        )

    def _parse_course_list(self) -> list[dict[str, Any]]:
        raw = self.task.courses
        if not raw:
            return [{
                'name': '默认课程',
                'url': self._build_course_url(),
                'course_id': self.task.class_id or NJGX_DEFAULT_COURSE_ID,
            }]

        result = []
        for item in self._parse_course_items(raw):
            if isinstance(item, str):
                result.append({
                    'name': item,
                    'url': self._build_course_url(item) if item.isdigit() else item,
                    'course_id': item if item.isdigit() else self.task.class_id,
                })
            elif isinstance(item, dict):
                cid = item.get('course_id', self.task.class_id)
                result.append({
                    'name': item.get('name', ''),
                    'url': item.get('url') or self._build_course_url(cid),
                    'course_id': cid,
                })
        return result

    def _is_logged_in(self) -> bool:
        try:
            cookies = self.driver.get_cookies()
            return any(c.get('name') == 'ASP.NET_SessionId' and c.get('value') for c in cookies)
        except Exception:
            return False

    def _auto_login(self):
        from selenium.common import ElementNotInteractableException, TimeoutException
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.wait import WebDriverWait

        self.driver.get(self._build_login_url())
        time.sleep(2)

        try:
            username_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'ctl10_UserName'))
            )
            username_input.clear()
            username_input.send_keys(self.task.username)

            password_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'ctl10_Password'))
            )
            password_input.clear()
            password_input.send_keys(self.task.password)

            capture_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'ctl10_code_op'))
            )
            capture_input.clear()
            capture_input.send_keys(self._recognize_image_captcha())

            self.driver.find_element(By.ID, 'ctl10_ImageButton1').click()
            time.sleep(5)
            self._dismiss_confirm_dialog()
            self._log_info('登录表单已提交 user=%s', self.task.username)
        except TimeoutException:
            self._log_error('超时未找到登录输入框')
            raise
        except ElementNotInteractableException:
            self._log_error('登录输入框不可交互')
            raise

    def _recognize_image_captcha(self) -> str:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.wait import WebDriverWait

        try:
            formdata_div = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'UserImageCheck'))
            )
            return self._recognize_captcha_screenshot(formdata_div, f'njgx_{self.task.username}.png')
        except Exception:
            self._log_exception('识别图形验证码失败')
            return ''

    def _play_courses(self):
        course_list = self._parse_course_list()
        if not course_list:
            self._log_warning('无课表数据')
            self._mark_course_complete()
            return

        first = course_list[0]
        self.current_course_url = first.get('url') or self._build_course_url(first.get('course_id'))
        self.is_complete = False
        self._open_course_home()
        self._start_monitor_thread(self._check_course_success)
        self._wait_until_complete()
        self._log_info('播放流程结束 user=%s', self.task.username)

    def _open_course_home(self):
        if self.is_complete:
            return

        # self.driver.switch_to.default_content()
        self._log_info('打开课程页: %s', self.current_course_url)
        self.driver.get(self.current_course_url)
        time.sleep(5)

        if self._find_and_play_first_unfinished():
            self._log_info('已开始播放未完成课程')
            return

        self._log_info('无未完成课程，任务完成')
        self._mark_course_complete()

    def _switch_to_playframe(self) -> bool:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.wait import WebDriverWait

        try:
            self.driver.switch_to.default_content()
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'playframeNew'))
            )
            self.driver.switch_to.frame('playframeNew')
            self._log_info('已切换到 playframeNew iframe')
            return True
        except Exception:
            self._log_exception('切换 playframeNew 失败')
            return False

    def _find_and_play_first_unfinished(self) -> bool:
        if not self._switch_to_playframe():
            return False
        return self._click_first_unfinished_in_form()

    def _click_first_unfinished_in_form(self) -> bool:
        from selenium.webdriver.common.by import By

        try:
            form1 = self.driver.find_element(By.ID, 'form1')
            divs = form1.find_elements(By.XPATH, './div')
            if len(divs) < 3:
                self._log_warning('form1 下 div 不足 3 个')
                return False

            scroll_div = divs[2].find_element(
                By.XPATH,
                ".//div[@style='overflow: scroll; overflow-x: hidden; height: 200;']",
            )
            links = scroll_div.find_elements(By.TAG_NAME, 'a')
            if not links:
                self._log_warning('未找到课程链接')
                return False

            for link in links:
                status = (link.text or '').strip()
                course_name = self.driver.execute_script(
                    "return arguments[0].previousSibling ? arguments[0].previousSibling.textContent.trim() : '';",
                    link,
                )
                course_name = (course_name or '').replace('&lt;', '').strip()
                self._log_info('课程: %s 状态: %s', course_name, status)

                if status != '已完成':
                    self._log_info('点击播放: %s', course_name)
                    link.click()
                    time.sleep(2)
                    return True
            return False
        except Exception:
            self._log_exception('查找未完成课程失败')
            return False

    def switch_to_playframe(self):
        from selenium.webdriver.support import expected_conditions as EC
        """
        切换到id为playframeNew的iframe
        """
        try:
            # 等待iframe加载
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "playframeNew"))
            )

            # 切换到iframe
            self.driver.switch_to.frame("playframeNew")
            print("✓ 已切换到 playframeNew iframe")
            return True
        except Exception as e:
            print(f"切换iframe失败: {e}")
            return False

    def _check_course_success(self):
        from selenium.webdriver.common.by import By
        sleep_time = 10
        self._log_info('开始监听播放进度 user=%s', self.task.username)

        while not self.is_complete and self.is_running:

            # 获取播放进度
            try:
                progress_el = self.driver.find_element(By.ID, 'spanThisProgress')
                progress_value = float((progress_el.text or '0').strip())
                self._log_info('播放进度: %.1f%%', progress_value)

                if progress_value >= 100:
                    self._log_info('当前小节已完成，查找下一节')
                    self._open_course_home()
                    time.sleep(5)

            except Exception:
                pass

            # 检测视频播放状态
            from selenium.webdriver.support import expected_conditions as EC
            # 等待元素存在
            try:
                # # 1. 等待元素存在于DOM中
                # play_button = WebDriverWait(self.driver, 10).until(
                #     EC.presence_of_element_located((By.ID, "container_display_button_play"))
                # )
                # self._log_info("✅ 播放按钮元素已找到")
                #
                # # 2. 检查是否可见
                # if play_button.is_displayed():
                #     self._log_info("▶️ 按钮已可见，直接点击播放")
                #     play_button.click()

                # 1. 等待元素存在于DOM中
                replay_button = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "container_display_button_replay"))
                )
                self._log_info("✅ 重放按钮元素已找到")

                # 2. 检查是否可见
                if replay_button.is_displayed():
                    self._log_info("▶️ 按钮已可见，直接点击播放")
                    replay_button.click()

            except TimeoutException:
                print("❌ 播放按钮未找到")
            except Exception as e:
                print(f"❌ 操作失败: {e}")


            time.sleep(sleep_time)

        self._log_info('播放监控结束 user=%s', self.task.username)
