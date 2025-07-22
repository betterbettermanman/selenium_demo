import os
import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


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
        # 打开需要登录的网站
        driver.get(
            "https://basic.smartedu.cn/teacherTraining/courseDetail?courseId=cb134d8b-ebe5-4953-8c2c-10d27b45b8dc&tag=2025%E5%B9%B4%E2%80%9C%E6%9A%91%E6%9C%9F%E6%95%99%E5%B8%88%E7%A0%94%E4%BF%AE%E2%80%9D%E4%B8%93%E9%A2%98&channelId=&libraryId=bb042e69-9a11-49a1-af22-0c3fab2e92b9&breadcrumb=2025%E5%B9%B4%E2%80%9C%E6%9A%91%E6%9C%9F%E6%95%99%E5%B8%88%E7%A0%94%E4%BF%AE%E2%80%9D%E4%B8%93%E9%A2%98&resourceId=d2bdf509-3049-4487-a985-eed857ca003a")
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
                                        # 如需进一步操作（如点击），可在此添加
                                        target.click()
                                    elif icon_title == "未开始":
                                        # 点击之后执行视频播放操作
                                        # TODO 找到class为vjs-big-play-button的播放按钮，并点击播放视频
                                        # 点击未开始课程
                                        target.click()
                                        print("      点击了'未开始'的课程")
                                        time.sleep(2)  # 等待视频区域加载

                                        # TODO 找到class为vjs-big-play-button的播放按钮，并点击播放视频
                                        try:
                                            # 等待播放按钮加载完成并点击
                                            play_button = wait.until(
                                                EC.element_to_be_clickable((By.CLASS_NAME, "vjs-big-play-button"))
                                            )
                                            play_button.click()
                                            print("      成功点击视频播放按钮")

                                            # 等待视频开始播放（可根据实际情况调整等待时间）
                                            time.sleep(5)

                                        except TimeoutException:
                                            print("      超时未找到vjs-big-play-button播放按钮")
                                        except NoSuchElementException:
                                            print("      未找到vjs-big-play-button播放按钮")
                                        except Exception as e:
                                            print(f"      点击播放按钮时发生错误: {str(e)}")
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

            # 备选方案：查找包含文本"目录"的div（不严格要求span标签）
            divs_with_text = driver.find_elements(By.XPATH, "//div[contains(text(), '目录')]")

            if divs_with_text:
                print(f"找到 {len(divs_with_text)} 个包含文本'目录'的div")
                for i, div in enumerate(divs_with_text, 1):
                    print(f"\n--- 包含文本的div {i}/{len(divs_with_text)} ---")
                    print(f"  class: {div.get_attribute('class')}")
                    print(f"  id: {div.get_attribute('id')}")

                    # 查找同级div元素
                    sibling_divs = div.find_elements(By.XPATH, "./following-sibling::div | ./preceding-sibling::div")

                    if sibling_divs:
                        print(f"  找到 {len(sibling_divs)} 个同级div元素")
                        for j, sibling in enumerate(sibling_divs, 1):
                            sibling_class = sibling.get_attribute("class")
                            print(f"    同级div {j}: class={sibling_class}")

                            # 查找类名以"resource-item resource-item-train"开头的子div
                            target_divs = sibling.find_elements(By.XPATH,
                                                                ".//div[starts-with(@class, 'resource-item resource-item-train')]")

                            if target_divs:
                                print(f"      找到 {len(target_divs)} 个符合条件的子div")
                    else:
                        print("  未找到同级div元素")
            else:
                print("未找到包含文本'目录'的div元素")

        input("查看结果后按回车键继续...")

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
