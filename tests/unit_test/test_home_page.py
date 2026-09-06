"""HomePage 页面切换契约测试。"""

from unittest.mock import MagicMock

from tests.web.designkit.pages.home_page import HomePage


def test_open_image_editor_returns_popup_page() -> None:
    """点击图片编辑入口后，页面对象应返回新打开的 Tab。

    该测试不启动真实浏览器，只验证 HomePage 与 Playwright popup 事件的
    调用契约，防止后续迁移再次遗漏源用例的 ``switchToPage("editor")``。
    """
    home_browser_page = MagicMock(name="home_page")
    editor_browser_page = MagicMock(name="editor_page")
    popup_info = MagicMock(name="popup_info")
    popup_info.value = editor_browser_page

    # 模拟 expect_popup() 的上下文管理器：进入后返回新 Tab 信息，
    # 退出时不吞掉异常，与 Playwright 同步 API 的语义保持一致。
    popup_scope = MagicMock(name="popup_scope")
    popup_scope.__enter__.return_value = popup_info
    popup_scope.__exit__.return_value = False
    home_browser_page.expect_popup.return_value = popup_scope

    page_object = HomePage(home_browser_page)
    returned_page = page_object.open_image_editor()

    home_browser_page.expect_popup.assert_called_once_with()
    home_browser_page.get_by_text.assert_called_once_with(
        "图片编辑 ✨",
        exact=True,
    )
    home_browser_page.get_by_text.return_value.click.assert_called_once_with()
    assert returned_page is editor_browser_page
