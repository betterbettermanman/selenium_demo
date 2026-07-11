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
from selenium.common import TimeoutException, ElementNotInteractableException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

# 初始化Flask应用
app = Flask(__name__)

# 初始化ocr识别器
ocr = ddddocr.DdddOcr()


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
        if int(row['requiredPeriod']) >= max_course_num:
            logger.info(f"{row['username']}已播放完成")
            continue
        complete_status = False
        check = TeacherTrainingChecker(row['name'], row['username'], row['password'],
                                       row['is_head'])
        thread = threading.Thread(target=check.exec_main)  # 注意这里没有()
        thread.start()  # 启动线程
        task_contain.append(row['username'])
        time.sleep(20)
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

    @staticmethod
    def parse_score_value(text):
        match = re.search(r'(\d+(?:\.\d+)?)', text or '')
        return float(match.group(1)) if match else 0

    def get_user_info(self):
        card = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "userbox"))
        )
        p_elements = card.find_elements(By.TAG_NAME, "p")
        user_info = {}
        for p in p_elements:
            text = p.text
            if "：" in text:
                key, value = text.split("：", 1)
                user_info[key.strip()] = value.strip()
        logger.info(user_info)
        return user_info

    def dismiss_popups(self):
        try:
            cancel_button = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.ID, "noWx"))
            )
            cancel_button.click()
            logger.info(f"{self.user_data_dir}关闭微信绑定提示")
        except (TimeoutException, NoSuchElementException):
            pass

    def start_course_chapter(self):
        if "/chapter/" in self.driver.current_url:
            self.current_course_id = self.driver.current_url.rsplit("/chapter/", 1)[-1]
            logger.info(f"{self.user_data_dir}开始学习章节: {self.current_course_id}")
            return True

        for chapter in self.driver.find_elements(By.CSS_SELECTOR, "li"):
            try:
                link = chapter.find_element(By.CSS_SELECTOR, "a[href*='/chapter/']")
            except NoSuchElementException:
                continue
            if "获得" in chapter.text:
                continue
            link.click()
            time.sleep(3)
            self.current_course_id = link.get_attribute("href").rsplit("/chapter/", 1)[-1]
            logger.info(f"{self.user_data_dir}点击未学章节: {chapter.text.strip()[:40]}")
            return True
        return False

    def open_daily_study(self):
        logger.info(f"{self.user_data_dir}打开日常学法")
        self.driver.get("https://www.scxfks.com/study/courses/year")
        time.sleep(3)

        study_links = self.driver.find_elements(By.LINK_TEXT, "进入学习")
        for index in range(len(study_links)):
            study_links = self.driver.find_elements(By.LINK_TEXT, "进入学习")
            if index >= len(study_links):
                break
            study_links[index].click()
            time.sleep(3)
            if self.start_course_chapter():
                return
            self.driver.get("https://www.scxfks.com/study/courses/year")
            time.sleep(2)

        self.driver.get("https://www.scxfks.com/study/courses/all")
        time.sleep(3)
        for link_text in ["继续学习", "开始学习", "进入学习"]:
            for study_link in self.driver.find_elements(By.LINK_TEXT, link_text):
                study_link.click()
                time.sleep(3)
                if self.start_course_chapter():
                    return

        logger.info(f"{self.user_data_dir}未找到可学习的课程")

    def open_exam(self):
        logger.info(f"{self.user_data_dir}打开法治素养测评")
        self.driver.get("https://www.scxfks.com/study/exam")
        time.sleep(3)

        page_text = self.driver.find_element(By.TAG_NAME, "body").text
        if "暂无测评安排" in page_text:
            logger.info(f"{self.user_data_dir}暂无测评安排，任务结束")
            self.is_complete = True
            return

        for link_text in ["进入考场", "开始测评", "参加考试"]:
            try:
                link = self.driver.find_element(By.LINK_TEXT, link_text)
                link.click()
                logger.info(f"{self.user_data_dir}进入测评考场")
                time.sleep(3)
                return
            except NoSuchElementException:
                continue

        logger.info(f"{self.user_data_dir}暂无可参加的测评")
        self.is_complete = True

    def open_home(self):
        if self.is_complete:
            return
        logger.info(f"{self.user_data_dir}打开首页，检测学习情况")
        self.driver.get("https://www.scxfks.com/study/index")
        time.sleep(3)
        self.dismiss_popups()
        user_info = self.get_user_info()
        credit_score = self.parse_score_value(user_info.get("学分累计", "0"))

        if credit_score < 100:
            self.open_daily_study()
        else:
            self.open_exam()

    # 判断是否结束
    def is_video_paused(self, video_element):
        return self.driver.execute_script("return arguments[0].paused;", video_element)

    def sss(self):
        self.is_login()
        self.open_home()

    def check_course_success(self):
        while not self.is_complete:
            sleep_time = 10
            try:
                if "/chapter/" in self.driver.current_url:
                    try:
                        limit_div = self.driver.find_element(By.CSS_SELECTOR, "div.limit")
                        if "已到达今日上限" in limit_div.text:
                            logger.info(f"{self.user_data_dir}已到达今日上限，1小时后重试")
                            sleep_time = 3600
                            time.sleep(sleep_time)
                            continue
                    except NoSuchElementException:
                        pass

                    wait_time = random.randint(10, 15)
                    logger.info(f"{self.user_data_dir}章节 {self.current_course_id} 学习中，等待{wait_time}秒")
                    time.sleep(wait_time)

                    back_btn = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'返回目录')]"))
                    )
                    back_btn.click()
                    logger.info(f"{self.user_data_dir}章节学习完成，返回目录")
                    time.sleep(3)
                    threading.Thread(target=self.open_home, daemon=True).start()
                    sleep_time = 30
                else:
                    if not self._is_logged_in():
                        logger.warning(f"{self.user_data_dir}登录失效，重新登录")
                        self.is_login()
                    sleep_time = 30
            except Exception as e:
                logger.error(f"{self.user_data_dir}检测学习状态失败: {str(e)}")
                if self._is_logged_in():
                    threading.Thread(target=self.open_home, daemon=True).start()
                else:
                    self.is_login()
                sleep_time = 20
            logger.info(f"{self.user_data_dir}间隔{sleep_time}秒，继续检测")
            time.sleep(sleep_time)

    def retry_play(self):
        max_retries = 5
        retry_count = 0
        # 点击播放按钮
        try:
            video = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'video'))
            )
            while max_retries > retry_count:
                self.driver.execute_script("arguments[0].play();", video)
                is_paused = self.is_video_paused(video)
                logger.info(f"{self.user_data_dir}暂停状态：{is_paused}")
                if not is_paused:
                    break
                time.sleep(5)
                retry_count += 1
        except Exception as e:
            logger.info(f"{self.user_data_dir}重播异常不处理")

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

    def _is_logged_in(self):
        if "/study/login" in self.driver.current_url:
            return False
        try:
            self.driver.find_element(By.CLASS_NAME, "userbox")
            return True
        except NoSuchElementException:
            pass
        try:
            self.driver.find_element(By.LINK_TEXT, "退出登录")
            return True
        except NoSuchElementException:
            pass
        return False

    def _get_login_tip(self):
        try:
            return self.driver.find_element(By.CSS_SELECTOR, "div.tip").text.strip()
        except NoSuchElementException:
            return ""

    def _refresh_captcha(self):
        try:
            self.driver.find_element(By.CLASS_NAME, "captcha").click()
            time.sleep(1)
        except NoSuchElementException:
            pass

    def _handle_login_notice(self):
        try:
            know_checkbox = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, "know"))
            )
            if not know_checkbox.is_selected():
                know_checkbox.click()
            WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.ID, "yes"))
            ).click()
            time.sleep(2)
            return True
        except TimeoutException:
            return False

    def is_login(self):
        if self._is_logged_in():
            logger.info(f"已登录:{self.username}")
            return
        logger.warning(f"{self.user_data_dir}未登录，请登录")
        self.auto_login()

    def auto_login(self):
        logger.info(f"{self.user_data_dir}开始自动登录")
        self.driver.get("https://www.scxfks.com/study/login")
        time.sleep(2)

        retry_count = 0
        while not self._is_logged_in():
            retry_count += 1
            logger.info(f"{self.user_data_dir}登录尝试第{retry_count}次")
            try:
                try:
                    login_btn = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.LINK_TEXT, "使用账号登录"))
                    )
                    login_btn.click()
                    time.sleep(1)
                except TimeoutException:
                    pass

                username_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='mobile']"))
                )
                username_input.clear()
                username_input.send_keys(self.username)

                password_input = self.driver.find_element(By.CSS_SELECTOR, "input[name='password']")
                password_input.clear()
                password_input.send_keys(self.password)

                if retry_count > 1:
                    self._refresh_captcha()

                capture_input = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='captcha']"))
                )
                capture_input.clear()
                captcha = self.get_formdata_img_src()
                if not captcha:
                    logger.warning(f"{self.user_data_dir}验证码识别为空，刷新后重试")
                    self._refresh_captcha()
                    continue
                capture_input.send_keys(captcha)

                login_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, 'button'))
                )
                login_button.click()
                self._handle_login_notice()
                time.sleep(3)

                if self._is_logged_in():
                    logger.info(f"{self.user_data_dir}登录成功，已进入首页")
                    return

                tip = self._get_login_tip()
                logger.warning(f"{self.user_data_dir}登录失败: {tip or '未知错误'}，重新识别验证码")
                self._refresh_captcha()
                time.sleep(1)
            except TimeoutException:
                logger.error(f"{self.user_data_dir}登录超时，刷新页面重试")
                self.driver.get("https://www.scxfks.com/study/login")
                time.sleep(2)
            except ElementNotInteractableException:
                logger.error(f"{self.user_data_dir}登录输入框不可交互，刷新页面重试")
                self.driver.get("https://www.scxfks.com/study/login")
                time.sleep(2)
            except Exception as e:
                logger.error(f"{self.user_data_dir}自动登录异常: {str(e)}，重试")
                time.sleep(2)

    def get_formdata_img_src(self, wait_time=10):
        """获取验证码图片并识别"""
        try:
            os.makedirs("png", exist_ok=True)
            formdata_div = WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'captcha'))
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
        global task_contain
        self.init_browser()
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
