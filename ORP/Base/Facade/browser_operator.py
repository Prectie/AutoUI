from typing import Dict, List, Optional
from urllib.parse import urlparse, urljoin

from selenium.common import TimeoutException
from selenium.webdriver.chrome.webdriver import WebDriver

from Utils.log_utils import LoggerManager
from Base.Core.selenium_element import WaitStrategy, ElementMixin


logger = LoggerManager().get_logger()


def _origin_from_url(url: str) -> str:
    """
      获取源地址
      支持传入:
        - https://test.com            -> https://test.com
        - https://test.com/login      -> https://test.com
    :param url: 需要解析的 url
    :return: 返回源地址
    """
    p = urlparse(url)
    if not p.scheme or not p.netloc:
        raise ValueError(f"检查传入的 url 是否正确, 正确的 url 需要包含(scheme 和 netloc), 但实际传入的 url 为: {url}")
    return f"{p.scheme}://{p.netloc}"


class BrowserMixin(ElementMixin):
    def __init__(self, driver: WebDriver, locators: Dict[str, str]):
        # 初始化 locator 与 driver
        super().__init__(driver, locators)

    def goto(self, path: str, origin: Optional[str] = None, infer_origin: bool = False) -> None:
        """
          统一跳转入口

          path 只允许两种写法:
            1) 绝对路径
            2) 相对路径, 但是必须以 / 开头, 如 /login
        :param path: 绝对路径或相对路径的 url
        :param origin: 源地址, 如 http://127.0.0.1:8080
        :param infer_origin: 控制是否自动获取当前浏览器的源地址(不传 origin 情况下中途跳转)
        """
        if path is None:
            raise ValueError("path 参数不能为空")

        path = str(path).strip()  # str化path, 并去掉前后空格
        if not path:
            raise ValueError("path 不能为空字符串")

        # 1.为绝对路径时, 直接跳转
        if path.startswith("http://") or path.startswith("https://"):
            self._driver.get(path)
            return

        # 2.为相对路径时
        if path.startswith("/"):
            base = None

            if origin:
                base = _origin_from_url(str(origin).strip())

            if (not base) and infer_origin:
                cur = self._driver.current_url
                base = _origin_from_url(cur)

            if not base:
                raise ValueError(f"所给的路径不正确, 请检查。所给的路径为：{path!r}, 源地址为：{origin!r}")

            # 拼接
            full = urljoin(base.rstrip("/") + "/", path.lstrip("/"))
            self._driver.get(full)
            return

        # 3.拒绝其他写法
        raise ValueError("所给路径的写法不正确, 请检查。所给的路径为：{path!r}")

    def close_current_window(self) -> None:
        """ 关闭浏览器 """
        self._driver.close()

    def refresh_window(self) -> None:
        """ 刷新当前标签页 """
        self._driver.refresh()

    def get_current_window_title(self) -> str:
        """ 获取当前窗口标题

        :return: str -> 返回当前窗口标题名称
        """
        return self._driver.title

    def _switch_to_handle(self, handle: str) -> None:
        """ 切换到指定的窗口句柄

        :param handle: 指定窗口句柄
        """
        self._driver.switch_to.window(handle)

    def get_current_handles(self) -> List[str]:
        return self._driver.window_handles

    def switch_to_new_window(self):
        """切换到最后一个打开的窗口(通常用于新开窗口后切换)

        注意: 仅支持同一进程下的同步状态, 异步状态使用该函数可能会出现问题
        """
        handles = self._driver.window_handles
        if not handles:
            logger.warning(f"当前没有任何窗口可切换")
            return
        # 调用切换到指定窗口句柄
        self._switch_to_handle(handles[-1])

    def switch_to_first_window(self):
        """ 切换到第一个打开的窗口 """
        handles = self._driver.window_handles
        if not handles:
            logger.warning(f"当前没有任何窗口可切换")
            return
        self._switch_to_handle(handles[0])

    def switch_to_previous_window(self):
        """ 回到上一级窗口 """
        handles = self._driver.window_handles
        if not handles:
            logger.warning(f"当前没有任何窗口可切换")
            return
        current_handle = self._driver.current_window_handle
        index = handles.index(current_handle)
        if index > 0:
            prev_handle = handles[index - 1]
            self._driver.switch_to.window(prev_handle)

    # ========================= 弹出框操作 =========================
    def click_dialog_confirm_button(self):
        """ 点击弹出框的确认按钮
        """
        alert = self._driver.switch_to.alert
        alert.accept()






