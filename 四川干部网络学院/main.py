import json
import os
import re
import threading
import time

import ddddocr
import requests
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


def get_local_storage_value(driver, key):
    """
    从localStorage中获取指定键的值

    :param driver: WebDriver实例
    :param key: 要获取的键名
    :return: 键对应的值，若不存在则返回None
    """
    try:
        # 执行JavaScript获取localStorage中的值
        value = driver.execute_script(f"return window.localStorage.getItem('{key}');")
        return value
    except Exception as e:
        print(f"获取localStorage值失败: {str(e)}")
        return None


def parse_courseid_by_regex(url):
    """使用正则表达式提取URL中的courseId"""
    # 正则匹配courseId=后面的内容（直到&或#结束）
    pattern = r'courseId=([^&#]+)'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None


def open_home(driver):
    print("打开首页，检测视频学习情况")
    global current_course_id
    url = "https://web.scgb.gov.cn/#/specialColumn/course?channelId=01957f20-dacd-76d7-8883-71f375adaab5&id=0194693f-09a5-7875-a64f-1573512205c7&channelName=%E4%B8%AD%E5%9B%BD%E5%BC%8F%E7%8E%B0%E4%BB%A3%E5%8C%96%E7%90%86%E8%AE%BA%E4%BD%93%E7%B3%BB"
    driver.get(url)
    time.sleep(2)
    is_next_page = judge_is_next_page(driver)
    while is_next_page:
        list_div = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "ivu-page-next"))
        )
        print("找到class为'ivu-page-next'的div元素")
        list_div.click()
        time.sleep(2)
        is_next_page = judge_is_next_page(driver)
    # 检测完成，关闭当前页面


def check_study_time():
    print("判断当前学习任务是否大于50学时")
    url = "https://api.scgb.gov.cn/api/services/app/class/app/getStudyProcess"
    response = requests.get(url=url, headers=headers)
    response_json = response.json()
    print(response_json)
    if int(response_json['result']['timesSum']) > 50:
        return False
    else:
        return True


# 全局变量存储当前课程ID和主页面句柄
current_course_id = None
main_window_handle = None  # 用于存储主页面的句柄
current_course_id = ""


def parse_courseid_by_regex(url):
    """从URL中解析courseId（复用之前的解析函数）"""
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
        # print(f"已记录主页面句柄: {main_window_handle}")

    try:
        # 等待class为"list"的div元素加载完成
        list_div = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "list"))
        )

        # 获取该div下的所有a标签
        a_tags = list_div.find_elements(By.TAG_NAME, "a")
        print(f"共找到{len(a_tags)}个a标签元素")

        # 遍历每个a标签，检查是否包含class为"status success"的div
        for index, a_tag in enumerate(a_tags, 1):
            try:
                # 获取a标签的链接和文本
                a_href = a_tag.get_attribute("href")
                # a_text = a_tag.text.strip()
                # print(f"文本: {a_text}")

                # 检查当前a标签内是否存在class为"status success"的div
                a_tag.find_element(By.XPATH, ".//div[@class='status success']")
                print(f"第{index}个a标签：视频播放完成")

            except NoSuchElementException:
                print(f"第{index}个a标签:视频未播放完成，在新的标签页开始播放视频")

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

                # 关闭之前的标签页（除了主页面和新打开的页面）
                for handle in all_handles:
                    if handle != new_handle:
                        driver.switch_to.window(handle)
                        driver.close()
                        # print(f"已关闭标签页: {handle}")

                # 切换到新打开的标签页
                driver.switch_to.window(new_handle)
                # print(f"已切换到新标签页: {new_handle}")

                # 解析课程ID
                current_course_id = parse_courseid_by_regex(a_href)
                print(f"当前课程ID: {current_course_id}")

                return False  # 找到未播放视频，返回False停止翻页

            except Exception as e:
                print(f"处理第{index}个a标签时出错: {str(e)}")

        print("未找到需要播放的视频，点击下一页")
        return True  # 所有视频已完成，返回True继续翻页

    except TimeoutException:
        print("未找到class为'list'的div元素，可能已到最后一页")
        return False
    except Exception as e:
        print(f"判断下一页时发生错误: {str(e)}")
        return False


def check_course_success():
    global current_course_id
    global is_running
    sleep_time = 10
    while True:
        check_play_success_url = "https://api.scgb.gov.cn/api/services/app/course/app/getCourseDetailByUserId?"
        print("检测课程id:", current_course_id)
        if current_course_id != "":
            payload = {
                "courseId": current_course_id
            }
            try:
                course_detail = requests.post(check_play_success_url, headers=headers,
                                              json=payload)
            except TimeoutException:
                print("链接超时")
                continue
            detail_json = course_detail.json()["result"]
            print(detail_json)
            if detail_json["totalPeriod"] == detail_json["watchTimes"]:
                print("已观看完成")
                if check_study_time():
                    # 播放下一个视频
                    threading.Thread(target=open_home, args=(driver,), daemon=True).start()
                    current_course_id = ""
                else:
                    is_running = False
                    break
            else:
                print("totalPeriod:", detail_json["totalPeriod"], "watchTimes:", detail_json["watchTimes"])
                sleep_time = int(detail_json["totalPeriod"]) - int(detail_json["watchTimes"])
        else:
            sleep_time = 10
        print(f"间隔{sleep_time}秒，继续检测")
        if sleep_time > 0:
            time.sleep(sleep_time)


def init_browser(user_data_dir, is_headless=False):
    # 创建保存用户数据的目录
    user_data_dir = os.path.join(os.getcwd(), user_data_dir)
    os.makedirs(user_data_dir, exist_ok=True)

    # 设置 Chrome 浏览器选项
    chrome_options = Options()
    if is_headless:
        chrome_options.add_argument("--headless")  # 无头模式，不显示浏览器窗口
    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")  # 保存用户数据
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    # 指定 ChromeDriver 的路径，请根据实际情况修改
    chromedriver_path = "D:\\develop\\workspace\\mine\\selenium_demo\\driver\\138\\chromedriver.exe"  # <-- 修改为你的驱动路径

    # 使用 Service 类来指定驱动路径（适配 Selenium 4.10.0+）
    service = Service(chromedriver_path)

    # 初始化 Chrome 浏览器驱动
    return webdriver.Chrome(service=service, options=chrome_options)


def is_login(driver, username, password):
    while True:
        driver.get("https://web.scgb.gov.cn/#/index")
        time.sleep(2)
        # 等待class为"list"的div元素加载完成
        store = get_local_storage_value(driver, "store")
        if store:
            store_json = json.loads(store)
            if "accessToken" in store_json['session']:
                headers['Authorization'] = "Bearer " + store_json['session']['accessToken']
                print("已登录")
                break
            else:
                print("未登录，请登录")
        else:
            print("未登录，请登录")
    # auto_login(driver, username, password)


def auto_login(driver, username, password):
    # 自动登录，校验用户名，密码是否正确
    try:
        # 使用XPath精准匹配placeholder属性
        username_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//input[@placeholder="请输入您的用户名"]')
            )
        )
        username_input.clear()  # 清空现有内容（可选）
        username_input.send_keys(username)
        # 使用XPath精准匹配placeholder属性
        password_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//input[@placeholder="请输入您的密码"]')
            )
        )
        print("找到密码输入框")

        # 输入密码
        password_input.clear()  # 清空现有内容（可选）
        password_input.send_keys(password)
        print("密码输入完成")
        # 检测验证码
        # 使用XPath精准匹配placeholder属性
        capture_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//input[@placeholder="请输入验证码"]')
            )
        )
        capture_input.clear()
        capture_input.send_keys(get_formdata_img_src(driver))
    except TimeoutException:
        print("超时未找到placeholder为'请输入密码'的输入框")
    except ElementNotInteractableException:
        print("密码输入框存在但不可交互（可能被禁用或隐藏）")
    except Exception as e:
        print(f"输入密码时发生错误: {str(e)}")


def get_formdata_img_src(driver, wait_time=10):
    """
    获取class为formdata的div下img标签的src属性

    :param driver: WebDriver实例
    :param wait_time: 最长等待时间（秒）
    :return: img的src属性值列表，若未找到则返回空列表
    """
    try:
        # 等待class为formdata的div加载完成
        formdata_div = WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located((By.CLASS_NAME, "validate-form-img"))
        )
        print("找到class为'formdata'的div元素")

        # 在该div下查找所有img标签
        img_tags = formdata_div.find_elements(By.TAG_NAME, "img")
        print(f"在formdata div下找到{len(img_tags)}个img标签")

        # 提取每个img标签的src属性
        src_list = []

        src = img_tags[0].get_attribute("src")
        if src:
            src_list.append(src)
            print(f"src: {src}")
            return recognize_verify_code(image_url=src)
        else:
            print(f"没有src属性")
    except TimeoutException:
        print("超时未找到class为'formdata'的div元素")
    except NoSuchElementException:
        print("在formdata div下未找到任何img标签")
    except Exception as e:
        print(f"获取img的src属性时发生错误: {str(e)}")
    return ""


# 初始化ocr识别器
ocr = ddddocr.DdddOcr()


def recognize_verify_code(image_path=None, image_url=None):
    """
    使用ddddocr识别验证码

    :param image_path: 本地验证码图片路径（二选一）
    :param image_url: 验证码图片URL（二选一）
    :return: 识别结果字符串，失败返回None
    """
    try:
        # 读取图片数据
        if image_path:
            # 从本地文件读取
            with open(image_path, 'rb') as f:
                image_data = f.read()
        elif image_url:
            # 从网络URL读取
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()  # 检查请求是否成功
            image_data = response.content
        else:
            print("请提供图片路径或图片URL")
            return None

        # 识别验证码
        result = ocr.classification(image_data)
        print(f"验证码识别结果: {result}")
        return result

    except Exception as e:
        print(f"验证码识别失败: {str(e)}")
        return None


if __name__ == '__main__':
    driver = init_browser(user_data_dir="徐杰", is_headless=True)
    # 判断用户是否登录
    store = is_login(driver)
    # 获取浏览器参数
    headers['Authorization'] = "Bearer " + store['session']['accessToken']
    open_home(driver)

    threading.Thread(target=check_course_success, daemon=True).start()
    while is_running:
        time.sleep(1)
    print("视频已全部播放完成")
