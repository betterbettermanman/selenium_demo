import base64
import json
import os
import random
import re
import sys
import threading
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
                                           row['is_head'], row['start_index'], row['no_play_videos'])
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
    def __init__(self, name, username, password, isHead, current_video_url_index, no_play_videos=None):
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
            'Host': 'dl.ccf.org.cn',
            'Connection': 'keep-alive',
            "hrttoken": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJPcmdhbklkIjoiMDE5ODMxMDAtZGI1Ni03MWNjLWI2NGQtNmY4NGQwYWM3MGQwIiwiQ2xpZW50VHlwZSI6IiIsIk9yZ2FuTmFtZSI6IuWvjOeJm-Wwj-WtpiIsIkFzc2Vzc1R5cGUiOjAsIlVzZXJJZCI6IjAxOTgzYzdmLTMxZWItN2I0NC1hNzRmLWZhZTRiYjliNmI3YiIsIk9yZ2FuUGF0aCI6IjJjNTUxYTczLTViNDEtMTFlZC05NTFhLTBjOWQ5MjY1MDRmMyxjMWJmNjBjNS01YjQxLTExZWQtOTUxYS0wYzlkOTI2NTA0ZjMsMDE4YTQ1YmMtZWVmNi03NzFmLTkzZGEtMzU2NDIyYzRkNTAyLGNkNGFlNWI0LTQxOTctNGUzNC1iNGVmLWNiMmVkNzg4YzNmYiwwMThjYWFhMy1lZDMzLTdkNDAtYmFhMy1iZjRlYTU3NzQ2ZTAsMDE5ODI2NDAtY2Y0YS03ZmQ1LWFiNDMtNzk4M2VmMDJiNmYwLDAxOTgzMTAwLWRiNTYtNzFjYy1iNjRkLTZmODRkMGFjNzBkMCIsImV4cCI6MTc1MzQ2MzE2MCwidXNlcm5hbWUiOiI3YTE1ZTZmNjNlYzM5YmM5In0.oQd_HlYVRr2_vC3U2DP31Vw62oYOgOLgWFD8n9KoEnI"
        }
        self.video_name = "眉山2024年度数字经济与驱动发展"
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

    def get_cookie_value(self, key: str) -> str or None:
        """
        根据 cookie 的 key 获取对应的 value。

        :param driver: Selenium WebDriver 实例
        :param key: cookie 的名称（name）
        :return: cookie 的值（value），如果不存在则返回 None
        """
        cookie = self.driver.get_cookie(key)
        return cookie['value'] if cookie else None

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
        time.sleep(2)
        element = self.driver.find_element(By.XPATH, "//div//*[@*='/our-course']")
        element.click()
        time.sleep(1)
        table = self.driver.find_element(By.CLASS_NAME, "el-table__body-wrapper")
        # 找到table下所有的tr
        tr_list = table.find_elements(By.TAG_NAME, "tr")

        for tr in tr_list:
            # 获取tr下所有的td
            td_list = tr.find_elements(By.TAG_NAME, "td")

            # 确保有至少6个td
            if len(td_list) >= 7:
                # 获取第6个td（索引为5）
                sixth_td = td_list[6]
                seven_td = td_list[7]
                # 方法1：直接获取div的文本
                div_text = sixth_td.find_element(By.TAG_NAME, "div").text
                a_tags = seven_td.find_elements(By.TAG_NAME, "a")

                print(f"第6个td的div值: {div_text}")
                if div_text == "待考试":
                    print("待考试")
                    a_tags[2].click()
                    # 切换标签
                    self.open_exam()
                    time.sleep(100)
                elif div_text == "待学习":
                    print("待考试")
                    a_tags[0].click()
                else:
                    print(div_text)

    def open_exam(self):
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
        time.sleep(2)

        logger.info("开始考试")
        for i in range(1, 31):
            time.sleep(0.5)
            self.answer_radio_question(f"char_{i}")
        for i in range(31, 51):
            time.sleep(0.5)
            self.answer_checkbox_question(f"char_{i}")
        for i in range(51, 66):
            time.sleep(0.5)
            self.answer_judge_question(f"char_{i}")
        time.sleep(1000)

    def answer_radio_question(self, id):
        # 获取问题文本
        question_div = self.driver.find_element(By.CSS_SELECTOR, "div.el-card__body")

        # 获取div内的所有文本
        question_text = question_div.text
        print(f"完整问题文本: {question_text}")

        # 找到所有选项的容器（通常是每个选项的label）
        option_elements = self.driver.find_elements(By.CLASS_NAME, "el-radio__label")
        answer = ""
        options = []
        for i, option in enumerate(option_elements):
            # 获取整个选项文本（包括A、B、C等标签）
            full_text = option.text.strip()
            options.append(full_text)
            answer = answer + f"\n{full_text}"
            print(f" {full_text}")

        # 调用GPT获取答案
        qwen_answer = get_qwen_answer(f"{question_text}{answer}")
        for item in qwen_answer:
            if item == "A":
                option_elements[0].click()
            elif item == "B":
                option_elements[1].click()
            elif item == "C":
                option_elements[2].click()
            elif item == "D":
                option_elements[3].click()
        logger.info("单选回答完成")
        # 点击下一题
        try:

            grandparent = self.driver.find_element(
                By.XPATH,
                "//span[contains(text(), '下一题')]/../.."
            )
            grandparent.click()
        except Exception as e:
            print(e)

    def answer_checkbox_question(self, div_id):
        # 找到包含问题的 div
        # 获取问题文本
        question_div = self.driver.find_element(By.CSS_SELECTOR, "div.el-card__body")

        # 获取div内的所有文本
        question_text = question_div.text
        print(f"完整问题文本: {question_text}")

        # 找到所有选项的容器（通常是每个选项的label）
        option_elements = self.driver.find_elements(By.CLASS_NAME, "el-checkbox")
        answer = ""
        options = []
        for i, option in enumerate(option_elements):
            # 获取整个选项文本（包括A、B、C等标签）
            full_text = option.text.strip()
            options.append(full_text)
            answer = answer + f"\n{full_text}"
            print(f"{full_text}")
        # 调用GPT获取答案
        qwen_answer = get_qwen_answer(f"{question_text}{answer}")
        for item in qwen_answer:
            if item == "A":
                option_elements[0].click()
            elif item == "B":
                option_elements[1].click()
            elif item == "C":
                option_elements[2].click()
            elif item == "D":
                option_elements[3].click()
            elif item == "E":
                option_elements[4].click()
            elif item == "F":
                option_elements[5].click()
        # 点击下一题
        try:

            grandparent = self.driver.find_element(
                By.XPATH,
                "//span[contains(text(), '下一题')]/../.."
            )
            grandparent.click()
        except Exception as e:
            print(e)

    def answer_judge_question(self, div_id):
        # 1. 获取问题文本
        # 获取问题文本
        question_div = self.driver.find_element(By.CSS_SELECTOR, "div.el-card__body")

        # 获取div内的所有文本
        question_text = question_div.text
        print(f"完整问题文本: {question_text}")

        # 2. 提取选项文本（"正确" 和 "错误"）

        option_elements = self.driver.find_elements(By.CLASS_NAME, "el-radio__input")
        qwen_answer = get_qwen_answer(f"{question_text}\n正确\n错误")
        for item in qwen_answer:
            if item == "A":
                option_elements[0].click()
            elif item == "B":
                option_elements[1].click()
        logger.info("判断题回答完成")
        # 点击下一题
        try:

            grandparent = self.driver.find_element(
                By.XPATH,
                "//span[contains(text(), '下一题')]/../.."
            )
            grandparent.click()
        except Exception as e:
            print(e)

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
            check_play_success_url = "https://dl.ccf.org.cn/courseZone/queryCourseCompletion?"
            logger.info(f"{self.user_data_dir}检测课程id: {self.current_course_id}")
            if self.current_course_id != "":
                params = {
                    "id": self.current_course_id
                }
                try:
                    course_detail = requests.post(check_play_success_url, headers=self.headers,
                                                  data=params)
                    # 可以打印完整的URL来验证
                    logger.info(f"完整请求URL: {course_detail.url}")
                    detail_json = course_detail.json()["data"]
                    logger.info(f"{self.user_data_dir}的【{self.current_course_id}】课程详情: {detail_json}")
                    if detail_json["isComplete"] == True:
                        logger.info("视频播放完成")
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
                            f"{self.user_data_dir}的【{self.current_course_id}】未观看完成")
                        sleep_time = random.randint(150, 300)
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
        self.driver.get("https://www.sedu.net/student/#/center")
        while True:
            # 检查登录状态
            jwtToken = self.get_local_storage_value("STUDENT-TOKEN")

            if jwtToken:
                # 2.请求头设置
                # self.headers['hrttoken'] = jwtToken
                # cookies = self.driver.get_cookies()
                #
                # # 3. 将 Cookies 转为 Cookie Header 字符串
                # cookie_header = "; ".join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
                # self.headers['Cookie'] = cookie_header
                logger.info(f"账号{self.username}已登录")
                return
            else:
                logger.warning(f"{self.user_data_dir}未登录，请登录")
            self.auto_login()
            time.sleep(2)

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
            # self.driver.get("https://www.sedu.net/student/#/login")
            # time.sleep(5)

            # # 定位iframe元素
            # iframe_xpath = '//div[@class="login-box"]/iframe'
            # iframe_element = self.driver.find_element(By.ID, iframe_xpath)
            #
            # # 切换到iframe上下文
            # self.driver.switch_to.frame(iframe_element)
            # logger.info("成功切换到目标iframe")
            # 输入用户名
            username_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='请输入身份证号/手机号/单位账号']"))
            )

            username_input.clear()
            username_input.send_keys(self.username)

            # 输入密码
            password_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='请输入密码']"))
            )
            password_input.clear()
            password_input.send_keys(self.password)

            # # 处理验证码
            capture_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="请输入验证码"]'))
            )
            capture_input.clear()
            captcha = self.get_base64_img_src()
            capture_input.send_keys(captcha)
            # 点击登录按钮
            login_buttons = self.driver.find_elements(By.XPATH, "//button[span='登录']")
            login_buttons[1].click()
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
            # 判断是否存在png文件夹
            os.makedirs("png", exist_ok=True)
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

    def get_base64_img_src(self, wait_time=10):

        # 等待验证码图片容器加载
        img_element = WebDriverWait(self.driver, wait_time).until(
            EC.presence_of_element_located((By.TAG_NAME, 'img'))
        )
        """
            从 img 元素的 src 提取 base64 并保存为图片
            :param img_element: Selenium 的 WebElement (img 标签)
            :param file_path: 保存路径，如 'output.png'
            """
        src = img_element.get_attribute("src")

        if src.startswith("data:image"):
            # 使用正则提取 MIME 类型和 Base64 数据
            match = re.match(r"data:(image/.+?);base64,(.*)", src)
            if match:
                # mime_type = match.group(1)  # 如 image/png
                base64_data = match.group(2)
                # 判断是否存在png文件夹
                os.makedirs("png", exist_ok=True)
                save_path = "png/" + self.username + ".png"  # 保存路径可自定义
                # 解码并保存
                with open(save_path, "wb") as f:
                    f.write(base64.b64decode(base64_data))
                logger.info(f"图片已保存: {save_path}")
                return recognize_verify_code(image_path=os.path.abspath(save_path))
            else:
                logger.error("Base64 数据格式错误")
        else:
            logger.error("src 不是 base64 图片")
        return ""

    def exec_main(self):
        self.init_browser()
        # 判断用户是否登录
        self.is_login()
        self.open_home()
        threading.Thread(target=self.check_course_success, daemon=True).start()
        # threading.Thread(target=self.check_course_play_status, daemon=True).start()
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
