import logging

from selenium import webdriver
from selenium.webdriver.chrome.service import Service


def open_browser(browser: str, download_dir: str):
    # 封装打开浏览器
    if browser.lower() == 'chrome':
        # 设置驱动路径
        service = Service("C:/Program Files/chrome-win64/chromedriver.exe")

        # 设置该浏览器的下载目录
        options = webdriver.ChromeOptions()
        if download_dir:
            options.add_experimental_option("prefs", {
                "download.default_directory": download_dir,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": False,
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False
            })
        # 隐藏新版"不安全下载"提示
        options.add_argument("--disable-features=InsecureDownloadWarnings")
        # 关闭扩展黑名单检查
        options.add_argument("--safebrowsing-disable-extension-blacklist")

        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        # 每个窗口都打开开发者工具, 用于调试
        # options.add_argument("--auto-open-devtools-for-tabs")
        return webdriver.Chrome(service=service, options=options)
    elif browser.lower() == 'firefox':
        # 这里没下firefox的驱动, 暂时先用 chrome
        return webdriver.Firefox()
    else:
        print("输入的浏览器不合法,请输入 chrome firefox")
        return None


