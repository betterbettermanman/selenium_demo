import re
import time

from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


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
            print(f"成功打开网页: {self.driver.title}")
            time.sleep(5)  # 等待页面加载
            # 检测是否登录，未登录，让用户自己登录
            while not self.check_login():
                print("间隔10秒继续检测")
                time.sleep(10)
            # 解析页面并更新课程状态
            time.sleep(5)  # 等待页面加载
            self._parse_page_elements()
            for course in self.target_courses:
                print(f"{course['title']}: {course['complete_status']}")
                # if course['title'] == "学科教学能力提升":
                #     course['complete_status'] = False
            print(f"检测耗时：{time.time() - start_time}")
            return self.target_courses  # 返回更新后的状态
        except Exception as e:
            print(f"检查课程状态时出错: {str(e)}")
            return None

    def check_login(self):
        try:
            self.wait.until(
                EC.element_to_be_clickable((By.XPATH, ".//div[starts-with(@class,'index-module_avatar')]"))
            )
            print("已登录")
            return True
        except TimeoutException:
            print("超时未找到用户信息")
            return False
        except NoSuchElementException:
            print("      未找到登录按钮")
        except Exception as e:
            print(f"      点击播放按钮时发生错误: {str(e)}")

    def _parse_page_elements(self):
        """解析页面元素，判断课程完成状态"""
        parent_divs = self.driver.find_elements(By.XPATH, ".//div[@class='fish-spin-container']")

        if not parent_divs:
            print("未找到主要容器元素")
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
                return False
        return True

    def _check_process_equality(self, process_div):
        """检查进度条的两个数值是否相等"""
        target_divs = process_div.find_elements(By.XPATH, ".//div[count(span) = 2]")
        if not target_divs:
            return True  # 无进度条时默认视为完成

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
