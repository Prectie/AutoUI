from typing import Union, Tuple, Callable

from selenium.common import NoSuchFrameException
from selenium.webdriver.remote.webdriver import WebDriver


def default_frame_to_be_available_and_switch_to_it() -> Callable[[WebDriver], bool]:
    """
    切换回默认iframe
    """
    def _predicate(driver: WebDriver):
        try:
            driver.switch_to.default_content()
            return True
        except NoSuchFrameException:
            return False

    return _predicate


def parent_frame_to_be_available_and_switch_to_it() -> Callable[[WebDriver], bool]:
    """
    切换回父级iframe, 如果当前iframe为顶级, 则保持不变
    """
    def _predicate(driver: WebDriver):
        try:
            driver.switch_to.parent_frame()
            return True
        except NoSuchFrameException:
            return False

    return _predicate
