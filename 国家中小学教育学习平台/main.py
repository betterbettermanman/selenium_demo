from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
import os


def automate_browser():
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

    try:
        # 打开需要登录的网站（示例使用 GitHub）
        driver.get("https://basic.smartedu.cn/teacherTraining/courseDetail?courseId=cb134d8b-ebe5-4953-8c2c-10d27b45b8dc&tag=2025%E5%B9%B4%E2%80%9C%E6%9A%91%E6%9C%9F%E6%95%99%E5%B8%88%E7%A0%94%E4%BF%AE%E2%80%9D%E4%B8%93%E9%A2%98&channelId=&libraryId=bb042e69-9a11-49a1-af22-0c3fab2e92b9&breadcrumb=2025%E5%B9%B4%E2%80%9C%E6%9A%91%E6%9C%9F%E6%95%99%E5%B8%88%E7%A0%94%E4%BF%AE%E2%80%9D%E4%B8%93%E9%A2%98&resourceId=d2bdf509-3049-4487-a985-eed857ca003a")
        print(f"成功打开网页: {driver.title}")
        time.sleep(2)
        # 查找包含<span>目录</span>的父级div
        parent_divs = driver.find_elements(By.XPATH, "//span[text()='目录']/parent::div")

        if parent_divs:
            print(f"找到 {len(parent_divs)} 个包含<span>目录</span>的父级div")

            for i, div in enumerate(parent_divs, 1):
                print(f"\n--- 父级div {i}/{len(parent_divs)} ---")
                print(f"  class: {div.get_attribute('class')}")
                print(f"  id: {div.get_attribute('id')}")

                # 获取div的所有子元素（用于调试）
                children = div.find_elements(By.XPATH, "./*")
                print(f"  子元素数量: {len(children)}")

                # 查找同级div元素
                sibling_divs = div.find_elements(By.XPATH, "./following-sibling::div | ./preceding-sibling::div")

                if sibling_divs:
                    print(f"  找到 {len(sibling_divs)} 个同级div元素")

                    # 打印前5个同级div的信息
                    for j, sibling in enumerate(sibling_divs[:5], 1):
                        sibling_class = sibling.get_attribute("class")
                        sibling_text = sibling.text.strip()
                        print(f"    同级div {j}: class={sibling_class}, text={sibling_text[:50]}...")

                        #todo 实现在div下，寻找以类名以resource-item resource-item-train 开头的div

                    if len(sibling_divs) > 5:
                        print(f"    ... 等 {len(sibling_divs)} 个同级div")
                else:
                    print("  未找到同级div元素")

                # 可以在这里对找到的div进行进一步操作
                # div.click()

        else:
            print("未找到包含<span>目录</span>的父级div元素")
            print("尝试查找包含文本'目录'的div...")

    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        # 关闭浏览器
        input("按回车键退出...")
        # driver.quit()
        # print("浏览器已关闭")
        print(f"用户数据已保存到: {user_data_dir}")


if __name__ == "__main__":
    automate_browser()