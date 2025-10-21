import os

from flask import Flask
from loguru import logger
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


def get_local_storage_value(key, driver1):
    """从localStorage中获取指定键的值"""
    try:
        value = driver1.execute_script(f"return window.localStorage.getItem('{key}');")
        return value
    except Exception as e:
        logger.error(f"获取localStorage值失败: {str(e)}")
        return None


def init_browser():
    user_data_dir = "15281785225"
    logger.info(f"{user_data_dir}开始初始化浏览器文件夹")
    # 创建保存用户数据的目录
    user_data_dir = os.path.join(os.getcwd(), "data", user_data_dir)
    os.makedirs(user_data_dir, exist_ok=True)
    logger.debug(f"用户数据目录: {user_data_dir}")

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
    logger.info(f"{user_data_dir}浏览器文件夹初始化成功")
    return driver


driver = init_browser()
driver.get("https://web.scgb.gov.cn/#/index")

# 初始化Flask应用
app = Flask(__name__)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4002)
