import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


def automate_browser():
    # 创建保存用户数据的目录
    user_data_dir = os.path.join(os.getcwd(), "chrome_user_data")
    os.makedirs(user_data_dir, exist_ok=True)

    # 设置 Chrome 浏览器选项
    chrome_options = Options()
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
    time.sleep(2)


if __name__ == "__main__":
    automate_browser()
    while True:
        time.sleep(1)
