from typing import Dict, List, Optional, Callable
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
        raise ValueError(f"所给路径的写法不正确, 请检查。所给的路径为：{path!r}")

    def close_current_window(self) -> None:
        """ 关闭浏览器 """
        self._driver.close()

    def refresh_window(self) -> None:
        """ 刷新当前标签页 """
        self._driver.refresh()

    def get_current_window_title(self) -> str:
        """
          获取当前窗口标题
        :return: str -> 返回当前窗口标题名称
        """
        return self._driver.title

    def _switch_to_handle(self, handle: str) -> None:
        """
          切换到指定的窗口句柄
        :param handle: 指定窗口句柄
        """
        self._driver.switch_to.window(handle)

    def get_current_handles(self) -> List[str]:
        """
          获取当前浏览器窗口所有句柄
        :return: 句柄数组
        """
        return self._driver.window_handles

    def wait_new_window_is_opened(
        self,
        wait_strategy: WaitStrategy = WaitStrategy.NEW_WINDOW_IS_OPENED,
        current_handles: Optional[List[str]] = None,
        **kw
    ):
        """
          等待新窗口的打开

        :param wait_strategy: 等待策略, 默认 WAIT_STALENESS (仅使用该策略)
        :param current_handles: 当前窗口的所有句柄
        :param kw: 等待配置: timeout, poll_frequency, ignored_exceptions
        :return: bool -> 操作成功返回 True, 失败返回 False
        """
        return self.wait(WaitStrategy.IGNORED_LOCATOR, wait_strategy, current_handles=current_handles, **kw)

    def switch_to_last_window(self, action: Callable[[], None]):
        """
          切换到最后一个打开的窗口(通常用于新开窗口后切换)
        :param action: 行为, 一般会打开一个新标签页
        """
        if not callable(action):
            raise ValueError("action 必须是可调用对象, 例如 lambda: ...")

        old_handles = self.get_current_handles()
        logger.info(f"{self.get_current_window_title()}")
        if not old_handles:
            logger.warning(f"当前没有任何窗口可切换")
            return

        # 执行行为, 行为一般会打开一个新标签页
        action()

        # 等待新窗口的打开
        self.wait_new_window_is_opened(current_handles=old_handles)

        # 使用差集进行切换
        now_handles = self.get_current_handles()
        new_set = set(now_handles) - set(old_handles)
        if not new_set:
            # 如果没有新窗口
            raise ValueError("未发现新窗口的打开, 请检查传入的行为是否打开了新窗口")
        else:
            new_handles = next(h for h in now_handles if h in new_set)

        self._switch_to_handle(new_handles)
        logger.info(f"{self.get_current_window_title()}")

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






