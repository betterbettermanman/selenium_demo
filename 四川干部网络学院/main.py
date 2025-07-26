import base64
import json
import os
import re
import sys
import threading
import time

import ddddocr
import requests
from loguru import logger
from selenium import webdriver
from selenium.common import TimeoutException, NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

current_course_id = ""
is_running = True
headers = {
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'X-Access-Token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2NDIxMTQ5MjAsInVzZXJuYW1lIjoiYWRtaW4ifQ.-HyWQh6A9y6ZmclS7ltpBu-GFb3liVk5VVj6laavOg0',
    'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
    'Accept': '*/*',
    'Host': 'www.cdjxjy.com',
    'Connection': 'keep-alive',
    "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJPcmdhbklkIjoiMDE5ODMxMDAtZGI1Ni03MWNjLWI2NGQtNmY4NGQwYWM3MGQwIiwiQ2xpZW50VHlwZSI6IiIsIk9yZ2FuTmFtZSI6IuWvjOeJm-Wwj-WtpiIsIkFzc2Vzc1R5cGUiOjAsIlVzZXJJZCI6IjAxOTgzYzdmLTMxZWItN2I0NC1hNzRmLWZhZTRiYjliNmI3YiIsIk9yZ2FuUGF0aCI6IjJjNTUxYTczLTViNDEtMTFlZC05NTFhLTBjOWQ5MjY1MDRmMyxjMWJmNjBjNS01YjQxLTExZWQtOTUxYS0wYzlkOTI2NTA0ZjMsMDE4YTQ1YmMtZWVmNi03NzFmLTkzZGEtMzU2NDIyYzRkNTAyLGNkNGFlNWI0LTQxOTctNGUzNC1iNGVmLWNiMmVkNzg4YzNmYiwwMThjYWFhMy1lZDMzLTdkNDAtYmFhMy1iZjRlYTU3NzQ2ZTAsMDE5ODI2NDAtY2Y0YS03ZmQ1LWFiNDMtNzk4M2VmMDJiNmYwLDAxOTgzMTAwLWRiNTYtNzFjYy1iNjRkLTZmODRkMGFjNzBkMCIsImV4cCI6MTc1MzQ2MzE2MCwidXNlcm5hbWUiOiI3YTE1ZTZmNjNlYzM5YmM5In0.oQd_HlYVRr2_vC3U2DP31Vw62oYOgOLgWFD8n9KoEnI"
}


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
    # logger.add(
    #     "info_logs.log",
    #     level="INFO",
    #     rotation="10 MB",  # 日志文件大小限制
    #     format="{time:YYYY-MM-DD HH:mm:ss} - {level} - {message}"
    # )


# 初始化日志配置
setup_info_only_logger()


def get_local_storage_value(driver, key):
    """从localStorage中获取指定键的值"""
    try:
        value = driver.execute_script(f"return window.localStorage.getItem('{key}');")
        return value
    except Exception as e:
        logger.error(f"获取localStorage值失败: {str(e)}")
        return None


def parse_courseid_by_regex(url):
    """从URL中解析courseId"""
    pattern = r'courseId=([^&#]+)'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None


video_url = [
    "https://web.scgb.gov.cn/#/specialColumn/course?channelId=01957f20-dacd-76d7-8883-71f375adaab5&id=0194693f-09a5-7875-a64f-1573512205c7&channelName=%E4%B8%AD%E5%9B%BD%E5%BC%8F%E7%8E%B0%E4%BB%A3%E5%8C%96%E7%90%86%E8%AE%BA%E4%BD%93%E7%B3%BB",
    "https://web.scgb.gov.cn/#/specialColumn/course?channelId=01957f20-dacd-76d7-8883-71f375adaab5&id=0194693f-09a5-7875-a64f-1573512205c7&channelName=%E4%B8%AD%E5%9B%BD%E5%BC%8F%E7%8E%B0%E4%BB%A3%E5%8C%96%E7%90%86%E8%AE%BA%E4%BD%93%E7%B3%BB"
]
current_video_url_index = 0


def open_home(driver):
    global current_video_url_index
    global current_course_id
    logger.info(f"打开首页，检测视频学习情况，current_video_url_index：{current_video_url_index}")
    url = video_url[current_video_url_index]
    driver.get(url)
    time.sleep(5)
    is_next_page = judge_is_next_page(driver)
    while is_next_page:
        try:
            list_div = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "ivu-page-next"))
            )
            logger.info("找到class为'ivu-page-next'的div元素")
            list_div.click()
            time.sleep(2)
            is_next_page = judge_is_next_page(driver)
        except NoSuchElementException:
            logger.error("未找到下一页元素，当前视频观看完成")
            current_video_url_index = current_video_url_index + 1
            threading.Thread(target=open_home, args=(driver,), daemon=True).start()
            break
        except Exception as e:
            logger.error(f"翻页操作失败: {str(e)}")
            break
    # logger.info("检测完成，关闭当前页面")


def check_study_time():
    logger.info("判断当前学习任务是否大于50学时")
    url = "https://api.scgb.gov.cn/api/services/app/class/app/getStudyProcess"
    try:
        response = requests.get(url=url, headers=headers)
        response_json = response.json()
        logger.info(f"当前已学习时长: {response_json['result']['timesSum']}")
        if int(response_json['result']['timesSum']) > 50:
            return False
        else:
            return True
    except Exception as e:
        logger.error(f"获取学习时长失败: {str(e)}")
        return True


# 全局变量存储当前课程ID和主页面句柄
current_course_id = None
main_window_handle = None  # 用于存储主页面的句柄
current_course_id = ""


def parse_courseid_by_regex(url):
    """从URL中解析courseId"""
    pattern = r'courseId=([^&#]+)'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None


def judge_is_next_page(driver):
    global current_course_id, main_window_handle

    # 首次运行时记录主页面句柄
    if not main_window_handle:
        main_window_handle = driver.current_window_handle
        logger.debug(f"已记录主页面句柄: {main_window_handle}")

    try:
        # 等待class为"list"的div元素加载完成
        list_div = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "list"))
        )

        # 获取该div下的所有a标签
        a_tags = list_div.find_elements(By.TAG_NAME, "a")
        logger.info(f"共找到{len(a_tags)}个a标签元素")

        # 遍历每个a标签，检查是否包含class为"status success"的div
        for index, a_tag in enumerate(a_tags, 1):
            try:
                # 获取a标签的链接和文本
                a_href = a_tag.get_attribute("href")
                # 检查当前a标签内是否存在class为"status success"的div
                a_tag.find_element(By.XPATH, ".//div[@class='status success']")
                logger.info(f"第{index}个a标签：视频播放完成")

            except NoSuchElementException:
                logger.info(f"第{index}个a标签:视频未播放完成，在新的标签页开始播放视频")

                # 记录当前所有标签页句柄（点击前）
                handles_before_click = driver.window_handles

                # 点击a标签打开新页面
                a_tag.click()

                # 等待新标签页打开
                WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(len(handles_before_click) + 1))

                # 获取所有标签页句柄（点击后）
                all_handles = driver.window_handles

                # 找到新打开的标签页句柄
                new_handle = [h for h in all_handles if h not in handles_before_click][0]

                # 关闭之前的标签页（除了新打开的页面）
                for handle in all_handles:
                    if handle != new_handle:
                        driver.switch_to.window(handle)
                        driver.close()
                        logger.debug(f"已关闭标签页: {handle}")

                # 切换到新打开的标签页
                driver.switch_to.window(new_handle)
                logger.debug(f"已切换到新标签页: {new_handle}")

                # 解析课程ID
                current_course_id = parse_courseid_by_regex(a_href)
                logger.info(f"当前课程ID: {current_course_id}")

                return False  # 找到未播放视频，返回False停止翻页

            except Exception as e:
                logger.error(f"处理第{index}个a标签时出错: {str(e)}")

        logger.info("未找到需要播放的视频，点击下一页")
        return True  # 所有视频已完成，返回True继续翻页

    except TimeoutException:
        logger.warning("未找到class为'list'的div元素，可能已到最后一页")
        return False
    except Exception as e:
        logger.error(f"判断下一页时发生错误: {str(e)}")
        return False


def check_course_success(driver, username, password):
    global current_course_id
    global is_running
    sleep_time = 10
    while True:
        check_play_success_url = "https://api.scgb.gov.cn/api/services/app/course/app/getCourseDetailByUserId?"
        logger.info(f"检测课程id: {current_course_id}")
        if current_course_id != "":
            payload = {
                "courseId": current_course_id
            }
            try:
                course_detail = requests.post(check_play_success_url, headers=headers,
                                              json=payload)
                detail_json = course_detail.json()["result"]
                logger.debug(f"课程详情: {detail_json}")
                if detail_json["totalPeriod"] == detail_json["watchTimes"]:
                    logger.info("已观看完成")
                    if check_study_time():
                        # 播放下一个视频
                        threading.Thread(target=open_home, args=(driver,), daemon=True).start()
                        current_course_id = ""
                    else:
                        is_running = False
                        break
                else:
                    logger.info(f"totalPeriod: {detail_json['totalPeriod']}, watchTimes: {detail_json['watchTimes']}")
                    sleep_time = (int(detail_json["totalPeriod"]) - int(detail_json["watchTimes"])) - 60
                    if sleep_time < 10:
                        sleep_time = 10
            except TimeoutException:
                logger.error("链接超时")
                continue
            except Exception as e:
                logger.error(f"检测课程状态失败: {str(e)}")
                # 登陆失效，进行重新登录
                is_login(driver, username, password)
                sleep_time = 10
        else:
            sleep_time = 10
        logger.info(f"间隔{sleep_time}秒，继续检测")
        if sleep_time > 0:
            time.sleep(sleep_time)


def init_browser(user_data_dir, is_headless=False):
    # 创建保存用户数据的目录
    user_data_dir = os.path.join(os.getcwd(), user_data_dir)
    os.makedirs(user_data_dir, exist_ok=True)
    logger.debug(f"用户数据目录: {user_data_dir}")

    # 设置 Chrome 浏览器选项
    chrome_options = Options()
    if is_headless:
        chrome_options.add_argument("--headless")  # 无头模式，不显示浏览器窗口
    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")  # 保存用户数据
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    # 指定 ChromeDriver 的路径
    chromedriver_path = "D:\\develop\\workspace\\mine\\selenium_demo\\driver\\138\\chromedriver.exe"

    # 使用 Service 类来指定驱动路径
    service = Service(chromedriver_path)

    # 初始化 Chrome 浏览器驱动
    return webdriver.Chrome(service=service, options=chrome_options)


def is_login(driver, username=None, password=None):
    while True:
        driver.get("https://web.scgb.gov.cn/#/index")
        time.sleep(2)
        # 检查登录状态
        store = get_local_storage_value(driver, "store")
        if store:
            try:
                store_json = json.loads(store)
                if "accessToken" in store_json['session']:
                    headers['Authorization'] = "Bearer " + store_json['session']['accessToken']
                    logger.info(f"已登录:{store_json['session']['nickName']}【{store_json['session']['organName']}】")
                    return store_json
                else:
                    logger.warning("未登录，请登录")
            except json.JSONDecodeError:
                logger.error("localStorage中store数据格式错误")
        else:
            logger.warning("未登录，请登录")
        auto_login(driver, username, password)
        time.sleep(5)


def download_current_img(driver, img_xpath, save_path="current_image.png"):
    """
    下载页面中当前显示的img图片（应对src动态生成的情况）

    :param driver: Selenium WebDriver实例
    :param img_xpath: 目标img标签的XPath
    :param save_path: 图片保存路径
    :return: 下载成功返回True，失败返回False
    """
    try:
        # 等待图片元素加载完成
        img_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, img_xpath))
        )

        # 通过JavaScript获取图片的Base64编码（当前页面显示的图片）
        # 原理：创建canvas，将图片绘制到canvas，再导出为Base64
        script = """
            var canvas = document.createElement('canvas');
            var ctx = canvas.getContext('2d');
            var img = arguments[0];
            canvas.width = img.naturalWidth;
            canvas.height = img.naturalHeight;
            ctx.drawImage(img, 0, 0);
            return canvas.toDataURL('image/png');
        """
        base64_data = driver.execute_script(script, img_element)

        # 处理Base64数据（去除前缀）
        if base64_data.startswith('data:image/png;base64,'):
            base64_data = base64_data.split(',')[1]
        else:
            print("获取的图片Base64格式不支持")
            return False

        # 解码并保存图片
        img_data = base64.b64decode(base64_data)
        with open(save_path, 'wb') as f:
            f.write(img_data)

        print(f"图片已保存至: {os.path.abspath(save_path)}")
        return True

    except Exception as e:
        print(f"下载图片失败: {str(e)}")
        return False


def auto_login(driver, username, password):
    try:
        logger.info("开始自动登录")
        # 输入用户名
        username_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="请输入您的用户名"]'))
        )
        username_input.clear()
        username_input.send_keys(username)

        # 输入密码
        password_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="请输入您的密码"]'))
        )
        logger.info("找到密码输入框")
        password_input.clear()
        password_input.send_keys(password)

        # # 处理验证码
        capture_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="请输入验证码"]'))
        )
        capture_input.clear()
        captcha = get_formdata_img_src(driver)
        capture_input.send_keys(captcha)
        # 点击登录按钮
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@class="ivu-form-item-content"]//button'))
        )
        login_button.click()
    except TimeoutException:
        logger.error("超时未找到登录相关输入框")
    except ElementNotInteractableException:
        logger.error("登录输入框不可交互")
    except Exception as e:
        logger.error(f"自动登录失败: {str(e)}")


def get_formdata_img_src(driver, wait_time=10):
    """获取验证码图片并识别"""
    try:
        # 等待验证码图片容器加载
        formdata_div = WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located((By.CLASS_NAME, "validate-form-img"))
        )
        logger.info("找到验证码图片容器")
        save_path = "captcha_screenshot.png"  # 保存路径可自定义
        success = formdata_div.screenshot(save_path)

        if success:
            print(f"图片元素截图已保存至: {os.path.abspath(save_path)}")
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


def exec_main(name, username, password):
    driver = init_browser(user_data_dir=name, is_headless=True)
    # 判断用户是否登录
    is_login(driver, username, password)
    driver.close()
    driver = init_browser(user_data_dir=name, is_headless=True)
    open_home(driver)
    threading.Thread(target=check_course_success, args=(driver, username, password,), daemon=True).start()
