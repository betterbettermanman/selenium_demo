import os
import random
import re
import sys
import threading
import time
from urllib.parse import urlparse, parse_qs

import ddddocr
import requests
from flask import current_app
from loguru import logger
from selenium import webdriver
from selenium.common import TimeoutException, NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

import json
from models import ScgbTask, db
from server import create_app

# 初始化ocr识别器
ocr = ddddocr.DdddOcr()


def setup_info_only_logger():
    # 移除默认的控制台输出（避免重复日志）
    logger.remove()

    # 添加新的控制台输出，设置级别为INFO
    # level="INFO" 表示只处理INFO及以上级别的日志
    logger.add(
        sys.stdout,
        level="INFO",
        # format="{time:YYYY-MM-DD HH:mm:ss} - Thread:{extra[thread_id]} - {level} - {message}",
    )

    # 可选：添加文件输出，同样限制级别为INFO
    logger.add(
        "logs/info_logs.log",
        level="INFO",
        rotation="100 MB",  # 日志文件大小限制
        format="{time:YYYY-MM-DD HH:mm:ss} - {level} - {message}"
    )


# 初始化日志配置
setup_info_only_logger()


def parse_courseid_by_regex(url):
    """从URL中解析courseId"""
    pattern = r'courseId=([^&#]+)'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None


def recognize_verify_code(image_path=None, image_url=None):
    """使用ddddocr识别验证码"""
    try:
        if image_path:
            with open(image_path, 'rb') as f:
                image_data = f.read()
        elif image_url:
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            image_data = response.content
        else:
            logger.warning("未提供验证码图片路径或URL")
            return None

        result = ocr.classification(image_data)
        logger.info(f"验证码识别结果: {result}")
        return result
    except Exception as e:
        logger.error(f"验证码识别失败: {str(e)}")
        return None


# 从url中提取id
def extract_id_from_url(url):
    # 解析 URL 结构
    parsed_url = urlparse(url)

    # 提取哈希（#）后的部分（包含路径和参数）
    hash_part = parsed_url.fragment

    # 从哈希部分中分离出查询参数（?后面的内容）
    # 先找到 ? 的位置，截取参数部分
    query_start = hash_part.find('?')
    if query_start == -1:
        return None  # 没有查询参数

    query_string = hash_part[query_start + 1:]

    # 解析查询参数为字典
    query_params = parse_qs(query_string)

    # 提取 id 参数（parse_qs 返回的值是列表，取第一个元素）
    id_value = query_params.get('id', [None])[0]
    return id_value


def extract_number_from_string(s):
    """从字符串中提取数字（支持整数和小数）"""
    # 使用正则表达式匹配数字（包括整数、小数）
    match = re.search(r'\d+\.?\d*', s)
    if match:
        # 转换为浮点数以便比较
        return float(match.group())
    return None  # 未找到数字


def compare_hours_str(hours_str):
    # logger.info('hours_str:',hours_str)
    # 按照 '/' 分割字符串
    parts = hours_str.split('/')

    # 检查分割后是否正好有两部分
    if len(parts) != 2:
        print(f"格式错误：{hours_str} - 无法按照 '/' 分割为两部分")
        return False

    # 去除两边的空白字符
    part1 = parts[0].strip()
    part2 = parts[1].strip()

    # 打印分割后的结果
    # print(f"分割后：左部分='{part1}', 右部分='{part2}'")

    # 判断是否相等
    is_equal = (extract_number_from_string(part1) == extract_number_from_string(part2))
    # print(f"两部分是否相等：{is_equal}\n")

    return is_equal


def open_init_browser(username):
    logger.info(f"{username}开始初始化浏览器文件夹")
    # 创建保存用户数据的目录
    user_data_dir = os.path.join(os.getcwd(), "data", username)
    os.makedirs(user_data_dir, exist_ok=True)
    logger.debug(f"用户数据目录: {user_data_dir}")

    # 设置 Chrome 浏览器选项
    chrome_options = Options()
    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")  # 保存用户数据
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    # 指定 ChromeDriver 的路径
    chromedriver_path = "chromedriver.exe"

    # 使用 Service 类来指定驱动路径
    service = Service(chromedriver_path)

    # 初始化 Chrome 浏览器驱动
    driver = webdriver.Chrome(service=service, options=chrome_options)
    logger.info(f"{user_data_dir}浏览器文件夹初始化成功")
    driver.get("https://web.scgb.gov.cn/#/index")
    time.sleep(7200)


# 清空文件夹
def remove_browser_dir(username):
    user_data_dir = os.path.join(os.getcwd(), "data", username)
    try:
        os.rmdir(user_data_dir)
        logger.info(f"文件夹 {user_data_dir} 删除成功")
    except OSError as e:
        logger.info(f"删除空文件夹失败: {e}")


class TeacherTrainingChecker:
    def __init__(self, id, username, password, isHead, no_play_videos=None, class_id="", courses=None):
        """
        初始化教师培训课程检查器（使用外部传入的浏览器实例）

        :param wait: 共享的显式等待对象
        :param target_courses: 需要检查的目标课程列表
        :param base_url: 培训首页URL
        """
        if no_play_videos is None:
            no_play_videos = []
        self.is_headless = isHead
        self.user_data_dir = username
        self.id = id
        self.nickName = ""
        self.organName = ""
        self.username = username
        self.password = password
        self.current_course_id = ""
        # 是否运行 0：未运行，1：运行中，2：接受验证码
        self.is_running = "0"
        self.headers = {
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'X-Access-Token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2NDIxMTQ5MjAsInVzZXJuYW1lIjoiYWRtaW4ifQ.-HyWQh6A9y6ZmclS7ltpBu-GFb3liVk5VVj6laavOg0',
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'Accept': '*/*',
            'Host': 'www.cdjxjy.com',
            'Connection': 'keep-alive',
            "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJPcmdhbklkIjoiMDE5ODMxMDAtZGI1Ni03MWNjLWI2NGQtNmY4NGQwYWM3MGQwIiwiQ2xpZW50VHlwZSI6IiIsIk9yZ2FuTmFtZSI6IuWvjOeJm-Wwj-WtpiIsIkFzc2Vzc1R5cGUiOjAsIlVzZXJJZCI6IjAxOTgzYzdmLTMxZWItN2I0NC1hNzRmLWZhZTRiYjliNmI3YiIsIk9yZ2FuUGF0aCI6IjJjNTUxYTczLTViNDEtMTFlZC05NTFhLTBjOWQ5MjY1MDRmMyxjMWJmNjBjNS01YjQxLTExZWQtOTUxYS0wYzlkOTI2NTA0ZjMsMDE4YTQ1YmMtZWVmNi03NzFmLTkzZGEtMzU2NDIyYzRkNTAyLGNkNGFlNWI0LTQxOTctNGUzNC1iNGVmLWNiMmVkNzg4YzNmYiwwMThjYWFhMy1lZDMzLTdkNDAtYmFhMy1iZjRlYTU3NzQ2ZTAsMDE5ODI2NDAtY2Y0YS03ZmQ1LWFiNDMtNzk4M2VmMDJiNmYwLDAxOTgzMTAwLWRiNTYtNzFjYy1iNjRkLTZmODRkMGFjNzBkMCIsImV4cCI6MTc1MzQ2MzE2MCwidXNlcm5hbWUiOiI3YTE1ZTZmNjNlYzM5YmM5In0.oQd_HlYVRr2_vC3U2DP31Vw62oYOgOLgWFD8n9KoEnI"
        }
        # 默认检测时间，当时间重复3次，说明观看异常，重新打开页面进行观看
        self.sleep_time = 10
        self.sleep_time_num = 0
        # 全局变量存储当前课程ID和主页面句柄
        self.main_window_handle = None  # 用于存储主页面的句柄
        # 指定视频课程
        self.specify_video = []
        # 是否必修
        self.is_must = False
        # 是否完成全部视频
        self.is_complete = False
        # 不看的视频id
        self.no_play_videos = no_play_videos
        # 班级id
        if class_id:
            self.class_id = class_id
        else:
            self.class_id = ""
        # 最大次数，超过就将当前课程放入不需要播放列表
        self.error_cursor_id = ""
        self.error_cursor_id_num = 0
        # 初始化驱动路径
        logger.info("初始化驱动路径")
        self.driver = self.init_browser()
        # 空course_id的循环次数
        self.null_course_id_num = 0
        # 特定课程集合
        self.courses = courses
        # 是否登陆状态
        self.is_login = False

    def get_current_course(self):
        for course in self.courses:
            # 0 未看完，1看完
            if course['status'] != '1':
                return course
        return ""

    def get_local_storage_value(self, key, driver1):
        """从localStorage中获取指定键的值"""
        try:
            value = driver1.execute_script(f"return window.localStorage.getItem('{key}');")
            return value
        except Exception as e:
            logger.error(f"获取localStorage值失败: {str(e)}")
            return None

    def is_element_exist(self, locator, timeout=10):
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False

    def open_home(self):
        if not self.is_running == "1":
            return
        # 判断是否有固定课程集合
        if self.courses:
            course = self.get_current_course()
            if not course:
                logger.info("课程已全部学完")
                self.is_complete = True
                self.is_running = "0"
                return
            base_url = "https://web.scgb.gov.cn/#/index"
            self.driver.get(f"{base_url}")
            time.sleep(2)
            # 必修
            new_url = f"https://web.scgb.gov.cn/#/course?id={course['id']}&className="
            logger.info(f"{self.nickName}打开页面：{new_url}")
            self.driver.get(f"{new_url}")
            # 解析课程ID
            time.sleep(2)
            self.close_model2()
            if self.is_element_exist((By.CLASS_NAME, "vjs-big-play-button")):
                try:
                    required_div = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((
                            By.CLASS_NAME,
                            "vjs-big-play-button"
                        ))
                    )
                    required_div.click()
                except Exception as e:
                    logger.info(f"{self.nickName}❌ 元素不可点击（可能被遮挡、隐藏、禁用或未加载）")
                    # logger.info(f"异常不处理:{str(e)}")
            self.current_course_id = course['id']
            logger.info(f"{self.nickName}当前课程ID: {self.current_course_id}")
        else:
            # 必修
            if self.is_must:
                logger.info(f"{self.nickName}进行必修学习")
                self.open_home_detail("必修")
                return
            logger.info(f"{self.nickName}进行选修学习")
            self.open_home_detail("选修")

    def course_list(self):
        url = "https://api.scgb.gov.cn/api/services/app/class/app/getClassSumPageListByUserId?maxResultCount=8&skipCount=0&pageIndex=1&studyStatus=2"
        max_retries = 3  # 最大重试次数
        retry_delay = 5  # 每次重试间隔 5 秒

        for attempt in range(max_retries + 1):  # 尝试次数 = 1次正常 + max_retries次重试
            try:
                response = requests.get(url=url, headers=self.headers, timeout=10)  # 建议添加超时
                response.raise_for_status()  # 检查 HTTP 错误状态码 (如 404, 500)
                response_json = response.json()
                return response_json
            except requests.exceptions.RequestException as e:
                logger.error(f"{self.nickName} 第 {attempt + 1} 次请求失败: {str(e)}")
            except KeyError as e:
                logger.error(
                    f"{self.nickName} JSON 响应缺少关键字段 {str(e)}: {response.text if 'response' in locals() else 'No response'}")
            except Exception as e:
                logger.error(f"{self.nickName} 解析响应或处理数据时发生未知错误: {str(e)}")

            # 如果不是最后一次尝试，则等待后重试
            if attempt < max_retries:
                logger.info(f"{self.nickName} 将在 {retry_delay} 秒后重试...")
                time.sleep(retry_delay)
            else:
                logger.error(f"{self.nickName} 已达到最大重试次数 ({max_retries})，放弃请求。")
                # 可以选择返回 False 结束，或返回 True 继续（根据你的业务逻辑）
                # 这里假设失败后不再继续，结束任务
                self.is_complete = False
                self.is_running = "0"
                return False  # 或者 return True，视情况而定

        # 理论上不会执行到这里，为了代码完整性
        return False

    def open_home_detail(self, label):
        try:
            logger.info(f"{self.nickName}进行{label}学习")
            # 必修
            self.driver.get(f"https://web.scgb.gov.cn/#/myClass?id={self.class_id}&collected=1")
            time.sleep(1)
            # 检测是否存在提示框
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.invisibility_of_element_located((By.CLASS_NAME, "el-loading-spinner")))
                # 等待 class 为 'el-loading-spinner' 的元素变得不可见
                logger.info(f"{self.nickName}等待 class 为 'el-loading-spinner' 的元素变得不可见")
                self.close_model3("ivu-modal-confirm-footer")
            except Exception as e:
                logger.info(e)
                # 如果未找到或出现其他异常，则跳过
                logger.info(f"{self.nickName}如果未找到或出现其他异常，则跳过")
                pass
            # time.sleep(2)
            # 等待包含class为num-info的div元素加载完成
            required_div = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    f"//div[text()=' {label} ']"
                ))
            )
            # 等待 class 为 'el-loading-spinner' 的元素变得不可见，最多20秒
            WebDriverWait(self.driver, 20).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "el-loading-spinner")))
            required_div.click()
            time.sleep(1)
            is_next_page = self.judge_is_next_page2()
            while is_next_page:
                # 如果不存在，检查是否只存在"ivu-page-next"类的元素
                try:
                    element = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "ivu-page-next"))
                    )
                    logger.info(f"{self.nickName}存在 下一页 的元素，点击")
                    # 等待 class 为 'el-loading-spinner' 的元素变得不可见
                    logger.info("等待 class 为 'el-loading-spinner' 的元素变得不可见")
                    WebDriverWait(self.driver, 20).until(
                        EC.invisibility_of_element_located((By.CLASS_NAME, "el-loading-spinner")))
                    element.click()
                    time.sleep(2)
                    is_next_page = self.judge_is_next_page2()
                except Exception as e:
                    logger.error(f"{self.nickName}两个类名的元素都不存在")

        except TimeoutException:
            print("超时：未找到class为'course-list'的元素")
        except Exception as e:
            print(f"发生错误：{str(e)}")

    def judge_is_next_page2(self):
        logger.info(f"{self.nickName}判断是否有可以播放的视频")
        required_div = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((
                By.CLASS_NAME,
                "course-list"
            ))
        )
        # 获取必修列表，然后进行播放
        direct_child_divs = required_div.find_elements(
            By.XPATH, "./div"  # 注意开头的点表示当前节点（required_div）
        )
        # 遍历每个子级div
        for index, child_div in enumerate(direct_child_divs, 1):
            try:
                # 获取当前子div中所有的span标签
                span_elements = child_div.find_elements(By.TAG_NAME, "span")

                if span_elements:
                    # print(f"第{index}个div内的span标签值：")
                    if not compare_hours_str(span_elements[3].text.strip()):
                        # 确保元素可点击后再点击
                        WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable(child_div)
                        )

                        # 记录当前所有标签页句柄（点击前）
                        handles_before_click = self.driver.window_handles
                        # 等待 class 为 'el-loading-spinner' 的元素变得不可见，最多20秒
                        WebDriverWait(self.driver, 20).until(
                            EC.invisibility_of_element_located((By.CSS_SELECTOR, "div.el-loading-mask.is-fullscreen")))
                        # 点击a标签打开新页面,所有点击之前判断，是否存在蒙层
                        child_div.click()

                        WebDriverWait(self.driver, 10).until(
                            EC.number_of_windows_to_be(len(handles_before_click) + 1))

                        # 获取所有标签页句柄（点击后）
                        all_handles = self.driver.window_handles

                        # 找到新打开的标签页句柄
                        new_handle = [h for h in all_handles if h not in handles_before_click][0]

                        # 切换到新标签页以获取URL
                        self.driver.switch_to.window(new_handle)
                        new_page_url = self.driver.current_url

                        # 检查cursor_id是否为目标值（这里假设目标值是"special_cursor_id"）
                        if extract_id_from_url(new_page_url) in self.no_play_videos:
                            # 如果是目标cursor_id，关闭新页面
                            self.driver.close()
                            logger.info(f"{self.nickName}检测到目标cursor_id，已关闭新页面")

                            # 切换回原来的页面
                            self.driver.switch_to.window(handles_before_click[0])
                            continue

                        # 如果不是目标cursor_id，继续处理
                        # 关闭之前的标签页（除了新打开的页面）
                        for handle in all_handles:
                            if handle != new_handle:
                                self.driver.switch_to.window(handle)
                                self.driver.close()
                                logger.debug(f"已关闭标签页: {handle}")

                        # 切换到新打开的标签页
                        self.driver.switch_to.window(new_handle)
                        logger.debug(f"{self.nickName}已切换到新标签页: {new_handle}")
                        # 解析课程ID
                        self.current_course_id = extract_id_from_url(new_page_url)
                        logger.info(f"{self.nickName}当前课程ID: {self.current_course_id}")
                        return False  # 找到未播放视频，返回False停止翻页

            except Exception as e:
                print(f"处理第{index}个div时出错：{str(e)}\n")

        logger.info(f"{self.nickName}未找到需要播放的视频，点击下一页")
        return True  # 所有视频已完成，返回True继续翻页

    def check_study_time2(self):
        # 自定义课程检测
        if self.courses:
            logger.info(f"{self.nickName} 判断自定义课程是否完成")
            num = 0
            for course in self.courses:
                if course['status'] == "0":
                    logger.info(f"{self.nickName}自定义课程全部未学习完成,进度：{num}/{len(self.courses)}")
                    requiredPeriod = f"进度：{num}/{len(self.courses)}"
                    ScgbTask.update_by_id(self.id, required_period=requiredPeriod)
                    return True
                else:
                    num = num + 1
            logger.info("自定义课程全部学习完成")
            return False
        # 官方课程检测
        else:
            logger.info(f"{self.nickName} 判断官方课程检测是否完成")
            url = "https://api.scgb.gov.cn/api/services/app/class/app/getClassDetailByUserId?classId=" + self.class_id

            max_retries = 3  # 最大重试次数
            retry_delay = 5  # 每次重试间隔 5 秒

            for attempt in range(max_retries + 1):  # 尝试次数 = 1次正常 + max_retries次重试
                try:
                    response = requests.get(url=url, headers=self.headers, timeout=10)  # 建议添加超时
                    response.raise_for_status()  # 检查 HTTP 错误状态码 (如 404, 500)
                    response_json = response.json()

                    # 发送学习时长结果
                    required_hours = round(int(response_json['result']['requiredPeriod']) / 3600, 2)
                    elective_hours = round(int(response_json['result']['electivePeriod']) / 3600, 2)
                    self.send_check_result(str(required_hours), str(elective_hours))
                    # 更新数据库
                    requiredPeriod = f"必修：{str(required_hours)}   选修：{str(elective_hours)}"
                    ScgbTask.update_by_id(self.id, required_period=requiredPeriod)
                    # 判断学习任务状态
                    if int(response_json['result']['electivePeriod']) < int(
                            response_json['result']['classElectiveTimes']) * 60 * 60:
                        logger.info(f"{self.nickName} 准备选修")
                        self.is_must = False
                        return True
                    elif int(response_json['result']['requiredPeriod']) < int(
                            response_json['result']['classTimes']) * 60 * 60:
                        logger.info(f"{self.nickName} 准备必修")
                        self.is_must = True
                        return True
                    else:
                        logger.info(f"{self.nickName} 选修和必修已全部学完，结束课程")
                        self.is_complete = True
                        self.is_running = "0"
                        return False

                except requests.exceptions.RequestException as e:
                    logger.error(f"{self.nickName} 第 {attempt + 1} 次请求失败: {str(e)}")
                except KeyError as e:
                    logger.error(
                        f"{self.nickName} JSON 响应缺少关键字段 {str(e)}: {response.text if 'response' in locals() else 'No response'}")
                except Exception as e:
                    logger.error(f"{self.nickName} 解析响应或处理数据时发生未知错误: {str(e)}")

                # 如果不是最后一次尝试，则等待后重试
                if attempt < max_retries:
                    logger.info(f"{self.nickName} 将在 {retry_delay} 秒后重试...")
                    time.sleep(retry_delay)
                else:
                    logger.error(f"{self.nickName} 已达到最大重试次数 ({max_retries})，放弃请求。")
                    # 可以选择返回 False 结束，或返回 True 继续（根据你的业务逻辑）
                    # 这里假设失败后不再继续，结束任务
                    self.is_complete = False
                    self.is_running = "0"
                    return False  # 或者 return True，视情况而定

            # 理论上不会执行到这里，为了代码完整性
            return False

    def send_check_result(self, requiredPeriod, electivePeriod, mentioned_list=None, mentioned_mobile_list=None):
        content = f"{self.nickName}学习进度：必修:{requiredPeriod};选修:{electivePeriod}"
        logger.info(content)
        data = {
            "msgtype": "text",
            "text": {
                "content": content,
                "mentioned_list": mentioned_list or [],
                "mentioned_mobile_list": mentioned_mobile_list or []
            }
        }
        """通用发送方法"""
        try:
            response = requests.post(
                url="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=edf2d6ba-55f1-48da-a5ce-619b329a1ec8",
                data=json.dumps(data),
                headers={"Content-Type": "application/json"}
            )
            result = response.json()
            if result.get("errcode") != 0:
                logger.info(f"发送失败：{result.get('errmsg')}")
            else:
                logger.info(f"{self.nickName}发送成功")
        except Exception as e:
            logger.error(f"请求异常：{str(e)}")

    def check_course_success(self):
        logger.info(f"{self.nickName}开始检验课程是否完成")
        sleep_time = 10
        call_login = False
        while self.is_running == "1":
            # 检验登陆状态是否失效，如果失效，退出当前课程
            if not self.check_login_status():
                logger.info(
                    f"{self.nickName}检验登陆状态是否失效，如果失效，退出当前课程检验登陆状态是否失效，如果失效，退出当前课程")
                self.is_login = False
                self.is_running = "0"
            # id为空超过10次循环，关闭当前线程 ，重启一个
            if self.null_course_id_num >= 10:
                logger.info(f"{self.nickName}id为空超过10次循环，关闭当前线程 ，重启一个")
                self.is_running = "0"
            if self.error_cursor_id_num == 2:
                logger.error(f"{self.nickName}错误播放超过数超过6次，将当前课程放入不播放列表")
                task = ScgbTask.query.get_or_404(self.id)
                task.no_play_videos.append(self.error_cursor_id)
                ScgbTask.update_by_id(self.id, no_play_videos=task.no_play_videos)
                self.current_course_id = ""
                self.error_cursor_id_num = 0
                threading.Thread(target=self.open_home, daemon=True).start()
                time.sleep(10)
                continue
            if self.sleep_time_num == 1:
                logger.error(f"{self.nickName}睡眠重复次数超过1次，重新打开页面")
                # self.is_login(self.driver)
                logger.info(f"{self.nickName}记录错误课程重试次数")
                if self.error_cursor_id == self.current_course_id:
                    self.error_cursor_id_num = self.error_cursor_id_num + 1
                else:
                    self.error_cursor_id = self.current_course_id
                    self.error_cursor_id_num = 0
                logger.info(
                    f"{self.nickName}error_cursor_id:{self.error_cursor_id},error_cursor_id_num:{self.error_cursor_id_num}")
                self.current_course_id = ""
                self.sleep_time_num = 0
                threading.Thread(target=self.open_home, daemon=True).start()
                time.sleep(10)
                continue
            if not self.current_course_id:
                logger.info(f"{self.nickName}课程id为空，间隔10秒，继续检测")
                time.sleep(10)
                self.null_course_id_num = self.null_course_id_num + 1
                continue
            check_play_success_url = "https://api.scgb.gov.cn/api/services/app/course/app/getCourseDetailByUserId?"
            logger.info(f"{self.nickName}检测课程id: {self.current_course_id}")
            if self.courses:
                payload = {"courseId": self.current_course_id}
            else:
                payload = {"courseId": self.current_course_id, "classId": self.class_id}
            try:
                course_detail = requests.post(check_play_success_url, headers=self.headers, json=payload)
                if course_detail.status_code == 401:
                    logger.info("登陆过期，退出运行")
                    self.is_login = False
                    self.is_running = "0"
                    continue
                detail_json = course_detail.json()["result"]
                # logger.info(f"{self.nickName}的【{self.current_course_id}】课程详情: {detail_json}")
                if detail_json["totalPeriod"] <= detail_json["watchTimes"]:
                    if self.check_study_time2():
                        # 播放下一个视频
                        logger.info(
                            f"{self.nickName}的【{self.current_course_id}】已观看完成，但未完成学时，继续播放下一个视频")
                        if self.courses:
                            # 更新数据库
                            task = ScgbTask.query.get_or_404(self.id)
                            new_task_courses = []
                            for c in task.courses:
                                if c['id'] == self.current_course_id:
                                    c['status'] = "1"
                                new_task_courses.append(c)
                            ScgbTask.update_by_id(self.id, courses=new_task_courses)
                            self.courses = new_task_courses
                        self.current_course_id = ""
                        threading.Thread(target=self.open_home, daemon=True).start()
                        sleep_time = 40
                    else:
                        logger.info("已全部观看完成，退出程序")
                        self.is_running = "0"
                        break
                else:
                    logger.info(f"{self.nickName}的【{self.current_course_id}】未观看完成")
                    if not call_login:
                        total_period = detail_json['totalPeriod']
                        watch_times = detail_json['watchTimes']
                        logger.info(f"{self.nickName}totalPeriod: {total_period}, watchTimes: {watch_times}")
                        sleep_time = (int(total_period) - int(watch_times))
                        # 间隔时间最小30秒，最大为：10分钟-20分钟以内的随机值
                        if sleep_time < 30:
                            sleep_time = 30
                        # logger.info(f"{self.nickName}记录睡眠值，以及重复次数")
                        if self.sleep_time == sleep_time:
                            self.sleep_time_num = self.sleep_time_num + 1
                        else:
                            self.sleep_time = sleep_time
                            self.sleep_time_num = 0
                    else:
                        logger.info(f"{self.nickName}重新登录，重新打开页面")
                        self.current_course_id = ""
                        threading.Thread(target=self.open_home, daemon=True).start()
                        sleep_time = 30
                call_login = False
            except TimeoutException:
                logger.error("链接超时")
                sleep_time = 10
            except Exception as e:
                logger.error(f"{self.nickName}检测课程状态失败: {str(e)}")
                # self.is_login()
                call_login = True
                sleep_time = 20

            self.sleep(sleep_time)

    def check_login_status(self):
        store = self.get_local_storage_value("store", self.driver)
        if store:
            try:
                store_json = json.loads(store)
                if "accessToken" in store_json['session']:
                    return True
                else:
                    logger.warning("未登录，请输入验证码进行登录")
                    return False
            except json.JSONDecodeError:
                logger.error("localStorage中store数据格式错误")
                return False

    def sleep(self, sleep_time):
        # 超过600秒间隔，进行随机
        if sleep_time > 1800:
            rd = random.randint(1200, 1800)
            logger.info(f"{self.nickName}间隔{rd}秒，继续检测")
            time.sleep(rd)
        else:
            logger.info(f"{self.nickName}间隔{sleep_time}秒，继续检测")
            time.sleep(sleep_time)

    def init_browser(self):
        logger.info(f"{self.username}开始初始化浏览器文件夹")
        # 创建保存用户数据的目录
        user_data_dir = os.path.join(os.getcwd(), "data", self.user_data_dir)
        os.makedirs(user_data_dir, exist_ok=True)
        logger.debug(f"用户数据目录: {user_data_dir}")

        # 设置 Chrome 浏览器选项
        chrome_options = Options()
        if self.is_headless == "0":
            chrome_options.add_argument("--headless")  # 无头模式，不显示浏览器窗口
        chrome_options.add_argument(f"--user-data-dir={user_data_dir}")  # 保存用户数据
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        # 指定 ChromeDriver 的路径
        chromedriver_path = "chromedriver.exe"

        # 使用 Service 类来指定驱动路径
        service = Service(chromedriver_path)

        # 初始化 Chrome 浏览器驱动
        driver = webdriver.Chrome(service=service, options=chrome_options)
        logger.info(f"{self.username}浏览器文件夹初始化成功")
        return driver

    # -------------------------------------------------------
    # 接口1：重新执行任务
    # 返回  "2":已登录，继续执行任务，"1":等待接受验证码，"0":"失败"
    # -------------------------------------------------------
    def check_login(self):
        self.driver.get("https://web.scgb.gov.cn/#/index")
        # 检测是否有公告
        try:
            notice = WebDriverWait(self.driver, 2).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'close'))
            )
            if notice and notice.is_displayed():
                notice.click()
            time.sleep(1)
        except TimeoutException:
            logger.info("---")
        # 检查登录状态
        store = self.get_local_storage_value("store", self.driver)
        if store:
            try:
                store_json = json.loads(store)
                if "accessToken" in store_json['session']:
                    self.headers['Authorization'] = "Bearer " + store_json['session']['accessToken']
                    logger.info(
                        f"已登录:{store_json['session']['nickName']}【{store_json['session']['organName']}】")
                    self.nickName = store_json['session']['nickName']
                    self.is_login = True
                    self.is_running = "1"
                    return "2", ""
                else:
                    logger.warning("未登录，请输入验证码进行登录")
            except json.JSONDecodeError:
                logger.error("localStorage中store数据格式错误")
        # time.sleep(3)
        logger.info(f"{self.username}开始自动登录")
        max_retry = 3  # 最大重试次数
        retry_count = 0  # 当前重试计数
        # 输入用户名（每次重试都重新定位，防止元素状态变化）
        username_input = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="请输入您的用户名"]'))
        )
        username_input.clear()
        username_input.send_keys(self.username)

        # 输入密码
        password_input = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="请输入您的密码"]'))
        )
        logger.info("找到密码输入框")
        password_input.clear()
        password_input.send_keys(self.password)

        while retry_count < max_retry:
            try:
                # 处理验证码
                capture_input = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="请输入验证码"]'))
                )
                capture_input.clear()

                # 获取验证码（假设self.get_formdata_img_src能正确识别验证码）
                captcha = self.get_formdata_img_src(driver1=self.driver)
                logger.info(f"{self.username}第{retry_count + 1}次尝试，识别验证码: {captcha}")
                if not captcha:
                    captcha = "123456"
                capture_input.send_keys(captcha)

                # 点击登录按钮
                login_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//div[@class="ivu-form-item-content"]//button'))
                )
                login_button.click()

                # 检测登录结果提示
                try:
                    # 等待可能出现的提示框
                    message = WebDriverWait(self.driver, 5).until(
                        EC.visibility_of_element_located((By.XPATH, '//div[@class="ivu-modal-header"]//p'))
                    )
                    logger.info(f"系统提示: {message.text}")

                    # 如果是验证码错误，准备重试
                    if message.text == "验证码错误或已过期，请重新输入！":
                        retry_count += 1
                        logger.info(f"验证码错误，准备第{retry_count + 1}次重试（共{max_retry}次）")

                        # 关闭提示框
                        visible_modal = None
                        modals = self.driver.find_elements(By.XPATH, '//div[@class="ivu-modal"]')
                        for modal in modals:
                            if modal.is_displayed():
                                visible_modal = modal
                                break

                        if visible_modal:
                            confirm_btn = visible_modal.find_element(
                                By.XPATH, './/div[@class="ivu-modal-footer"]//button[.//span[text()="确定"]]'
                            )
                            confirm_btn.click()
                            # 等待弹窗关闭
                            WebDriverWait(self.driver, 5).until(
                                EC.invisibility_of_element(visible_modal)
                            )
                        else:
                            logger.warning("未找到提示弹窗")

                        # 有些网站需要点击验证码图片刷新，这里根据实际情况添加
                        # captcha_img = self.driver.find_element(By.XPATH, '//img[@alt="验证码"]')
                        # captcha_img.click()
                        continue  # 进入下一次循环重试

                    # 其他错误提示（如用户名密码错误）
                    else:
                        logger.error(f"登录失败: {message.text}")
                        return "0", message.text

                except Exception:
                    # 未出现提示框，视为登录成功
                    logger.info(f"{self.username} 登录成功,接受手机验证码")
                    self.is_running = "2"
                    return "1", "登录成功,接受手机验证码"

            except ElementNotInteractableException:
                logger.error("登录输入框不可交互")
                return "0", "登录输入框不可交互"
            except Exception as e:
                logger.error(f"登录过程发生错误: {str(e)}")
                retry_count += 1
                if retry_count >= max_retry:
                    return "0", f"登录失败，已达最大重试次数: {str(e)}"
                continue

        # 达到最大重试次数
        logger.error(f"超过最大重试次数({max_retry}次)，登录失败")
        return "0", f"验证码多次错误，已达最大重试次数({max_retry}次)"

    # 校验验证码
    def validate_code(self, code):
        phone_input = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="请输入验证码"]'))
        )
        logger.info(f"{self.username}等待接受验证码")
        phone_input.send_keys(code)
        # # 点击登录按钮
        login_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@class="ivu-form-item-content"]//button'))
        )
        login_button.click()
        time.sleep(3)
        # 检查登录状态
        store = self.get_local_storage_value("store", self.driver)
        if store:
            try:
                store_json = json.loads(store)
                if "accessToken" in store_json['session']:
                    self.headers['Authorization'] = "Bearer " + store_json['session']['accessToken']
                    logger.info(
                        f"已登录:{store_json['session']['nickName']}【{store_json['session']['organName']}】")
                    ScgbTask.update_by_id(self.id, nick_name=store_json['session']['nickName'],
                                          organ_name=store_json['session']['organName'])
                    self.nickName = store_json['session']['nickName']
                    self.organName = store_json['session']['organName']
                    self.is_login = True
                    self.is_running = "1"
                    # 更新名称到数据库中
                    return True, ""
                else:
                    logger.warning("未登录，请输入验证码进行登录")
            except json.JSONDecodeError:
                logger.error("localStorage中store数据格式错误")
        else:
            logger.warning("未登录，请输入验证码进行登录")
        # 关闭提示框，清空验证码输入
        self.close_model()
        phone_input.clear()
        return False, "登录失败"

    def get_formdata_img_src(self, wait_time=10, driver1=None):
        """获取验证码图片并识别"""
        try:
            # 等待验证码图片容器加载
            formdata_div = WebDriverWait(driver1, wait_time).until(
                EC.presence_of_element_located((By.CLASS_NAME, "validate-form-img"))
            )
            logger.info("找到验证码图片容器")
            os.makedirs("png", exist_ok=True)
            save_path = "png/" + self.username + ".png"  # 保存路径可自定义
            success = formdata_div.screenshot(save_path)

            if success:
                logger.info(f"{self.nickName}图片元素截图已保存至: {os.path.abspath(save_path)}")
                return recognize_verify_code(image_path=os.path.abspath(save_path))
            else:
                print("截图保存失败，可能元素不可见或尺寸为0")
                return ""
        except TimeoutException:
            logger.error("超时未找到验证码图片容器")
        except NoSuchElementException:
            logger.error("未找到验证码图片")
        except Exception as e:
            logger.error(f"获取验证码图片失败: {str(e)}")
        return ""

    def exec_main(self):
        # 等待验证码
        self.check_study_time2()
        self.open_home()

        """启动异步线程，在新线程中初始化上下文"""

        def thread_target():
            # 1. 新线程中创建应用实例（或获取已存在的）
            app = create_app() if not current_app else current_app._get_current_object()

            # 2. 手动推送应用上下文（关键步骤）
            with app.app_context():
                # 3. 执行核心任务（此时已在上下文内，可正常操作数据库）
                self.check_course_success()

        # 启动线程
        thread = threading.Thread(target=thread_target)
        thread.start()
        while self.is_running == "1":
            time.sleep(1)

        # 判断token过期，或者异常推出的情况
        if self.is_complete:
            logger.info(f"{self.nickName}视频已全部播放完成")
            task = ScgbTask.query.get_or_404(self.id)
            task.status = "2"
            db.session.commit()
            # todo 截图个人中心全屏图片，作为留证，图片名称为nickName.png
            # self.driver.get("")
        else:
            logger.info(f"{self.nickName}异常停止")
            # 打开首页，刷新登录页面
            self.driver.get("https://web.scgb.gov.cn/#/index")
            time.sleep(10)
        self.driver.close()

    # 中国干部
    def exec_main2(self):
        course_list = [
            "https://cela.e-celap.cn/page.html#/pc/nc/pagecourse/coursePlayer?id=d6d710e41c21403cb6b2681e06414071&classid=0318a246a8a84125b6a5660e6898adc4&type=ztb",
            "https://cela.e-celap.cn/page.html#/pc/nc/pagecourse/coursePlayer?id=0c1e50460f664acdb0cb35df27c8c622&classid=0318a246a8a84125b6a5660e6898adc4&type=ztb",
            "https://cela.e-celap.cn/page.html#/pc/nc/pagecourse/coursePlayer?id=9899995bdded48a8a73c27a3e84d7c33&classid=0318a246a8a84125b6a5660e6898adc4&type=ztb",
            "https://cela.e-celap.cn/page.html#/pc/nc/pagecourse/coursePlayer?id=e4a2b3764791450ba2fe290293086321&classid=0318a246a8a84125b6a5660e6898adc4&type=ztb",
            "https://cela.e-celap.cn/page.html#/pc/nc/pagecourse/coursePlayer?id=1c01d3dab0324c86ab1d28b0a570f96c&classid=0318a246a8a84125b6a5660e6898adc4&type=ztb",
            "https://cela.e-celap.cn/page.html#/pc/nc/pagecourse/coursePlayer?id=8d4345b95e5a447ba1a5424a614cf343&classid=0318a246a8a84125b6a5660e6898adc4&type=ztb",
            "https://cela.e-celap.cn/page.html#/pc/nc/pagecourse/coursePlayer?id=448969a5dc774d04bf411c7cf7be7188&classid=0318a246a8a84125b6a5660e6898adc4&type=ztb",
            "https://cela.e-celap.cn/page.html#/pc/nc/pagecourse/coursePlayer?id=e4c0b118b32040babe7cfb653b60cdbd&classid=0318a246a8a84125b6a5660e6898adc4&type=ztb",
            "https://cela.e-celap.cn/page.html#/pc/nc/pagecourse/coursePlayer?id=5228f334fc24463fa251d4d0f8fdc741&classid=0318a246a8a84125b6a5660e6898adc4&type=ztb"
        ]

        # 循环处理每个课程
        for course in course_list:
            print(f"开始处理课程：{course}")
            self.driver.get(course)
            time.sleep(3)  # 页面加载等待

            # 循环检查进度直到100%
            while True:
                try:
                    # 1. 获取进度：class=el-progress__text
                    progress_elem = self.driver.find_element(By.CLASS_NAME, "el-progress__text")
                    progress_text = progress_elem.text.strip()
                    print(f"当前课程进度：{progress_text}")

                    # 2. 完成判断
                    if progress_text == "100%":
                        print("✅ 课程已完成，进入下一个")
                        break

                    # 3. 未完成 → 点击【你提供的精准播放按钮】
                    print("▶ 未完成，点击播放按钮")
                    try:
                        # 根据你提供的元素定位播放按钮（最精准）
                        play_button = self.driver.find_element(
                            By.CSS_SELECTOR,
                            "div.emiya-video-control-backdrop.pointer-events-auto"
                        )
                        play_button.click()
                    except NoSuchElementException:
                        print("⚠️ 未找到播放按钮，可能已在播放")

                    # 4. 等待1分钟再次检查
                    print("⏰ 等待60秒后重新检查...")
                    time.sleep(60)

                except NoSuchElementException:
                    print("⚠️ 未找到进度元素，页面加载中，等待3秒重试")
                    time.sleep(3)
                except Exception as e:
                    print(f"❌ 异常：{str(e)}，等待5秒重试")
                    time.sleep(5)

        print("🎉 所有课程全部自动播放完成！")
        logger.info(f"{self.nickName}视频已全部播放完成")
        task = ScgbTask.query.get_or_404(self.id)
        task.status = "2"
        db.session.commit()
        self.driver.close()

    def exec_main3(self):
        # 点击中国干部按钮，进行登录,并切换到当前页面
        try:
            print("点击：中国干部网络学院")
            child_div1 = self.driver.find_element(By.XPATH, '//span[text()="中国干部网络学院"]')
            self.switch_page(child_div1)
            time.sleep(5)
        except Exception as e:
            print(f"未找到 中国干部网络学院 按钮，跳过，错误：{e}")

        # 打开课程目标页面
        course_label = self.driver.find_element(By.XPATH, '//label[text()="树立和践行正确政绩观学习教育网上专题班"]')
        self.switch_page(course_label)
        time.sleep(5)

        # 循环打开课程列表，判断是否播放完成
        # 你的目标链接
        course_url = "https://cela.e-celap.cn/page.html#/pc/nc/pagespecial/specialDetail?id=0318a246a8a84125b6a5660e6898adc4"

        # ===================== 外层循环：直到所有课程都完成才退出 =====================
        while True:
            # 1. 新建标签页并打开链接
            self.driver.execute_script(f"window.open('{course_url}');")

            # 2. 关闭原来的标签页（第一个标签）
            # self.driver.close()
            time.sleep(3)

            # 3. 切换到新打开的标签页（必须加，否则焦点不在新页面）
            self.driver.switch_to.window(self.driver.window_handles[-1])

            # 判断是否有【报名】按钮，有就点击，没有跳过
            try:
                # 查找 报名 按钮
                apply_btn = self.driver.find_element(By.XPATH, '//div[@class="btn" and text()=" 报名 "]')
                if apply_btn.is_displayed():  # 确保可见再点击
                    print("✅ 找到报名按钮，点击报名")
                    apply_btn.click()
                    time.sleep(2)
            except NoSuchElementException:
                print("ℹ️ 页面未找到报名按钮，跳过")

            # 无论是否报名，最终都点击【课程】tab
            try:
                course_tab = self.driver.find_element(By.XPATH, '//span[contains(text()," 课程 ")]')
                course_tab.click()
                print("✅ 已切换到【课程】页面")
                time.sleep(2)
            except NoSuchElementException:
                print("⚠️ 未找到课程标签页")

            import re  # 正则提取百分比

            # ===================== 遍历 detail_desc_item，判断进度并点击 =====================
            video_flag = False
            try:
                detail_items = self.driver.find_elements(By.CLASS_NAME, "detail_desc_item")
                total = len(detail_items)
                print(f"\n📊 找到课程卡片总数：{total}")

                for i, item in enumerate(detail_items):
                    text = item.text.strip()
                    print(f"\n--- 第 {i + 1} 个课程 ---")
                    print(text)

                    # 1. 用正则提取最后一行的百分比（匹配 xx%）
                    match = re.search(r'(\d+)%', text)
                    if match:
                        progress = int(match.group(1))  # 转为数字：0, 50, 100
                        print(f"→ 学习进度：{progress}%")

                        # 2. 判断：没学完就点击
                        if progress < 100:
                            print(f"✅ 进度不足100%，点击课程卡片并打开新标签页")
                            # 点击（会新开标签）
                            # 获取当前 item 下的所有直接子 div，并点击第三个
                            child_divs = item.find_elements(By.XPATH, "./div")
                            if len(child_divs) >= 3:
                                third_div = child_divs[2]  # 第三个，索引从0开始
                                self.switch_page(third_div)  # 点击并新开页面
                                time.sleep(3)

                            video_flag = True
                            break  # 只处理第一个未完成；去掉break则全部依次处理

                    else:
                        print("⚠️ 未找到进度百分比")

            except Exception as e:
                print(f"遍历课程异常：{str(e)}")

            # 如果本轮没有找到任何未完成的课程，直接退出整个大循环
            if not video_flag:
                print("\n🎉 所有课程均已完成 100%！自动退出循环")
                break
            time.sleep(3)
            # 循环检查进度直到100%
            # 加一个标记，记录是否已经检测到 100%
            progress_100_found = False

            while True:
                try:
                    # 1. 获取进度：class=el-progress__text
                    progress_elem = self.driver.find_element(By.CLASS_NAME, "el-progress__text")
                    progress_text = progress_elem.text.strip()
                    print(f"当前课程进度：{progress_text}")

                    # 2. 完成判断（修改这里）
                    if progress_text == "100%":
                        if not progress_100_found:
                            # 第一次发现 100%，标记一下，再等一轮
                            print("✅ 第一次检测到 100%，等待一轮后再次确认...")
                            progress_100_found = True
                        else:
                            # 第二次确认 100%，才真正退出
                            print("✅ 第二次确认 100%，课程已完成，关闭视频页，返回课程列表")
                            # 关闭当前窗口 + 切回上一个窗口
                            self.driver.close()
                            all_windows = self.driver.window_handles
                            self.driver.switch_to.window(all_windows[-1])
                            break

                    else:
                        # 只要不是 100%，就重置标记
                        progress_100_found = False

                        # 3. 未完成 → 点击【你提供的精准播放按钮】
                        print("▶ 未完成，点击播放按钮")
                        try:
                            # 根据你提供的元素定位播放按钮（最精准）
                            play_button = self.driver.find_element(
                                By.CSS_SELECTOR,
                                "div.emiya-video-control-backdrop.pointer-events-auto"
                            )
                            play_button.click()
                        except NoSuchElementException:
                            print("⚠️ 未找到播放按钮，可能已在播放")

                    # 4. 等待1分钟再次检查
                    print("⏰ 等待60秒后重新检查...")
                    time.sleep(60)

                except NoSuchElementException:
                    print("⚠️ 未找到进度元素，页面加载中，等待3秒重试")
                    time.sleep(3)
                except Exception as e:
                    print(f"❌ 异常：{str(e)}，等待5秒重试")
                    time.sleep(5)

        print("🎉 所有课程全部自动播放完成！")
        logger.info(f"{self.nickName}视频已全部播放完成")
        task = ScgbTask.query.get_or_404(self.id)
        task.status = "2"
        db.session.commit()
        self.driver.close()

    def switch_page(self, child_div):
        try:
            # 记录点击前的窗口
            handles_before = self.driver.window_handles
            original_handle = self.driver.current_window_handle

            # 点击
            child_div.click()
            print("点击成功，等待新窗口打开...")

            # 等待新窗口出现
            WebDriverWait(self.driver, 10).until(EC.number_of_windows_to_be(len(handles_before) + 1))

            # 获取新窗口
            all_handles = self.driver.window_handles
            new_handle = [h for h in all_handles if h not in handles_before][0]

            # ===================== 核心修复 =====================
            # 1. 先切换到新窗口
            self.driver.switch_to.window(new_handle)
            print(f"已切换到新窗口：{self.driver.current_url}")

            # 2. 关闭原来的旧窗口（不会影响当前操作）
            # try:
            #     self.driver.switch_to.window(original_handle)
            #     self.driver.close()
            # except NoSuchWindowException:
            #     print("原窗口已关闭，跳过关闭操作")

            # 3. 再次确保停留在新窗口
            self.driver.switch_to.window(new_handle)
            print("窗口切换完成 ✅")

        except Exception as e:
            print(f"switch_page 异常：{str(e)}")

    def switch_page_close(self, child_div):
        try:
            # 记录点击前的所有窗口
            handles_before = self.driver.window_handles
            original_handle = self.driver.current_window_handle

            # 点击课程，打开新标签
            child_div.click()
            print("点击成功，等待新窗口打开...")

            # 等待新窗口出现
            WebDriverWait(self.driver, 10).until(EC.number_of_windows_to_be(len(handles_before) + 1))

            # 获取最新打开的窗口
            all_handles = self.driver.window_handles
            new_handle = [h for h in all_handles if h not in handles_before][0]

            # ===================== 核心功能：只保留新页面，关闭其他所有 =====================
            # 1. 切换到新页面
            self.driver.switch_to.window(new_handle)

            # 2. 遍历所有旧页面，全部关闭
            for handle in handles_before:
                try:
                    self.driver.switch_to.window(handle)
                    self.driver.close()
                except:
                    pass

            # 3. 最终切回新页面（现在浏览器里只有这一个页面了）
            self.driver.switch_to.window(new_handle)

            print(f"✅ 已关闭所有旧页面，当前仅保留：{self.driver.current_url}")

        except Exception as e:
            print(f"switch_page_close 异常：{str(e)}")

    def close_model(self):
        # 关闭提示框
        visible_modal = None
        modals = self.driver.find_elements(By.XPATH, '//div[@class="ivu-modal"]')
        for modal in modals:
            if modal.is_displayed():
                visible_modal = modal
                break

        if visible_modal:
            confirm_btn = visible_modal.find_element(
                By.XPATH, './/div[@class="ivu-modal-footer"]//button[.//span[text()="确定"]]'
            )
            confirm_btn.click()
            # 等待弹窗关闭
            WebDriverWait(self.driver, 5).until(
                EC.invisibility_of_element(visible_modal)
            )
        else:
            logger.warning("未找到提示弹窗，直接重试")

    def close_model2(self):
        # 关闭提示框
        visible_modal = None
        modals = self.driver.find_elements(By.XPATH, '//div[@class="ivu-modal"]')
        for modal in modals:
            if modal.is_displayed():
                visible_modal = modal
                break

        if visible_modal:
            confirm_btn = visible_modal.find_elements(
                By.XPATH, '//div[@class="ivu-modal-footer"]//button'
            )
            confirm_btn[1].click()
            # 等待弹窗关闭
            WebDriverWait(self.driver, 5).until(
                EC.invisibility_of_element(visible_modal)
            )
        else:
            logger.warning(f"{self.nickName}未找到提示弹窗")

    def close_model3(self, footer_name):
        # 关闭提示框
        visible_modal = None
        modals = self.driver.find_elements(By.XPATH, '//div[@class="ivu-modal"]')
        for modal in modals:
            if modal.is_displayed():
                visible_modal = modal
                break

        if visible_modal:
            confirm_btn = visible_modal.find_element(
                By.XPATH, f'.//div[@class="{footer_name}"]//button[.//span[text()="确定"]]'
            )
            confirm_btn.click()
            # 等待弹窗关闭
            WebDriverWait(self.driver, 5).until(
                EC.invisibility_of_element(visible_modal)
            )
        else:
            logger.warning("未找到提示弹窗，直接重试")

    def resend_code(self):
        logger.info("检测是否可以重新发送验证码")
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "tips"))
            )
            logger.info("找到重新发送验证码容器2")
            # 1. 获取 element 下直接子级 span 的文本值
            try:
                # 使用 XPath 定位直接子级 span（./ 表示当前元素的直接子元素）
                direct_span = element.find_element(By.TAG_NAME, "span")
                # 获取 span 的文本值（strip() 去除首尾空白字符）
                span_text = direct_span.text.strip()
                logger.info(f"直接子级 span 的值：{span_text}")
                if span_text == "重发验证码":
                    direct_span.click()
                    return True, ""
                return False, span_text
            except Exception as e:
                logger.error(f"获取直接子级 span 失败：{str(e)}")
                span_text = ""  # 失败时赋予默认值
                return False, "请重试"
        except TimeoutException:
            logger.error("超时未找到验证码图片容器")
        except NoSuchElementException:
            logger.error("未找到验证码图片")
        except Exception as e:
            logger.error(f"获取验证码图片失败: {str(e)}")
        # element = self.driver.find_element(By.XPATH, '//span[text="重发验证码"]')
        # element.click()
        return False, "请重试"

    def close_browser(self):
        logger.info(f"{self.username}开始关闭浏览器")
        self.is_running = "0"
        self.driver.quit()
