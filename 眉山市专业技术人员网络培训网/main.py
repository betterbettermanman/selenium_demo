import json
import os
import random
import re
import sys
import threading
from urllib.parse import unquote
from urllib.parse import urlparse, parse_qs

import ddddocr
import requests
from flask import Flask, request, jsonify
from loguru import logger
from selenium import webdriver
from selenium.common import TimeoutException, NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

# 初始化Flask应用
app = Flask(__name__)

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


config_path = "config.json"
play_result_data = read_json_config(config_path)


def select_data():
    # 打印结果
    if not play_result_data:
        print("task_config表中没有数据")
        return
    # 打印表头
    print(
        f" {'名称':<10} {'用户名':<15} {'密码':<15} {'是否头部':<8} {'起始索引':<8} {'状态':<8} {'创建时间'}")
    print("-" * 80)

    # 打印每条记录
    for row in play_result_data:
        # 处理datetime对象的格式化
        created_at = row['created_at'].strftime('%Y-%m-%d %H:%M:%S') if row['created_at'] else ''
        print(
            f"{row['name']:<15} "
            f"{row['username']:<10} "
            f"{row['password']:<15} "
            f"{row['is_head']:<8} "
            f"{row['start_index']:<8} "
            f"{row['status']:<8} "
            f"{created_at}"
        )

    print(f"\n共查询到 {len(play_result_data)} 条记录")
    return play_result_data


def insert_data(name, username, password, is_head, start_index):
    # 插入一条数据
    play_result_data.update({
        "name": name,
        "username": username,
        "password": password,
        "is_head": is_head,
        "start_index": start_index,
        "no_play_videos": [],
        "status": 1,
        "requiredPeriod": "",
        "electivePeriod": "",
        "created_at": time.strftime('%Y-%m-%d %H:%M:%S'),
        "updated_at": ""
    })
    #  写回文件（保持缩进和中文显示）
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(play_result_data, f, ensure_ascii=False, indent=2)  # indent=2 保持格式化


def update_data(username, status=None, requiredPeriod=None, electivePeriod=None):
    for data in play_result_data:
        if data['username'] == username:
            if status:
                data['status'] = status
            if requiredPeriod:
                data['requiredPeriod'] = requiredPeriod
            if electivePeriod:
                data['electivePeriod'] = electivePeriod
            data["updated_at"] = time.strftime('%Y-%m-%d %H:%M:%S')
    #  写回文件（保持缩进和中文显示）
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(play_result_data, f, ensure_ascii=False, indent=2)  # indent=2 保持格式化
    logger.info(f"{username}数据更新成功")


def continue_task():
    result = select_data()
    for row in result:
        # 判断是否执行完成
        if row['status'] != '2':
            check = TeacherTrainingChecker(row['name'], row['username'], row['password'],
                                           row['is_head'], row['start_index'], row['no_play_videos'], row['video_name'])
            thread = threading.Thread(target=check.exec_main)  # 注意这里没有()
            thread.start()  # 启动线程
            time.sleep(10)
    logger.info("继续未完成的工作")


import time
import dashscope

# 设置你的 API Key
dashscope.api_key = "sk-b1fc73875d134f34b0f2d579b9291281"  # 替换为你的实际密钥


def get_qwen_answer(question_content):
    """
    调用 Qwen 模型，输入题目内容，返回选择题答案选项（如 'A'）

    :param question_content: 题目文本（支持单选/多选题）
    :return: 答案字母（如 'C'），失败时返回 None
    """
    messages = [
        {
            'role': 'system',
            'content': '你是一个知识丰富的助手，请根据问题给出准确、简洁的回答。'
                       '如果是选择题，请在最后明确写出答案选项，并只返回选项字母（如：C）'
                       '如果是判断题，正确返回：A，错误返回：B'
        },
        {
            'role': 'user',
            'content': question_content
        }
    ]

    try:
        time_start = time.time()
        response = dashscope.Generation.call(
            model="qwen3-8b",
            messages=messages,
            enable_thinking=False,
            result_format='text'
        )
        time_end = time.time()

        # 检查响应是否成功
        if response.status_code == 200:
            answer = response.output.text.strip()
            print(f"✅ 模型响应: {answer}")
            print(f"⏱ 耗时: {time_end - time_start:.2f} 秒")

            # 提取答案字母（A / B / C / D / ...）
            # 假设模型输出类似 "C" 或 "答案：C"，我们只取最后一个字母
            import re
            match = re.findall(r'[A-Z]', answer)
            if match:
                unique_match = list(dict.fromkeys(match))
                return unique_match
            else:
                print("⚠️ 未从响应中提取到有效选项字母，返回D")
                return ["D"]
        else:
            print(f"❌ 调用失败: {response.code} - {response.message}")
            return None

    except Exception as e:
        print(f"❌ 请求出错: {str(e)}")
        return None


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


def extract_id_from_url(url):
    # 解析 URL 结构
    parsed_url = urlparse(url)

    # 提取哈希（#）后的部分（包含路径和参数）
    hash_part = parsed_url.fragment  # 结果为：/course?id=018a4061-a884-7856-81a5-77be717dede0&className=&classId=019815fe-ec44-753d-9b1d-554f017df106

    # 从哈希部分中分离出查询参数（?后面的内容）
    # 先找到 ? 的位置，截取参数部分
    query_start = hash_part.find('?')
    if query_start == -1:
        return None  # 没有查询参数

    query_string = hash_part[
                   query_start + 1:]  # 结果为：id=018a4061-a884-7856-81a5-77be717dede0&className=&classId=019815fe-ec44-753d-9b1d-554f017df106

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


class TeacherTrainingChecker:
    def __init__(self, name, username, password, isHead, current_video_url_index, no_play_videos=None, video_name=None):
        """
        初始化教师培训课程检查器（使用外部传入的浏览器实例）

        :param wait: 共享的显式等待对象
        :param target_courses: 需要检查的目标课程列表
        :param base_url: 培训首页URL
        """
        if no_play_videos is None:
            no_play_videos = []
        self.is_headless = isHead
        self.user_data_dir = name
        self.username = username
        self.password = password
        self.current_course_id = ""
        self.is_running = True
        self.headers = {
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'Accept': '*/*',
            'Host': 'gp.chinahrt.com',
            'Connection': 'keep-alive',
            "hrttoken": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJPcmdhbklkIjoiMDE5ODMxMDAtZGI1Ni03MWNjLWI2NGQtNmY4NGQwYWM3MGQwIiwiQ2xpZW50VHlwZSI6IiIsIk9yZ2FuTmFtZSI6IuWvjOeJm-Wwj-WtpiIsIkFzc2Vzc1R5cGUiOjAsIlVzZXJJZCI6IjAxOTgzYzdmLTMxZWItN2I0NC1hNzRmLWZhZTRiYjliNmI3YiIsIk9yZ2FuUGF0aCI6IjJjNTUxYTczLTViNDEtMTFlZC05NTFhLTBjOWQ5MjY1MDRmMyxjMWJmNjBjNS01YjQxLTExZWQtOTUxYS0wYzlkOTI2NTA0ZjMsMDE4YTQ1YmMtZWVmNi03NzFmLTkzZGEtMzU2NDIyYzRkNTAyLGNkNGFlNWI0LTQxOTctNGUzNC1iNGVmLWNiMmVkNzg4YzNmYiwwMThjYWFhMy1lZDMzLTdkNDAtYmFhMy1iZjRlYTU3NzQ2ZTAsMDE5ODI2NDAtY2Y0YS03ZmQ1LWFiNDMtNzk4M2VmMDJiNmYwLDAxOTgzMTAwLWRiNTYtNzFjYy1iNjRkLTZmODRkMGFjNzBkMCIsImV4cCI6MTc1MzQ2MzE2MCwidXNlcm5hbWUiOiI3YTE1ZTZmNjNlYzM5YmM5In0.oQd_HlYVRr2_vC3U2DP31Vw62oYOgOLgWFD8n9KoEnI"
        }
        self.video_name = video_name
        self.current_video_url_index = current_video_url_index
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

    def get_session_storage_value(self, key):
        """从sessionStorage中获取指定键的值"""
        try:
            # 使用JavaScript获取sessionStorage中的值
            value = self.driver.execute_script(f"return window.sessionStorage.getItem('{key}');")
            return value
        except Exception as e:
            logger.error("获取sessionStorage值失败")
            return None

    def get_local_storage_value(self, key):
        """从localStorage中获取指定键的值"""
        try:
            value = self.driver.execute_script(f"return window.localStorage.getItem('{key}');")
            return value
        except Exception as e:
            logger.error(f"获取localStorage值失败: {str(e)}")
            return None

    def open_home(self):
        if self.is_complete:
            return
        logger.info(f"{self.user_data_dir}进行学习")
        logger.info(
            f"{self.user_data_dir}打开首页，检测视频学习情况，current_video_url_index：{self.current_video_url_index}")
        url = "https://gp.chinahrt.com/index.html#/v_trainplan_list"
        self.driver.get(url)
        time.sleep(5)
        logger.info("获取列表第一个的视频进度和考试进度")
        # 获取该div下所有的span元素
        parent_elements = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".fl.ml30"))
        )

        # 存储所有找到的dt元素
        current_course = ""
        # 遍历每个父元素，查找其下的所有dt标签
        for parent in parent_elements:
            course_div = parent.find_element(By.CLASS_NAME, "course-title")
            # 在div内部查找所有span标签
            span_elements = course_div.find_elements(By.TAG_NAME, "span")

            # 提取所有span标签的文本值
            span_values = [span.text for span in span_elements]

            # 打印结果
            logger.info("所有span标签的值：")
            is_return = False
            for value in span_values:
                logger.info(value)
                if value == self.video_name:
                    current_course = parent
                    is_return = True
            if is_return:
                break
        # 开始判断是否完成课程
        column_wrap = current_course.find_element(By.CLASS_NAME, "column-wrap")
        video_process = column_wrap.find_elements(By.CLASS_NAME, "el-progress__text")
        # 如果不为已学100%，找到去激活按钮，进行激活
        # 如果不是已学100%
        if video_process and "已学100%" != video_process[0].text:
            # 优先处理去激活
            try:
                activate_btn = column_wrap.find_element(By.XPATH, ".//button[contains(text(), '去激活')]")
                activate_btn.click()
                logger.info("激活课程")
                # todo 如果有啥额外操作，都可以在这里实现
                time.sleep(5)
                self.open_home()
                return "course"
            except NoSuchElementException:
                logger.info("当前课程无去激活按钮，检查是否需要学习")

            # 处理去学习/继续学习
            try:
                learn_btn = column_wrap.find_element(By.XPATH,
                                                     ".//button[contains(text(), '去学习') or contains(text(), '继续学习')]")
                learn_btn.click()
                logger.info("打开课程，获取课程列表，判断每个课程列表是否完成")
                self.open_course()
                return "course"
            except NoSuchElementException:
                logger.warning("当前课程没有可操作的按钮")
                return "course"
        # 如果不为已考100%，找到去考试按钮，进行考试
        if "已考100%" != video_process[1].text:
            learn_elements = column_wrap.find_element(By.XPATH, ".//button[.//text()='去考试' or .= '去考试']")
            learn_elements.click()
            logger.info("打开考试")
            self.open_exam()
            return "exam"
        logger.info("当前课程已完成")
        return "complete"

    def open_course(self):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.course-list.cb'))
            )
            logger.info("课程列表元素已找到")
            time.sleep(5)
        except TimeoutException:
            logger.info("超过10秒未找到课程列表元素")

        try:
            # 定位到class为"course-list cb"的div元素
            course_list_div = self.driver.find_element(By.CSS_SELECTOR, 'div.course-list.cb')

            # 在div下找到ul元素
            ul_element = course_list_div.find_element(By.TAG_NAME, 'ul')

            # 获取ul下所有的li元素
            all_li_elements = ul_element.find_elements(By.TAG_NAME, 'li')

            # 遍历并处理所有li元素
            for index, li in enumerate(all_li_elements, 1):
                # 判断进度是否100%
                # 在当前li下定位class为"progress-line"的div
                progress_div = li.find_element(By.CSS_SELECTOR, 'div.progress-line')

                # 从div中获取span元素的值
                span_value = progress_div.find_element(By.TAG_NAME, 'span').text

                logger.info(f"第{index}个li中的span值: {span_value}")
                if span_value == "100%":
                    continue
                logger.info(f"第{index}个li元素的文本内容: {li.text}")
                target_div = li.find_element(By.CSS_SELECTOR, 'div')  # 可根据实际情况修改选择器

                # 确保元素可点击后再点击
                WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable(target_div)
                ).click()
                break

            time.sleep(10)
            original_window = self.driver.current_window_handle  # 记录原始标签页句柄
            # 等待新标签页打开（最多等待10秒）
            WebDriverWait(self.driver, 10).until(
                lambda d: len(d.window_handles) > 1
            )

            # 切换到新标签页
            for window_handle in self.driver.window_handles:
                if window_handle != original_window:
                    self.driver.switch_to.window(window_handle)
                    print("已切换到新标签页")
                    break

            # 在新标签页中操作元素（示例：获取页面标题和某个元素）
            # print(f"新标签页标题: {self.driver.title}")
            course_list_div2 = self.driver.find_element(By.CSS_SELECTOR, 'div.course-catalog.m0')
            all_li_elements = course_list_div2.find_elements(By.TAG_NAME, 'li')
            for index, li in enumerate(all_li_elements, 1):
                logger.info(li.text)
                a_values = li.find_elements(By.TAG_NAME, 'a')
                logger.info(a_values[1].text)
                if a_values[1].text.__contains__("已学完"):
                    continue
                # 点击当前li
                logger.info("点击课程，跳转到新的页面进行播放，并且记录课程id")

                a_values[1].click()
                break
            time.sleep(10)
            # 记录当前窗口句柄（第一个新标签页）
            first_new_window_handle = self.driver.current_window_handle
            # 切换到最新打开的标签页
            second_new_window = None
            for window_handle in self.driver.window_handles:
                if window_handle != original_window and window_handle != first_new_window_handle:
                    second_new_window = window_handle
                    self.driver.switch_to.window(window_handle)
                    logger.info("已切换到第二个新标签页")
                    break

            # 操作第二个新标签页（示例）
            # logger.info(f"第二个新标签页标题: {self.driver.title}")

            # 关闭第一个新标签页
            for window_handle in self.driver.window_handles:
                if window_handle == first_new_window_handle:
                    self.driver.switch_to.window(first_new_window_handle)
                    self.driver.close()
                    # 切换到第二个新标签页
                    self.driver.switch_to.window(second_new_window)
                    logger.info("已关闭第一个标签页")

            # 定位iframe元素
            iframe_xpath = '//div[@class="video-container"]/iframe'
            iframe_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, iframe_xpath))
            )

            # 切换到iframe上下文
            self.driver.switch_to.frame(iframe_element)
            logger.info("成功切换到目标iframe2")
            # 这里可以添加对第二个新标签页的操作 pausecenterchehhidfompc
            required_div = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((
                    By.XPATH,
                    '//div[starts-with(@class, "pausecenter")]'
                ))
            )

            required_div.click()
            self.current_course_id = self.extract_param_from_hash_url(self.driver.current_url, "courseId")
            self.trainplanId = self.extract_param_from_hash_url(self.driver.current_url, "trainplanId")
            self.platformId = self.extract_param_from_hash_url(self.driver.current_url, "platformId")
            logger.info(f"点击开始播放视频：{self.current_course_id}")
        except Exception as e:
            print(f"获取元素时发生错误: {e}")

    def open_exam(self):
        logger.info("打开考试")
        go_exam = "button.Clearfix.goExam"
        go_exam_success = False
        try:
            go_exam_button = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, go_exam))
            )
            go_exam_button.click()
            go_exam_success = True
            el_message_box__btns = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "el-message-box__btns"))
            )
            button_elements = el_message_box__btns.find_elements(By.XPATH, "./button")
            button_elements[1].click()
            logger.info("✅ '确认' 按钮已点击！")
        except Exception as e:
            logger.info("去考试元素找不到，开始检测继续考试元素")

        if not go_exam_success:
            continue_exam = "button.Clearfix.continueExam"
            try:
                continue_exam_button = WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, continue_exam))
                )
                continue_exam_button.click()
                logger.info("点击继续考试")
            except Exception as e:
                logger.info("继续考试元素找不到")

        logger.info("开始考试")
        for i in range(1, 26):
            self.answer_radio_question(f"char_{i}")
        for i in range(26, 46):
            self.answer_checkbox_question(f"char_{i}")
        for i in range(46, 56):
            self.answer_judge_question(f"char_{i}")
        logger.info("答题完成，点击交卷")
        # todo 待测试
        element = self.driver.find_element(By.LINK_TEXT, "我要交卷")
        element.click()

    def answer_radio_question(self, id):
        # 获取问题文本
        question_box = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//div[@id='{id}']//div[@class='question-box oh']/h2"))
        )
        question_text = question_box.text
        print(f"问题: {question_text}")

        # 获取选项及其值
        radio_group = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, f"//div[@id='{id}']//div[contains(@class, 'ml40') and contains(@class, 'radio_group')]"))
        )
        answer = ""
        options = radio_group.find_elements(By.XPATH, ".//label")
        for option in options:
            letter = option.find_element(By.XPATH, ".//span[@class='el-radio__label']").text.split()[0]  # 获取选项字母
            value = option.find_element(By.XPATH, ".//span[@data-v-7915584a]").text  # 获取选项值
            print(f"{letter}: {value}")
            answer = answer + f"\n{letter}. {value}"
        # 调用GPT获取答案
        qwen_answer = get_qwen_answer(f"{question_text}{answer}")
        for item in qwen_answer:
            if item == "A":
                options[0].click()
            elif item == "B":
                options[1].click()
            elif item == "C":
                options[2].click()
            elif item == "D":
                options[3].click()
        logger.info("第一题回答完成")

    def answer_checkbox_question(self, div_id):
        # 找到包含问题的 div
        question_div = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//div[@id='{div_id}']//div[@class='question-box oh']/h2"))
        )
        question_text = question_div.text
        print(f"问题: {question_text}")

        # 找到包含选项的 div
        options_div = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//div[@id='{div_id}']//div[contains(@class, 'check_group')]"))
        )

        # 提取所有选项及其值
        options_elements = options_div.find_elements(By.XPATH, ".//label")
        options = {}
        answer = ""
        for option in options_elements:
            letter = option.find_element(By.XPATH, ".//span[@class='el-checkbox__label']").text.split()[0]  # 获取选项字母
            value = option.find_element(By.XPATH, ".//span[@data-v-7915584a]").text  # 获取选项值
            options[letter] = value
            print(f"{letter}: {value}")
            answer = answer + f"\n{letter}. {value}"
        # 调用GPT获取答案
        qwen_answer = get_qwen_answer(f"{question_text}{answer}")
        for item in qwen_answer:
            if item == "A":
                options_elements[0].click()
            elif item == "B":
                options_elements[1].click()
            elif item == "C":
                options_elements[2].click()
            elif item == "D":
                options_elements[3].click()
            elif item == "E":
                options_elements[4].click()
            elif item == "F":
                options_elements[5].click()
        logger.info("多选题回答完成")

    def answer_judge_question(self, div_id):
        # 1. 获取问题文本
        question_element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//div[@id='{div_id}']//div[@class='question-box oh']/h2"))
        )
        question_text = question_element.text
        print(f"问题: {question_text}")

        # 2. 提取选项文本（"正确" 和 "错误"）
        option_labels = self.driver.find_elements(By.XPATH,
                                                  f"//div[@id='{div_id}']//label[@role='radio']//span[@class='el-radio__label']")

        qwen_answer = get_qwen_answer(f"{question_text}\n正确\n错误")
        for item in qwen_answer:
            if item == "A":
                option_labels[0].click()
            elif item == "B":
                option_labels[1].click()
        logger.info("判断题回答完成")

    def extract_param_from_hash_url(self, url, param_name):
        """
        从哈希路由URL中提取指定参数的值
        """
        # 匹配哈希路由后的查询参数
        pattern = f'{param_name}=([^&]+)'
        match = re.search(pattern, url)

        if match:
            # URL解码（处理中文等特殊字符）
            return unquote(match.group(1))
        return None

    def send_check_result(self, requiredPeriod, electivePeriod, mentioned_list=None, mentioned_mobile_list=None):
        update_data(self.username, requiredPeriod=requiredPeriod, electivePeriod=electivePeriod)
        content = self.user_data_dir + "：必修:" + requiredPeriod + ";选修:" + electivePeriod
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
                logger.info("发送成功")
        except Exception as e:
            logger.error(f"请求异常：{str(e)}")

    def check_course_success(self):
        sleep_time = 10
        call_login = False
        while self.is_running:
            if self.sleep_time_num == 100:
                logger.info(f"{self.user_data_dir}睡眠重复次数超过3次，重新打开页面")
                self.is_login()
                threading.Thread(target=self.open_home, daemon=True).start()
                self.current_course_id = ""
                self.sleep_time_num = 0
                time.sleep(10)
                continue
            check_play_success_url = "https://gp.chinahrt.com/gp6/lms/stu/course/courseDetail?"
            logger.info(f"{self.user_data_dir}检测课程id: {self.current_course_id}")
            if self.current_course_id != "":
                params = {
                    "courseId": self.current_course_id,
                    "trainplanId": self.trainplanId,
                    "platformId": self.platformId,
                }
                logger.info(params)
                logger.info(self.headers)
                try:
                    course_detail = requests.get(check_play_success_url, headers=self.headers,
                                                 params=params)
                    # 可以打印完整的URL来验证
                    logger.info(f"完整请求URL: {course_detail.url}")
                    detail_json = course_detail.json()["data"]
                    # logger.info(f"{self.user_data_dir}的【{self.current_course_id}】课程详情: {detail_json}")
                    if detail_json["learnPercent"] == 100:
                        # 当前视频已播放完成，可以关闭当前窗体，然后刷新页面，播放下一个视频
                        self.driver.close()
                        # 获取关闭后的窗口句柄
                        remaining_handles = self.driver.window_handles
                        logger.info(f"关闭后标签页数量: {len(remaining_handles)}")

                        # 如果还有剩余的tab，切换到第一个
                        if remaining_handles:
                            self.driver.switch_to.window(remaining_handles[0])
                            logger.info("已切换到剩余的第一个标签页")
                        else:
                            logger.info("所有标签页已关闭")
                            # if self.check_study_time2():
                            #     # 播放下一个视频
                        logger.info(
                            f"{self.user_data_dir}的【{self.current_course_id}】已观看完成，但未完成学时，继续播放下一个视频")
                        threading.Thread(target=self.open_home, daemon=True).start()
                        self.current_course_id = ""
                        sleep_time = 60
                        # else:
                        #     logger.info("已全部观看完成，退出程序")
                        #     self.is_running = False
                        # break
                    else:
                        # 当前视频未播放完成，间隔5-10分钟继续检测
                        logger.info(
                            f"{self.user_data_dir}的【{self.current_course_id}】未观看完成，进度：{detail_json['learnPercent']}")
                        sleep_time = random.randint(300, 600)
                except TimeoutException:
                    logger.error("链接超时")
                    continue
                except Exception as e:
                    logger.error(f"{self.user_data_dir}检测课程状态失败: {str(e)}，可能登陆失效，进行登录检测")
                    self.is_login()
                    call_login = True
                    sleep_time = 20
            else:
                sleep_time = 10
            logger.debug("记录睡眠值，以及重复次数")
            if self.sleep_time == sleep_time:
                self.sleep_time_num = self.sleep_time_num + 1
            else:
                self.sleep_time = sleep_time
                self.sleep_time_num = 0

            logger.info(f"{self.user_data_dir}间隔{sleep_time}秒，继续检测")
            time.sleep(sleep_time)

    def check_course_play_status(self):
        while self.is_running:
            logger.info("间隔30秒，检测视频播放状态")
            time.sleep(30)
            # 尝试查找"课程评价弹框，当出现课程评价弹框，说明当前课程已完成"
            # 等待并查找文本为 "课程评价" 的 span 元素
            try:
                complete_span = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, '//span[text()="课程评价"]'))
                )
                logger.info("✅ 找到 '课程评价' 标签，当前课程已完成")
                # 当前视频已播放完成，可以关闭当前窗体，然后刷新页面，播放下一个视频
                self.driver.close()
                # 获取关闭后的窗口句柄
                remaining_handles = self.driver.window_handles
                print(f"关闭后标签页数量: {len(remaining_handles)}")

                # 如果还有剩余的tab，切换到第一个
                if remaining_handles:
                    self.driver.switch_to.window(remaining_handles[0])
                    print("已切换到剩余的第一个标签页")
                else:
                    print("所有标签页已关闭")
                    # if self.check_study_time2():
                    #     # 播放下一个视频
                time.sleep(30)
                continue  # 表示已完成，可以切换下一个课程
            except TimeoutException:
                logger.info("🟢 未找到 '课程评价' 标签，当前课程可能未完成")

            # 尝试查找 pausecenter 元素（最多等待3秒）
            try:
                required_div = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((
                        By.XPATH,
                        '//div[starts-with(@class, "pausecenter")]'
                    ))
                )

                # 获取 style 中的 display 属性
                display_style = required_div.value_of_css_property('display')

                # 判断 display 是否为 'none'
                if display_style == 'none':
                    logger.info(f"pausecenter 元素存在，但 display: {display_style}，跳过点击")
                else:
                    required_div.click()
                    logger.info(f"pausecenter 元素 visible (display: {display_style})，已点击")

            except TimeoutException:
                logger.info("未找到 pausecenter 元素（超时），跳过点击")
            except NoSuchElementException:
                logger.info("未找到 pausecenter 元素，跳过点击")
            except Exception as e:
                logger.warning(f"检查或点击 pausecenter 元素时发生异常: {e}")

    def init_browser(self):
        logger.info(f"{self.user_data_dir}开始初始化浏览器文件夹")
        # 创建保存用户数据的目录
        user_data_dir = os.path.join(os.getcwd(), "data", self.user_data_dir)
        os.makedirs(user_data_dir, exist_ok=True)
        logger.debug(f"用户数据目录: {user_data_dir}")

        # 设置 Chrome 浏览器选项
        chrome_options = Options()
        if self.is_headless:
            chrome_options.add_argument("--headless")  # 无头模式，不显示浏览器窗口
        chrome_options.add_argument(f"--user-data-dir={user_data_dir}")  # 保存用户数据
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        # 指定 ChromeDriver 的路径
        chromedriver_path = "chromedriver.exe"

        # 使用 Service 类来指定驱动路径
        service = Service(chromedriver_path)

        # 初始化 Chrome 浏览器驱动
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        logger.info(f"{self.user_data_dir}浏览器文件夹初始化成功")

    def is_login(self):
        while True:
            self.auto_login()
            time.sleep(10)
            self.driver.get("https://gp.chinahrt.com/index.html#/v_user_set")
            time.sleep(2)
            # 检查登录状态
            jwtToken = self.get_session_storage_value("jwtToken")

            if jwtToken:
                realName = self.get_session_storage_value("realName")
                orgName = self.get_session_storage_value("orgName")
                self.headers['hrttoken'] = jwtToken
                logger.info(f"已登录:{realName}【{orgName}】")
                return
            else:
                logger.warning(f"{self.user_data_dir}未登录，请登录")

    def get_element_in_iframe(self, iframe_locator, element_locator):
        """
        在iframe中获取元素
        :param iframe_locator: iframe的定位器 (例如(By.ID, 'iframe_id'))
        :param element_locator: 要查找的元素的定位器
        :return: 找到的元素或None
        """
        try:
            # 切换到iframe
            self.driver.switch_to.frame(self.driver.find_element(*iframe_locator))

            # 在iframe中查找元素
            element = self.driver.find_element(*element_locator)
            return element

        except Exception as e:
            logger.error(f"在iframe中获取元素失败: {str(e)}")
            return None
        finally:
            # 切回主文档，避免影响后续操作
            self.driver.switch_to.default_content()

    def login_through_iframe(self):
        """
        通过指定XPath的iframe进行登录操作
        :param username: 登录用户名
        :param password: 登录密码
        :return: 是否登录成功
        """
        try:
            # 定位iframe元素
            iframe_xpath = '//div[@class="login-box"]/iframe'
            iframe_element = self.driver.find_element(By.XPATH, iframe_xpath)

            # 切换到iframe上下文
            self.driver.switch_to.frame(iframe_element)
            logger.info("成功切换到目标iframe")

            # 在iframe中定位用户名输入框并输入
            # 注意：这里的XPath需要根据实际页面调整
            username_input = self.driver.find_element(By.XPATH, '//input[@placeholder="账号"]')
            username_input.clear()
            username_input.send_keys(self.username)

            # 在iframe中定位密码输入框并输入
            password_input = self.driver.find_element(By.XPATH, '//input[@name="密码"]')
            password_input.clear()
            password_input.send_keys(self.password)

            # 点击登录按钮
            login_button = self.driver.find_element(By.XPATH, '//button[@type="submit" or text()="登录"]')
            login_button.click()
            logger.info("登录信息已提交")

            # 等待登录操作完成（可根据实际情况调整等待时间）
            time.sleep(2)
            return True

        except NoSuchElementException as e:
            logger.error(f"未找到元素: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"登录过程出错: {str(e)}")
            return False
        finally:
            # 无论成功失败，都切回主文档
            self.driver.switch_to.default_content()
            logger.info("已切换回主文档")

    def auto_login(self):
        try:
            logger.info(f"{self.user_data_dir}开始自动登录")
            self.driver.get("http://meishan.scjxjypx.com/")
            time.sleep(5)

            # 定位iframe元素
            iframe_xpath = '//div[@class="login-box"]/iframe'
            iframe_element = self.driver.find_element(By.XPATH, iframe_xpath)

            # 切换到iframe上下文
            self.driver.switch_to.frame(iframe_element)
            logger.info("成功切换到目标iframe")
            # 输入用户名
            username_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="账号"]'))
            )

            username_input.clear()
            username_input.send_keys(self.username)

            # 输入密码
            password_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="密码"]'))
            )
            password_input.clear()
            password_input.send_keys(self.password)

            # # 处理验证码
            capture_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="验证码"]'))
            )
            capture_input.clear()
            captcha = self.get_formdata_img_src()
            capture_input.send_keys(captcha)
            # 点击登录按钮
            login_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//button[@class="el-button logbtn cb mt5 el-button--default el-button--small"]'))
            )
            login_button.click()
        except TimeoutException:
            logger.error("超时未找到登录相关输入框")
        except ElementNotInteractableException:
            logger.error("登录输入框不可交互")
        except Exception as e:
            logger.error(f"自动登录失败: {str(e)}")

    def get_formdata_img_src(self, wait_time=10):
        """获取验证码图片并识别"""
        try:
            # 等待验证码图片容器加载
            formdata_div = WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_element_located((By.XPATH, '//img[@alt="验证码"]'))
            )
            logger.info("找到验证码图片容器")
            save_path = "png/" + self.username + ".png"  # 保存路径可自定义
            success = formdata_div.screenshot(save_path)

            if success:
                logger.info(f"{self.user_data_dir}图片元素截图已保存至: {os.path.abspath(save_path)}")
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
        self.init_browser()
        # 判断用户是否登录
        self.is_login()
        if self.open_home() == "course":
            threading.Thread(target=self.check_course_success, daemon=True).start()
            threading.Thread(target=self.check_course_play_status, daemon=True).start()
        while self.is_running:
            time.sleep(1)
        logger.info(f"{self.user_data_dir}视频已全部播放完成")
        self.driver.close()
        update_data(self.username, status="2")


# 执行任务
@app.route('/execTask', methods=['POST'])
def exec_task():
    # 创建对象，执行任务
    logger.info("创建对象，执行任务")
    check = TeacherTrainingChecker(request.json['name'], request.json['username'], request.json['password'],
                                   request.json['isHead'], request.json['startIndex'])
    thread = threading.Thread(target=check.exec_main)  # 注意这里没有()
    thread.start()  # 启动线程
    logger.info("任务已保存到数据库中，并开始执行")
    return jsonify({"result": "任务已开始"}), 200


if __name__ == '__main__':
    continue_task()
    app.run(host='0.0.0.0', port=7002)
