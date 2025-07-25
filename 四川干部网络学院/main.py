import os
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

headers = {
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'X-Access-Token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2NDIxMTQ5MjAsInVzZXJuYW1lIjoiYWRtaW4ifQ.-HyWQh6A9y6ZmclS7ltpBu-GFb3liVk5VVj6laavOg0',
    'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
    'Accept': '*/*',
    'Host': 'www.cdjxjy.com',
    'Connection': 'keep-alive',
    "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJPcmdhbklkIjoiMDE5ODMxMDAtZGI1Ni03MWNjLWI2NGQtNmY4NGQwYWM3MGQwIiwiQ2xpZW50VHlwZSI6IiIsIk9yZ2FuTmFtZSI6IuWvjOeJm-Wwj-WtpiIsIkFzc2Vzc1R5cGUiOjAsIlVzZXJJZCI6IjAxOTgzYzdmLTMxZWItN2I0NC1hNzQyLWJjODk4NzE0YzcwYSIsIk9yZ2FuUGF0aCI6IjJjNTUxYTczLTViNDEtMTFlZC05NTFhLTBjOWQ5MjY1MDRmMyxjMWJmNjBjNS01YjQxLTExZWQtOTUxYS0wYzlkOTI2NTA0ZjMsMDE4YTQ1YmMtZWVmNi03NzFmLTkzZGEtMzU2NDIyYzRkNTAyLGNkNGFlNWI0LTQxOTctNGUzNC1iNGVmLWNiMmVkNzg4YzNmYiwwMThjYWFhMy1lZDMzLTdkNDAtYmFhMy1iZjRlYTU3NzQ2ZTAsMDE5ODI2NDAtY2Y0YS03ZmQ1LWFiNDMtNzk4M2VmMDJiNmYwLDAxOTgzMTAwLWRiNTYtNzFjYy1iNjRkLTZmODRkMGFjNzBkMCIsImV4cCI6MTc1MzQ1OTkxMiwidXNlcm5hbWUiOiIyYzhjZTFlY2U5YjQwM2ZjIn0.bzWJGvRWlLluc0Q1CEHYBNr0POQMXo4qCIzZn4-kaNc"
}

def play_video(driver):
    global current_course_id
    url = "https://api.scgb.gov.cn/api/packageItem/GetPackageCourseItemPage?maxResultCount=100&skipCount=0&pageIndex=1&packageId=01957f20-dacd-76d7-8883-71f375adaab5"
    # 获取所有 Cookie

    payload = {}

    response = requests.request("GET", url, headers=headers, data=payload, verify=False)
    print(response.json())
    responseJson = response.json()
    result = responseJson["result"]
    for item in result['records']:
        # 判断当前课程是否观看完成
        check_play_success_url = "https://api.scgb.gov.cn/api/services/app/course/app/getCourseDetailByUserId?"
        payload = {
            "courseId": item["courseId"]
        }

        course_detail = requests.post(check_play_success_url, headers=headers, json=payload)  # 注意是 json= 而不是 data=
        detail_json = course_detail.json()["result"]
        # print(detail_json)
        # print("totalPeriod:", detail_json["totalPeriod"], "watchTimes:", detail_json["watchTimes"])
        if detail_json["totalPeriod"] == detail_json["watchTimes"]:
            print(item["contentName"] + "  已观看完成")
        else:
            print("未观看完成，打开视频，继续观看")
            url = "https://web.scgb.gov.cn/#/specialColumn/courseware?courseId=" + item[
                "courseId"] + "&channelId=01957f20-dacd-76d7-8883-71f375adaab5&channelName=中国式现代化理论体系"
            driver.get(url)
            print(f"成功打开网页: {driver.title}")
            time.sleep(2)
            try:
                rate_button = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@class='vjs-big-play-button']")))
                rate_button.click()
            except TimeoutException:
                print("      超时未找到vjs-big-play-button播放按钮")
            except NoSuchElementException:
                print("      未找到vjs-big-play-button播放按钮")
            except Exception as e:
                print(f"      点击播放按钮时发生错误: {str(e)}")
            current_course_id = item["courseId"]
            break
    print("开始播放视频")

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
driver = webdriver.Chrome(service=service, options=chrome_options)
wait = WebDriverWait(driver, 10)
play_video(driver)


def check_course_success():
    global current_course_id
    sleep_time = 10
    while True:
        check_play_success_url = "https://api.scgb.gov.cn/api/services/app/course/app/getCourseDetailByUserId?"
        print(current_course_id)
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
                # 播放下一个视频
                threading.Thread(target=play_video, args=(driver,), daemon=True).start()
                current_course_id = ""
            else:
                print("totalPeriod:", detail_json["totalPeriod"], "watchTimes:", detail_json["watchTimes"])
                sleep_time = int(detail_json["totalPeriod"]) - int(detail_json["watchTimes"])
        print(f"间隔{sleep_time}秒，继续检测")
        if sleep_time > 0:
            time.sleep(sleep_time)


if __name__ == '__main__':
    threading.Thread(target=check_course_success, daemon=True).start()
    while True:
        time.sleep(1)
