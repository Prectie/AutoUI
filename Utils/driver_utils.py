import os
import shutil
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.service import Service


def _is_truthy(value: Optional[str]) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _chrome_service() -> Optional[Service]:
    driver_path = os.getenv("CHROMEDRIVER_PATH")
    if driver_path:
        return Service(driver_path)

    default_windows_path = "C:/Program Files/chrome-win64/chromedriver.exe"
    if os.path.exists(default_windows_path):
        return Service(default_windows_path)

    path_driver = shutil.which("chromedriver")
    if path_driver:
        return Service(path_driver)

    # Selenium Manager will try to resolve the matching driver.
    return None


def _need_headless() -> bool:
    if _is_truthy(os.getenv("SELENIUM_HEADLESS")):
        return True
    if os.name == "nt":
        return False
    return not (os.getenv("DISPLAY") or os.getenv("WAYLAND_DISPLAY"))


def open_browser(browser: str, download_dir: str):
    # 封装打开浏览器
    if browser.lower() == 'chrome':
        # 设置该浏览器的下载目录
        options = webdriver.ChromeOptions()
        chrome_binary = os.getenv("CHROME_BINARY_PATH")
        if chrome_binary:
            options.binary_location = chrome_binary

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
        options.add_argument("--window-size=1440,1000")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        if _need_headless():
            options.add_argument("--headless=new")

        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        # 每个窗口都打开开发者工具, 用于调试
        # options.add_argument("--auto-open-devtools-for-tabs")
        service = _chrome_service()
        if service:
            return webdriver.Chrome(service=service, options=options)
        return webdriver.Chrome(options=options)
    elif browser.lower() == 'firefox':
        # 这里没下firefox的驱动, 暂时先用 chrome
        return webdriver.Firefox()
    else:
        print("输入的浏览器不合法,请输入 chrome firefox")
        return None


