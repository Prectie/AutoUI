import allure

from Page.base_page import BasePage


class AdminConsolePage(BasePage):
    """ 后台管理页面

      PS: 包含三个子页面, 现仅用到运行监控页面, 若用到其它两个页面再拆
    """
    _locators = {
        "action_通用文本容器": "//span[text()='{}']",

        "action_指定用户运行的场景_选择操作": "//div[contains(@class, 'transition')]//tbody[@tabindex]"
                                              "//div[contains(text(), '用户信息：用户({})操作推演')]"
                                              "//ancestor::td//following-sibling::td//div[text()='{}']"
                                              "//ancestor::td//following-sibling::td[contains(@class, 'column_9')]"
                                              "//span[text()='{}']//parent::button",
        
        "iframe_运行实例管理": "//iframe[contains(@src, '5100')]",
    }

    @allure.step("进入子页面")
    def _enter_subpage(self, subpage):
        """
          进入子页面
        :param subpage: 子页面名称
        """
        self.base.element_op.click_by_keyword('action_通用文本容器', subpage)

    @allure.step("删除任务")
    def _delete_business(self):
        # 点击弹出框的确认
        self.base.browser_op.click_dialog_confirm_button()
        


    @allure.step("运行实例管理_操作业务场景")
    def perform_instance_action(self, subpage, account_name, scenario_name, operate):
        """
          进入子页面, 操作指定用户运行的场景
        :param subpage: 子页面名称
        :param account_name: 用户名称
        :param scenario_name: 场景名称
        :param operate: 操作(如停止任务、删除任务、暂停任务等)
        :return:
        """
        # 进入运行实例管理页面
        self._enter_subpage(subpage)
        # 进入 iframe
        self.base.element_op.switch_iframe_by_keyword('iframe_运行实例管理')
        # 操作指定场景
        self.base.element_op.click_by_keyword(
            'action_指定用户运行的场景_选择操作',
            account_name,
            scenario_name,
            operate
        )
        if '删除' in operate:
            pass
        # 点击弹出框的确认
        self.base.browser_op.click_dialog_confirm_button()
        # 返回顶层 iframe
        self.base.element_op.switch_default_iframe()
