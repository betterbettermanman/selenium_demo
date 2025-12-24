import os
import time

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# 创建保存用户数据的目录
user_data_dir = os.path.join(os.getcwd(), "data", "11111")
os.makedirs(user_data_dir, exist_ok=True)

# 设置 Chrome 浏览器选项
chrome_options = Options()

chrome_options.add_argument(f"--user-data-dir={user_data_dir}")  # 保存用户数据
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
# 指定 ChromeDriver 的路径
chromedriver_path = "chromedriver.exe"

# 使用 Service 类来指定驱动路径
service = Service(chromedriver_path)

# 初始化 Chrome 浏览器驱动
driver = webdriver.Chrome(service=service, options=chrome_options)



driver.get("https://www.scxfks.com/study/index")
# driver.save_screenshot("screenshot.png")
# print("页面截图已保存")
print("------")
time.sleep(1)
login_link = driver.find_element(By.LINK_TEXT, "使用账号登录")
login_link.click()
time.sleep(1000)
driver.quit()