import os
import re
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


class TeacherTrainingChecker:
    def __init__(self, chromedriver_path, target_courses, base_url, user_data_dir="chrome_user_data"):
        """
        初始化教师培训课程检查器
        :param chromedriver_path: Chrome驱动路径
        :param target_courses: 需要检查的目标课程列表
        :param base_url: 培训首页URL
        :param user_data_dir: 用户数据保存目录
        """
        self.chromedriver_path = chromedriver_path
        self.target_courses = target_courses  # 目标课程列表
        self.base_url = base_url  # 基础页面URL
        self.user_data_dir = os.path.join(os.getcwd(), user_data_dir)
        self.driver = None  # 浏览器驱动
        self.wait = None  # 显式等待对象

        # 初始化浏览器配置
        self._init_browser()

    def _init_browser(self):
        """初始化浏览器配置及驱动"""
        # 创建用户数据目录
        os.makedirs(self.user_data_dir, exist_ok=True)

        # 配置Chrome选项
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # 无头模式
        chrome_options.add_argument(f"--user-data-dir={self.user_data_dir}")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--start-maximized")

        # 初始化驱动
        service = Service(self.chromedriver_path)
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)  # 最长等待10秒

    def check_course_status(self):
        """检查所有目标课程的完成状态"""
        try:
            # 打开目标页面
            start_time = time.time()
            self.driver.get(self.base_url)
            print(f"成功打开网页: {self.driver.title}")
            time.sleep(5)  # 等待页面加载

            # 解析页面并更新课程状态
            self._parse_page_elements()
            for course in self.target_courses:
                print(f"{course['title']}: {course['complete_status']}")
            print(f"检测耗时：{time.time() - start_time}")
            return self.target_courses  # 返回更新后的状态
        except Exception as e:
            print(f"检查课程状态时出错: {str(e)}")
            return None

    def _parse_page_elements(self):
        """解析页面元素，判断课程完成状态"""
        parent_divs = self.driver.find_elements(By.XPATH, ".//div[@class='fish-spin-container']")

        if not parent_divs:
            print("未找到主要容器元素")
            return

        # print(f"找到 {len(parent_divs)} 个主容器元素")
        for i, parent_div in enumerate(parent_divs, 1):
            # print(f"\n--- 处理第 {i} 个主容器 ---")
            self._process_parent_div(parent_div)

    def _process_parent_div(self, parent_div):
        """处理每个主容器div"""
        div_children = parent_div.find_elements(By.XPATH, "./div")
        # print(f"主容器包含 {len(div_children)} 个子元素")

        for j, child in enumerate(div_children, 1):
            # print(f"\n--- 处理第 {j} 个子元素 ---")
            # child_class = child.get_attribute('class')
            # print(f"子元素class: {child_class}")

            if self._is_div_empty(child):
                # print("子元素为空，跳过处理")
                continue

            # 检查是否为"学科教学能力提升"相关模块
            target_divs = child.find_elements(By.XPATH, ".//div[starts-with(@class, 'index-module_phase_main')]")
            if target_divs:
                self._handle_subject_teaching_module(target_divs[0])
            else:
                self._handle_other_course_modules(child)

    def _handle_subject_teaching_module(self, target_div):
        """处理学科教学能力提升模块"""
        # print("检测到学科教学能力提升模块")
        module_text = target_div.text.strip()
        # print(f"模块信息: {module_text}")

        if self._compare_hours(module_text):
            # print("需要观看视频，标记为已完成（示例逻辑）")
            self._update_course_status("学科教学能力提升", True)

    def _handle_other_course_modules(self, child_div):
        """处理其他课程模块（如大力弘扬教育家精神等）"""
        # print("检测到普通课程模块")
        study_divs = child_div.find_elements(By.XPATH, "./div")

        for study_div in study_divs:
            if self._is_div_empty(study_div):
                continue

            course_title = self._get_course_title(study_div)
            if not course_title:
                print("未提取到课程标题，跳过")
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
                # print("学习进度未完成")
                return False
        return True

    def _check_process_equality(self, process_div):
        """检查进度条的两个数值是否相等"""
        target_divs = process_div.find_elements(By.XPATH, ".//div[count(span) = 2]")
        if not target_divs:
            return True  # 无进度条时默认视为完成（根据实际需求调整）

        for div in target_divs:
            spans = div.find_elements(By.TAG_NAME, "span")
            if len(spans) != 2:
                continue

            try:
                num1 = float(re.search(r'\d+\.\d+|\d+', spans[0].text).group())
                num2 = float(re.search(r'\d+\.\d+|\d+', spans[1].text).group())
                return num1 == num2
            except (AttributeError, ValueError):
                return False  # 无法解析数值时视为未完成
        return False

    def _update_course_status(self, title, status):
        """更新目标课程的完成状态"""
        for course in self.target_courses:
            if course["title"] == title:
                course["complete_status"] = status
                # print(f'已更新课程"{title}"的状态为: {status}')
                return
        print(f'未找到课程"{title}"，无法更新状态')

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
            print(f"无法提取有效学时数值: {text}")
            return False

        try:
            return float(numbers[0]) == float(numbers[1])  # 不相等则需要学习
        except ValueError:
            print(f"学时数值转换失败: {numbers}")
            return False

    def close(self):
        """关闭浏览器驱动，释放资源"""
        if self.driver:
            self.driver.quit()
            print("浏览器已关闭")


# 示例用法
if __name__ == "__main__":
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

    # 创建检查器实例
    checker = TeacherTrainingChecker(
        chromedriver_path=CHROMEDRIVER_PATH,
        target_courses=target_courses,
        base_url=BASE_URL
    )

    # 检查课程状态
    result = checker.check_course_status()
    if result:
        print("\n最终课程状态:")
        for course in result:
            print(f"{course['title']}: {'已完成' if course['complete_status'] else '未完成'}")

    # 关闭浏览器
    # checker.close()
    while True:
        time.sleep(1)
