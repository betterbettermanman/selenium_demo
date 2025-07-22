import os
import time

from selenium import webdriver
from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# 创建保存用户数据的目录
user_data_dir = os.path.join(os.getcwd(), "自动登录")
os.makedirs(user_data_dir, exist_ok=True)

# 设置 Chrome 浏览器选项
chrome_options = Options()
chrome_options.add_argument(f"--user-data-dir={user_data_dir}")  # 保存用户数据
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--start-maximized")  # 最大化窗口，确保元素可见


def login():
    # driver.get("https://auth.smartedu.cn/uias/login")
    time.sleep(2)
    username = "15328784913"
    password = "Kai520wo830!"
    username_input = wait.until(
        EC.element_to_be_clickable((By.XPATH, ".//input[@id='username']"))
    )
    username_input.send_keys(username)
    password_input = wait.until(
        EC.element_to_be_clickable((By.XPATH, ".//input[@id='tmpPassword']"))
    )
    password_input.send_keys(password)
    agree_input = wait.until(
        EC.element_to_be_clickable((By.XPATH, ".//input[@id='agreementCheckbox']"))
    )
    agree_input.click()
    loginBtn = wait.until(
        EC.element_to_be_clickable((By.XPATH, ".//button[@id='loginBtn']"))
    )
    loginBtn.click()
    # 验证码验证


# 指定 ChromeDriver 的路径，请根据实际情况修改
chromedriver_path = "D:\\develop\\workspace\\mine\\selenium_demo\\driver\\138\\chromedriver.exe"  # <-- 修改为你的驱动路径

# 使用 Service 类来指定驱动路径（适配 Selenium 4.10.0+）
service = Service(chromedriver_path)

# 初始化 Chrome 浏览器驱动
driver = webdriver.Chrome(service=service, options=chrome_options)
# 创建等待对象，最长等待10秒
wait = WebDriverWait(driver, 10)
wait_3 = WebDriverWait(driver, 2)
# 打开需要登录的网站
driver.get(
    "https://basic.smartedu.cn/training/10f7b3d6-e1c6-4a2e-ba76-e2f2af4674a5")
print(f"成功打开网页: {driver.title}")
# 检测页面有没有登录按钮，如果有就说明未登录，进行自动登录
# 创建等待对象，最长等待10秒
wait = WebDriverWait(driver, 10)
# 等待播放按钮加载完成并点击

try:
    # 等待播放按钮加载完成并点击
    login_button = wait.until(
        EC.element_to_be_clickable((By.XPATH, ".//div[text()='登录']"))
    )
    if login_button:
        print("有登录按钮，进行自动登录")
        login_button.click()
        login()
    else:
        print("无登录按钮，检测是否有用户信息")

except TimeoutException:
    print("超时未找到登录按钮")
except NoSuchElementException:
    print("      未找到登录按钮")
except Exception as e:
    print(f"      点击播放按钮时发生错误: {str(e)}")

while True:
    time.sleep(1)
