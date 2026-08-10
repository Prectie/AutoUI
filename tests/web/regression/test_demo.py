import pytest
from playwright.sync_api import expect

@pytest.mark.case_data("demo", "search_cases")
def test_search_order(order_console_page, case):
    order_console_page.goto()
    order_console_page.search_order(case["keyword"])
    expect(order_console_page.order_row(case["expected_order"])).to_be_visible()