"""
乐山公需课（LSGX）任务执行器 —— 参考示例

网站编码：LSGX
可参考项目：selenium_demo/乐山市公需课/main.py
"""
import logging
import os
import threading
import time
from typing import Any

from models import db
from selenium.common import TimeoutException, ElementNotInteractableException
from services.task_runner import BaseTaskRunner, register_runner, update_task_fields

logger = logging.getLogger(__name__)

LSGX_HOME_URL = 'https://www.ls1018.com.cn/'
LSGX_DEFAULT_COURSE_URL = 'https://www.ls1018.com.cn/course/118.html'


@register_runner('LSGX')
class LsgxTaskRunner(BaseTaskRunner):
    """乐山公需课任务执行器。"""

    def __init__(self, task, website):
        super().__init__(task, website)
        self.driver = None
        self.is_complete = False
        self.is_running = True
        self.current_course_url = LSGX_DEFAULT_COURSE_URL
        self._monitor_thread = None

    def run(self):
        logger.info(
            '[LSGX] 开始任务 id=%s user=%s class_id=%s enable_sms=%s headless=%s',
            self.task.id,
            self.task.username,
            self.task.class_id,
            self.website.enable_sms_code,
            self.task.is_head,
        )
        try:
            self._build_context_log()
            self._init_browser()
            self._login()
            self._play_courses()
            update_task_fields(self.task, status='2')
            logger.info('[LSGX] 任务 id=%s 执行完成', self.task.id)
        except Exception as exc:
            logger.exception('[LSGX] 任务 id=%s 执行失败: %s', self.task.id, exc)
            db.session.rollback()
            update_task_fields(self.task, status='1')
            raise
        finally:
            self.is_running = False
            self._cleanup()

    def _build_context_log(self):
        course_list = self._parse_course_list()
        skip_videos = self.task.no_play_videos or []
        logger.info('[LSGX] 课表条目数=%s 跳过视频=%s', len(course_list), skip_videos)
        for idx, item in enumerate(course_list, start=1):
            logger.info('[LSGX] 课表[%s] %s', idx, item)

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

        if isinstance(raw, list):
            result = []
            for item in raw:
                if isinstance(item, str):
                    result.append({'name': item, 'url': item, 'course_id': self.task.class_id})
                elif isinstance(item, dict):
                    result.append({
                        'name': item.get('name', ''),
                        'url': item.get('url', ''),
                        'course_id': item.get('course_id', self.task.class_id),
                    })
            return result

        if isinstance(raw, dict):
            return [{
                'name': raw.get('name', ''),
                'url': raw.get('url', LSGX_DEFAULT_COURSE_URL),
                'course_id': raw.get('course_id', self.task.class_id),
            }]

        return []

    def _init_browser(self):
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
        except ImportError as exc:
            raise RuntimeError('请先安装 selenium: pip install selenium') from exc

        user_data_dir = os.path.join(
            os.getcwd(), 'browser_data', 'LSGX', str(self.task.id), self.task.username
        )
        os.makedirs(user_data_dir, exist_ok=True)

        options = Options()
        if self.task.is_head == '1':
            options.add_argument('--headless=new')
        options.add_argument(f'--user-data-dir={user_data_dir}')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--start-maximized')
        options.add_argument('--no-sandbox')

        chromedriver_path = os.getenv('CHROMEDRIVER_PATH', '../driver/chromedriver.exe')
        service = Service(chromedriver_path) if os.path.exists(chromedriver_path) else Service()

        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.maximize_window()
        self.driver.implicitly_wait(10)
        logger.info('[LSGX] 浏览器已启动 headless=%s', self.task.is_head == '1')

    def _login(self):
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.wait import WebDriverWait

        time.sleep(5)
        logger.info('[LSGX] 打开首页 %s', LSGX_HOME_URL)
        self.driver.get(LSGX_HOME_URL)
        time.sleep(3)
        try:
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
                logger.info('[LSGX] 需要手机验证码，等待处理...')
                time.sleep(30)

            self.driver.find_element(By.ID, 'logSub').click()
            time.sleep(10)
            logger.info('[LSGX] 登录完成 user=%s', self.task.username)
        except TimeoutException:
            logger.error("超时未找到登录相关输入框")
        except ElementNotInteractableException:
            logger.error("登录输入框不可交互")
        except Exception as e:
            logger.error(f"自动登录失败: {str(e)}")

    def _play_courses(self):
        """播放课表：启动监控线程，打开课程页并等待全部完成。"""
        course_list = self._parse_course_list()
        if not course_list:
            logger.warning('[LSGX] 无课表数据，跳过播放')
            self._mark_course_complete()
            return

        first_course = course_list[0]
        self.current_course_url = first_course.get('url') or LSGX_DEFAULT_COURSE_URL
        self.is_complete = False

        self._open_course_home()

        self._monitor_thread = threading.Thread(
            target=self._check_course_success,
            daemon=True,
            name=f'lsgx-monitor-{self.task.id}',
        )
        self._monitor_thread.start()

        while not self.is_complete and self.is_running:
            time.sleep(1)

        logger.info('[LSGX] 课表播放流程结束 user=%s', self.task.username)

    def _open_course_home(self):
        """打开课程首页，查找并播放第一个未完成视频。"""
        if self.is_complete:
            return

        logger.info('[LSGX] 打开课程页: %s', self.current_course_url)
        self.driver.get(self.current_course_url)
        time.sleep(5)

        if self.find_and_play_first_unfinished():
            logger.info('[LSGX] 已找到未完成课程并开始播放')
            return

        logger.info('[LSGX] 没有未完成课程，标记任务完成')
        self._mark_course_complete()

    def find_and_play_first_unfinished(self) -> bool:
        """找到第一个未学完的课程并打开播放页。"""
        from selenium.webdriver.common.by import By

        try:
            ml_lists = self.driver.find_elements(By.CLASS_NAME, 'ml-list')
            if not ml_lists:
                logger.warning('[LSGX] 未找到课程列表 ml-list')
                return False

            for item in ml_lists:
                a_tag = item.find_element(By.CLASS_NAME, 'begin')
                href = a_tag.get_attribute('href')
                if not href:
                    continue

                flish_text = ''
                try:
                    flish_element = item.find_element(By.CLASS_NAME, 'flish')
                    flish_text = (flish_element.text or '').strip()
                except Exception:
                    logger.info('[LSGX] 列表项无 flish 标记，尝试直接打开: %s', href)
                    self._open_video_tab(href)
                    return True

                logger.info('[LSGX] 课程状态: %s', flish_text)
                if flish_text != '已学完':
                    self._open_video_tab(href)
                    return True

            return False
        except Exception:
            logger.exception('[LSGX] 查找未完成课程失败')
            return False

    def _mark_course_complete(self):
        """课程全部学完：设置完成标志并同步更新数据库。"""
        self.is_complete = True
        if update_task_fields(self.task, status='2'):
            logger.info('[LSGX] 任务 id=%s 课程已全部学完，状态已更新为完成', self.task.id)
        else:
            logger.error('[LSGX] 任务 id=%s 课程已学完，但状态更新失败', self.task.id)

    def _open_video_tab(self, href: str):
        """在新标签页打开视频链接并切换过去。"""
        self.driver.execute_script("window.open(arguments[0])", href)
        self.driver.switch_to.window(self.driver.window_handles[-1])
        logger.info('[LSGX] 已切换到播放页: %s', self.driver.current_url)

    def _check_course_success(self):
        """后台监控视频播放进度，结束后继续打开下一节。"""
        from selenium.webdriver.common.by import By

        sleep_time = 10
        logger.info('[LSGX] 开始监听播放进度 user=%s', self.task.username)

        while not self.is_complete and self.is_running:
            if self.check_page_error():
                logger.warning('[LSGX] 页面异常，重新打开课程页')
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
                        currentTime: video.currentTime,
                        duration: video.duration
                    };
                """, video)

                progress = 0.0
                if info['duration'] and info['duration'] > 0:
                    progress = (info['currentTime'] / info['duration']) * 100
                logger.info('[LSGX] 播放进度: %.1f%%', progress)

                if info['ended']:
                    logger.info('[LSGX] 当前视频已播完，查找下一节')
                    self._open_course_home()
                    time.sleep(5)
                elif info['paused'] and info['currentTime'] > 0:
                    logger.info('[LSGX] 视频暂停，尝试继续播放')
                    video.click()
                    time.sleep(5)
                elif not info['paused']:
                    logger.debug('[LSGX] 视频播放中')
                elif info['currentTime'] == 0:
                    logger.info('[LSGX] 视频未开始，点击播放')
                    video.click()
                    time.sleep(5)
            except Exception as exc:
                logger.warning('[LSGX] 获取视频进度失败: %s', exc)

            time.sleep(sleep_time)

        logger.info('[LSGX] 播放监控结束 user=%s', self.task.username)

    def check_page_error(self) -> bool:
        """检测页面是否出现 502/404 等错误。"""
        try:
            page_source = (self.driver.page_source or '').lower()
            error_keywords = [
                '502 bad gateway',
                'bad gateway',
                '无法访问此网站',
                '无法访问',
                '连接已重置',
                '连接超时',
                '504 gateway timeout',
                '500 internal server error',
                '页面加载失败',
                'page not found',
                '404',
            ]
            for keyword in error_keywords:
                if keyword in page_source:
                    logger.warning('[LSGX] 检测到页面错误关键词: %s', keyword)
                    return True
            return False
        except Exception as exc:
            logger.error('[LSGX] 检测页面错误异常: %s', exc)
            return True

    def _cleanup(self):
        if self.driver:
            try:
                self.driver.quit()
                logger.info('[LSGX] 浏览器已关闭')
            except Exception:
                logger.exception('[LSGX] 关闭浏览器失败')
            finally:
                self.driver = None
