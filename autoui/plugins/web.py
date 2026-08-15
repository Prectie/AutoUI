"""
Web UI 测试插件。

本模块负责将 AutoUI 的 Settings 配置应用到
pytest-playwright 的浏览器上下文中，并提供 Web UI 测试所需的页面对象 fixture。

主要功能包括：

1. 设置浏览器的 base_url、viewport、locale 和 timezone；
2. 忽略测试环境中的 HTTPS 证书错误；
3. 创建并返回 OrderConsolePage 页面对象。
"""

import pytest

from autoui.platforms.web.pages.order_console_page import OrderConsolePage

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
def order_console_page(page):
    return OrderConsolePage(page)

