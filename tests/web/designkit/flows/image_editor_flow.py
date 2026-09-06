"""DesignKit 图片编辑业务流程。"""

from pathlib import Path

import allure

from tests.web.designkit.pages import EditorPage, HomePage


class ImageEditorFlow:
    """以业务操作组织首页与图片编辑器页面能力。"""

    def __init__(self, home_page: HomePage) -> None:
        """创建从 DesignKit 首页开始的图片编辑流程。

        参数：
            home_page: 绑定当前 pytest 测试页面的首页对象。
        """
        self._home_page = home_page
        self._editor_page: EditorPage | None = None

    def _current_editor(self) -> EditorPage:
        """返回已打开的编辑器，否则暴露业务调用顺序错误。"""
        if self._editor_page is None:
            raise RuntimeError("必须先调用 open_editor() 打开图片编辑器")
        return self._editor_page

    @allure.step("进入图片编辑器")
    def open_editor(self) -> None:
        """打开 DesignKit 首页及图片编辑器，并处理可选宣传弹窗。"""
        self._home_page.goto()
        self._editor_page = EditorPage(self._home_page.open_image_editor())
        self._editor_page.dismiss_promotion_if_visible()

    @allure.step("上传标准图片：{image_path}")
    def upload_standard_image(self, image_path: Path) -> None:
        """上传测试场景指定的标准图片。"""
        self._current_editor().upload_image(image_path)

    @allure.step("添加标题并应用 VIP 字体：{font_name}")
    def add_title_with_vip_font(self, font_name: str) -> str:
        """添加标题、打开字体面板并应用指定 VIP 字体。

        参数：
            font_name: DesignKit 字体面板中的精确字体名称，由测试场景提供。

        返回：
            页面最终显示的已选字体名称。
        """
        editor = self._current_editor()
        editor.open_add_menu()
        editor.add_title()
        editor.open_font_selector()
        return editor.choose_vip_font(font_name)

    @allure.step("下载图片编辑结果")
    def download_result(self, output_dir: Path) -> Path:
        """下载当前图片编辑结果到测试项产物目录。"""
        return self._current_editor().download_to(output_dir)
