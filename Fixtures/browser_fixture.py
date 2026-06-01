import pytest

from Config.settings import (
    BASE_URL,
    DEFAULT_VIEWPORT,
    DEFAULT_LOCALE,
    DEFAULT_TIMEZONE,
)
from Pages.order_console_page import OrderConsolePage


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "base_url": BASE_URL,
        "viewport": DEFAULT_VIEWPORT,
        "locale": DEFAULT_LOCALE,
        "timezone_id": DEFAULT_TIMEZONE,
        "ignore_https_errors": True,
    }

@pytest.fixture
def order_console_page(page):
    return OrderConsolePage(page)
