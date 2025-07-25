import os
import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


def automate_browser():
    # 创建保存用户数据的目录
    user_data_dir = os.path.join(os.getcwd(), "chrome_user_data")
    os.makedirs(user_data_dir, exist_ok=True)

    # 设置 Chrome 浏览器选项
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 无头模式，不显示浏览器窗口
    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")  # 保存用户数据
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    # 指定 ChromeDriver 的路径，请根据实际情况修改
    chromedriver_path = "D:\\develop\\workspace\\mine\\selenium_demo\\driver\\138\\chromedriver.exe"  # <-- 修改为你的驱动路径

    # 使用 Service 类来指定驱动路径（适配 Selenium 4.10.0+）
    service = Service(chromedriver_path)

    # 初始化 Chrome 浏览器驱动
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # 打开需要登录的网站（示例使用 GitHub）
    driver.get("https://www.cdjxjy.com/IndexMain.aspx#/student/SelectCourseRecord.aspx")
    print(f"成功打开网页: {driver.title}")
    time.sleep(5)
    wait = WebDriverWait(driver, 10)
    check_questionnaire(wait)
    # target_divs = wait.until(
    #     EC.presence_of_all_elements_located(
    #         (By.CLASS_NAME, "warning")
    #     )
    # )
    # print(len(target_divs))
    check_waning(driver, wait)
    # 打开待修课程，进行观看



# 检测问卷调查，关闭问卷调查
def check_questionnaire(wait):
    try:
        target_divs = wait.until(
            EC.presence_of_all_elements_located(
                (By.CLASS_NAME, "layui-layer-title")
            )
        )
        print("找到问卷调查按钮")
    except TimeoutException:
        print("超时未找到问卷调查按钮")
    except NoSuchElementException:
        print("未找到vjs-big-play-button播放按钮")
    except Exception as e:
        print(f"点击播放按钮时发生错误: {str(e)}")

    target_divs = wait.until(
        EC.presence_of_all_elements_located(
            (By.CLASS_NAME, "layui-layer-setwin")
        )
    )
    # 遍历每个目标div，查找其中的a标签并点击
    for div in target_divs:
        try:
            # 在当前div下查找a标签
            a_tag = div.find_element(By.TAG_NAME, "a")

            # 确保a标签可点击后再点击
            wait.until(EC.element_to_be_clickable(a_tag)).click()
            print("成功点击a标签")

            # 如果只需要点击第一个找到的a标签，可以在这里添加break
            # break

        except NoSuchElementException:
            print("当前div中未找到a标签")
        except TimeoutException:
            print("a标签不可点击或超时")
        except Exception as e:
            print(f"点击a标签时发生错误: {str(e)}")


# 判断课时是否达标
def check_waning(driver, wait):
    url = "https://www.cdjxjy.com/student/SelectCourseRecord.aspx"
    # 获取所有 Cookie
    all_cookies = driver.get_cookies()
    headers = {
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'X-Access-Token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2NDIxMTQ5MjAsInVzZXJuYW1lIjoiYWRtaW4ifQ.-HyWQh6A9y6ZmclS7ltpBu-GFb3liVk5VVj6laavOg0',
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
        'Accept': '*/*',
        'Host': 'www.cdjxjy.com',
        'Connection': 'keep-alive'
    }
    # 打印所有 Cookie 的信息
    for cookie in all_cookies:
        # print(f"Cookie 名称: {cookie['name']}, 值: {cookie['value']}")
        if "logincookie" == cookie['name']:
            headers["Cookie"] = "logincookie=" + cookie["value"]
    payload = {}
    response = requests.request("GET", url, headers=headers, data=payload, verify=False)
    print(response.text)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 查找所有class为warning的div标签
    warning_divs = soup.find_all('div', class_='warning')

    # 遍历每个warning div，查找内部的span标签
    for div in warning_divs:
        # 查找当前div下的所有span标签
        spans = div.find_all('p')
        # 获取span标签的文本内容（去除前后空格）
        span_text = spans[0].get_text(strip=True)
        study_result = analyze_course_status(span_text)
        print(study_result)

    # print("解析完成")
    return study_result['已获得学时是否大于应修学分']


import re


def analyze_course_status(text):
    # 定义正则表达式匹配模式
    # 匹配应修学分（提取数字，支持整数和小数）
    credit_pattern = r'应修网上课程(\d+\.?\d*)学分'
    # 匹配已获得学时（提取数字，支持整数和小数）
    hour_pattern = r'已获得(\d+\.?\d*)学时'

    # 提取应修学分
    credit_match = re.search(credit_pattern, text)
    if not credit_match:
        return "未找到应修学分信息"

    # 提取已获得学时
    hour_match = re.search(hour_pattern, text)
    if not hour_match:
        return "未找到已获得学时信息"

    # 转换为浮点数进行比较
    try:
        required_credit = float(credit_match.group(1))
        obtained_hour = float(hour_match.group(1))
    except ValueError:
        return "提取的数值格式错误"

    # 判断已获得学时是否大于应修学分
    is_enough = obtained_hour > required_credit

    # 构建结果
    result = {
        "应修学分": required_credit,
        "已获得学时": obtained_hour,
        "已获得学时是否大于应修学分": is_enough
    }

    return result


if __name__ == "__main__":
    automate_browser()
    while True:
        time.sleep(1)
