"""百度搜索 smoke 测试。"""

from playwright.sync_api import Page


def test_baidu_search(page: Page, baidu_page) -> None:
    """验证打开百度、输入关键词、点击搜索和结果断言。"""
    keyword = "Playwright"

    baidu_page.open()
    baidu_page.search(keyword)
    baidu_page.assert_results_contain(keyword)
