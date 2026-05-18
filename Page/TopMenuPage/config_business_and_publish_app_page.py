import time

import allure

from Page.base_page import BasePage


class ConfigBusinessAndPublishAppPage(BasePage):
    """ 配置业务/发布应用 页面
    """
    _locators = {
        "action_搜索输入框": "//div[contains(@id, 'K8_YWLYGL_SETTING')]//input[contains(@id, 'qqfield')]",
        "action_查询": "//div[contains(@id, 'K8_YWLYGL_SETTING')]//div[text()='查询']",
        "action_指定业务启动": "//div[contains(@id, 'K8_YWLYGL_SETTING')]//td[contains(@class, 'YWLYGL_BT')]"
                               "//span[text()='{}']//ancestor::td"
                               "//preceding-sibling::td[contains(@class, 'actioncolumn')]//div[@data-qtip='启动']"
    }

    @allure.step("搜索业务")
    def search(self, biz):
        """
          搜索指定业务应用
        :param biz: 业务名称
        """
        # 搜索框填入名称
        self.base.element_op.input_by_keyword('action_搜索输入框', value=biz)
        # 点击查询按钮
        self.base.element_op.click_by_keyword('action_查询')

    @allure.step("启动指定业务并切换tab")
    def start_business(self, biz):
        """
          启动指定业务并切换至其标签页
        :param biz: 业务名称
        """
        # 点击启动并切换标签页
        self.base.browser_op.switch_to_last_window(
            lambda: self.base.element_op.click_by_keyword('action_指定业务启动', biz)
        )




