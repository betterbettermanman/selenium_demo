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

from 国家中小学教育学习平台2.main_tool import TeacherTrainingChecker


class TeacherTrainingAutomator:
    def __init__(self, chromedriver_path, user_data_dir="chrome_user_data", headless=True, title=""):
        """
        初始化教师培训课程自动播放工具

        Args:
            chromedriver_path (str): ChromeDriver的路径
            user_data_dir (str): 用户数据保存目录
            headless (bool): 是否启用无头模式
        """
        self.chromedriver_path = chromedriver_path
        self.user_data_dir = os.path.join(os.getcwd(), user_data_dir)
        self.headless = headless
        self.title = title

        # 初始化浏览器驱动和等待对象
        self.driver = None
        self.wait = None
        self.wait_3 = None

        # 创建用户数据目录
        os.makedirs(self.user_data_dir, exist_ok=True)

        # 初始化浏览器
        self._init_browser()

        # 线程控制标志
        self.running = True

    def _init_browser(self):
        """初始化浏览器配置和驱动"""
        # 设置Chrome浏览器选项
        chrome_options = Options()

        if self.headless:
            chrome_options.add_argument("--headless=new")  # 新版无头模式

        chrome_options.add_argument(f"--user-data-dir={self.user_data_dir}")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--no-sandbox")  # 解决权限问题
        chrome_options.add_argument("--disable-dev-shm-usage")  # 解决共享内存问题

        # 初始化驱动
        service = Service(self.chromedriver_path)
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

        # 创建等待对象
        self.wait = WebDriverWait(self.driver, 10)
        self.wait_3 = WebDriverWait(self.driver, 2)

    def open_course_page(self, course_url):
        """打开课程页面"""
        try:
            self.driver.get(course_url)
            print(f"成功打开网页: {self.title}")
            time.sleep(5)  # 等待页面加载
            return True
        except Exception as e:
            print(f"打开课程页面失败: {str(e)}")
            return False

    def start_automation(self):
        """开始自动化流程"""
        # 启动主流程和检查流程
        Thread(target=self._automate_browser, daemon=True).start()
        Thread(target=self._check_play_status, daemon=True).start()

    def _automate_browser(self):
        """自动化浏览器操作主逻辑"""
        try:
            # 查找包含<span>目录</span>的父级div
            parent_divs = self.driver.find_elements(By.XPATH, "//span[text()='目录']/parent::div")

            if parent_divs:
                # print(f"找到 {len(parent_divs)} 个包含<span>目录</span>的父级div")

                for i, div in enumerate(parent_divs, 1):
                    # print(f"\n--- 父级div {i}/{len(parent_divs)} ---")
                    # print(f"  class: {div.get_attribute('class')}")
                    # print(f"  id: {div.get_attribute('id')}")

                    # 获取div的所有子元素
                    # children = div.find_elements(By.XPATH, "./*")
                    # print(f"  子元素数量: {len(children)}")

                    # 查找同级div元素
                    sibling_divs = div.find_elements(By.XPATH, "./following-sibling::div | ./preceding-sibling::div")

                    if sibling_divs:
                        # print(f"  找到 {len(sibling_divs)} 个同级div元素")

                        # 遍历每个同级div
                        for j, sibling in enumerate(sibling_divs, 1):
                            # sibling_class = sibling.get_attribute("class")
                            # print(f"\n    --- 同级div {j}/{len(sibling_divs)} (class={sibling_class}) ---")

                            # 展开所有可展开的目录
                            self._click_eligible_divs()

                            # 查找课程资源项
                            target_divs = sibling.find_elements(By.XPATH,
                                                                ".//div[starts-with(@class, 'resource-item resource-item-train')]")

                            if target_divs:
                                # print(f"    找到 {len(target_divs)} 个符合条件的子div")

                                # 处理每个课程项
                                for k, target in enumerate(target_divs, 1):
                                    # target_class = target.get_attribute("class")
                                    target_text = target.text.strip()
                                    # print(f"目标div {k}: class={target_class}, text={target_text[:50]}...")

                                    # 检查课程状态并处理
                                    if self._handle_course_item(target, target_text):
                                        break  # 找到并处理一个课程后退出循环
                    else:
                        print("  未找到同级div元素")

            else:
                print("未找到包含<span>目录</span>的父级div元素")
                print("尝试查找包含文本'目录'的div...")

            print("视频开始播放中...")

        except Exception as e:
            print(f"发生错误: {e}")

    def _click_eligible_divs(self):
        """展开所有可展开的目录项"""
        success_count = 0
        try:
            # 定位所有class为fish-collapse-header的div
            target_divs = self.wait.until(
                EC.presence_of_all_elements_located(
                    (By.CLASS_NAME, "fish-collapse-header")
                )
            )
            # print(f"找到{len(target_divs)}个class为fish-collapse-header的div")

            # 遍历每个div，检查并点击可展开项
            for idx, target_div in enumerate(target_divs, 1):
                # print(f"\n--- 处理第{idx}个div ---")

                # 获取当前div的父级元素
                parent_element = target_div.find_element(By.XPATH, "..")

                # 查找父级下的所有直接子div
                parent_child_divs = parent_element.find_elements(By.XPATH, "./div")
                # print(f"父级元素的直接子div数量: {len(parent_child_divs)}")

                # 判断是否只有1个子div（可展开）
                if len(parent_child_divs) == 1:
                    # print("父级仅有1个子div，符合条件")

                    # 点击展开
                    self.wait.until(EC.element_to_be_clickable(target_div))
                    target_div.click()
                    # print("成功点击该div")
                    success_count += 1

            # print(f"\n操作完成，共成功点击{success_count}个div")
            return success_count

        except Exception as e:
            print(f"处理过程中出错: {str(e)}")
            return 0

    def _handle_course_item(self, target_div, title):
        """处理单个课程项，根据状态进行相应操作"""
        try:
            # 查找状态图标
            status_div = target_div.find_element(By.XPATH, ".//div[@class='status-icon']")
            icon = status_div.find_element(By.TAG_NAME, "i")
            icon_title = icon.get_attribute("title")
            print(f"{title}课程状态: {icon_title}")

            if icon_title in ["进行中", "未开始"]:
                # 点击课程
                target_div.click()
                print(f"点击了'{icon_title}'的课程")
                time.sleep(2)  # 等待页面切换
                self._play_video()
                return True

        except Exception as e:
            print(f"未找到符合条件的i标签: {str(e)}")

        return False

    def _play_video(self):
        """播放视频并设置播放参数"""
        # 点击视频中间播放按钮
        self._click_play_button()
        # 点击提示
        self._click_know_button()
        # 点击视频控制按钮
        self._click_control_button()
        # 设置2倍速度
        self._set_playback_rate_2x()

    def _click_play_button(self):
        """点击视频播放按钮"""
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
        """点击"我知道了"按钮"""
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
        """点击视频控制栏按钮"""
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
        """设置视频播放速度为2倍速"""
        try:
            rate_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[@title='Playback Rate']"))
            )
            # print(f"  播放速度控制按钮class: {rate_button.get_attribute('class')}")

            # 点击切换播放速度
            rate_button.click()
            rate_button.click()
            rate_button.click()
            print("成功设置播放速度为2倍速")
            return True

        except Exception as e:
            print(f"设置播放速度时出错: {str(e)}")
            return False

    def _check_play_status(self):
        """检查视频播放状态，完成后自动播放下一个"""
        global course_status
        sleep_num = 10
        while self.running:
            try:
                time.sleep(sleep_num)
                # 检查是否出现"再学一遍"按钮
                self.wait.until(EC.visibility_of_element_located((By.XPATH, "//div[text()='再学一遍']")))
                print("找到【再学一遍】标签，准备播放下一篇")
                # 检测当前视频是否播放完成，未播放完成则启动下一篇播放
                course_status = checker.check_course_status()
                for course in course_status:
                    print(f"{course['title']}: {'已完成' if course['complete_status'] else '未完成'}")
                    if course['title'] == self.title:
                        if course['complete_status']:
                            print("已完成，关闭当前页面")
                            self.driver.close()
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
        # 启动新的视频播放
        print("启动新的视频播放")
        newVideoplay(course_status)

    def stop(self):
        """停止自动化并关闭浏览器"""
        self.running = False
        if self.driver:
            self.driver.quit()
            print("浏览器已关闭")


def newVideoplay(course_status):
    # 标志变量：记录是否有课程被处理（即执行了自动化）
    has_processed = False

    for course in course_status:
        COURSE_URL = course['url']
        title = course['title']
        complete_status = course['complete_status']

        if not complete_status:
            # 标记为已处理
            has_processed = True

            # 创建自动化工具实例并执行
            automator = TeacherTrainingAutomator(
                chromedriver_path=CHROMEDRIVER_PATH,
                headless=True,
                user_data_dir=user_data_dir,
                title=title
            )

            if automator.open_course_page(COURSE_URL):
                automator.start_automation()
                break  # 处理一个未完成的课程后退出循环

    # 只有当所有课程都未处理（即has_processed仍为False）时，才打印最后一句话
    if not has_processed:
        print("视频已全部播放完毕，请检查...")


# 目标课程列表（可根据实际需求修改）
target_courses = [
    {
        "title": "大力弘扬教育家精神",
        "url": "https://basic.smartedu.cn/teacherTraining/courseDetail?courseId=cb134d8b-ebe5-4953-8c2c-10d27b45b8dc&tag=2025%E5%B9%B4%E2%80%9C%E6%9A%91%E6%9C%9F%E6%95%99%E5%B8%88%E7%A0%94%E4%BF%AE%E2%80%9D%E4%B8%93%E9%A2%98&channelId=&libraryId=bb042e69-9a11-49a1-af22-0c3fab2e92b9&breadcrumb=2025%E5%B9%B4%E2%80%9C%E6%9A%91%E6%9C%9F%E6%95%99%E5%B8%88%E7%A0%94%E4%BF%AE%E2%80%9D%E4%B8%93%E9%A2%98&resourceId=d2bdf509-3049-4487-a985-eed857ca003a",
        "complete_status": False,
    },
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

# 配置参数
CHROMEDRIVER_PATH = "D:\\develop\\workspace\\mine\\selenium_demo\\driver\\138\\chromedriver.exe"  # 替换为实际路径
BASE_URL = "https://basic.smartedu.cn/training/10f7b3d6-e1c6-4a2e-ba76-e2f2af4674a5"
user_data_dir = "chrome_user_data"
# 创建检查器实例
checker = TeacherTrainingChecker(
    chromedriver_path="D:\\develop\\workspace\\mine\\selenium_demo\\driver\\139\\chromedriver.exe",
    target_courses=target_courses,
    base_url=BASE_URL,
    user_data_dir="chrome_user_data1",
)

# 使用示例
if __name__ == "__main__":
    # 检查课程状态
    result = checker.check_course_status()
    if result:
        newVideoplay(result)
    while True:
        sleep(1)
