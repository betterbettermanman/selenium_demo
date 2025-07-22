import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait

# 创建保存用户数据的目录
user_data_dir = os.path.join(os.getcwd(), "chrome_user_data")
os.makedirs(user_data_dir, exist_ok=True)

# 设置 Chrome 浏览器选项
chrome_options = Options()
# chrome_options.add_argument("--headless")  # 无头模式，不显示浏览器窗口
chrome_options.add_argument(f"--user-data-dir={user_data_dir}")  # 保存用户数据
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--start-maximized")  # 最大化窗口，确保元素可见

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
    "https://basic.smartedu.cn/teacherTraining/courseDetail?courseId=0bc83fd8-4ee9-4bb2-bf9d-f858ee13ed8f&tag=2025%E5%B9%B4%E2%80%9C%E6%9A%91%E6%9C%9F%E6%95%99%E5%B8%88%E7%A0%94%E4%BF%AE%E2%80%9D%E4%B8%93%E9%A2%98&channelId=&libraryId=bb042e69-9a11-49a1-af22-0c3fab2e92b9&breadcrumb=2025%E5%B9%B4%E2%80%9C%E6%9A%91%E6%9C%9F%E6%95%99%E5%B8%88%E7%A0%94%E4%BF%AE%E2%80%9D%E4%B8%93%E9%A2%98&resourceId=e473c567-3950-4521-923a-532e128f373e")
print(f"成功打开网页: {driver.title}")
while True:
    time.sleep(1)
