import os
import re
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

# 创建保存用户数据的目录
user_data_dir = os.path.join(os.getcwd(), "home")
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
# 打开需要登录的网站
driver.get("https://basic.smartedu.cn/training/10f7b3d6-e1c6-4a2e-ba76-e2f2af4674a5")
print(f"成功打开网页: {driver.title}")
# 等待页面完全加载
time.sleep(5)

target = [
    {
        "title": "大力弘扬教育家精神",
        "url": "https://basic.smartedu.cn/teacherTraining/courseDetail?courseId=cb134d8b-ebe5-4953-8c2c-10d27b45b8dc&tag=2025%E5%B9%B4%E2%80%9C%E6%9A%91%E6%9C%9F%E6%95%99%E5%B8%88%E7%A0%94%E4%BF%AE%E2%80%9D%E4%B8%93%E9%A2%98&channelId=&libraryId=bb042e69-9a11-49a1-af22-0c3fab2e92b9&breadcrumb=2025%E5%B9%B4%E2%80%9C%E6%9A%91%E6%9C%9F%E6%95%99%E5%B8%88%E7%A0%94%E4%BF%AE%E2%80%9D%E4%B8%93%E9%A2%98&resourceId=d2bdf509-3049-4487-a985-eed857ca003a",
        "complete_status": False,
    },
    {
        "title": "数字素养提升",
        "url": "https://basic.smartedu.cn/teacherTraining/courseDetail?courseId=0bc83fd8-4ee9-4bb2-bf9d-f858ee13ed8f&tag=2025%E5%B9%B4%E2%80%9C%E6%9A%91%E6%9C%9F%E6%95%99%E5%B8%88%E7%A0%94%E4%BF%AE%E2%80%9D%E4%B8%93%E9%A2%98&channelId=&libraryId=bb042e69-9a11-49a1-af22-0c3fab2e92b9&breadcrumb=2025%E5%B9%B4%E2%80%9C%E6%9A%91%E6%9C%9F%E6%95%99%E5%B8%88%E7%A0%94%E4%BF%AE%E2%80%9D%E4%B8%93%E9%A2%98&resourceId=4bc3d1c8-2358-4e1c-ac79-a70620ed175c",
        "complete_status": False,
    },
    {
        "title": "科学素养提升",
        "url": "https://basic.smartedu.cn/teacherTraining/courseDetail?courseId=d21a7e80-cbb4-492a-9625-d8ea8f844515&tag=2025%E5%B9%B4%E2%80%9C%E6%9A%91%E6%9C%9F%E6%95%99%E5%B8%88%E7%A0%94%E4%BF%AE%E2%80%9D%E4%B8%93%E9%A2%98&channelId=&libraryId=bb042e69-9a11-49a1-af22-0c3fab2e92b9&breadcrumb=2025%E5%B9%B4%E2%80%9C%E6%9A%91%E6%9C%9F%E6%95%99%E5%B8%88%E7%A0%94%E4%BF%AE%E2%80%9D%E4%B8%93%E9%A2%98&resourceId=7626d7f5-0d47-4f1e-998f-8a55f39043d7",
        "complete_status": False,
    }, {
        "title": "心理健康教育能力提升",
        "url": "https://basic.smartedu.cn/teacherTraining/courseDetail?courseId=e6a702f8-552d-49f6-89e7-b40ce5e445af&tag=2025%E5%B9%B4%E2%80%9C%E6%9A%91%E6%9C%9F%E6%95%99%E5%B8%88%E7%A0%94%E4%BF%AE%E2%80%9D%E4%B8%93%E9%A2%98&channelId=&libraryId=bb042e69-9a11-49a1-af22-0c3fab2e92b9&breadcrumb=2025%E5%B9%B4%E2%80%9C%E6%9A%91%E6%9C%9F%E6%95%99%E5%B8%88%E7%A0%94%E4%BF%AE%E2%80%9D%E4%B8%93%E9%A2%98&resourceId=119325b4-2204-4103-9d06-aea35ed21374",
        "complete_status": False,
    }, {
        "title": "学科教学能力提升",
        "url": "https://basic.smartedu.cn/teacherTraining/courseDetail?courseId=895caa6f-6c42-411d-ab7c-2b43facebd9f&tag=2025%E5%B9%B4%E2%80%9C%E6%9A%91%E6%9C%9F%E6%95%99%E5%B8%88%E7%A0%94%E4%BF%AE%E2%80%9D%E4%B8%93%E9%A2%98&channelId=&libraryId=bb042e69-9a11-49a1-af22-0c3fab2e92b9&breadcrumb=2025%E5%B9%B4%E2%80%9C%E6%9A%91%E6%9C%9F%E6%95%99%E5%B8%88%E7%A0%94%E4%BF%AE%E2%80%9D%E4%B8%93%E9%A2%98&resourceId=d4807973-1dd3-41ce-b647-75f60b94bd99",
        "complete_status": False,
    },
]


def method1():
    parent_divs = driver.find_elements(By.XPATH,
                                       ".//div[@class='fish-spin-container']")
    if parent_divs:
        print(f"找到 {len(parent_divs)} 个包含fish-spin-container的父级div")
        for i, div in enumerate(parent_divs, 1):
            print(f"\n--- 父级div {i}/{len(parent_divs)} ---")
            print(f"  class: {div.get_attribute('class')}")
            print(f"  id: {div.get_attribute('id')}")
            # 获取所有div子元素
            div_children = div.find_elements(By.XPATH, "./div")
            if div_children:
                print(f"  子元素数量: {len(div_children)}")
                if len(div_children):
                    # 遍历每个同级div，查找其下符合条件的子div
                    for j, children in enumerate(div_children, 1):
                        print(f"  class: {children.get_attribute('class')}")
                        # 判断子元素是否为空
                        if not is_div_empty(children):
                            # 获取底下子元素，判断是否包含以：index-module_phase_peroid开头
                            target_divs = children.find_elements(By.XPATH,
                                                                 ".//div[starts-with(@class, 'index-module_phase_main')]")
                            if target_divs:
                                print("属于学科教学能力提示，并解析需要的总时长")
                                print(target_divs[0].text.strip())
                                if compare_hours(target_divs[0].text.strip()):
                                    print("需要看视频，获取第一个视频进行播放")
                                    # 遍历列表，匹配标题并修改状态
                                    for item in target:
                                        if item["title"] == "学科教学能力提升":
                                            # 根据实际情况修改状态（此处示例改为True）
                                            item["complete_status"] = True
                                            print(
                                                f'已更新标题为学科教学能力提升的complete_status为：True')
                                            break
                            else:
                                print("属于每个学科都要学习,解析每个学科学习时长进度")
                                div_study_children = children.find_elements(By.XPATH, "./div")
                                is_break = False
                                for _, div_study in enumerate(div_study_children, 1):
                                    if is_break:
                                        break
                                    # print(f"  class: {div_study.get_attribute('class')}")
                                    match_title = get_title(div_study)
                                    complete_status = get_complete_status(div_study)

                                    # 遍历列表，匹配标题并修改状态
                                    for item in target:
                                        if item["title"] == match_title:
                                            # 根据实际情况修改状态（此处示例改为True）
                                            item["complete_status"] = complete_status
                                            print(
                                                f'已更新标题为"{match_title}"的complete_status为：{item["complete_status"]}')
                                            break
                                    else:
                                        print(f'未找到标题为"{match_title}"的项')
                        else:
                            print("空元素不处理")

    else:
        print("未找到主要元素")

    print(target)


def get_title(div_study):
    process_divs = div_study.find_elements(By.XPATH,
                                           ".//div[starts-with(@class, 'index-module_title')]")
    print(f"len(process_divs): {len(process_divs)},{process_divs[0].text.strip()}")
    chinese_chars = re.findall(r'[\u4e00-\u9fa5]+', process_divs[0].text.strip())
    title = ''.join(chinese_chars)
    print(title)  # 输出：大力弘扬教育家精神
    return title


def get_complete_status(div_study):
    process_divs = div_study.find_elements(By.XPATH,
                                           ".//div[starts-with(@class, 'index-module_process')]")
    for k, processC in enumerate(process_divs, 1):

        if not get_divs_with_two_spans_and_compare(processC):
            print("值不相等，继续学习")
            return False
    return True


def get_divs_with_two_spans_and_compare(parent_div):
    """
    获取包含2个span的div，并比较这2个span中的数值是否相等

    Returns:
        list: 每个符合条件的div的比较结果，格式为：
              [{"div": div元素, "span_values": [原始值1, 原始值2], "is_equal": True/False}, ...]
    """
    global is_equal
    try:
        target_divs = parent_div.find_elements(By.XPATH, ".//div[count(span) = 2]")
        if not target_divs:
            is_equal = True

        for div in target_divs:
            spans = div.find_elements(By.TAG_NAME, "span")
            span_values = [span.text.strip() for span in spans]

            # 提取数值部分并比较
            is_equal = False
            if len(span_values) == 2:
                try:
                    # 从文本中提取数值（处理如 "2.00" 或 "2" 的格式）
                    num1 = float(re.search(r'\d+\.\d+|\d+', span_values[0]).group())
                    num2 = float(re.search(r'\d+\.\d+|\d+', span_values[1]).group())
                    is_equal = num1 == num2
                except (AttributeError, ValueError):
                    # 无法提取数值时的默认处理
                    is_equal = False



    except Exception as e:
        print(f"处理过程中出错: {str(e)}")

    return is_equal


def is_div_empty(div_element):
    """
    判断div元素内容是否为空（包括无文本、无子元素或仅包含空白字符）

    Args:
        div_element: 要检查的div元素

    Returns:
        bool: 如果div为空返回True，否则返回False
    """
    # 获取div的文本内容
    div_text = div_element.text.strip()

    # 检查文本内容是否为空
    if not div_text:
        # 文本为空，进一步检查是否有子元素
        try:
            children = div_element.find_elements(By.XPATH, "./*")
            return len(children) == 0  # 没有子元素则为空
        except Exception:
            return True  # 发生异常（如元素不可用），默认视为空
    else:
        return False  # 有文本内容则不为空


def compare_hours(text):
    """
    解析字符串中的两个学时数值并比较是否相等

    Args:
        text: 包含学时信息的字符串，如 "已认定 0.00 / 认定 3 学时"

    Returns:
        tuple: (第一个数值, 第二个数值, 是否相等的布尔值)
    """
    # 使用正则表达式提取所有浮点数（包括整数和小数）
    numbers = re.findall(r'\d+\.\d+|\d+', text)

    if len(numbers) != 2:
        raise ValueError(f"字符串中未找到两个数值！提取结果: {numbers}")

    # 转换为浮点数进行比较
    num1 = float(numbers[0])
    num2 = float(numbers[1])

    return num1 == num2


if __name__ == "__main__":
    method1()
    while True:
        time.sleep(1)
