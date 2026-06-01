from playwright.sync_api import Page, Locator, expect


class OrderConsolePage:
    def __init__(self, page: Page):
        self.page = page

    @property
    def order_no_input(self) -> Locator:
        return self.page.get_by_label("订单号")

    @property
    def query_button(self) -> Locator:
        return self.page.get_by_role("button", name="查询")

    def order_row(self, order_no: str) -> Locator:
        return self.page.get_by_role("row").filter(has_text=order_no)

    def goto(self) -> None:
        self.page.goto("/")

    def search_order(self, order_no: str) -> None:
        self.order_no_input.fill(order_no)
        self.query_button.click()

    def expect_order_visible(self, order_no: str) -> None:
        expect(self.order_row(order_no)).to_be_visible()