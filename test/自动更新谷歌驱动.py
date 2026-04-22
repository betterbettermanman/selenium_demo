from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

MIRROR_URL = "https://registry.npmmirror.com/-/binary/chromedriver/"
MIRROR_LATEST_RELEASE_URL = f"{MIRROR_URL}LATEST_RELEASE"


def install_chromedriver_path() -> str:
    """
    在中国网络环境下优先使用 npmmirror 下载 ChromeDriver，
    如果失败则自动回退到官方源。
    """
    try:
        print("正在尝试通过国内镜像下载/更新 ChromeDriver ...")
        return ChromeDriverManager(
            url=MIRROR_URL,
            latest_release_url=MIRROR_LATEST_RELEASE_URL,
        ).install()
    except Exception as mirror_error:
        print(f"国内镜像下载失败，准备回退官方源：{mirror_error}")
        print("正在尝试通过官方源下载/更新 ChromeDriver ...")
        return ChromeDriverManager().install()


def build_driver() -> webdriver.Chrome:
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--start-maximized")
    service = Service(install_chromedriver_path())
    return webdriver.Chrome(service=service, options=chrome_options)


def main() -> None:
    driver = build_driver()
    try:
        driver.get("https://www.baidu.com")
        print(f"页面标题：{driver.title}")
        input("浏览器已打开，按回车键退出...")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()