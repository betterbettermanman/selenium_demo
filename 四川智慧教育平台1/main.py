import json
import os
import random
import re
import sys
import threading
import time
from urllib.parse import unquote

import ddddocr
import requests
from flask import Flask
from loguru import logger
from selenium import webdriver
from selenium.common import TimeoutException, ElementNotInteractableException
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


def select_data():
    global max_course_num, max_task_num, chapterId_list

    play_result_data = read_json_config(config_path)
    # 打印结果
    if not play_result_data:
        print("task_config表中没有数据")
        return
    # 打印表头
    print(
        f" {'名称':<15} {'用户名':<10} {'密码':<15} {'是否头部':<8} {'进度':<8}")
    print("-" * 80)
    max_task_num = play_result_data['max_task_num']
    max_course_num = play_result_data['max_course_num']
    chapterId_list = play_result_data['chapterId_list']
    # 打印每条记录
    for row in play_result_data['data']:
        # 处理datetime对象的格式化
        print(
            f"{row['name']:<15} "
            f"{row['username']:<10} "
            f"{row['password']:<15}       "
            f"{row['is_head']:<8}   "
            f"{row['requiredPeriod']:<8} "
        )

    print(f"\n共查询到 {len(play_result_data)} 条记录")
    return play_result_data['data']


def update_data(username, status=None, requiredPeriod=None, electivePeriod=None):
    json_config = read_json_config(config_path)
    for data in json_config['data']:
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
        json.dump(json_config, f, ensure_ascii=False, indent=2)  # indent=2 保持格式化
    logger.info(f"{username}数据更新成功,数据值：{requiredPeriod}")


# 添加容器，一次最多运行15个，然后动态检测，是否运行完成，运行完成，重新添加进去
task_contain = []
max_task_num = 10
max_course_num = 0
chapterId_list = {
    "1983723413983899648": [0, 1],
    "1985277519445798912": [2, 3],
    "1985638406501347328": [4, 5, 6, 7],
}


def continue_task():
    logger.info("重启任务")
    result = select_data()
    complete_status = True
    for row in result:
        if len(task_contain) >= max_task_num:
            break
        # 判断当前容器是否包含当前任务
        if row['username'] in task_contain:
            logger.info(f"当前容器{task_contain}包含当前任务：{row['username']}")
            continue
        # 判断是否执行完成
        if int(row['requiredPeriod']) == max_course_num:
            logger.info(f"{row['username']}已播放完成")
            continue
        complete_status = False
        check = TeacherTrainingChecker(row['name'], row['username'], row['password'],
                                       row['is_head'])
        thread = threading.Thread(target=check.exec_main)  # 注意这里没有()
        thread.start()  # 启动线程
        task_contain.append(row['username'])
        time.sleep(10)
    if complete_status:
        logger.info(f"✅✅✅✅✅✅✅✅✅任务已全部完成！✅✅✅✅✅✅✅✅✅")


class TeacherTrainingChecker:
    def __init__(self, name, username, password, isHead):
        """
        初始化教师培训课程检查器（使用外部传入的浏览器实例）

        :param wait: 共享的显式等待对象
        :param target_courses: 需要检查的目标课程列表
        :param base_url: 培训首页URL
        """
        self.is_headless = isHead
        self.user_data_dir = name
        self.username = username
        self.password = password
        self.current_course_id = ""
        self.headers = {
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'Accept': '*/*',
            'Host': 'basic.sc.smartedu.cn',
            'Connection': 'keep-alive',
        }
        # 默认检测时间，当时间重复3次，说明观看异常，重新打开页面进行观看
        self.sleep_time = 10
        self.sleep_time_num = 0
        # 全局变量存储当前课程ID和主页面句柄
        self.main_window_handle = None  # 用于存储主页面的句柄
        # 是否完成全部视频
        self.is_complete = False
        # chapterId
        self.chapterId = ""
        # 上一次进度值
        self.schedule = -1

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

    def open_home(self):
        if self.is_complete:
            return
        logger.info(f"{self.user_data_dir}进行学习")
        logger.info(
            f"{self.user_data_dir}打开首页，检测视频学习情况")
        url = "https://basic.sc.smartedu.cn/hd/teacherTraining/coursedatail?courseId=1983723370145034240"
        self.driver.get(url)
        time.sleep(10)
        divs = self.driver.find_elements(By.CLASS_NAME, "course-list-cell")
        required_period = 0
        if len(divs) == 0:
            logger.info(f"{self.user_data_dir}获取页面失败，重新打开首页")
            jwtToken = self.get_cookies_values("Teaching_Autonomic_Learning_Token")
            if jwtToken:
                threading.Thread(target=self.open_home, daemon=True).start()
                return
            else:
                threading.Thread(target=self.sss, daemon=True).start()
                return
        for index, div in enumerate(divs):
            required_period = required_period + 1
            try:
                status = div.find_element(By.XPATH, ".//div[@class='status']")
                if status.text != "已学习":
                    div.click()
                    logger.info(f"{self.user_data_dir}点击未播放视频,当前进度{index + 1}/{len(divs)}")
                    time.sleep(10)
                    # 点击播放按钮
                    video = WebDriverWait(self.driver, 20).until(
                        EC.element_to_be_clickable((By.ID, 'video'))
                    )
                    self.driver.execute_script("arguments[0].play();", video)
                    logger.info(f"{self.user_data_dir}开始播放")
                    # 从url中提取course_id
                    self.current_course_id = self.extract_param_from_hash_url(self.driver.current_url, "subsectionId")
                    # 切换chapterId
                    # 遍历字典，检查index是否在键数组中
                    for key, value_list in chapterId_list.items():
                        if index in value_list:
                            self.chapterId = key
                            break  # 找到后退出循环
                    return
            except Exception as e:
                div.click()
                logger.info("点击未播放视频")
                time.sleep(5)
                # 点击播放按钮
                video = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.ID, 'video'))
                )
                self.driver.execute_script("arguments[0].play();", video)
                logger.info("开始播放")
                # 从url中提取course_id
                self.current_course_id = self.extract_param_from_hash_url(self.driver.current_url, "subsectionId")
                # 切换chapterId
                # 遍历字典，检查index是否在键数组中
                for key, value_list in chapterId_list.items():
                    if index in value_list:
                        self.chapterId = key
                        break  # 找到后退出循环
                return

        update_data(self.username, requiredPeriod=required_period)
        self.is_complete = True

    def sss(self):
        self.is_login()
        self.open_home()

    def check_course_success(self):
        sleep_time = 10
        while not self.is_complete:
            check_play_success_url = f"https://basic.sc.smartedu.cn/hd/teacherTraining/api/studyCourseUser/chapterProcess?chapterId={self.chapterId}"
            logger.info(f"{self.user_data_dir}检测课程id: {self.current_course_id}")
            if self.current_course_id != "":
                try:
                    course_detail = requests.get(check_play_success_url, headers=self.headers)
                    # 可以打印完整的URL来验证
                    logger.info(f"{self.user_data_dir}完整请求URL: {course_detail.url}")
                    detail_json = course_detail.json()["returnData"]["studySubsectionUsers"]
                    logger.info(f"{self.user_data_dir}的【{self.current_course_id}】课程详情: {detail_json}")
                    for detail in detail_json:
                        if self.current_course_id == detail["subsectionId"]:

                            if int(detail["schedule"]) >= 100:
                                logger.info(
                                    f"{self.user_data_dir}的【{self.current_course_id}】已观看完成，继续播放下一个视频")
                                threading.Thread(target=self.open_home, daemon=True).start()
                            else:
                                # 判断当前进度值，与上一次是否相等，如果相等，就说明，播放异常，重新打开
                                if self.schedule == int(detail["schedule"]):
                                    logger.info("两次进度一致，播放异常，重新打开")
                                    threading.Thread(target=self.open_home, daemon=True).start()

                                # 当前视频未播放完成，间隔5-10分钟继续检测
                                logger.info(
                                    f"{self.user_data_dir}的【{self.current_course_id}】未观看完成，进度：{detail['schedule']}")
                                sleep_time = random.randint(150, 300)

                except TimeoutException:
                    logger.error("链接超时")
                    continue
                except Exception as e:
                    logger.error(f"{self.user_data_dir}检测课程状态失败: {str(e)}，可能登陆失效，进行登录检测")
                    self.is_login()
                    sleep_time = 20
            else:
                sleep_time = 30
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
        if not self.is_headless:
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
            time.sleep(5)
            # 检查登录状态
            jwtToken = self.get_cookies_values("Teaching_Autonomic_Learning_Token")

            if jwtToken:
                self.headers['x-token'] = jwtToken
                logger.info(f"已登录:{self.username}")
                return
            else:
                logger.warning(f"{self.user_data_dir}未登录，请登录")
            self.auto_login()

    def auto_login(self):
        try:
            logger.info(f"{self.user_data_dir}开始自动登录")
            self.driver.get(
                "https://basic.sc.smartedu.cn/ThirdPortalService/user/otherlogin!login.ac?appkey=C56DA16ECBC56FBEEC908DA09E45C72C917A80118F057FA1F0B5BAE41CC9CC9DECD5BDB7133FE17C328C5D37B37CA8E7&pkey=5D79CA42E45C5273DF8532D09E1F158B15E25919CDB958940F84D5E63F5F53A1ECD5BDB7133FE17C328C5D37B37CA8E7&params=718F83A5347CBFDB7D1A9065FA090FE949D92330BB9A3351FE0715C5B8A3E86F37916C1004E835C7C7F964E3F301477F7D37F04485FA8707845DAAA23356236ED1D326CF5A5E3C263470516EE9B4A2ED")
            time.sleep(2)

            username_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'loginName'))
            )
            username_input.clear()
            username_input.send_keys(self.username)

            password_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'password'))
            )
            password_input.send_keys(self.password)

            login_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'submit-btn'))
            )
            login_button.click()
            # 尝试5秒检测是否存在，确认弹框，如果找到，点击取消，如果没找到，直接跳过
            try:
                # 查找包含"取消"文本的a标签
                cancel_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), '取消')]"))
                )
                cancel_button.click()
                logger.info(f"{self.user_data_dir}成功点击取消按钮")
            except TimeoutException:
                logger.info(f"{self.user_data_dir}5秒内未找到取消按钮，跳过")
        except TimeoutException:
            logger.error("超时未找到登录相关输入框")
        except ElementNotInteractableException:
            logger.error("登录输入框不可交互")
        except Exception as e:
            logger.error(f"自动登录失败: {str(e)}")

    def exec_main(self):
        global task_contain
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
        task_contain = [num for num in task_contain if num != self.username]
        # 重新触发任务，将任务加到指定数量
        logger.info("重新触发任务，将任务加到指定数量")
        continue_task()


if __name__ == '__main__':
    continue_task()
    app.run(host='0.0.0.0', port=7002)
