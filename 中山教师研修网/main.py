import base64
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


config_path = "config.json"
play_result_data = read_json_config(config_path)


def select_data():
    # 打印结果
    if not play_result_data:
        print("task_config表中没有数据")
        return
    # 打印表头
    print(
        f" {'名称':<15} {'用户名':<10} {'密码':<15} {'是否头部':<8} {'起始索引':<8} {'进度':<8} {'创建时间'}")
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
            f"{row['requiredPeriod']:<8} "
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
    # todo 需要动态修改的
    target_num = 2
    result = select_data()
    for row in result:
        # 判断是否执行完成
        if int(row['requiredPeriod']) < target_num:
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
        # transparent_back(image_data)
        result = ocr.classification(image_data)
        logger.info(f"验证码识别结果: {result}")
        return result
    except Exception as e:
        logger.error(f"验证码识别失败: {str(e)}")
        return None


def transparent_back(img):
    img = img.convert('RGBA')
    L, H = img.size
    color_list = []  # 将需要去除的像素颜色放到列表当中
    for i in range(25):  # 找到范围
        color_list.append(img.getpixel((i, i)))
    for h in range(H):
        for l in range(L):
            dot = (l, h)
            color_1 = img.getpixel(dot)
            if color_1 in color_list:
                color_1 = color_1[:-1] + (0,)
                img.putpixel(dot, color_1)
    return img


def extract_value_from_url(url, key):
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
    value = query_params.get(key, [None])[0]
    return value


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


def download_captcha_image(driver, save_path="captcha.png"):
    """
    下载验证码图片

    Args:
        driver: Selenium WebDriver 实例
        save_path: 图片保存路径
    """
    try:
        # 等待验证码区域加载完成
        captcha_div = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.captcha-body.captcha"))
        )

        # 在验证码div内查找img标签
        img_element = captcha_div.find_element(By.TAG_NAME, "img")

        # 获取图片src属性
        img_src = img_element.get_attribute("src")

        if not img_src:
            print("未找到图片src属性")
            return False

        print(f"找到图片地址: {img_src}")

        # 下载并保存图片
        if img_src.startswith('data:image'):
            # 处理base64编码的图片
            return save_base64_image(img_src, save_path)
        else:
            # 处理URL图片
            return download_image_from_url(driver, img_src, save_path)

    except Exception as e:
        print(f"下载验证码图片失败: {e}")
        return False


def save_base64_image(base64_string, save_path):
    """保存base64编码的图片"""
    try:
        # 提取base64数据部分
        base64_data = re.sub('^data:image/.+;base64,', '', base64_string)

        # 解码并保存
        image_data = base64.b64decode(base64_data)
        with open(save_path, 'wb') as f:
            f.write(image_data)

        print(f"Base64图片已保存至: {save_path}")
        return True
    except Exception as e:
        print(f"保存Base64图片失败: {e}")
        return False


def parse_display_from_style(style_string):
    """
    从style字符串中解析display值
    """
    if not style_string:
        return "未设置"

    # 分割样式规则
    styles = style_string.split(';')

    for style in styles:
        style = style.strip()
        if style.startswith('display:'):
            # 提取display值
            return style.split(':')[1].strip()

    return "未找到display属性"


def download_image_from_url(driver, img_url, save_path):
    """从URL下载图片"""
    try:
        # 处理相对URL
        if img_url.startswith('//'):
            img_url = 'https:' + img_url
        elif img_url.startswith('/'):
            current_url = driver.current_url
            img_url = urljoin(current_url, img_url)

        # 获取当前页面的cookies
        cookies = driver.get_cookies()

        # 创建session并添加cookies
        session = requests.Session()
        for cookie in cookies:
            session.cookies.set(cookie['name'], cookie['value'])

        # 添加headers模拟浏览器
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        # 下载图片
        response = session.get(img_url, headers=headers, timeout=10)
        response.raise_for_status()

        # 保存图片
        with open(save_path, 'wb') as f:
            f.write(response.content)

        print(f"图片已保存至: {save_path}")
        return True

    except Exception as e:
        print(f"从URL下载图片失败: {e}")
        return False


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
            'Host': 'basic.sc.smartedu.cn',
            'Connection': 'keep-alive',
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

    def get_cookies_values(self, key):
        cookies = self.driver.get_cookies()
        for cookie in cookies:
            if cookie['name'] == key:
                return cookie['value']

        return None

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
            f"{self.user_data_dir}打开首页，检测视频学习情况")
        url = "https://m.zsjsjy.com/teacher/train/train/train/listForMine.do?paramMap[trainMode]="
        self.driver.get(url)
        time.sleep(5)
        table = self.driver.find_element(By.ID, "onlineTrain")
        trs = table.find_elements(By.TAG_NAME, "tr")

        # 使用切片从第二个tr开始遍历（索引1开始）
        for tr in trs[1:]:
            tds = tr.find_elements(By.TAG_NAME, "td")
            # 确保有足够的td元素
            if len(tds) > 5:
                div = tds[5].find_element(By.TAG_NAME, "div")
                if div.text == "视频未完成":
                    div.click()
                    self.open_course()
                    return
                elif div.text == "评价未完成":
                    div.click()
                    self.open_evaluate()

        logger.info("课程全部学完")
        # update_data(self.username, requiredPeriod=requiredPeriod)
        self.is_complete = True

    def open_course(self):
        try:
            original_window = self.driver.current_window_handle  # 记录原始标签页句柄
            # 等待新标签页打开（最多等待10秒）
            WebDriverWait(self.driver, 10).until(
                lambda d: len(d.window_handles) > 1
            )

            # 切换到新标签页
            for window_handle in self.driver.window_handles:
                if window_handle != original_window:
                    self.driver.switch_to.window(window_handle)
                    print("已切换到视频播放标签页")
                    break

            # 点击播放按钮
            play_button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "canvas[class^='play'][class$='-canvas']")))
            # play_button = self.driver.find_element(By.XPATH, "playchjkprhusbvs-canvas")
            play_button.click()
        except TimeoutException:
            logger.info("超过10秒未找到课程列表元素")

    def open_evaluate(self):
        original_window = self.driver.current_window_handle  # 记录原始标签页句柄
        # 等待新标签页打开（最多等待10秒）
        WebDriverWait(self.driver, 10).until(
            lambda d: len(d.window_handles) > 1
        )

        # 切换到新标签页
        for window_handle in self.driver.window_handles:
            if window_handle != original_window:
                self.driver.switch_to.window(window_handle)
                logger.info("已切换到新标签页")
                break
        logger.info("视频播放完成，准备开始评价")
        time.sleep(5)
        main = self.driver.find_element(By.CLASS_NAME, "g-pk-main")
        tb = main.find_element(By.CLASS_NAME, "m-pk-tb")
        tds = tb.find_elements(By.TAG_NAME, "td")
        ps = tds[0].find_elements(By.TAG_NAME, "p")
        for p in ps:
            spans = p.find_elements(By.TAG_NAME, "span")
            spans[5].click()

        submit = self.driver.find_element(By.XPATH, ".//a[text()='提交评价']")
        submit.click()
        confirm = self.driver.find_element(By.XPATH, ".//a[text()='确定']")
        confirm.click()
        logger.info("视频播放完成，提交评价")
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
        logger.info("已切换回原始标签页")

    def check_course_success(self):
        sleep_time = 10
        time.sleep(10)
        while not self.is_complete:
            try:
                logger.info(f"{self.user_data_dir}检测开始课程")
                # 定位元素
                element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-title='点击暂停']"))
                )

                # 获取style属性
                style_attr = element.get_attribute("style")

                # 解析display值
                display_value = parse_display_from_style(style_attr)
                if display_value == "none":
                    logger.info("当前课程已完成，继续下一个")
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
                    logger.info("已切换回原始主页标签页")
                    threading.Thread(target=self.open_home, daemon=True).start()
                else:
                    logger.info("当前课程未完成，等待下一次检测")
                    sleep_time = random.randint(150, 300)
                logger.info(f"元素的display属性值为: {display_value}")
                logger.info(f"{self.user_data_dir}间隔{sleep_time}秒，继续检测")
                time.sleep(sleep_time)
            except Exception as e:
                time.sleep(30)
                logger.info("检测异常，间隔30秒，继续检测")

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
            # time.sleep(10)
            # self.driver.get("https://gp.chinahrt.com/index.html#/v_user_set")
            time.sleep(3)
            # 检查登录状态
            jwtToken = self.get_cookies_values("JSESSIONID")

            if jwtToken:
                # realName = self.get_session_storage_value("realName")
                # orgName = self.get_session_storage_value("orgName")
                self.headers['x-token'] = jwtToken
                logger.info(f"已登录:{self.username}")
                return
            else:
                logger.warning(f"{self.user_data_dir}未登录，请登录")

    def auto_login(self):
        try:
            logger.info(f"{self.user_data_dir}开始自动登录")
            self.driver.get(
                "https://tyrz.gd.gov.cn/pscp/sso/static/?redirect_uri=https%3A%2F%2Fsmartauth.zsedu.cn%2Fsso%2Fgzc%2Fredirect_callback%3Fclient_name%3Dgd-gzc%26original%3Dhttps%253A%252F%252Fm.zsjsjy.com%252Flogin.do%253Ftheme%253Dzsjsjy&client_id=tyrz_zs_zhjy")
            time.sleep(2)
            # 切换到账号密码模式
            password_model = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, '账号密码'))
            )
            password_model.click()

            # 账号
            username_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='请输入账号']"))
            )
            username_input.clear()
            username_input.send_keys(self.username)

            # 密码
            password_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='请输入密码']"))
            )
            password_input.clear()
            password_input.send_keys(self.password)

            # # 处理验证码
            capture_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="请输入图中算式的计算结果"]'))
            )
            capture_input.clear()
            # captcha = self.get_formdata_img_src()
            # capture_input.send_keys(captcha)
            time.sleep(10)
            # 点击登录
            login_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.gd-btn.gd-btn-primary'))
            )
            login_button.click()

        except TimeoutException:
            logger.error("超时未找到登录相关输入框")
        except ElementNotInteractableException:
            logger.error("登录输入框不可交互")
        except Exception as e:
            logger.error(f"自动登录失败: {str(e)}")

    def exec_main(self):
        self.init_browser()
        # 判断用户是否登录
        self.is_login()
        self.open_home()
        threading.Thread(target=self.check_course_success, daemon=True).start()
        # threading.Thread(target=self.check_course_play_status, daemon=True).start()
        while not self.is_complete:
            time.sleep(1)
        logger.info(f"{self.user_data_dir}视频已全部播放完成")
        self.driver.close()
        # update_data(self.username, status="2")


if __name__ == '__main__':
    continue_task()
    app.run(host='0.0.0.0', port=7002)
