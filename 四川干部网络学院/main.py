import base64
import configparser
import json
import os
import re
import sys
import threading
import time
from urllib.parse import urlparse, parse_qs

import ddddocr
import requests
from loguru import logger
from selenium import webdriver
from selenium.common import TimeoutException, NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

# 初始化ocr识别器
ocr = ddddocr.DdddOcr()
current_course_id = ""
is_must = False
is_running = True
headers = {
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'X-Access-Token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2NDIxMTQ5MjAsInVzZXJuYW1lIjoiYWRtaW4ifQ.-HyWQh6A9y6ZmclS7ltpBu-GFb3liVk5VVj6laavOg0',
    'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
    'Accept': '*/*',
    'Host': 'www.cdjxjy.com',
    'Connection': 'keep-alive',
    "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJPcmdhbklkIjoiMDE5ODMxMDAtZGI1Ni03MWNjLWI2NGQtNmY4NGQwYWM3MGQwIiwiQ2xpZW50VHlwZSI6IiIsIk9yZ2FuTmFtZSI6IuWvjOeJm-Wwj-WtpiIsIkFzc2Vzc1R5cGUiOjAsIlVzZXJJZCI6IjAxOTgzYzdmLTMxZWItN2I0NC1hNzRmLWZhZTRiYjliNmI3YiIsIk9yZ2FuUGF0aCI6IjJjNTUxYTczLTViNDEtMTFlZC05NTFhLTBjOWQ5MjY1MDRmMyxjMWJmNjBjNS01YjQxLTExZWQtOTUxYS0wYzlkOTI2NTA0ZjMsMDE4YTQ1YmMtZWVmNi03NzFmLTkzZGEtMzU2NDIyYzRkNTAyLGNkNGFlNWI0LTQxOTctNGUzNC1iNGVmLWNiMmVkNzg4YzNmYiwwMThjYWFhMy1lZDMzLTdkNDAtYmFhMy1iZjRlYTU3NzQ2ZTAsMDE5ODI2NDAtY2Y0YS03ZmQ1LWFiNDMtNzk4M2VmMDJiNmYwLDAxOTgzMTAwLWRiNTYtNzFjYy1iNjRkLTZmODRkMGFjNzBkMCIsImV4cCI6MTc1MzQ2MzE2MCwidXNlcm5hbWUiOiI3YTE1ZTZmNjNlYzM5YmM5In0.oQd_HlYVRr2_vC3U2DP31Vw62oYOgOLgWFD8n9KoEnI"
}
video_name = ["中国式现代化理论体系", "习近平新时代中国特色社会主义思想", "总体国家安全观", "习近平强军思想"]
current_video_url_index = 0
# 全局变量存储当前课程ID和主页面句柄
main_window_handle = None  # 用于存储主页面的句柄


def setup_info_only_logger():
    # 移除默认的控制台输出（避免重复日志）
    logger.remove()

    # 添加新的控制台输出，设置级别为INFO
    # level="INFO" 表示只处理INFO及以上级别的日志
    logger.add(
        sys.stdout,
        level="INFO",
        # format="{time:YYYY-MM-DD HH:mm:ss} - Thread:{extra[thread_id]} - {level} - {message}",
    )

    # 可选：添加文件输出，同样限制级别为INFO
    # logger.add(
    #     "info_logs.log",
    #     level="INFO",
    #     rotation="10 MB",  # 日志文件大小限制
    #     format="{time:YYYY-MM-DD HH:mm:ss} - {level} - {message}"
    # )


# 初始化日志配置
setup_info_only_logger()


def get_local_storage_value(driver, key):
    """从localStorage中获取指定键的值"""
    try:
        value = driver.execute_script(f"return window.localStorage.getItem('{key}');")
        return value
    except Exception as e:
        logger.error(f"获取localStorage值失败: {str(e)}")
        return None


def parse_courseid_by_regex(url):
    """从URL中解析courseId"""
    pattern = r'courseId=([^&#]+)'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None


def open_home2(driver):
    global current_course_id
    # 打开个人中心，检测未结业班级列表
    # driver.get("https://web.scgb.gov.cn/#/personal")
    # time.sleep(10)

    try:
        # # 等待包含class为num-info的div元素加载完成
        # num_info_div = WebDriverWait(driver, 10).until(
        #     EC.presence_of_element_located((By.CLASS_NAME, "num-info"))
        # )
        #
        # # 获取该div下所有的span元素
        # span_elements = num_info_div.find_elements(By.TAG_NAME, "span")
        #
        # # 提取所有span元素的文本值
        # span_values = [span.text for span in span_elements if span.text.strip()]
        #
        # # 打印结果
        # print("num-info下的所有span值：")
        # # print(span_values[6])
        # # return span_values[2]=="100%",span_values[5]=="100%"
        # for value in span_values:
        #     print(value)
        # 课程观看，分必修和选修
        # 必修
        driver.get("https://web.scgb.gov.cn/#/myClass?id=019815fe-ec44-753d-9b1d-554f017df106&collected=1")
        time.sleep(5)
        # 等待包含class为num-info的div元素加载完成

        required_div = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((
                By.XPATH,
                "//div[@class='item' and text()=' 必修 ']"
            ))
        )
        required_div.click()
        time.sleep(5)
        required_div = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((
                By.CLASS_NAME,
                "course-list"
            ))
        )
        # 获取必修列表，然后进行播放
        direct_child_divs = required_div.find_elements(
            By.XPATH, "./div"  # 注意开头的点表示当前节点（required_div）
        )
        # 遍历每个子级div
        for index, child_div in enumerate(direct_child_divs, 1):
            try:
                # 获取当前子div中所有的span标签
                span_elements = child_div.find_elements(By.TAG_NAME, "span")

                if span_elements:
                    # print(f"第{index}个div内的span标签值：")
                    if not compare_hours_str(span_elements[3].text.strip()):
                        # 确保元素可点击后再点击
                        WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable(child_div)
                        )

                        # 记录当前所有标签页句柄（点击前）
                        handles_before_click = driver.window_handles

                        # 点击a标签打开新页面
                        child_div.click()

                        WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(len(handles_before_click) + 1))

                        # 获取所有标签页句柄（点击后）
                        all_handles = driver.window_handles

                        # 找到新打开的标签页句柄
                        new_handle = [h for h in all_handles if h not in handles_before_click][0]

                        # 关闭之前的标签页（除了新打开的页面）
                        for handle in all_handles:
                            if handle != new_handle:
                                driver.switch_to.window(handle)
                                driver.close()
                                logger.debug(f"已关闭标签页: {handle}")

                        # 切换到新打开的标签页
                        driver.switch_to.window(new_handle)
                        logger.debug(f"已切换到新标签页: {new_handle}")
                        # 获取新页面的URL
                        new_page_url = driver.current_url
                        # print(f"新页面URL: {new_page_url}")
                        # print(f"新页面URL: {extract_id_from_url(new_page_url)}")
                        # 解析课程ID
                        current_course_id = extract_id_from_url(new_page_url)
                        logger.info(f"当前课程ID: {current_course_id}")

                        return False  # 找到未播放视频，返回False停止翻页
                else:
                    logger.info(f"第{index}个div内未找到任何span标签")

            except Exception as e:
                logger.error(f"处理第{index}个div时出错：{str(e)}\n")
    except TimeoutException:
        logger.error("超时：未找到class为'course-list'的元素")
    except Exception as e:
        logger.error(f"发生错误：{str(e)}")


def extract_id_from_url(url):
    # 解析 URL 结构
    parsed_url = urlparse(url)

    # 提取哈希（#）后的部分（包含路径和参数）
    hash_part = parsed_url.fragment  # 结果为：/course?id=018a4061-a884-7856-81a5-77be717dede0&className=&classId=019815fe-ec44-753d-9b1d-554f017df106

    # 从哈希部分中分离出查询参数（?后面的内容）
    # 先找到 ? 的位置，截取参数部分
    query_start = hash_part.find('?')
    if query_start == -1:
        return None  # 没有查询参数

    query_string = hash_part[
                   query_start + 1:]  # 结果为：id=018a4061-a884-7856-81a5-77be717dede0&className=&classId=019815fe-ec44-753d-9b1d-554f017df106

    # 解析查询参数为字典
    query_params = parse_qs(query_string)

    # 提取 id 参数（parse_qs 返回的值是列表，取第一个元素）
    id_value = query_params.get('id', [None])[0]
    return id_value

def extract_number_from_string(s):
    """从字符串中提取数字（支持整数和小数）"""
    # 使用正则表达式匹配数字（包括整数、小数）
    match = re.search(r'\d+\.?\d*', s)
    if match:
        # 转换为浮点数以便比较
        return float(match.group())
    return None  # 未找到数字
def compare_hours_str(hours_str):
    # 按照 '/' 分割字符串
    parts = hours_str.split('/')

    # 检查分割后是否正好有两部分
    if len(parts) != 2:
        print(f"格式错误：{hours_str} - 无法按照 '/' 分割为两部分")
        return False

    # 去除两边的空白字符
    part1 = parts[0].strip()
    part2 = parts[1].strip()

    # 打印分割后的结果
    # print(f"分割后：左部分='{part1}', 右部分='{part2}'")

    # 判断是否相等
    is_equal = (extract_number_from_string(part1) == extract_number_from_string(part2))
    # print(f"两部分是否相等：{is_equal}\n")

    return is_equal


def open_home(driver):
    global current_video_url_index
    global is_must
    if is_must:
        open_home2(driver)
        return
    logger.info(f"打开首页，检测视频学习情况，current_video_url_index：{current_video_url_index}")
    url = "https://web.scgb.gov.cn/#/specialColumn/course?channelId=01957f20-dacd-76d7-8883-71f375adaab5&id=0194693f-09a5-7875-a64f-1573512205c7&channelName=%E4%B8%AD%E5%9B%BD%E5%BC%8F%E7%8E%B0%E4%BB%A3%E5%8C%96%E7%90%86%E8%AE%BA%E4%BD%93%E7%B3%BB"
    driver.get(url)
    # 切换左侧标签
    # 等待10秒，检查是否存在同时有两个类名的元素
    title = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, "//div[@title='" + video_name[current_video_url_index] + "']"))
    )
    title.click()
    time.sleep(5)
    is_next_page = judge_is_next_page(driver)
    while is_next_page:
        # 当存在class：ivu-page-next ivu-page-disabled说明没有下一页了
        # 首先检查是否存在同时包含两个类名的元素
        try:
            # 等待10秒，检查是否存在同时有两个类名的元素
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".ivu-page-next.ivu-page-disabled"))
            )
            logger.info("存在 class 为 'ivu-page-next ivu-page-disabled' 的元素")
            current_video_url_index = current_video_url_index + 1
            threading.Thread(target=open_home, args=(driver,), daemon=True).start()
            break
        except TimeoutException:
            # 如果不存在，检查是否只存在"ivu-page-next"类的元素
            try:
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "ivu-page-next"))
                )
                logger.info("存在 class 为 'ivu-page-next' 的元素")
                element.click()
                time.sleep(2)
                is_next_page = judge_is_next_page(driver)
            except TimeoutException:
                print("两个类名的元素都不存在")

        except Exception as e:
            logger.error(f"翻页操作失败: {str(e)}")
            break


def check_study_time():
    logger.info("判断当前学习任务是否大于50学时")
    url = "https://api.scgb.gov.cn/api/services/app/class/app/getStudyProcess"
    try:
        response = requests.get(url=url, headers=headers)
        response_json = response.json()
        logger.info(f"当前已学习时长: {response_json['result']['timesSum']}")
        if int(response_json['result']['timesSum']) > 50:
            return False
        else:
            return True
    except Exception as e:
        logger.error(f"获取学习时长失败: {str(e)}")
        return True


def parse_courseid_by_regex(url):
    """从URL中解析courseId"""
    pattern = r'courseId=([^&#]+)'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None


def judge_is_next_page(driver):
    global current_course_id, main_window_handle

    # 首次运行时记录主页面句柄
    if not main_window_handle:
        main_window_handle = driver.current_window_handle
        logger.debug(f"已记录主页面句柄: {main_window_handle}")

    try:
        # 等待class为"list"的div元素加载完成
        list_div = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "list"))
        )

        # 获取该div下的所有a标签
        a_tags = list_div.find_elements(By.TAG_NAME, "a")
        logger.info(f"共找到{len(a_tags)}个a标签元素")

        # 遍历每个a标签，检查是否包含class为"status success"的div
        for index, a_tag in enumerate(a_tags, 1):
            try:
                # 获取a标签的链接和文本
                a_href = a_tag.get_attribute("href")
                # 检查当前a标签内是否存在class为"status success"的div
                a_tag.find_element(By.XPATH, ".//div[@class='status success']")
                logger.info(f"第{index}个a标签：视频播放完成")

            except NoSuchElementException:
                logger.info(f"第{index}个a标签:视频未播放完成，在新的标签页开始播放视频")

                # 记录当前所有标签页句柄（点击前）
                handles_before_click = driver.window_handles

                # 点击a标签打开新页面
                a_tag.click()

                # 等待新标签页打开
                WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(len(handles_before_click) + 1))

                # 获取所有标签页句柄（点击后）
                all_handles = driver.window_handles

                # 找到新打开的标签页句柄
                new_handle = [h for h in all_handles if h not in handles_before_click][0]

                # 关闭之前的标签页（除了新打开的页面）
                for handle in all_handles:
                    if handle != new_handle:
                        driver.switch_to.window(handle)
                        driver.close()
                        logger.debug(f"已关闭标签页: {handle}")

                # 切换到新打开的标签页
                driver.switch_to.window(new_handle)
                logger.debug(f"已切换到新标签页: {new_handle}")

                # 解析课程ID
                current_course_id = parse_courseid_by_regex(a_href)
                logger.info(f"当前课程ID: {current_course_id}")

                return False  # 找到未播放视频，返回False停止翻页

            except Exception as e:
                logger.error(f"处理第{index}个a标签时出错: {str(e)}")

        logger.info("未找到需要播放的视频，点击下一页")
        return True  # 所有视频已完成，返回True继续翻页

    except TimeoutException:
        logger.warning("未找到class为'list'的div元素，可能已到最后一页")
        return False
    except Exception as e:
        logger.error(f"判断下一页时发生错误: {str(e)}")
        return False


def check_course_success(driver, username, password):
    global current_course_id
    global is_running
    sleep_time = 10
    call_login = False
    while True:
        check_play_success_url = "https://api.scgb.gov.cn/api/services/app/course/app/getCourseDetailByUserId?"
        logger.info(f"检测课程id: {current_course_id}")
        if current_course_id != "":
            payload = {
                "courseId": current_course_id
            }
            try:
                course_detail = requests.post(check_play_success_url, headers=headers,
                                              json=payload)
                detail_json = course_detail.json()["result"]
                logger.debug(f"课程详情: {detail_json}")
                if detail_json["totalPeriod"] == detail_json["watchTimes"]:
                    logger.info("已观看完成")
                    if check_study_time():
                        # 播放下一个视频
                        threading.Thread(target=open_home, args=(driver,), daemon=True).start()
                        current_course_id = ""
                    else:
                        is_running = False
                        break
                else:
                    if not call_login:
                        logger.info(
                            f"totalPeriod: {detail_json['totalPeriod']}, watchTimes: {detail_json['watchTimes']}")
                        sleep_time = (int(detail_json["totalPeriod"]) - int(detail_json["watchTimes"])) - 60
                        if sleep_time < 10:
                            sleep_time = 10
                    else:
                        print("重新登录，重新打开页面")
                        threading.Thread(target=open_home, args=(driver,), daemon=True).start()
                        current_course_id = ""
                        call_login = False
            except TimeoutException:
                logger.error("链接超时")
                continue
            except Exception as e:
                logger.error(f"检测课程状态失败: {str(e)}")
                # 登陆失效，进行重新登录
                is_login(driver, username, password)
                call_login = True
                sleep_time = 20
        else:
            sleep_time = 10
        logger.info(f"间隔{sleep_time}秒，继续检测")
        if sleep_time > 0:
            time.sleep(sleep_time)


def init_browser(user_data_dir, is_headless=False):
    # 创建保存用户数据的目录
    user_data_dir = os.path.join(os.getcwd(), user_data_dir)
    os.makedirs(user_data_dir, exist_ok=True)
    logger.debug(f"用户数据目录: {user_data_dir}")

    # 设置 Chrome 浏览器选项
    chrome_options = Options()
    if is_headless:
        chrome_options.add_argument("--headless")  # 无头模式，不显示浏览器窗口
    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")  # 保存用户数据
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    # 指定 ChromeDriver 的路径
    chromedriver_path = "chromedriver.exe"

    # 使用 Service 类来指定驱动路径
    service = Service(chromedriver_path)

    # 初始化 Chrome 浏览器驱动
    return webdriver.Chrome(service=service, options=chrome_options)


def is_login(driver, username=None, password=None):
    while True:
        driver.get("https://web.scgb.gov.cn/#/index")
        time.sleep(2)
        # 检查登录状态
        store = get_local_storage_value(driver, "store")
        if store:
            try:
                store_json = json.loads(store)
                if "accessToken" in store_json['session']:
                    headers['Authorization'] = "Bearer " + store_json['session']['accessToken']
                    logger.info(f"已登录:{store_json['session']['nickName']}【{store_json['session']['organName']}】")
                    return store_json
                else:
                    logger.warning("未登录，请登录")
            except json.JSONDecodeError:
                logger.error("localStorage中store数据格式错误")
        else:
            logger.warning("未登录，请登录")
        auto_login(driver, username, password)
        time.sleep(5)


def download_current_img(driver, img_xpath, save_path="current_image.png"):
    """
    下载页面中当前显示的img图片（应对src动态生成的情况）

    :param driver: Selenium WebDriver实例
    :param img_xpath: 目标img标签的XPath
    :param save_path: 图片保存路径
    :return: 下载成功返回True，失败返回False
    """
    try:
        # 等待图片元素加载完成
        img_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, img_xpath))
        )

        # 通过JavaScript获取图片的Base64编码（当前页面显示的图片）
        # 原理：创建canvas，将图片绘制到canvas，再导出为Base64
        script = """
            var canvas = document.createElement('canvas');
            var ctx = canvas.getContext('2d');
            var img = arguments[0];
            canvas.width = img.naturalWidth;
            canvas.height = img.naturalHeight;
            ctx.drawImage(img, 0, 0);
            return canvas.toDataURL('image/png');
        """
        base64_data = driver.execute_script(script, img_element)

        # 处理Base64数据（去除前缀）
        if base64_data.startswith('data:image/png;base64,'):
            base64_data = base64_data.split(',')[1]
        else:
            print("获取的图片Base64格式不支持")
            return False

        # 解码并保存图片
        img_data = base64.b64decode(base64_data)
        with open(save_path, 'wb') as f:
            f.write(img_data)

        print(f"图片已保存至: {os.path.abspath(save_path)}")
        return True

    except Exception as e:
        print(f"下载图片失败: {str(e)}")
        return False


def auto_login(driver, username, password):
    try:
        logger.info("开始自动登录")
        # 输入用户名
        username_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="请输入您的用户名"]'))
        )
        username_input.clear()
        username_input.send_keys(username)

        # 输入密码
        password_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="请输入您的密码"]'))
        )
        logger.info("找到密码输入框")
        password_input.clear()
        password_input.send_keys(password)

        # # 处理验证码
        capture_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="请输入验证码"]'))
        )
        capture_input.clear()
        captcha = get_formdata_img_src(driver)
        capture_input.send_keys(captcha)
        # 点击登录按钮
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//div[@class="ivu-form-item-content"]//button'))
        )
        login_button.click()
        # 判断是的为第一次登录，修改登录密码
    except TimeoutException:
        logger.error("超时未找到登录相关输入框")
    except ElementNotInteractableException:
        logger.error("登录输入框不可交互")
    except Exception as e:
        logger.error(f"自动登录失败: {str(e)}")


def get_formdata_img_src(driver, wait_time=10):
    """获取验证码图片并识别"""
    try:
        # 等待验证码图片容器加载
        formdata_div = WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located((By.CLASS_NAME, "validate-form-img"))
        )
        logger.info("找到验证码图片容器")
        save_path = "captcha_screenshot.png"  # 保存路径可自定义
        success = formdata_div.screenshot(save_path)

        if success:
            print(f"图片元素截图已保存至: {os.path.abspath(save_path)}")
            return recognize_verify_code(image_path=os.path.abspath(save_path))
        else:
            print("截图保存失败，可能元素不可见或尺寸为0")
            return ""
    except TimeoutException:
        logger.error("超时未找到验证码图片容器")
    except NoSuchElementException:
        logger.error("未找到验证码图片")
    except Exception as e:
        logger.error(f"获取验证码图片失败: {str(e)}")
    return ""


def recognize_verify_code(image_path=None, image_url=None):
    """使用ddddocr识别验证码"""
    try:
        if image_path:
            with open(image_path, 'rb') as f:
                image_data = f.read()
        elif image_url:
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            image_data = response.content
        else:
            logger.warning("未提供验证码图片路径或URL")
            return None

        result = ocr.classification(image_data)
        logger.info(f"验证码识别结果: {result}")
        return result
    except Exception as e:
        logger.error(f"验证码识别失败: {str(e)}")
        return None


def exec_main(name, username, password, is_head=True):
    driver = init_browser(user_data_dir=name, is_headless=is_head)
    # 判断用户是否登录
    is_login(driver, username, password)
    driver.close()
    driver = init_browser(user_data_dir=name, is_headless=is_head)
    open_home(driver)
    threading.Thread(target=check_course_success, args=(driver, username, password,), daemon=True).start()


def read_config():
    # 创建配置解析器对象
    config = configparser.ConfigParser()

    # 获取配置文件路径（兼容开发环境和打包后的环境）
    if getattr(sys, 'frozen', False):
        # 打包后的环境
        base_dir = os.path.dirname(sys.executable)
    else:
        # 开发环境
        base_dir = os.path.dirname(os.path.abspath(__file__))

    config_path = os.path.join(base_dir, 'config.ini')

    # 检查配置文件是否存在
    if not os.path.exists(config_path):
        print(f"错误：配置文件 {config_path} 不存在！")
        return
        # 读取配置文件
    config.read(config_path, encoding='utf-8')
    return config


if __name__ == '__main__':
    # 读取配置文件
    config = read_config()
    name = config['DEFAULT']['name']
    username = config['DEFAULT']['username']
    password = config['DEFAULT']['password']
    isHead = bool(config['DEFAULT']['isHead'])
    if 'isMust' in config['DEFAULT']:
        is_must = bool(config['DEFAULT']['isMust'])
    if 'startIndex' in config['DEFAULT']:
        current_video_url_index = int(config['DEFAULT']['startIndex'])
    exec_main(name, username, password, is_head=isHead)
    while is_running:
        time.sleep(1)
    print("视频已全部播放完成")
