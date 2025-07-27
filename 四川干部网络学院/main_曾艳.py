import time

from 四川干部网络学院.main import is_running, exec_main

name = "曾艳"

username = "13618045535"

password = "Abcd1234"

if __name__ == '__main__':
    exec_main(name, username, password)
    while is_running:
        time.sleep(1)
    print("视频已全部播放完成")
