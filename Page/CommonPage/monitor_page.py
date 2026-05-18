import time

import allure

from Enum.wait_strategy import WaitStrategy
from Page.base_page import BasePage


class MonitorPage(BasePage):
    """ 运行实例监控页面, 负责管理模型任务
    """
    _locators = {
        "action_指定的正在运行的场景_停止任务按钮": "//div[contains(text(), '{}')]//parent::td"
                                                     "//following-sibling::td[contains(@class, 'column_4')]"
                                                     "//span[text()='正在运行']//ancestor::td"
                                                     "//following-sibling::td[contains(@class, 'column_9')]"
                                                     "//span[text()='停止任务']//parent::button",
        "query_指定场景的正在运行状态": "//div[contains(text(), '{}')]//parent::td"
                                        "//following-sibling::td[contains(@class, 'column_4')]"
                                        "//span[text()='正在运行']"
    }

    @allure.step("停止指定任务")
    def stop_task(self, task) -> int:
        """
        停止指定任务

        :param task: 指定的任务
        :return: 若页面上该场景不存在正在运行的状态返回 0, 反之说明该场景在该页面中仍然存在正在运行状态
        """
        # 进入监控页面
        # TODO 不要跳转到另一个端口，在原URL上通过后台管理进行停止任务
        self.goto(URLEnum.ORP_MONITOR.value)
        # 找到指定任务, 点击停止按钮
        self.base.element_op.click_by_keyword('action_指定的正在运行的场景_停止任务按钮', task)
        # 点击弹出框的确认
        self.base.browser_op.click_dialog_confirm_button()
        # 因为删除成功没有任何提示, 且延迟比较大, 强制等待 1.5s
        time.sleep(1.5)
        # 再次尝试获取该场景的正在运行状态, 若无返回 0
        ret = self.base.element_op.get_elements_by_keyword('query_指定场景的正在运行状态', task, wait_strategy=WaitStrategy.GET_ALL)
        return len(ret)
