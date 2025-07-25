import json
import os
import re
import threading
import time

import requests
from selenium import webdriver
from selenium.common import TimeoutException, NoSuchElementException
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
        is_next_page = judge_is_next_page(driver)


def check_study_time():
    url = "https://api.scgb.gov.cn/api/services/app/class/app/getStudyProcess"
    response = requests.get(url=url, headers=headers)
    response_json = response.json()
    print(response_json)
    if int(response_json['result']['timesSum']) > 50:
        return False
    else:
        return True


def judge_is_next_page(driver):
    global current_course_id
    # 等待class为"list"的div元素加载完成
    list_div = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "list"))
    )
    # print("找到class为'list'的div元素")

    # 获取该div下的所有a标签
    a_tags = list_div.find_elements(By.TAG_NAME, "a")
    print(f"共找到{len(a_tags)}个a标签元素")

    # 遍历每个a标签，检查是否包含class为"status success"的div
    for index, a_tag in enumerate(a_tags, 1):
        try:
            # 可选：获取该a标签的其他信息（如链接、文本）
            a_href = a_tag.get_attribute("href")
            a_text = a_tag.text.strip()
            print(f"文本: {a_text}")
            # 检查当前a标签内是否存在class为"status success"的div
            # 使用相对路径查找（.//表示在当前元素内部查找）
            a_tag.find_element(By.XPATH, ".//div[@class='status success']")
            # print(f"第{index}个a标签：包含class为'status success'的div")

        except NoSuchElementException:
            print(f"检测到视频未播放完成,开始播放视频")
            a_tag.click()
            # print("开始播放视频")
            current_course_id = parse_courseid_by_regex(a_href)
            return False
        except Exception as e:
            print(f"处理第{index}个a标签时出错: {str(e)}")
    print("未找到需要播放的视频，点击下一页")
    return True


def check_course_success():
    global current_course_id
    global is_running
    sleep_time = 10
    while True:
        check_play_success_url = "https://api.scgb.gov.cn/api/services/app/course/app/getCourseDetailByUserId?"
        print("课程id:", current_course_id)
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
            # print(detail_json)
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
        print(f"间隔{sleep_time}秒，继续检测")
        if sleep_time > 0:
            time.sleep(sleep_time)


def init_browser():
    # 创建保存用户数据的目录
    user_data_dir = os.path.join(os.getcwd(), "chrome_user_data")
    os.makedirs(user_data_dir, exist_ok=True)

    # 设置 Chrome 浏览器选项
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # 无头模式，不显示浏览器窗口
    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")  # 保存用户数据
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    # 指定 ChromeDriver 的路径，请根据实际情况修改
    chromedriver_path = "D:\\develop\\workspace\\mine\\selenium_demo\\driver\\138\\chromedriver.exe"  # <-- 修改为你的驱动路径

    # 使用 Service 类来指定驱动路径（适配 Selenium 4.10.0+）
    service = Service(chromedriver_path)

    # 初始化 Chrome 浏览器驱动
    return webdriver.Chrome(service=service, options=chrome_options)


def is_login(driver):
    driver.get("https://web.scgb.gov.cn/#/index")
    time.sleep(2)
    while True:
        # 等待class为"list"的div元素加载完成
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "btn curp"))
            )
            break
        except TimeoutException:
            print("未登录，请登录")


if __name__ == '__main__':
    driver = init_browser()
    # 判断用户是否登录 todo
    is_login(driver)
    # driver.get("https://web.scgb.gov.cn/#/personal")
    # 获取浏览器参数
    store = json.loads(get_local_storage_value(driver, "store"))
    headers['Authorization'] = "Bearer " + store['session']['accessToken']
    open_home(driver)

    threading.Thread(target=check_course_success, daemon=True).start()
    while is_running:
        time.sleep(1)
    print("视频已全部播放完成")
