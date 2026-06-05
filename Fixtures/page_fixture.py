import pytest
from Pages.order_console_page import OrderConsolePage


@pytest.fixture
def order_console_page(page):
    return OrderConsolePage(page)