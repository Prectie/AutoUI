"""ImageEditorFlow 公开 Interface 测试。"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from tests.web.designkit.flows.image_editor_flow import ImageEditorFlow


def test_image_editor_flow_orchestrates_page_capabilities() -> None:
    """Flow 应隐藏跨页面编排，并只返回测试断言需要的结果。"""
    home_page = MagicMock(name="home_page")
    browser_page = MagicMock(name="browser_page")
    home_page.open_image_editor.return_value = browser_page

    editor_page = MagicMock(name="editor_page")
    editor_page.choose_vip_font.return_value = "VIP Font"
    downloaded_file = Path("artifacts/result.png")
    editor_page.download_to.return_value = downloaded_file

    with patch(
        "tests.web.designkit.flows.image_editor_flow.EditorPage",
        return_value=editor_page,
    ) as editor_page_type:
        flow = ImageEditorFlow(home_page)
        flow.open_editor()
        flow.upload_standard_image(Path("standard.jpg"))
        selected_font = flow.add_title_with_vip_font("VIP Font")
        result = flow.download_result(Path("artifacts"))

    home_page.goto.assert_called_once_with()
    home_page.open_image_editor.assert_called_once_with()
    editor_page_type.assert_called_once_with(browser_page)
    editor_page.dismiss_promotion_if_visible.assert_called_once_with()
    editor_page.upload_image.assert_called_once_with(Path("standard.jpg"))
    editor_page.open_add_menu.assert_called_once_with()
    editor_page.add_title.assert_called_once_with()
    editor_page.open_font_selector.assert_called_once_with()
    editor_page.choose_vip_font.assert_called_once_with("VIP Font")
    editor_page.download_to.assert_called_once_with(Path("artifacts"))
    assert selected_font == "VIP Font"
    assert result == downloaded_file


def test_image_editor_flow_requires_open_editor_first() -> None:
    """错误的业务调用顺序应在进入 Page Object 前清晰失败。"""
    flow = ImageEditorFlow(MagicMock(name="home_page"))

    with pytest.raises(RuntimeError, match=r"open_editor\(\)"):
        flow.upload_standard_image(Path("standard.jpg"))
