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
user_data_dir = os.path.join(os.getcwd(), "杨小兰")
os.makedirs(user_data_dir, exist_ok=True)

# 设置 Chrome 浏览器选项
chrome_options = Options()
chrome_options.add_argument("--headless")  # 无头模式，不显示浏览器窗口
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
    "https://basic.smartedu.cn/teacherTraining/courseDetail?courseId=895caa6f-6c42-411d-ab7c-2b43facebd9f&tag=2025%E5%B9%B4%E2%80%9C%E6%9A%91%E6%9C%9F%E6%95%99%E5%B8%88%E7%A0%94%E4%BF%AE%E2%80%9D%E4%B8%93%E9%A2%98&channelId=&libraryId=bb042e69-9a11-49a1-af22-0c3fab2e92b9&breadcrumb=2025%E5%B9%B4%E2%80%9C%E6%9A%91%E6%9C%9F%E6%95%99%E5%B8%88%E7%A0%94%E4%BF%AE%E2%80%9D%E4%B8%93%E9%A2%98&resourceId=d4807973-1dd3-41ce-b647-75f60b94bd99")
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
                        # 将为扩展开的都打开
                        click_eligible_divs(wait)
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
        print("      视频开始播放中...")
    except Exception as e:
        print(f"      发生错误: {e}")
    finally:
        # 关闭浏览器
        print("      ")


def click_eligible_divs(wait):
    """
    遍历所有class为fish-collapse-header的div，检查每个div的父级是否只有1个子div，
    对符合条件的div执行点击操作

    Args:
        driver: WebDriver实例
        wait: WebDriverWait实例

    Returns:
        int: 成功点击的元素数量
    """
    success_count = 0
    try:
        # 1. 定位所有class为fish-collapse-header的div（可能有多个）
        target_divs = wait.until(
            EC.presence_of_all_elements_located(
                (By.CLASS_NAME, "fish-collapse-header")
            )
        )
        print(f"找到{len(target_divs)}个class为fish-collapse-header的div")

        # 2. 遍历每个div，检查其父级条件
        for idx, target_div in enumerate(target_divs, 1):
            print(f"\n--- 处理第{idx}个div ---")

            # 3. 获取当前div的父级元素
            parent_element = target_div.find_element(By.XPATH, "..")  # 父级

            # 4. 查找父级下的所有直接子div（仅下一级）
            parent_child_divs = parent_element.find_elements(By.XPATH, "./div")
            print(f"父级元素的直接子div数量: {len(parent_child_divs)}")

            # 5. 判断是否只有1个子div
            if len(parent_child_divs) == 1:
                print("父级仅有1个子div，符合条件")

                # 6. 点击当前div（即父级唯一的子div）
                wait.until(EC.element_to_be_clickable(target_div))
                target_div.click()
                print("成功点击该div")
                success_count += 1
            else:
                print(f"父级有{len(parent_child_divs)}个子div，不符合条件，跳过")

        print(f"\n操作完成，共成功点击{success_count}个div")
        return success_count

    except Exception as e:
        print(f"处理过程中出错: {str(e)}")
        return 0


def play_video(wait):
    # 点击视频中间播放按钮
    click_play(wait)
    # 点击提示
    click_know()
    # 点击视频左下角播放按钮
    click_control_button(wait)
    # 设置2倍速度
    click_li_with_span_2x(wait)


def click_play(wait):
    try:
        # 等待播放按钮加载完成并点击
        play_button = wait.until(
            EC.element_to_be_clickable((By.CLASS_NAME, "vjs-big-play-button"))
        )
        play_button.click()
        print("      成功点击视频播放按钮")
    except TimeoutException:
        print("      超时未找到vjs-big-play-button播放按钮")
    except NoSuchElementException:
        print("      未找到vjs-big-play-button播放按钮")
    except Exception as e:
        print(f"      点击播放按钮时发生错误: {str(e)}")


def click_know():
    try:
        # 查找包含<span>我知道</span>的button按钮（使用相对路径从当前页面查找）
        know_button = wait_3.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[.//span[text()='我知道了']]")
            )
        )
        # 点击按钮
        know_button.click()
        print("      找到并点击了包含<span>我知道了</span>的按钮")
    except TimeoutException:
        print("      超时未找到包含<span>我知道了</span>的按钮")
    except NoSuchElementException:
        print("      未找到包含<span>我知道了</span>的按钮")
    except Exception as e:
        print(f"      点击'我知道了'按钮时发生错误: {str(e)}")


def click_control_button(wait):
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


def click_li_with_span_2x(wait):
    """
    找到包含<span>值为"2x"</span>的li元素并点击

    Args:
        driver: WebDriver实例
        wait: WebDriverWait实例

    Returns:
        bool: 是否成功点击至少一个元素
    """
    try:
        # 使用XPath定位目标li元素
        rate_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@title='Playback Rate']")))
        print(f"  class: {rate_button.get_attribute('class')}")

        # 点击元素
        rate_button.click()
        rate_button.click()
        rate_button.click()
        print("      成功点击目标li元素")
        return True

    except Exception as e:
        print(f"      点击li元素时出错: {str(e)}")
        return False


# 检测是否重新播放
def check_play():
    sleep_num = 10
    while True:
        try:
            time.sleep(sleep_num)
            wait.until(EC.visibility_of_element_located((By.XPATH, "//div[text()='再学一遍']")))
            print("      找到<div>再学一遍</div>标签，进行下一篇播放")
            # 如果需要点击该div，可以添加以下代码
            Thread(target=automate_browser).start()
        except TimeoutException:
            print(f"      超时未找到<div>再学一遍</div>标签,间隔{sleep_num}秒继续寻找")
        except NoSuchElementException:
            print("      未找到<div>再学一遍</div>标签")
        except Exception as e:
            print(f"      查找'再学一遍'div时发生错误: {str(e)}")


if __name__ == "__main__":
    Thread(target=automate_browser).start()
    Thread(target=check_play).start()

    while True:
        time.sleep(1)
