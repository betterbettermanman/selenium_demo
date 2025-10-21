import json
import logging
import os
import re
import time
from threading import Thread
from time import sleep

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# 初始化日志配置
logging.basicConfig(
    level=logging.INFO,  # 日志级别：DEBUG < INFO < WARNING < ERROR < CRITICAL
    format='%(asctime)s - %(levelname)s - %(message)s',  # 日志格式
    datefmt='%Y-%m-%d %H:%M:%S',  # 时间格式
    handlers=[
        # logging.FileHandler('teacher_training.log', encoding='utf-8'),  # 写入文件
        logging.StreamHandler()  # 输出到控制台
    ]
)

course_status = None
checker = None
is_running = True


class TeacherTrainingChecker:
    def __init__(self, driver, wait, target_courses, base_url):
        """
        初始化教师培训课程检查器（使用外部传入的浏览器实例）

        :param driver: 共享的浏览器驱动实例
        :param wait: 共享的显式等待对象
        :param target_courses: 需要检查的目标课程列表
        :param base_url: 培训首页URL
        """
        self.driver = driver
        self.wait = wait
        self.target_courses = target_courses  # 目标课程列表
        self.base_url = base_url  # 基础页面URL

    def check_course_status(self):
        """检查所有目标课程的完成状态"""
        try:
            # 打开目标页面
            start_time = time.time()
            self.driver.get(self.base_url)
            logging.info(f"成功打开网页: {self.driver.title}")
            time.sleep(10)  # 等待页面加载
            # 解析页面并更新课程状态
            self._parse_page_elements()
            for course in self.target_courses:
                logging.info(f"{course['title']}: {course['complete_status']}")
            logging.info(f"检测耗时：{time.time() - start_time}")
            return self.target_courses  # 返回更新后的状态
        except Exception as e:
            logging.error(f"检查课程状态时出错: {str(e)}", exc_info=True)  # exc_info打印堆栈信息
            return None

    def _parse_page_elements(self):
        """解析页面元素，判断课程完成状态"""
        parent_divs = self.driver.find_elements(By.XPATH, ".//div[@class='fish-spin-container']")

        if not parent_divs:
            logging.warning("未找到主要容器元素")
            return

        for i, parent_div in enumerate(parent_divs, 1):
            self._process_parent_div(parent_div)

    def _process_parent_div(self, parent_div):
        """处理每个主容器div"""
        div_children = parent_div.find_elements(By.XPATH, "./div")

        for j, child in enumerate(div_children, 1):
            if self._is_div_empty(child):
                continue

            # 检查是否为"学科教学能力提升"相关模块
            target_divs = child.find_elements(By.XPATH, ".//div[starts-with(@class, 'index-module_phase_main')]")
            if target_divs:
                self._handle_subject_teaching_module(target_divs[0])
            else:
                self._handle_other_course_modules(child)

    def _handle_subject_teaching_module(self, target_div):
        """处理学科教学能力提升模块"""
        module_text = target_div.text.strip()
        if self._compare_hours(module_text):
            self._update_course_status("学科教学能力提升", True)

    def _handle_other_course_modules(self, child_div):
        """处理其他课程模块（如大力弘扬教育家精神等）"""
        study_divs = child_div.find_elements(By.XPATH, "./div")

        for study_div in study_divs:
            if self._is_div_empty(study_div):
                continue

            course_title = self._get_course_title(study_div)
            if not course_title:
                logging.debug("未提取到课程标题，跳过")  # 调试信息用DEBUG
                continue

            is_complete = self._get_course_complete_status(study_div)
            self._update_course_status(course_title, is_complete)

    def _get_course_title(self, study_div):
        """从元素中提取课程标题"""
        title_divs = study_div.find_elements(By.XPATH, ".//div[starts-with(@class, 'index-module_title')]")
        if not title_divs:
            return None

        title_text = title_divs[0].text.strip()
        chinese_chars = re.findall(r'[\u4e00-\u9fa5]+', title_text)  # 提取中文标题
        return ''.join(chinese_chars) if chinese_chars else None

    def _get_course_complete_status(self, study_div):
        """判断课程是否完成"""
        process_divs = study_div.find_elements(By.XPATH, ".//div[starts-with(@class, 'index-module_process')]")
        for process_div in process_divs:
            if not self._check_process_equality(process_div):
                return False
        return True

    def _check_process_equality(self, process_div):
        """检查进度条的两个数值是否相等"""
        target_divs = process_div.find_elements(By.XPATH, ".//div[count(span) = 2]")
        if not target_divs:
            logging.debug("无进度条，默认视为完成")
            return True

        for div in target_divs:
            spans = div.find_elements(By.TAG_NAME, "span")
            if len(spans) != 2:
                continue

            try:
                num1 = float(re.search(r'\d+\.\d+|\d+', spans[0].text).group())
                num2 = float(re.search(r'\d+\.\d+|\d+', spans[1].text).group())
                return num1 == num2
            except (AttributeError, ValueError) as e:
                logging.warning(f"解析进度数值失败: {e}")
                return False
        return False

    def _update_course_status(self, title, status):
        """更新目标课程的完成状态"""
        for course in self.target_courses:
            if course["title"] == title:
                course["complete_status"] = status
                return
        logging.warning(f'未找到课程"{title}"，无法更新状态')

    def _is_div_empty(self, div_element):
        """判断div元素是否为空"""
        div_text = div_element.text.strip()
        if div_text:
            return False  # 有文本内容则不为空

        # 检查是否有子元素
        children = div_element.find_elements(By.XPATH, "./*")
        return len(children) == 0

    def _compare_hours(self, text):
        """比较学时是否相等（判断是否需要学习）"""
        numbers = re.findall(r'\d+\.\d+|\d+', text)
        if len(numbers) != 2:
            logging.warning(f"无法提取有效学时数值: {text}")
            return False

        try:
            return float(numbers[0]) == float(numbers[1])
        except ValueError as e:
            logging.error(f"学时数值转换失败: {numbers}, 错误: {e}")
            return False


class TeacherTrainingAutomator:
    def __init__(self, driver, wait, wait_3, title="", main_window_handle=""):
        """
        初始化教师培训课程自动播放工具（使用外部传入的浏览器实例）

        Args:
            driver: 共享的浏览器驱动实例
            wait: 共享的显式等待对象（10秒）
            wait_3: 共享的显式等待对象（2秒）
            title: 课程标题
            main_window_handle: 主窗口句柄
        """
        self.driver = driver
        self.wait = wait
        self.wait_3 = wait_3
        self.title = title
        self.main_window_handle = main_window_handle  # 保存主窗口句柄
        self.current_window_handle = ""  # 当前窗口句柄

        # 线程控制标志
        self.running = True

    def open_course_page(self, course_url):
        """在新标签页打开课程页面并切换到该标签页"""
        try:
            # 记录当前窗口句柄（主窗口）
            self.main_window_handle = self.driver.current_window_handle

            # 在新标签页打开课程URL
            self.driver.execute_script(f"window.open('{course_url}');")

            # 等待新标签页加载
            time.sleep(2)

            # 获取所有窗口句柄
            all_handles = self.driver.window_handles

            # 切换到新打开的标签页（最后一个）
            for handle in all_handles:
                if handle != self.main_window_handle:
                    self.driver.switch_to.window(handle)
                    self.current_window_handle = handle
                    break

            logging.info(f"成功在新标签页打开网页: {self.title}")
            time.sleep(5)  # 等待页面加载
            return True
        except Exception as e:
            logging.error(f"打开课程页面失败: {str(e)}", exc_info=True)
            return False

    def switch_to_main_tab(self):
        """切换到主标签页"""
        if self.main_window_handle and self.main_window_handle in self.driver.window_handles:
            self.driver.switch_to.window(self.main_window_handle)
            logging.info("已切换到主标签页")
            return True
        logging.warning("切换到主标签页失败")
        return False

    def switch_to_current_tab(self):
        """切换到当前课程标签页"""
        if self.current_window_handle and self.current_window_handle in self.driver.window_handles:
            self.driver.switch_to.window(self.current_window_handle)
            logging.info(f"已切换到课程标签页: {self.title}")
            return True
        logging.warning("切换到课程标签页失败")
        return False

    def close_current_tab(self):
        """关闭当前课程标签页并切换回主标签页"""
        if self.current_window_handle and self.current_window_handle in self.driver.window_handles:
            self.driver.switch_to.window(self.current_window_handle)
            self.driver.close()
            logging.info(f"已关闭课程标签页: {self.title}")
            self.switch_to_main_tab()
            return True
        return False

    def start_automation(self):
        Thread(target=self._automate_browser, daemon=True).start()
        Thread(target=self._check_play_status, daemon=True).start()

    def _automate_browser(self):
        try:
            # 确保在当前课程标签页操作
            self.switch_to_current_tab()

            parent_divs = self.driver.find_elements(By.XPATH, "//span[text()='目录']/parent::div")

            if parent_divs:
                for i, div in enumerate(parent_divs, 1):
                    sibling_divs = div.find_elements(By.XPATH, "./following-sibling::div | ./preceding-sibling::div")

                    if sibling_divs:
                        for j, sibling in enumerate(sibling_divs, 1):
                            self._click_eligible_divs()
                            target_divs = sibling.find_elements(By.XPATH,
                                                                ".//div[starts-with(@class, 'resource-item resource-item-train')]")

                            if target_divs:
                                for k, target in enumerate(target_divs, 1):
                                    target_text = target.text.strip()
                                    if self._handle_course_item(target, target_text):
                                        break
                    else:
                        logging.debug("  未找到同级div元素")

            else:
                logging.info("未找到包含<span>目录</span>的父级div元素")
                logging.info("尝试查找包含文本'目录'的div...")

        except Exception as e:
            logging.error(f"自动化浏览器操作出错: {e}", exc_info=True)

    def _click_eligible_divs(self):
        success_count = 0
        try:
            target_divs = self.wait.until(
                EC.presence_of_all_elements_located(
                    (By.CLASS_NAME, "fish-collapse-header")
                )
            )

            for idx, target_div in enumerate(target_divs, 1):
                parent_element = target_div.find_element(By.XPATH, "..")
                parent_child_divs = parent_element.find_elements(By.XPATH, "./div")

                if len(parent_child_divs) == 1:
                    self.wait.until(EC.element_to_be_clickable(target_div))
                    target_div.click()
                    success_count += 1

            return success_count

        except Exception as e:
            logging.error(f"处理可点击div时出错: {str(e)}")
            return 0

    def _handle_course_item(self, target_div, title):
        try:
            status_div = target_div.find_element(By.XPATH, ".//div[@class='status-icon']")
            icon = status_div.find_element(By.TAG_NAME, "i")
            icon_title = icon.get_attribute("title")
            logging.info(f"{title}课程状态: {icon_title}")

            if icon_title in ["进行中", "未开始"]:
                target_div.click()
                logging.info(f"点击了'{icon_title}'的课程")
                time.sleep(2)
                self._play_video()
                return True

        except Exception as e:
            logging.warning(f"未找到符合条件的i标签: {str(e)}")

        return False

    def _play_video(self):
        self._click_play_button()
        self._click_know_button()
        self._click_control_button()
        self._set_playback_rate_2x()

    def _click_play_button(self):
        try:
            play_button = self.wait.until(
                EC.element_to_be_clickable((By.CLASS_NAME, "vjs-big-play-button"))
            )
            play_button.click()
            logging.info("成功点击视频播放按钮")
        except TimeoutException:
            logging.warning("超时未找到vjs-big-play-button播放按钮")
        except NoSuchElementException:
            logging.warning("未找到vjs-big-play-button播放按钮")
        except Exception as e:
            logging.error(f"点击播放按钮时发生错误: {str(e)}")

    def _click_know_button(self):
        try:
            know_button = self.wait_3.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[.//span[text()='我知道了']]")
                )
            )
            know_button.click()
            logging.info("找到并点击了【我知道了】按钮")
        except TimeoutException:
            logging.debug("超时未找到【我知道了】按钮")  # 非关键按钮，用DEBUG
        except NoSuchElementException:
            logging.debug("未找到【我知道了】按钮")
        except Exception as e:
            logging.error(f"点击'我知道了'按钮时发生错误: {str(e)}")

    def _click_control_button(self):
        try:
            control_bar = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "vjs-control-bar"))
            )
            target_button = control_bar.find_element(
                By.XPATH, ".//div//button"
            )
            self.wait.until(EC.element_to_be_clickable(target_button))
            target_button.click()
            logging.info("成功点击vjs-control-bar按钮")
        except TimeoutException:
            logging.warning("超时未找到vjs-control-bar按钮")
        except NoSuchElementException:
            logging.warning("未找到vjs-control-bar按钮")
        except Exception as e:
            logging.error(f"点击vjs-control-bar中button时发生错误: {str(e)}")

    def _set_playback_rate_2x(self):
        try:
            rate_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[@title='Playback Rate']"))
            )

            rate_button.click()
            rate_button.click()
            rate_button.click()
            logging.info("成功设置播放速度为2倍速")
            return True

        except Exception as e:
            logging.error(f"设置播放速度时出错: {str(e)}")
            return False

    def _check_play_status(self):
        global course_status
        sleep_num = 60
        while self.running:
            try:
                time.sleep(sleep_num)
                # 确保在当前课程标签页检查
                self.switch_to_current_tab()

                self.wait.until(EC.visibility_of_element_located((By.XPATH, "//div[text()='再学一遍']")))
                logging.info("找到【再学一遍】标签，准备播放下一篇")

                # 切换到主标签页检查课程状态
                self.switch_to_main_tab()
                course_status = checker.check_course_status()

                # 切回当前标签页继续处理
                self.switch_to_current_tab()

                for course in course_status:
                    logging.info(f"{course['title']}: {'已完成' if course['complete_status'] else '未完成'}")
                    if course['title'] == self.title:
                        if course['complete_status']:
                            logging.info("已完成，准备播放下一个")
                            self.running = False
                        else:
                            logging.info("未完成，继续播放")
                            Thread(target=self._automate_browser, daemon=True).start()
            except TimeoutException:
                logging.info(f"超时未找到【再学一遍】标签, {sleep_num}秒后继续检查")
            except NoSuchElementException:
                logging.warning("未找到<div>再学一遍</div>标签")
            except Exception as e:
                logging.error(f"查找'再学一遍'div时发生错误: {str(e)}")

        # 关闭当前标签页
        self.close_current_tab()
        # 启动新的视频播放
        logging.info("启动新的视频播放")
        newVideoplay(course_status, self.driver, self.wait, self.wait_3, self.main_window_handle)

    def stop(self):
        self.running = False
        logging.info("自动化已停止")


def newVideoplay(course_status, driver, wait, wait_3, main_window_handle):
    global is_running
    has_processed = False

    for course in course_status:
        COURSE_URL = course['url']
        title = course['title']
        complete_status = course['complete_status']

        if not complete_status:
            has_processed = True

            # 使用共享的浏览器实例创建自动化工具，传入主窗口句柄
            automator = TeacherTrainingAutomator(
                driver=driver,
                wait=wait,
                wait_3=wait_3,
                title=title,
                main_window_handle=main_window_handle
            )

            if automator.open_course_page(COURSE_URL):
                automator.start_automation()
                break

    if not has_processed:
        logging.info("视频已全部播放完毕，请检查...")
        # 打开学时页面，进行截图操作，并保存下来
        save_play_result(driver)
        driver.quit()
        is_running = False
        logging.info("浏览器已关闭")


def save_play_result(driver):
    try:
        # 2. 打开指定页面
        url = BASE_URL  # 👈 替换为你想打开的网址
        driver.get(url)

        # 3. 等待页面加载完成（可选：等待某个元素出现）
        # 例如：等待 body 加载
        # wait = WebDriverWait(driver, 10)
        # wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # 可选：等待几秒确保动态内容加载（如 JS 渲染的内容）
        time.sleep(5)

        # 4. 截图并保存到本地
        screenshot_path = "学时截图.png"  # 保存的文件名
        driver.save_screenshot(screenshot_path)
        # 或者使用：
        # driver.get_screenshot_as_file(screenshot_path)

        logging.info(f"✅ 页面截图已保存至: {screenshot_path}")

    except Exception as e:
        logging.error(f"❌ 操作失败: {e}")


def init_shared_browser(head=True, user_data_dir2="chrome_user_data", chromedriver_path=None):
    user_data = os.path.join(os.getcwd(), user_data_dir2)
    os.makedirs(user_data, exist_ok=True)
    logging.debug(f"Chrome用户数据目录: {user_data}")

    chrome_options = Options()
    if head:
        chrome_options.add_argument("--headless")  # 无头模式
        logging.debug("启用无头模式")
    chrome_options.add_argument(f"--user-data-dir={user_data}")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--start-maximized")

    chromedriver_path = chromedriver_path
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # 获取主窗口句柄
    main_window_handle = driver.current_window_handle

    wait = WebDriverWait(driver, 10)
    wait_3 = WebDriverWait(driver, 2)

    return driver, wait, wait_3, main_window_handle  # 返回主窗口句柄


def check_login():
    driver, wait, _, _ = init_shared_browser(head=False, user_data_dir2=user_data_dir,
                                             chromedriver_path=CHROMEDRIVER_PATH)
    driver.get(BASE_URL)
    logging.info(f"成功打开网页: {driver.title}")
    time.sleep(5)  # 等待页面加载
    while True:
        try:
            wait.until(
                EC.element_to_be_clickable((By.XPATH, ".//div[starts-with(@class,'index-module_avatar')]"))
            )
            logging.info("已登录")
            break
        except TimeoutException:
            logging.warning("超时未找到用户信息,间隔10秒继续检测")
            time.sleep(10)
        except NoSuchElementException:
            logging.warning("      未找到登录按钮")
        except Exception as e:
            logging.error(f"      登录检测时发生错误: {str(e)}")

    driver.close()


def auto_login():
    driver.get("https://auth.smartedu.cn/uias/login")


def read_json_config(config_path):
    """
    读取JSON配置文件
    :param config_path: 配置文件路径
    :return: 配置字典，如果出错返回None
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(config_path):
            print(f"错误：配置文件 {config_path} 不存在")
            return None

        # 打开并读取JSON文件
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)  # 自动转换为Python字典/列表
            return config

    except json.JSONDecodeError as e:
        print(f"错误：JSON格式解析失败 - {str(e)}")
        return None
    except Exception as e:
        print(f"读取配置文件出错 - {str(e)}")
        return None


config_json = read_json_config("config.json")

# 需要修改的地方
CHROMEDRIVER_PATH = "chromedriver.exe"
BASE_URL = config_json["base_url"]
target_courses = config_json["target_courses"]

user_data_dir = "user_data_dir"

if __name__ == "__main__":
    check_login()
    # 初始化共享浏览器，获取主窗口句柄
    driver, wait, wait_3, main_window_handle = init_shared_browser(head=True, user_data_dir2=user_data_dir,
                                                                   chromedriver_path=CHROMEDRIVER_PATH)
    checker = TeacherTrainingChecker(
        driver=driver,
        wait=wait,
        target_courses=target_courses,
        base_url=BASE_URL
    )

    result = checker.check_course_status()
    if result:
        course_status = result
        # 传入主窗口句柄
        newVideoplay(course_status, driver, wait, wait_3, main_window_handle)

    while is_running:
        sleep(1)
