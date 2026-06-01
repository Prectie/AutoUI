import pytest

from Core.data_loader import load_yaml


order_data = load_yaml("Data/demo.yaml")


@pytest.mark.parametrize("case", order_data["search_cases"], ids=lambda case: case["name"])
def test_search_order(order_console_page, case):
    order_console_page.goto()
    order_console_page.search_order(case["keyword"])
    order_console_page.expect_order_visible(case["expected_order"])