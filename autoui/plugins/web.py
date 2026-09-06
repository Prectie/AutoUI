"""
Web UI 测试插件。

本模块负责将 AutoUI 的 Settings 配置应用到
pytest-playwright 的浏览器上下文中，并提供 Web UI 测试所需的页面对象 fixture。

主要功能包括：

1. 设置浏览器的 base_url、viewport、locale 和 timezone；
2. 忽略测试环境中的 HTTPS 证书错误；
3. 创建当前测试项使用的 WebStepRuntime；
4. 创建 OrderConsolePage、BaiduPage、HomePage、CommonPage 和 EditorPage 页面对象。

依赖关系：
    pytest-playwright 提供 page 和 browser context，
    runtime plugin 提供 autoui_logger，
    本模块负责把这些基础设施注入 Web 层对象。
"""

import pytest
from playwright.sync_api import Page

from autoui.core.logging.autoui_logger import AutoUILogger
from autoui.platforms.web.pages.baidu_page import BaiduPage
from autoui.platforms.web.pages.common_page import CommonPage
from autoui.platforms.web.pages.editor_page import EditorPage
from autoui.platforms.web.pages.home_page import HomePage
from autoui.platforms.web.pages.order_console_page import OrderConsolePage
from autoui.platforms.web.steps import WebStepRuntime


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, settings):
    """
    为 pytest-playwright 的 BrowserContext 提供统一配置。

    参数：
        browser_context_args:
            pytest-playwright 默认提供的浏览器上下文参数。
            通过解包可以保留原有配置。

        settings:
            AutoUI 项目的全局 Settings 配置。

    返回：
        合并后的 BrowserContext 配置字典。

    配置内容包括：

        base_url:
            页面访问的基础 URL。

        viewport:
            浏览器视口宽高。

        locale:
            浏览器语言区域设置。

        timezone_id:
            浏览器时区。

        ignore_https_errors:
            忽略 HTTPS 证书错误，适合测试环境使用。
    """
    # 先保留 pytest-playwright 的默认上下文配置，
    # 再使用 AutoUI 的 settings 覆盖项目需要统一管理的配置。
    return {
        **browser_context_args,

        # 页面访问时使用的基础 URL。
        "base_url": settings.base_url,

        # 浏览器窗口的视口大小。
        "viewport": {
            "width": settings.viewport.width,
            "height": settings.viewport.height,
        },

        # 浏览器的语言区域。
        "locale": settings.locale,

        # 浏览器使用的时区。
        "timezone_id": settings.timezone_id,

        # 测试环境可能使用自签名证书，因此忽略 HTTPS 证书错误
        "ignore_https_errors": True,
    }

@pytest.fixture
def web_step_runtime(
    page: Page,
    autoui_logger: AutoUILogger,
) -> WebStepRuntime:
    """
    为当前测试项创建 WebStepRuntime 适配对象。

    参数：
        page:
            pytest-playwright 为当前测试项提供的 Page。
            WebStepRuntime 通过它访问 BrowserContext 的 tracing，
            但不负责页面或 Trace 文件的生命周期。

        autoui_logger:
            runtime plugin 提供的当前测试项级 AutoUILogger。
            它已经绑定 ExecutionIdentity、output_path 和 JSONL handler。

    返回：
        绑定当前测试项日志上下文的 WebStepRuntime。

    生命周期：
        fixture 默认使用 function scope，
        因此每个测试项都会获得独立的 WebStepRuntime 实例。

    设计边界：
        本 fixture 只负责依赖注入；WebStepRuntime 不创建 logger、handler
        或日志文件，也不执行具体的 Playwright 操作。
    """
    return WebStepRuntime(
        page=page,
        autoui_logger=autoui_logger,
    )


@pytest.fixture
def order_console_page(page):
    """
    为回归测试提供 OrderConsolePage 页面对象。

    参数：
        page:
            pytest-playwright 为当前测试项提供的 Page 实例。

    返回：
        绑定该 Page 的 OrderConsolePage。

    生命周期：
        fixture 默认使用 function scope，页面对象只服务于当前测试项。
    """
    return OrderConsolePage(page)


@pytest.fixture
def baidu_page(page, web_step_runtime: WebStepRuntime):
    """
    为 smoke 测试提供已注入步骤运行时的 BaiduPage。

    参数：
        page:
            pytest-playwright 为当前测试项提供的 Page 实例。

        web_step_runtime:
            当前测试项的 WebStepRuntime，负责把页面对象中的业务步骤
            转换为 business_step JSONL 事件。

    返回：
        同时绑定 Page 和 WebStepRuntime 的 BaiduPage。

    生命周期：
        fixture 默认使用 function scope，页面对象与步骤运行时只服务于当前测试项。
    """
    return BaiduPage(page, web_step_runtime)


@pytest.fixture
def home_page(page: Page, web_step_runtime: WebStepRuntime) -> HomePage:
    """为图片编辑器回归用例提供首页页面对象。"""
    return HomePage(page, web_step_runtime)


@pytest.fixture
def common_page(page: Page, web_step_runtime: WebStepRuntime) -> CommonPage:
    """为图片编辑器回归用例提供通用弹窗页面对象。"""
    return CommonPage(page, web_step_runtime)


@pytest.fixture
def editor_page(page: Page, web_step_runtime: WebStepRuntime) -> EditorPage:
    """为图片编辑器回归用例提供编辑器页面对象。"""
    return EditorPage(page, web_step_runtime)

