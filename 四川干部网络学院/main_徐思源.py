import threading
import time

from 四川干部网络学院.main import init_browser, is_login, open_home, check_course_success, is_running
username = "13679644177"

password = "Abcd1234@"

if __name__ == '__main__':
    driver = init_browser(user_data_dir="徐思源", is_headless=True)
    # 判断用户是否登录
    store = is_login(driver,username,password)

    open_home(driver)

    threading.Thread(target=check_course_success, daemon=True).start()
    while is_running:
        time.sleep(1)
    print("视频已全部播放完成")
