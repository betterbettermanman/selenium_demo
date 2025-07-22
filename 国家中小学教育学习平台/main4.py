import os
import time
from threading import Thread

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
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
# 打开需要登录的网站
driver.get(
    "https://basic.smartedu.cn/teacherTraining/courseDetail?courseId=e3b6492d-bc7c-4440-ab5e-8d02debd8ceb&tag=2025%E5%B9%B4%E2%80%9C%E6%9A%91%E6%9C%9F%E6%95%99%E5%B8%88%E7%A0%94%E4%BF%AE%E2%80%9D%E4%B8%93%E9%A2%98&channelId=&libraryId=bb042e69-9a11-49a1-af22-0c3fab2e92b9&breadcrumb=2025%E5%B9%B4%E2%80%9C%E6%9A%91%E6%9C%9F%E6%95%99%E5%B8%88%E7%A0%94%E4%BF%AE%E2%80%9D%E4%B8%93%E9%A2%98&resourceId=316b91d2-2815-4491-986a-308716d6956d")
print(f"成功打开网页: {driver.title}")
# 等待页面完全加载
time.sleep(5)


# 查找目录
def automate_browser():
    try:
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

                    # 遍历每个同级div，查找其下符合条件的子div
                    for j, sibling in enumerate(sibling_divs, 1):
                        sibling_class = sibling.get_attribute("class")
                        print(f"\n    --- 同级div {j}/{len(sibling_divs)} (class={sibling_class}) ---")

                        # 查找类名以"resource-item resource-item-train"开头的子div
                        target_divs = sibling.find_elements(By.XPATH,
                                                            ".//div[starts-with(@class, 'resource-item resource-item-train')]")

                        if target_divs:
                            print(f"    找到 {len(target_divs)} 个符合条件的子div")

                            # 打印每个目标div的信息
                            for k, target in enumerate(target_divs, 1):
                                target_class = target.get_attribute("class")
                                target_text = target.text.strip()
                                print(f"      目标div {k}: class={target_class}, text={target_text[:50]}...")

                                # 在当前div下查找class为"status-icon"的div中的i标签
                                try:
                                    # 使用相对路径查找当前div下的i标签
                                    status_div = target.find_element(By.XPATH,
                                                                     ".//div[@class='status-icon']")
                                    # 在status_div中查找i标签
                                    icon = status_div.find_element(By.TAG_NAME, "i")
                                    # 获取title属性值
                                    icon_title = icon.get_attribute("title")
                                    print(f"      status-icon下i标签title属性值: {icon_title}")

                                    if icon_title == "进行中":
                                        # 点击进行中课程
                                        target.click()
                                        print("      点击了'进行中'的课程")
                                        time.sleep(2)  # 等待页面切换
                                        play_video(wait)
                                        break

                                    elif icon_title == "未开始":
                                        # 点击未开始课程
                                        target.click()
                                        print("      点击了'未开始'的课程")
                                        time.sleep(2)  # 等待视频区域加载
                                        play_video(wait)
                                        break

                                except Exception as e:
                                    print(f"      未找到符合条件的i标签: {str(e)}")

                        else:
                            print("    未找到符合条件的子div")

                    if len(sibling_divs) > 5:
                        print(f"    ... 等 {len(sibling_divs)} 个同级div")
                else:
                    print("  未找到同级div元素")

        else:
            print("未找到包含<span>目录</span>的父级div元素")
            print("尝试查找包含文本'目录'的div...")
        print("查看结果后按回车键继续...")

    except Exception as e:
        print(f"发生错误: {e}")


def play_video(wait):
    try:
        # 等待播放按钮加载完成并点击
        play_button = wait.until(
            EC.element_to_be_clickable((By.CLASS_NAME, "vjs-big-play-button"))
        )
        play_button.click()
        print("      成功点击视频播放按钮")

        try:
            # 查找包含<span>我知道</span>的button按钮（使用相对路径从当前页面查找）
            know_button = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[.//span[text()='我知道了']]")
                )
            )
            # 点击按钮
            know_button.click()
            print("      找到并点击了包含<span>我知道</span>的按钮")
        except TimeoutException:
            print("      超时未找到包含<span>我知道</span>的按钮")
        except NoSuchElementException:
            print("      未找到包含<span>我知道</span>的按钮")
        except Exception as e:
            print(f"      点击'我知道'按钮时发生错误: {str(e)}")

        # TODO 获取class为vjs-control-bar中div下button按钮，并点击
        try:
            # 定位class为vjs-control-bar的元素，再查找其下div中的button
            control_bar = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "vjs-control-bar"))
            )
            # 查找control_bar下div中的button（使用相对路径）
            target_button = control_bar.find_element(
                By.XPATH, ".//div//button"  # .//表示从当前元素（control_bar）开始查找
            )
            # 确保按钮可点击后点击
            wait.until(EC.element_to_be_clickable(target_button))
            target_button.click()
            print("      成功点击vjs-control-bar中div下的button按钮")
        except TimeoutException:
            print("      超时未找到vjs-control-bar中div下的button按钮")
        except NoSuchElementException:
            print("      未找到vjs-control-bar中div下的button按钮")
        except Exception as e:
            print(f"      点击vjs-control-bar中button时发生错误: {str(e)}")

    except TimeoutException:
        print("      超时未找到vjs-big-play-button播放按钮")
    except NoSuchElementException:
        print("      未找到vjs-big-play-button播放按钮")
    except Exception as e:
        print(f"      点击播放按钮时发生错误: {str(e)}")


# 检测是否重新播放
def check_play():
    while True:
        try:
            time.sleep(20)
            learn_another_div = wait.until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//div[text()='再学一遍']")
                )
            )
            print("      找到<div>再学一遍</div>标签，进行下一篇播放")
            # 如果需要点击该div，可以添加以下代码
            Thread(target=automate_browser).start()
        except TimeoutException:
            print("      超时未找到<div>再学一遍</div>标签,间隔20秒继续寻找")
        except NoSuchElementException:
            print("      未找到<div>再学一遍</div>标签")
        except Exception as e:
            print(f"      查找'再学一遍'div时发生错误: {str(e)}")


if __name__ == "__main__":
    # automate_browser()
    Thread(target=automate_browser).start()
    Thread(target=check_play).start()

    while True:
        time.sleep(1)
