import pytest

from autoui.core.config import settings
from autoui.platforms.web.pages.order_console_page import OrderConsolePage


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
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


@pytest.fixture
def order_console_page(page):
    return OrderConsolePage(page)