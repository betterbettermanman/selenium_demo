import os
import re
import time
from threading import Thread
from time import sleep

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

course_status = None
checker = None
is_running = True


def init_shared_browser(head=True, user_data_dir2="chrome_user_data", chromedriver_path=None):
    user_data = os.path.join(os.getcwd(), user_data_dir2)
    os.makedirs(user_data, exist_ok=True)

    chrome_options = Options()
    if head:
        chrome_options.add_argument("--headless")  # 无头模式
    chrome_options.add_argument(f"--user-data-dir={user_data}")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--start-maximized")

    chromedriver_path = chromedriver_path
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # 获取主窗口句柄
    main_window_handle = driver.current_window_handle

    wait = WebDriverWait(driver, 10)
    wait_3 = WebDriverWait(driver, 2)

    return driver, wait, wait_3, main_window_handle  # 返回主窗口句柄
# 需要修改的地方
CHROMEDRIVER_PATH = "D:\\develop\\workspace\\mine\\selenium_demo\\driver\\138\\chromedriver.exe"
BASE_URL = "https://pc.xuexi.cn/points/login.html?ref=https%3A%2F%2Fwww.xuexi.cn%2F"

user_data_dir = "18380442322"

def check_login():
    driver, wait, _, _ = init_shared_browser(head=False, user_data_dir2=user_data_dir,
                                             chromedriver_path=CHROMEDRIVER_PATH)
    driver.get(BASE_URL)
    print(f"成功打开网页: {driver.title}")
    time.sleep(5)  # 等待页面加载
    while True:
        try:
            wait.until(
                EC.element_to_be_clickable((By.XPATH, ".//a[starts-with(@class,'logged-link')]"))
            )
            print("已登录")
            break
        except TimeoutException:
            print("超时未找到用户信息,间隔10秒继续检测")
            time.sleep(10)
        except NoSuchElementException:
            print("      未找到登录按钮")
        except Exception as e:
            print(f"      点击播放按钮时发生错误: {str(e)}")

    driver.close()

if __name__ == "__main__":
    check_login()
    # 初始化共享浏览器，获取主窗口句柄
    driver, wait, wait_3, main_window_handle = init_shared_browser(head=True, user_data_dir2=user_data_dir,
                                                                   chromedriver_path=CHROMEDRIVER_PATH)
