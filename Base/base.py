from Base.Facade.browser_operator import BrowserMixin
from Base.Facade.element_operator import KeywordMixin
from Base.Facade.mouse_action import MouseAction
from Base.Facade.wait_operator import WaitMixin
from Utils.log_utils import LoggerManager

logger = LoggerManager.get_logger()


class Base:
    # 初始化, 默认 chrome 浏览器
    def __init__(self, driver, locators):
        self.element_op = KeywordMixin(driver, locators)
        self.browser_op = BrowserMixin(driver, locators)
        self.mouse_op = MouseAction(driver, locators)
        self.wait_op = WaitMixin(driver, locators)


