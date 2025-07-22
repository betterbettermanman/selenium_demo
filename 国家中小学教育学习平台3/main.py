import os
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

from 国家中小学教育学习平台3.main_tool import TeacherTrainingChecker

course_status = None
checker = None
CHROMEDRIVER_PATH = "D:\\develop\\workspace\\mine\\selenium_demo\\driver\\138\\chromedriver.exe"


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

            print(f"成功在新标签页打开网页: {self.title}")
            time.sleep(5)  # 等待页面加载
            return True
        except Exception as e:
            print(f"打开课程页面失败: {str(e)}")
            return False

    def switch_to_main_tab(self):
        """切换到主标签页"""
        if self.main_window_handle and self.main_window_handle in self.driver.window_handles:
            self.driver.switch_to.window(self.main_window_handle)
            print("已切换到主标签页")
            return True
        print("切换到主标签页失败")
        return False

    def switch_to_current_tab(self):
        """切换到当前课程标签页"""
        if self.current_window_handle and self.current_window_handle in self.driver.window_handles:
            self.driver.switch_to.window(self.current_window_handle)
            print(f"已切换到课程标签页: {self.title}")
            return True
        print("切换到课程标签页失败")
        return False

    def close_current_tab(self):
        """关闭当前课程标签页并切换回主标签页"""
        if self.current_window_handle and self.current_window_handle in self.driver.window_handles:
            self.driver.switch_to.window(self.current_window_handle)
            self.driver.close()
            print(f"已关闭课程标签页: {self.title}")
            self.switch_to_main_tab()
            return True
        return False

    # 以下方法保持不变，省略...
    def start_automation(self):
        Thread(target=self._automate_browser, daemon=True).start()
        Thread(target=self._check_play_status, daemon=True).start()

    def _automate_browser(self):
        try:
            # 确保在当前课程标签页操作
            self.switch_to_current_tab()

            # 原有逻辑保持不变...
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
                        print("  未找到同级div元素")

            else:
                print("未找到包含<span>目录</span>的父级div元素")
                print("尝试查找包含文本'目录'的div...")

            print("视频开始播放中...")

        except Exception as e:
            print(f"发生错误: {e}")

    # 其他方法保持不变...
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
            print(f"处理过程中出错: {str(e)}")
            return 0

    def _handle_course_item(self, target_div, title):
        try:
            status_div = target_div.find_element(By.XPATH, ".//div[@class='status-icon']")
            icon = status_div.find_element(By.TAG_NAME, "i")
            icon_title = icon.get_attribute("title")
            print(f"{title}课程状态: {icon_title}")

            if icon_title in ["进行中", "未开始"]:
                target_div.click()
                print(f"点击了'{icon_title}'的课程")
                time.sleep(2)
                self._play_video()
                return True

        except Exception as e:
            print(f"未找到符合条件的i标签: {str(e)}")

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
            print("成功点击视频播放按钮")
        except TimeoutException:
            print("超时未找到vjs-big-play-button播放按钮")
        except NoSuchElementException:
            print("未找到vjs-big-play-button播放按钮")
        except Exception as e:
            print(f"点击播放按钮时发生错误: {str(e)}")

    def _click_know_button(self):
        try:
            know_button = self.wait_3.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[.//span[text()='我知道了']]")
                )
            )
            know_button.click()
            print("找到并点击了【我知道了】按钮")
        except TimeoutException:
            print("超时未找到【我知道了】按钮")
        except NoSuchElementException:
            print("未找到【我知道了】按钮")
        except Exception as e:
            print(f"点击'我知道了'按钮时发生错误: {str(e)}")

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
            print("成功点击vjs-control-bar按钮")
        except TimeoutException:
            print("超时未找到vjs-control-bar按钮")
        except NoSuchElementException:
            print("未找到vjs-control-bar按钮")
        except Exception as e:
            print(f"点击vjs-control-bar中button时发生错误: {str(e)}")

    def _set_playback_rate_2x(self):
        try:
            rate_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[@title='Playback Rate']"))
            )

            rate_button.click()
            rate_button.click()
            rate_button.click()
            print("成功设置播放速度为2倍速")
            return True

        except Exception as e:
            print(f"设置播放速度时出错: {str(e)}")
            return False

    def _check_play_status(self):
        global course_status
        sleep_num = 10
        while self.running:
            try:
                time.sleep(sleep_num)
                # 确保在当前课程标签页检查
                self.switch_to_current_tab()

                self.wait.until(EC.visibility_of_element_located((By.XPATH, "//div[text()='再学一遍']")))
                print("找到【再学一遍】标签，准备播放下一篇")

                # 切换到主标签页检查课程状态
                self.switch_to_main_tab()
                course_status = checker.check_course_status()

                # 切回当前标签页继续处理
                self.switch_to_current_tab()

                for course in course_status:
                    print(f"{course['title']}: {'已完成' if course['complete_status'] else '未完成'}")
                    if course['title'] == self.title:
                        if course['complete_status']:
                            print("已完成，准备播放下一个")
                            self.running = False
                        else:
                            print("未完成，继续播放")
                            Thread(target=self._automate_browser, daemon=True).start()
            except TimeoutException:
                print(f"超时未找到【再学一遍】标签, {sleep_num}秒后继续检查")
            except NoSuchElementException:
                print("未找到<div>再学一遍</div>标签")
            except Exception as e:
                print(f"查找'再学一遍'div时发生错误: {str(e)}")

        # 关闭当前标签页
        self.close_current_tab()
        # 启动新的视频播放
        print("启动新的视频播放")
        newVideoplay(course_status, self.driver, self.wait, self.wait_3, self.main_window_handle)

    def stop(self):
        self.running = False
        print("自动化已停止")


is_running = True


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
        print("视频已全部播放完毕，请检查...")
        driver.quit()
        is_running = False
        print("浏览器已关闭")


def init_shared_browser(head=True, user_data_dir2="chrome_user_data", chromedriver_path=None):
    user_data = os.path.join(os.getcwd(), user_data_dir2)
    os.makedirs(user_data, exist_ok=True)

    chrome_options = Options()
    if head:
        chrome_options.add_argument("--headless")  # 无头模式
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


BASE_URL = "https://basic.smartedu.cn/training/10f7b3d6-e1c6-4a2e-ba76-e2f2af4674a5"
target_courses = [
    {
        "title": "大力弘扬教育家精神",
        "url": "https://basic.smartedu.cn/teacherTraining/courseDetail?courseId=cb134d8b-ebe5-4953-8c2c-10d27b45b8dc&tag=2025%E5%B9%B4%E2%80%9C%E6%9A%91%E6%9C%9F%E6%95%99%E5%B8%88%E7%A0%94%E4%BF%AE%E2%80%9D%E4%B8%93%E9%A2%98&channelId=&libraryId=bb042e69-9a11-49a1-af22-0c3fab2e92b9&breadcrumb=2025%E5%B9%B4%E2%80%9C%E6%9A%91%E6%9C%9F%E6%95%99%E5%B8%88%E7%A0%94%E4%BF%AE%E2%80%9D%E4%B8%93%E9%A2%98&resourceId=d2bdf509-3049-4487-a985-eed857ca003a",
        "complete_status": False,
    },
    # 其他课程保持不变...
    {
        "title": "数字素养提升",
        "url": "https://basic.smartedu.cn/teacherTraining/courseDetail?courseId=0bc83fd8-4ee9-4bb2-bf9d-f858ee13ed8f&tag=2025%E5%B9%B4%E2%80%9C%E6%9A%91%E6%9C%9F%E6%95%99%E5%B8%88%E7%A0%94%E4%BF%AE%E2%80%9D%E4%B8%93%E9%A2%98&channelId=&libraryId=bb042e69-9a11-49a1-af22-0c3fab2e92b9&breadcrumb=2025%E5%B9%B4%E2%80%9C%E6%9A%91%E6%9C%9F%E6%95%99%E5%B8%88%E7%A0%94%E4%BF%AE%E2%80%9D%E4%B8%93%E9%A2%98&resourceId=4bc3d1c8-2358-4e1c-ac79-a70620ed175c",
        "complete_status": False,
    },
    {
        "title": "科学素养提升",
        "url": "https://basic.smartedu.cn/teacherTraining/courseDetail?courseId=d21a7e80-cbb4-492a-9625-d8ea8f844515&tag=2025%E5%B9%B4%E2%80%9C%E6%9A%91%E6%9C%9F%E6%95%99%E5%B8%88%E7%A0%94%E4%BF%AE%E2%80%9D%E4%B8%93%E9%A2%98&channelId=&libraryId=bb042e69-9a11-49a1-af22-0c3fab2e92b9&breadcrumb=2025%E5%B9%B4%E2%80%9C%E6%9A%91%E6%9C%9F%E6%95%99%E5%B8%88%E7%A0%94%E4%BF%AE%E2%80%9D%E4%B8%93%E9%A2%98&resourceId=7626d7f5-0d47-4f1e-998f-8a55f39043d7",
        "complete_status": False,
    }, {
        "title": "心理健康教育能力提升",
        "url": "https://basic.smartedu.cn/teacherTraining/courseDetail?courseId=e6a702f8-552d-49f6-89e7-b40ce5e445af&tag=2025%E5%B9%B4%E2%80%9C%E6%9A%91%E6%9C%9F%E6%95%99%E5%B8%88%E7%A0%94%E4%BF%AE%E2%80%9D%E4%B8%93%E9%A2%98&channelId=&libraryId=bb042e69-9a11-49a1-af22-0c3fab2e92b9&breadcrumb=2025%E5%B9%B4%E2%80%9C%E6%9A%91%E6%9C%9F%E6%95%99%E5%B8%88%E7%A0%94%E4%BF%AE%E2%80%9D%E4%B8%93%E9%A2%98&resourceId=119325b4-2204-4103-9d06-aea35ed21374",
        "complete_status": False,
    }, {
        "title": "学科教学能力提升",
        "url": "https://basic.smartedu.cn/teacherTraining/courseDetail?courseId=895caa6f-6c42-411d-ab7c-2b43facebd9f&tag=2025%E5%B9%B4%E2%80%9C%E6%9A%91%E6%9C%9F%E6%95%99%E5%B8%88%E7%A0%94%E4%BF%AE%E2%80%9D%E4%B8%93%E9%A2%98&channelId=&libraryId=bb042e69-9a11-49a1-af22-0c3fab2e92b9&breadcrumb=2025%E5%B9%B4%E2%80%9C%E6%9A%91%E6%9C%9F%E6%95%99%E5%B8%88%E7%A0%94%E4%BF%AE%E2%80%9D%E4%B8%93%E9%A2%98&resourceId=d4807973-1dd3-41ce-b647-75f60b94bd99",
        "complete_status": False,
    },
]
user_data_dir = "周婷"

if __name__ == "__main__":
    # 初始化共享浏览器，获取主窗口句柄
    driver, wait, wait_3, main_window_handle = init_shared_browser(head=False, user_data_dir2=user_data_dir,
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
