from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# 核心：让WebDriver Manager自动处理驱动的下载和配置
service = Service(ChromeDriverManager().install())

# 将配置好的service传给Chrome驱动
driver = webdriver.Chrome(service=service)

# 现在你可以正常使用driver了
driver.get("https://www.google.com")
print(driver.title)

driver.quit()