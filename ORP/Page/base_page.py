from abc import ABC

import allure

from Base.base import Base
from Utils.log_utils import LoggerManager


class BasePage(ABC):
    """最顶层的抽象基类, 所有页面都继承自它, 提供最通用的操作和方法
    """
    _locators = {
        "query_期望提示信息": "//*[contains(text(), '{}')]",
    }

    def __init__(self, driver):
        self.driver = driver
        self.logger = LoggerManager().get_logger()

        # 按 MRO 顺序(从 top -> bottom) 的顺序合并每一级的 _locators
        merged = {}
        for cls in self.__class__.__mro__:
            # 只合并在当前类定义的 _locators, 跳过 object/ABC
            if '_locators' in cls.__dict__:
                merged.update(cls.__dict__['_locators'])
        self._locators = merged
        self.base = Base(driver, self._locators)

    @allure.step("进入指定url")
    def goto(self, url: str):
        """ 在当前 driver 上通过 url 直接跳转页面
        :param url: 目标 url
        """
        self.base.browser_op.goto(url)

