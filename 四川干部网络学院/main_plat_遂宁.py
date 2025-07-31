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


config_path = "play_result_遂宁.json"
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

    def get_local_storage_value(self, key):
        """从localStorage中获取指定键的值"""
        try:
            value = self.driver.execute_script(f"return window.localStorage.getItem('{key}');")
            return value
        except Exception as e:
            logger.error(f"获取localStorage值失败: {str(e)}")
            return None

    def get_source_compulsory_elective(self):
        """获取必修和选修进度"""
        # 打开个人中心，检测未结业班级列表
        self.driver.get("https://web.scgb.gov.cn/#/personal")
        time.sleep(10)

        try:
            # 等待包含class为num-info的div元素加载完成
            num_info_div = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "num-info"))
            )

            # 获取该div下所有的span元素
            span_elements = num_info_div.find_elements(By.TAG_NAME, "span")

            # 提取所有span元素的文本值
            span_values = [span.text for span in span_elements if span.text.strip()]

            # 打印结果
            return span_values[2] == "100%", span_values[5] == "100%"
        except Exception as e:
            logger.error("获取比选失败")

    def play_specify_video(self):
        if self.specify_video:
            for video in self.specify_video:
                self.driver.get(video["url"])
                self.current_course_id = video["course_id"]
                return True
        return False

    def open_home(self):
        if self.is_complete:
            return
        if self.is_must:
            self.open_home2()
            return
        if self.play_specify_video():
            return
        logger.info(f"{self.user_data_dir}进行选修学习")
        logger.info(
            f"{self.user_data_dir}打开首页，检测视频学习情况，current_video_url_index：{self.current_video_url_index}")
        url = "https://web.scgb.gov.cn/#/specialColumn/course?channelId=01957f20-dacd-76d7-8883-71f375adaab5&id=0194693f-09a5-7875-a64f-1573512205c7&channelName=%E4%B8%AD%E5%9B%BD%E5%BC%8F%E7%8E%B0%E4%BB%A3%E5%8C%96%E7%90%86%E8%AE%BA%E4%BD%93%E7%B3%BB"
        self.driver.get(url)
        # 切换左侧标签
        # 等待10秒，检查是否存在同时有两个类名的元素
        try:
            title = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[@title='" + self.video_name[self.current_video_url_index] + "']"))
            )
            title.click()
            time.sleep(5)
        except Exception as e:
            logger.error(f"检测首页异常，进行重试")
            threading.Thread(target=self.open_home, daemon=True).start()
            return
        is_next_page = self.judge_is_next_page()
        while is_next_page:
            # 当存在class：ivu-page-next ivu-page-disabled说明没有下一页了
            # 首先检查是否存在同时包含两个类名的元素
            try:
                # 等待10秒，检查是否存在同时有两个类名的元素
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".ivu-page-next.ivu-page-disabled"))
                )
                logger.info("存在 class 为 'ivu-page-next ivu-page-disabled' 的元素")
                self.current_video_url_index = self.current_video_url_index + 1
                threading.Thread(target=self.open_home, daemon=True).start()
                break
            except TimeoutException:
                # 如果不存在，检查是否只存在"ivu-page-next"类的元素
                try:
                    element = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "ivu-page-next"))
                    )
                    logger.info(f"{self.user_data_dir}存在 class 为 'ivu-page-next' 的元素")
                    element.click()
                    time.sleep(2)
                    is_next_page = self.judge_is_next_page()
                except Exception as e:
                    logger.error(f"{self.user_data_dir}两个类名的元素都不存在")

            except Exception as e:
                logger.error(f"翻页操作失败: {str(e)}")
                break

    def open_home2(self):
        try:
            logger.info(f"{self.user_data_dir}进行必修学习")
            # 必修
            self.driver.get("https://web.scgb.gov.cn/#/myClass?id=0197beca-df9e-7a23-9b84-eb2bb4c43ecf&collected=1")
            time.sleep(5)
            # 等待包含class为num-info的div元素加载完成

            required_div = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    "//div[@class='item' and text()=' 必修 ']"
                ))
            )
            required_div.click()
            time.sleep(5)
            is_next_page = self.judge_is_next_page2()
            while is_next_page:
                # 如果不存在，检查是否只存在"ivu-page-next"类的元素
                try:
                    element = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "ivu-page-next"))
                    )
                    logger.info(f"{self.user_data_dir}存在 下一页 的元素，点击")
                    element.click()
                    time.sleep(2)
                    is_next_page = self.judge_is_next_page2()
                except Exception as e:
                    logger.error("两个类名的元素都不存在")

        except TimeoutException:
            print("超时：未找到class为'course-list'的元素")
        except Exception as e:
            print(f"发生错误：{str(e)}")

    def judge_is_next_page2(self):
        logger.info(f"{self.user_data_dir}判断是否有可以播放的视频")
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

                        # 点击a标签打开新页面
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
                            logger.info(f"{self.user_data_dir}检测到目标cursor_id，已关闭新页面")

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
                        logger.debug(f"{self.user_data_dir}已切换到新标签页: {new_handle}")
                        # 解析课程ID
                        self.current_course_id = extract_id_from_url(new_page_url)
                        logger.info(f"{self.user_data_dir}当前课程ID: {self.current_course_id}")
                        return False  # 找到未播放视频，返回False停止翻页

            except Exception as e:
                print(f"处理第{index}个div时出错：{str(e)}\n")

        logger.info(f"{self.user_data_dir}未找到需要播放的视频，点击下一页")
        return True  # 所有视频已完成，返回True继续翻页

    def check_study_time(self):
        logger.info(f"{self.user_data_dir}判断当前学习任务是否大于50学时")
        url = "https://api.scgb.gov.cn/api/services/app/class/app/getStudyProcess"
        try:
            response = requests.get(url=url, headers=self.headers)
            response_json = response.json()
            logger.info(f"{self.user_data_dir}当前已学习时长: {response_json['result']['timesSum']}")
            if int(response_json['result']['timesSum']) > 100:
                return False
            else:
                return True
        except Exception as e:
            logger.error(f"{self.user_data_dir}获取学习时长失败: {str(e)}")
            return True

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

    def check_study_time2(self):
        logger.info(f"{self.user_data_dir}判断当前学习任务选修和必修是否完成")
        url = "https://api.scgb.gov.cn/api/services/app/class/app/getClassDetailByUserId?classId=019815fe-ec44-753d-9b1d-554f017df106"
        try:
            response = requests.get(url=url, headers=self.headers)
            response_json = response.json()
            logger.info(f"{self.user_data_dir}学习进度详情：{response_json}")
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
                    # 检查当前a标签内是否存在class为"status success"的div
                    a_tag.find_element(By.XPATH, ".//div[@class='status success']")
                    # logger.info(f"第{index}个a标签：视频播放完成")

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
            logger.error(f"判断下一页时发生错误: {str(e)}")
            return False

    def check_course_success(self):
        sleep_time = 10
        call_login = False
        while self.is_running:
            if self.sleep_time_num == 3:
                logger.info(f"{self.user_data_dir}睡眠重复次数超过3次，重新打开页面")
                self.is_login()
                threading.Thread(target=self.open_home, daemon=True).start()
                self.current_course_id = ""
                self.sleep_time_num = 0
                time.sleep(10)
                continue
            check_play_success_url = "https://api.scgb.gov.cn/api/services/app/course/app/getCourseDetailByUserId?"
            logger.info(f"{self.user_data_dir}检测课程id: {self.current_course_id}")
            if self.current_course_id != "":
                payload = {
                    "courseId": self.current_course_id
                }
                try:
                    course_detail = requests.post(check_play_success_url, headers=self.headers,
                                                  json=payload)
                    detail_json = course_detail.json()["result"]
                    logger.info(f"{self.user_data_dir}的【{self.current_course_id}】课程详情: {detail_json}")
                    if detail_json["totalPeriod"] == detail_json["watchTimes"]:
                        if self.check_study_time2():
                            # 播放下一个视频
                            logger.info(
                                f"{self.user_data_dir}的【{self.current_course_id}】已观看完成，但未完成学时，继续播放下一个视频")
                            threading.Thread(target=self.open_home, daemon=True).start()
                            self.current_course_id = ""
                            sleep_time = 60
                        else:
                            logger.info("已全部观看完成，退出程序")
                            self.is_running = False
                            break
                    else:
                        logger.info(f"{self.user_data_dir}的【{self.current_course_id}】未观看完成")
                        if not call_login:
                            logger.info(
                                f"{self.user_data_dir}totalPeriod: {detail_json['totalPeriod']}, watchTimes: {detail_json['watchTimes']}")
                            sleep_time = (int(detail_json["totalPeriod"]) - int(detail_json["watchTimes"]))
                            # 间隔时间最小30秒，最大为：10分钟-20分钟以内的随机值
                            if sleep_time < 30:
                                sleep_time = 30
                            if sleep_time > 600:
                                sleep_time = random.randint(600, 1200)
                        else:
                            logger.info("重新登录，重新打开页面")
                            threading.Thread(target=self.open_home, daemon=True).start()
                            self.current_course_id = ""
                    call_login = False
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
    app.run(host='0.0.0.0', port=6002)
