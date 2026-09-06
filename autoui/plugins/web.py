"""AutoUI 桌面 Web 与 pytest-playwright 的配置集成。"""

import pytest

from autoui.core.config.settings import Settings


@pytest.fixture(scope="session")
def browser_context_args(
    browser_context_args: dict[str, object],
    settings: Settings,
) -> dict[str, object]:
    """将不可变 AutoUI Settings 转换为 BrowserContext 参数。

    参数：
        browser_context_args: pytest-playwright 提供的默认上下文参数。
        settings: CLI 与 YAML 合并后得到的 session 配置。

    返回：
        保留原有配置，并由 AutoUI 覆盖目标地址、视口、语言和时区的字典。
    """
    return {
        **browser_context_args,
        "base_url": settings.base_url,
        "viewport": {
            "width": settings.viewport.width,
            "height": settings.viewport.height,
        },
        "locale": settings.locale,
        "timezone_id": settings.timezone_id,
        "ignore_https_errors": True,
    }
