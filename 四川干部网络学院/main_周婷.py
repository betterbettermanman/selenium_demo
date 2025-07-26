import time

from 四川干部网络学院.main import is_running, exec_main

name = "周婷"
username = "18783363361"

password = "ZTzt1219089650@"

if __name__ == '__main__':
    exec_main(name, username, password)
    while is_running:
        time.sleep(1)
    print("视频已全部播放完成")
