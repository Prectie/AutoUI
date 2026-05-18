import allure
from selenium.common import NoSuchElementException

from Page.base_page import BasePage


class LoginPage(BasePage):
    """定位器命名规则说明

    操作器(Action): 所有可交互元素(点击/输入/提交), 如：按钮，输入框，可点击元素等
    读取器(Query): 仅用于获取信息(文本/属性/状态), 如：纯展示的元素
    导航器(Context): 需要切换上下文的容器, 如：下拉菜单等
    iframe: 单独为 iframe 列一个分类
    """
    _locators = {
        "action_账号输入框": "//input[@placeholder='账号']",
        "action_密码输入框": "//input[@placeholder='请输入密码']",
        "action_登录按钮": "//*[contains(@class, 'login-btn')]",
    }

    def _entry(self):
        """进入登录页"""
        if not self._env_url:
            raise ValueError("env_url 未配置, 无法自动跳转到登录页, 请通过 pytest --env 或 toml 配置登录地址")
        self.goto(self._env_url)

    """ 业务逻辑 """
    @allure.step("执行 登录 操作")
    def login(self, username, password, times: int = 1):
        """
        进入登录页面, 默认点击登录一次, 次数可配置
        """
        # 进入登录页面
        self._entry()
        # 清空输入框并输入账号密码
        self.base.element_op.clear_and_input_by_keyword('action_账号输入框', value=username)

        self.base.element_op.clear_and_input_by_keyword('action_密码输入框', value=password, timeout=10, poll_frequency=0.5, ignored_exceptions=NoSuchElementException)

        time = 0
        while time < times:
            # 点击登录
            self.base.element_op.click_by_keyword("action_登录按钮")
            time += 1



