"""DesignKit 图片编辑器 Page Object。"""

from __future__ import annotations

import random
from pathlib import Path

from playwright.sync_api import Locator, Page, expect


class EditorPage:
    """封装上传图片、编辑标题、选择字体和下载的页面能力。"""

    def __init__(self, page: Page) -> None:
        """绑定当前测试项打开的图片编辑器页面。

        参数：
            page: ``HomePage.open_image_editor`` 返回的新页面。
        """
        self.page = page

    @property
    def promotion_close_button(self) -> Locator:
        """返回可能出现的宣传弹窗关闭按钮。"""
        return self.page.locator(".xdesign-promotion-modal__close")

    @property
    def open_image_button(self) -> Locator:
        """返回图片选择区域中的“打开图片”按钮。"""
        return self.page.locator("#selectImage").get_by_role(
            "button",
            name="打开图片",
            exact=True,
        )

    @property
    def loading_text(self) -> Locator:
        """返回编辑器画布上传过程中的“加载中”提示。"""
        # 页面还会为其他区域渲染同名加载节点；限定到编辑器容器，避免
        # Playwright strict mode 因匹配多个元素而拒绝执行等待。
        return self.page.locator("#editor-container").get_by_text(
            "加载中",
            exact=True,
        )

    @property
    def acknowledgement_button(self) -> Locator:
        """返回可能出现的“我知道了”提示按钮。"""
        return self.page.get_by_text("我知道了", exact=True)

    @property
    def add_menu_button(self) -> Locator:
        """返回左侧“添加”菜单按钮。"""
        return self.page.get_by_text("添加", exact=True)

    @property
    def local_upload_item(self) -> Locator:
        """返回“本地上传”菜单项。"""
        return self.page.get_by_text("本地上传", exact=True)

    @property
    def title_item(self) -> Locator:
        """返回添加菜单中的“标题”菜单项。"""
        return self.page.get_by_text("标题", exact=True)

    @property
    def text_edit_area(self) -> Locator:
        """返回标题文本编辑区域。"""
        return self.page.locator("#j-text-edit-area")

    @property
    def font_selector(self) -> Locator:
        """返回当前文字图层的字体选择器。"""
        return self.page.locator(".text-fontFamily .ant-select-selection-item")

    @property
    def visible_font_panel(self) -> Locator:
        """返回处于展开状态的字体下拉面板。"""
        return self.page.locator(
            "//div[contains(@class,'ant-select-dropdown') "
            "and contains(@class,'text-fontFamily__dropdown') "
            "and not(contains(@class,'ant-select-dropdown-hidden'))]"
        )

    @property
    def available_vip_fonts(self) -> Locator:
        """返回未选中的 VIP 字体选项集合。"""
        return self.visible_font_panel.locator(
            ".text-fontFamily__item.ant-select-item-option"
            "[data-track-vip='1']:not(.ant-select-item-option-selected)"
        )

    @property
    def download_button(self) -> Locator:
        """返回编辑器顶部下载按钮。"""
        return self.page.locator(".download-btn")

    @property
    def visible_download_confirm_button(self) -> Locator:
        """返回展开下载菜单中的可见下载确认按钮。"""
        return self.page.locator(
            ".m-download-wrap-popover .m-download-wrap__btn"
        )

    def dismiss_promotion_if_visible(self) -> None:
        """关闭当前编辑器页面中可能出现的宣传弹窗。"""
        if self.promotion_close_button.is_visible():
            self.promotion_close_button.click()

    def upload_image(self, image_path: Path) -> None:
        """上传指定图片并等待编辑态就绪。

        参数：
            image_path: 必须存在的本地图片文件。

        异常：
            FileNotFoundError: 图片文件不存在。
            Playwright 异常: 文件选择或页面等待失败。
        """
        if not image_path.is_file():
            raise FileNotFoundError(f"测试素材不存在：{image_path}")

        with self.page.expect_file_chooser() as file_chooser_info:
            self.open_image_button.click()
        file_chooser_info.value.set_files(str(image_path))

        expect(self.loading_text).to_be_hidden(timeout=60_000)
        if self.acknowledgement_button.is_visible():
            self.acknowledgement_button.click()

    def open_add_menu(self) -> None:
        """展开左侧添加菜单并确认菜单内容可见。"""
        self.add_menu_button.click()
        expect(self.local_upload_item).to_be_visible()

    def add_title(self) -> None:
        """添加标题文字图层并确认编辑区域出现。"""
        self.title_item.click()
        expect(self.text_edit_area).to_be_visible()

    def open_font_selector(self) -> None:
        """打开字体选择器并确认下拉面板可见。"""
        self.font_selector.click()
        expect(self.visible_font_panel).to_be_visible()

    def choose_random_vip_font(self) -> str:
        """选择前十二个候选项中的一个 VIP 字体并返回字体名称。

        异常：
            AssertionError: 没有候选字体，或点击后字体名称没有变化。
        """
        before_font_name = self.font_selector.inner_text().strip()
        option_count = self.available_vip_fonts.count()
        if option_count == 0:
            raise AssertionError("没有找到可选择的 VIP 字体")

        option_index = random.randrange(min(option_count, 12))
        self.available_vip_fonts.nth(option_index).click()

        after_font_name = self.font_selector.inner_text().strip()
        if not after_font_name or after_font_name == before_font_name:
            raise AssertionError("VIP 字体点击后未切换成功")
        return after_font_name

    def download_to(self, output_dir: Path) -> Path:
        """下载编辑结果到当前测试项目录并返回最终文件路径。

        参数：
            output_dir: pytest-playwright 为当前测试项提供的产物目录。

        返回：
            保存后的下载文件路径。
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        self.download_button.click()
        expect(self.visible_download_confirm_button).to_be_visible()

        with self.page.expect_download(timeout=120_000) as download_info:
            self.visible_download_confirm_button.click()

        download = download_info.value
        downloaded_path = output_dir / Path(download.suggested_filename).name
        download.save_as(str(downloaded_path))
        return downloaded_path
