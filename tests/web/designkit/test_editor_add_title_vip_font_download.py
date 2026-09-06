"""DesignKit 图片编辑器会员 VIP 字体下载回归用例。"""

from pathlib import Path

import allure
import pytest

from tests.resources.paths import EDITOR_STANDARD_IMAGE
from tests.web.designkit.flows import ImageEditorFlow


@allure.parent_suite("Desktop Web")
@allure.suite("DesignKit")
@allure.label("product", "DesignKit")
@allure.feature("图片编辑")
@allure.story("会员应用 VIP 字体并下载")
@pytest.mark.regression
@pytest.mark.requires_login
def test_editor_add_title_vip_font_download(
    image_editor_flow: ImageEditorFlow,
    output_path: str,
) -> None:
    """验证会员应用 VIP 字体后可以下载非空图片编辑结果。"""
    image_editor_flow.open_editor()
    image_editor_flow.upload_standard_image(EDITOR_STANDARD_IMAGE)
    selected_font = image_editor_flow.add_title_with_vip_font()
    downloaded_file = image_editor_flow.download_result(Path(output_path))

    assert selected_font, "未获得已选择的 VIP 字体名称"
    assert downloaded_file.is_file(), f"下载文件不存在：{downloaded_file}"
    assert downloaded_file.stat().st_size > 0, f"下载文件为空：{downloaded_file}"
