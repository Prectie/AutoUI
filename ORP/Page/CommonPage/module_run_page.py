import allure

from Page.base_page import BasePage


class ModuleRunPage(BasePage):
    """ 建模与运行系统页面, 负责进入不同页面
    """
    _locators = {
        "action_进入选择功能页": "//span[text()='{}']",
    }

    @allure.step("进入指定菜单")
    def goto_page(self, page: str):
        self.base.element_op.click_by_keyword('action_进入选择功能页', page)
