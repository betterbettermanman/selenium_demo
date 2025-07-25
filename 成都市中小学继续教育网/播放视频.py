import os
import time

from selenium import webdriver
from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

url = "https://www.cdjxjy.com/Student/CoursePlay.aspx?cid=a254db13-4250-49d6-a3c0-418741a6dd52&scid=dba5d634-bfeb-4de9-940a-77b9a6a0c063"
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

# 打开需要登录的网站（示例使用 GitHub）
driver.get(url)
time.sleep(5)
print(f"成功打开网页: {driver.title}")
wait = WebDriverWait(driver, 10)
try:
    target_divs = wait.until(
        EC.presence_of_all_elements_located(
            (By.CLASS_NAME, "outter")
        )
    )
    # 使用XPath ".."获取直接父元素
    parent_element = target_divs[0].find_element(By.XPATH, "..")
    # 确保父元素可点击后再执行点击
    wait.until(EC.element_to_be_clickable(parent_element))
    parent_element.click()
    print("点击播放按钮")
except TimeoutException:
    print("超时未找到问卷调查按钮")
except NoSuchElementException:
    print("未找到vjs-big-play-button播放按钮")
except Exception as e:
    print(f"点击播放按钮时发生错误: {str(e)}")

questionnaire_div = wait.until(
    EC.presence_of_element_located(
        (By.XPATH, "//div[normalize-space(text())='学习记录']")
    )
)
questionnaire_div.click()

txtareainnertContents = wait.until(
    EC.presence_of_element_located(
        (By.ID, "txtareainnertContents")
    )
)
txtareainnertContents.send_keys("内容要点")
time.sleep(500)
txtareaExperience = wait.until(
    EC.presence_of_element_located(
        (By.ID, "txtareaExperience")
    )
)
txtareaExperience.send_keys("体会")

button = wait.until(
    EC.presence_of_element_located(
        (By.ID, "AddRecord")
    )
)
print("提交完成")

while True:
    time.sleep(5)
