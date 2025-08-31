import json
import os
import random
import re
import sys
import threading
import time
from urllib.parse import urlparse, parse_qs

import ddddocr
import requests
from flask import Flask
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


config_path = "v2_config.json"
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


def update_data(username, status=None, requiredPeriod=None, electivePeriod=None, cursor_id=None):
    for data in play_result_data:
        if data['username'] == username:
            if status:
                data['status'] = status
            if requiredPeriod:
                data['requiredPeriod'] = requiredPeriod
            if electivePeriod:
                data['electivePeriod'] = electivePeriod
            if cursor_id:
                data['no_play_videos'].append(cursor_id)
            data["updated_at"] = time.strftime('%Y-%m-%d %H:%M:%S')
    #  写回文件（保持缩进和中文显示）
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(play_result_data, f, ensure_ascii=False, indent=2)  # indent=2 保持格式化
    logger.info(f"{username}数据更新成功")


def update_course(username, course_id=None):
    for data in play_result_data:
        if data['username'] == username:
            if course_id:
                for course in data['courses']:
                    if course['id'] == course_id:
                        course['status'] = '1'
            data["updated_at"] = time.strftime('%Y-%m-%d %H:%M:%S')
        #  写回文件（保持缩进和中文显示）
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(play_result_data, f, ensure_ascii=False, indent=2)  # indent=2 保持格式化


def continue_task():
    result = select_data()
    for row in result:
        # 判断是否执行完成
        if row['status'] != '2':
            check = TeacherTrainingChecker(row['name'], row['username'], row['password'],
                                           row['is_head'], row['start_index'], row['no_play_videos'], row['courses'])
            thread = threading.Thread(target=check.exec_main)  # 注意这里没有()
            thread.start()  # 启动线程
            time.sleep(10)
    logger.info("继续未完成的工作")


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


def compare_hours_str(hours_str, teacher):
    return hours_str == teacher


class TeacherTrainingChecker:
    def __init__(self, name, username, password, isHead, current_video_url_index, no_play_videos=None, courses=None):
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
            'X-Access-Token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2NDIxMTQ5MjAsInVzZXJuYW1lIjoiYWRtaW4ifQ.-HyWQh6A9y6ZmclS7ltpBu-GFb3liVk5VVj6laavOg0',
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'Accept': '*/*',
            'Host': 'www.cdjxjy.com',
            'Connection': 'keep-alive',
            "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJPcmdhbklkIjoiMDE5ODMxMDAtZGI1Ni03MWNjLWI2NGQtNmY4NGQwYWM3MGQwIiwiQ2xpZW50VHlwZSI6IiIsIk9yZ2FuTmFtZSI6IuWvjOeJm-Wwj-WtpiIsIkFzc2Vzc1R5cGUiOjAsIlVzZXJJZCI6IjAxOTgzYzdmLTMxZWItN2I0NC1hNzRmLWZhZTRiYjliNmI3YiIsIk9yZ2FuUGF0aCI6IjJjNTUxYTczLTViNDEtMTFlZC05NTFhLTBjOWQ5MjY1MDRmMyxjMWJmNjBjNS01YjQxLTExZWQtOTUxYS0wYzlkOTI2NTA0ZjMsMDE4YTQ1YmMtZWVmNi03NzFmLTkzZGEtMzU2NDIyYzRkNTAyLGNkNGFlNWI0LTQxOTctNGUzNC1iNGVmLWNiMmVkNzg4YzNmYiwwMThjYWFhMy1lZDMzLTdkNDAtYmFhMy1iZjRlYTU3NzQ2ZTAsMDE5ODI2NDAtY2Y0YS03ZmQ1LWFiNDMtNzk4M2VmMDJiNmYwLDAxOTgzMTAwLWRiNTYtNzFjYy1iNjRkLTZmODRkMGFjNzBkMCIsImV4cCI6MTc1MzQ2MzE2MCwidXNlcm5hbWUiOiI3YTE1ZTZmNjNlYzM5YmM5In0.oQd_HlYVRr2_vC3U2DP31Vw62oYOgOLgWFD8n9KoEnI"
        }
        self.video_name = ["中国式现代化理论体系", "习近平新时代中国特色社会主义思想", "总体国家安全观",
                           "习近平强军思想"]
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
        # 班级id
        self.class_id = "019815fe-ec44-753d-9b1d-554f017df106"
        # 最大次数，超过就将当前课程放入不需要播放列表
        self.error_cursor_id = ""
        self.error_cursor_id_num = 0
        # courses
        self.courses = courses

    def get_current_course(self):
        for course in self.courses:
            # 0 未看完，1看完
            if course['status'] != '1':
                return course

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
        self.open_test()

    def judge_is_next_page(self):
        # 首次运行时记录主页面句柄
        if not self.main_window_handle:
            self.main_window_handle = self.driver.current_window_handle
            logger.debug(f"已记录主页面句柄: {self.main_window_handle}")

        try:
            # 等待class为"list"的div元素加载完成
            list_div = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "list"))
            )

            # 获取该div下的所有a标签
            a_tags = list_div.find_elements(By.TAG_NAME, "a")
            # logger.info(f"共找到{len(a_tags)}个a标签元素")

            # 遍历每个a标签，检查是否包含class为"status success"的div
            for index, a_tag in enumerate(a_tags, 1):
                try:
                    # 获取a标签的链接和文本
                    a_href = a_tag.get_attribute("href")
                    # 检查cursor_id是否为目标值（这里假设目标值是"special_cursor_id"）
                    if parse_courseid_by_regex(a_href) in self.no_play_videos:
                        continue
                    # 检查当前a标签内是否存在class为"status success"的div
                    a_tag.find_element(By.XPATH, ".//div[@class='status success']")

                except NoSuchElementException:
                    logger.info(f"{self.user_data_dir}第{index}个a标签:视频未播放完成，在新的标签页开始播放视频")

                    # 记录当前所有标签页句柄（点击前）
                    handles_before_click = self.driver.window_handles

                    # 点击a标签打开新页面
                    a_tag.click()

                    # 等待新标签页打开
                    WebDriverWait(self.driver, 10).until(EC.number_of_windows_to_be(len(handles_before_click) + 1))

                    # 获取所有标签页句柄（点击后）
                    all_handles = self.driver.window_handles

                    # 找到新打开的标签页句柄
                    new_handle = [h for h in all_handles if h not in handles_before_click][0]

                    # 关闭之前的标签页（除了新打开的页面）
                    for handle in all_handles:
                        if handle != new_handle:
                            self.driver.switch_to.window(handle)
                            self.driver.close()
                            logger.debug(f"已关闭标签页: {handle}")

                    # 切换到新打开的标签页
                    self.driver.switch_to.window(new_handle)
                    logger.debug(f"已切换到新标签页: {new_handle}")

                    # 解析课程ID
                    self.current_course_id = parse_courseid_by_regex(a_href)
                    logger.info(f"{self.user_data_dir}当前课程ID: {self.current_course_id}")

                    return False  # 找到未播放视频，返回False停止翻页

                except Exception as e:
                    logger.error(f"处理第{index}个a标签时出错: {str(e)}")

            logger.info(f"{self.user_data_dir}未找到需要播放的视频，点击下一页")
            return True  # 所有视频已完成，返回True继续翻页

        except TimeoutException:
            logger.warning("未找到class为'list'的div元素，可能已到最后一页")
            return False
        except Exception as e:
            # todo 异常情况重试
            logger.error(f"判断下一页时发生错误: {str(e)}")
            return False

    def is_element_exist(self, locator, timeout=10):
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False

    def open_test(self):
        base_url = "https://web.scgb.gov.cn/#/index"
        self.driver.get(f"{base_url}")
        time.sleep(2)
        course = self.get_current_course()
        # 必修
        new_url = f"https://web.scgb.gov.cn/#/course?id={course['id']}&className="
        logger.info(f"打开页面：{new_url}")
        self.driver.get(f"{new_url}")
        # 解析课程ID
        time.sleep(12)
        if self.is_element_exist((By.CLASS_NAME, "vjs-big-play-button")):
            try:
                required_div = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((
                        By.CLASS_NAME,
                        "vjs-big-play-button"
                    ))
                )
                if required_div:
                    required_div.click()
            except:
                logger.info("异常不处理")
        self.current_course_id = course['id']
        logger.info(f"{self.user_data_dir}当前课程ID: {self.current_course_id}")
    def check_study_time2(self):
        logger.info(f"{self.user_data_dir}判断当前学习任务选修和必修是否完成")
        url = "https://api.scgb.gov.cn/api/services/app/class/app/getClassDetailByUserId?classId=" + self.class_id
        try:
            response = requests.get(url=url, headers=self.headers)
            response_json = response.json()
            # logger.info(f"{self.user_data_dir}学习进度详情：{response_json}")
            self.send_check_result(str(round(int(response_json['result']['requiredPeriod']) / 3600, 1)),
                                   str(round(int(response_json['result']['electivePeriod']) / 3600, 1)))
            # 判断选修
            if int(response_json['result']['electivePeriod']) < int(
                    response_json['result']['classElectiveTimes']) * 60 * 60:
                logger.info(f"{self.user_data_dir}准备选修")
                self.is_must = False
                return True
            elif int(response_json['result']['requiredPeriod']) < int(response_json['result']['classTimes']) * 60 * 60:
                logger.info(f"{self.user_data_dir}准备必修")
                self.is_must = True
                return True
            # 判断必修
            logger.info(f"{self.user_data_dir}选修和必修已全部学完，结束课程")
            self.is_complete = True
            self.is_running = False
            return False
        except Exception as e:
            logger.error(f"{self.user_data_dir}获取学习时长失败: {str(e)}")
            return True

    def send_check_result(self, requiredPeriod, electivePeriod, mentioned_list=None, mentioned_mobile_list=None):
        update_data(self.username, requiredPeriod=requiredPeriod, electivePeriod=electivePeriod)
        content = self.user_data_dir + "学习进度：必修:" + requiredPeriod + ";选修:" + electivePeriod
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
                logger.info("发送成功")
        except Exception as e:
            logger.error(f"请求异常：{str(e)}")

    def check_course_success(self):
        sleep_time = 10
        call_login = False
        while self.is_running:
            if self.error_cursor_id_num == 2:
                logger.error(f"{self.user_data_dir}错误播放超过数超过6次，将当前课程放入不播放列表")
                update_data(self.username, cursor_id=self.error_cursor_id)
                self.current_course_id = ""
                self.error_cursor_id_num = 0
                threading.Thread(target=self.open_home, daemon=True).start()
                time.sleep(10)
                continue
            if self.sleep_time_num == 1:
                logger.error(f"{self.user_data_dir}睡眠重复次数超过3次，重新打开页面")
                self.is_login()
                logger.info(f"{self.user_data_dir}记录错误课程重试次数")
                if self.error_cursor_id == self.current_course_id:
                    self.error_cursor_id_num = self.error_cursor_id_num + 1
                else:
                    self.error_cursor_id = self.current_course_id
                    self.error_cursor_id_num = 0
                logger.info(
                    f"{self.user_data_dir}error_cursor_id:{self.error_cursor_id},error_cursor_id_num:{self.error_cursor_id_num}")
                self.current_course_id = ""
                self.sleep_time_num = 0
                threading.Thread(target=self.open_home, daemon=True).start()
                time.sleep(10)
                continue
            if not self.current_course_id:
                logger.info(f"{self.user_data_dir}课程id为空，间隔10秒，继续检测")
                time.sleep(10)
                continue
            check_play_success_url = "https://api.scgb.gov.cn/api/services/app/course/app/getCourseDetailByUserId?"
            logger.info(f"{self.user_data_dir}检测课程id: {self.current_course_id}")
            payload = {"courseId": self.current_course_id}
            try:
                course_detail = requests.post(check_play_success_url, headers=self.headers, json=payload)
                detail_json = course_detail.json()["result"]
                logger.info(f"{self.user_data_dir}的【{self.current_course_id}】课程详情: {detail_json}")
                if detail_json["totalPeriod"] <= detail_json["watchTimes"]:
                    if self.check_study_time2():
                        # 播放下一个视频
                        logger.info(
                            f"{self.user_data_dir}的【{self.current_course_id}】已观看完成，但未完成学时，继续播放下一个视频")
                        # 更新播放状态
                        update_course(self.username, self.current_course_id)
                        self.current_course_id = ""
                        threading.Thread(target=self.open_home, daemon=True).start()
                        sleep_time = 40
                    else:
                        logger.info("已全部观看完成，退出程序")
                        self.is_running = False
                        break
                else:
                    logger.info(f"{self.user_data_dir}的【{self.current_course_id}】未观看完成")
                    if not call_login:
                        total_period = detail_json['totalPeriod']
                        watch_times = detail_json['watchTimes']
                        logger.info(f"{self.user_data_dir}totalPeriod: {total_period}, watchTimes: {watch_times}")
                        sleep_time = (int(total_period) - int(watch_times))
                        # 间隔时间最小30秒，最大为：10分钟-20分钟以内的随机值
                        if sleep_time < 30:
                            sleep_time = 30
                        logger.debug("记录睡眠值，以及重复次数")
                        if self.sleep_time == sleep_time:
                            self.sleep_time_num = self.sleep_time_num + 1
                        else:
                            self.sleep_time = sleep_time
                            self.sleep_time_num = 0
                    else:
                        logger.info(f"{self.user_data_dir}重新登录，重新打开页面")
                        self.current_course_id = ""
                        threading.Thread(target=self.open_home, daemon=True).start()
                        sleep_time = 30
                call_login = False
            except TimeoutException:
                logger.error("链接超时")
                sleep_time = 10
            except Exception as e:
                logger.error(f"{self.user_data_dir}检测课程状态失败: {str(e)}，可能登陆失效，进行登录检测")
                self.is_login()
                call_login = True
                sleep_time = 20

            self.sleep(sleep_time)

    def sleep(self, sleep_time):
        # 超过600秒间隔，进行随机
        if sleep_time > 1800:
            rd = random.randint(1200, 1800)
            logger.info(f"{self.user_data_dir}间隔{rd}秒，继续检测")
            time.sleep(rd)
        else:
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
        while True:
            self.driver.get("https://web.scgb.gov.cn/#/index")
            time.sleep(2)
            # 检查登录状态
            store = self.get_local_storage_value("store")
            if store:
                try:
                    store_json = json.loads(store)
                    if "accessToken" in store_json['session']:
                        self.headers['Authorization'] = "Bearer " + store_json['session']['accessToken']
                        logger.info(f"已登录:{store_json['session']['nickName']}【{store_json['session']['organName']}】")
                        return store_json
                    else:
                        logger.warning("未登录，请登录")
                except json.JSONDecodeError:
                    logger.error("localStorage中store数据格式错误")
            else:
                logger.warning("未登录，请登录")
            self.auto_login()
            time.sleep(5)

    def auto_login(self):
        try:
            logger.info(f"{self.user_data_dir}开始自动登录")
            # 输入用户名
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

            # # 处理验证码
            capture_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="请输入验证码"]'))
            )
            capture_input.clear()
            captcha = self.get_formdata_img_src()
            capture_input.send_keys(captcha)
            # 点击登录按钮
            login_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//div[@class="ivu-form-item-content"]//button'))
            )
            login_button.click()
            # 判断是的为第一次登录，修改登录密码
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
                EC.presence_of_element_located((By.CLASS_NAME, "validate-form-img"))
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
        self.check_study_time2()
        self.open_home()
        threading.Thread(target=self.check_course_success, daemon=True).start()
        while self.is_running:
            time.sleep(1)
        logger.info(f"{self.user_data_dir}视频已全部播放完成")
        self.driver.close()
        update_data(self.username, status="2")


if __name__ == '__main__':
    continue_task()
    app.run(host='0.0.0.0', port=5002)
