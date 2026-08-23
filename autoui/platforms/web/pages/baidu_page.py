"""百度搜索页面对象。"""

import re

from playwright.sync_api import Locator, Page, expect


class BaiduPage:
    """封装百度首页搜索流程。

    这是一个框架 smoke 示例，使用百度作为稳定、无需登录的外部页面，
    用来验证 Page.goto、Locator.fill、Locator.click 和结果断言的最小闭环。
    """

    BASE_URL = "https://www.baidu.com/"

    def __init__(self, page: Page) -> None:
        self.page = page

    @property
    def search_input(self) -> Locator:
        """百度首页搜索输入框。

        元素信息来自实际页面探索：ARIA role 为 textbox。
        """
        return self.page.get_by_role("textbox")

    @property
    def search_button(self) -> Locator:
        """百度一下按钮。"""
        return self.page.get_by_role("button", name="百度一下")

    @property
    def result_headings(self) -> Locator:
        """搜索结果标题集合。

        元素信息来自实际结果页探索：搜索结果标题暴露为 level=3 heading。
        """
        return self.page.get_by_role("heading", level=3)

    def open(self) -> None:
        """打开百度首页。"""
        self.page.goto(self.BASE_URL)

    def search(self, keyword: str) -> None:
        """输入关键词并提交搜索。

        参数：
            keyword:
                要搜索的非空文本。关键词会被记录到 Locator.fill 的技术日志中，
                便于回放本次测试实际输入了什么。
        """
        if not keyword.strip():
            raise ValueError("搜索关键词不能为空")

        self.search_input.fill(keyword)
        with self.page.expect_navigation(wait_until="domcontentloaded"):
            self.search_button.click()

    def assert_results_contain(self, keyword: str) -> None:
        """断言至少有一个搜索结果标题包含关键词。"""
        matching_results = self.result_headings.filter(
            has_text=re.compile(re.escape(keyword), re.IGNORECASE)
        )
        expect(matching_results.first).to_be_visible(timeout=15000)
