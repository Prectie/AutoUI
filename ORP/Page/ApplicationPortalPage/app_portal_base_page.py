import allure

from Page.base_page import BasePage


class APPPortalBasePage(BasePage):
    """ 应用门户基础页面, 负责进入不同的应用助手
    """
    _locators = {
        "iframe_应用门户": "//iframe[@src='/user_apps_center_new.html']",
        "action_武器装备智能检索助手": "//div[@id='middle-container']//div[@title='武器装备智能检索助手']",
    }

    def _switch_portal_iframe(self):
        """ 切换到应用门户的 iframe
        """
        self.base.element_op.switch_iframe_by_keyword('iframe_应用门户')

    """ 业务逻辑 """
    @allure.step("进入武器装备智能检索助手页面")
    def enter_armament_search_page(self):
        """ 进入武器装备智能检索助手页面
        （这里可以修改为动态的, 根据传入的页面名称进入对应的页面）
        """
        # 切换到助手所在的 iframe 页面
        self._switch_portal_iframe()
        # 获取当前窗口所有句柄
        old_handles = self.base.browser_op.get_current_handles()
        # 点击进入
        self.base.element_op.click_by_keyword('action_武器装备智能检索助手')
        # 等待新窗口的打开
        self.base.wait_op.wait_new_window_is_opened(current_handles=old_handles)
        # 进入新标签页
        self.base.browser_op.switch_to_new_window()
