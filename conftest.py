"""AutoUI pytest 插件注册入口。

pytest 会从 ``pytest_plugins`` 加载项目级插件，
使测试用例可以直接使用 AutoUI 的配置、Web 和 Allure 集成。
各插件只负责自己的基础设施边界，测试用例不需要重复初始化这些对象。
"""

import os
from pathlib import Path


# 浏览器二进制随项目缓存，但不进入版本控制。使用 setdefault 保留 CI 或
# 开发者显式提供的 PLAYWRIGHT_BROWSERS_PATH。
os.environ.setdefault(
    "PLAYWRIGHT_BROWSERS_PATH",
    str(Path(__file__).resolve().parent / ".playwright-browsers"),
)


# web：Playwright BrowserContext 配置；
# options：--env、--site 等命令行参数和 Settings fixture；
# allure_reporting：运行 labels 与失败诊断附件。
pytest_plugins = [
    "autoui.plugins.web",
    "autoui.plugins.options",
    "autoui.plugins.allure_reporting",
]
