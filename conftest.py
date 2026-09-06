"""AutoUI pytest 插件注册入口。

pytest 会从 ``pytest_plugins`` 加载项目级插件，
使测试用例可以直接使用 AutoUI 的配置、数据、日志和 Web fixture。
各插件只负责自己的基础设施边界，测试用例不需要重复初始化这些对象。
"""

# data：YAML 测试数据读取和参数化；
# web：Playwright BrowserContext 配置及 Page Object fixture；
# options：--env、--site 等命令行参数和 Settings fixture；
# runtime：ExecutionIdentity 以及测试项级结构化日志生命周期。
pytest_plugins = [
    "autoui.plugins.data",
    "autoui.plugins.web",
    "autoui.plugins.options",
    "autoui.plugins.runtime",
]
