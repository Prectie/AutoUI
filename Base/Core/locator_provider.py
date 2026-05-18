from typing import Dict, Tuple, Union, List

from selenium.webdriver.common.by import By

from Utils.log_utils import LoggerManager

logger = LoggerManager.get_logger()


class LocatorMixin:
    """ 定位器处理 Mixin """
    def __init__(self, locators: Dict[str, str]):
        # 由 LocatorMixin 管理 _locators
        self._locators = locators

    def _get_locator_dict(self) -> Dict[str, Tuple[str, str]]:
        """
        获取每个页面的 _locator

        :return: dict[str, Tuple[str, str]] -> 返回 定位器管理器, 形如 {'action_登录': (By.Xpath, "//*[text='登录']")}
        """
        locators = getattr(self, "_locators", None)
        # 校验
        if not isinstance(locators, dict):
            logger.error(f"AttributeError: {self.__class__.__name__} 未定义 '_locators'")
            raise AttributeError(f"{self.__class__.__name__} 未定义 '_locators'")
        return locators

    def _get_locator(self, keyword: str) -> Union[Tuple[str, str], List[Tuple[str, str]]]:
        """
        从 _locator_map 中根据关键字返回具体的定位器, 不加定位方式时(By.xx) 该方法默认 By.XPath 定位方式

        :param keyword: 关键字名称, 定位器来源
        :return: Tuple[str, str] | List[Tuple[str, str]] -> 单级定位器或多级定位器
        """
        try:
            loc = self._get_locator_dict()[keyword]
        except KeyError:
            logger.error(f"KeyError: {self.__class__.__name__}.'_locators' 中未定义 {keyword}")
            raise KeyError(f"{self.__class__.__name__}.'_locators' 中未定义 {keyword}")

        # 单字符串 -> 返回时带上 By.XPath
        if isinstance(loc, str):
            return By.XPATH, loc
        # 字符串列表 -> 返回多级 XPath
        if isinstance(loc, list) and all(isinstance(item, str) for item in loc):
            return [(By.XPATH, item) for item in loc]
        return loc

    def _format_locator(self, keyword: str, *args) -> Union[Tuple[str, str], List[Tuple[str, str]]]:
        """
        返回格式化后的定位器, 支持单级或多级的返回

        :param keyword: 关键字名称, 定位器来源
        :param args: 用于格式化定位器字符串中的占位符 (如 "//div[text()='{}']")
        :return: Tuple[str, str] | List[Tuple[str, str]] -> 格式化后的单级定位器或多级定位器
        """
        loc = self._get_locator(keyword)
        if isinstance(loc, tuple):
            by, value = loc
            return by, (value.format(*args) if args else value)
        if isinstance(loc, list):
            # 格式化每一级定位器
            if args:
                return [(by, value.format(*args)) for by, value in loc]
            return loc
        raise TypeError(f"不支持的定位器类型: {type(loc)}")
