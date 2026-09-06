"""DesignKit 首页 Page Object。"""

from playwright.sync_api import Locator, Page


class HomePage:
    """封装从 DesignKit 首页进入图片编辑器的页面能力。"""

    def __init__(self, page: Page) -> None:
        """绑定当前测试项的首页。

        参数：
            page: pytest-playwright 创建的页面；本对象不负责其生命周期。
        """
        self.page = page

    @property
    def image_editor_entry(self) -> Locator:
        """返回首页的“图片编辑”入口。"""
        return self.page.get_by_text("图片编辑 ✨", exact=True)

    def goto(self) -> None:
        """使用 pytest-playwright 注入的 ``base_url`` 打开首页。"""
        self.page.goto("/")

    def open_image_editor(self) -> Page:
        """打开图片编辑器并返回新建的浏览器页面。

        返回：
            图片编辑入口创建的新 ``Page``。

        异常：
            点击未创建新 Tab 时，Playwright 抛出等待 popup 超时异常。
        """
        # 必须在点击前监听 popup，避免新 Tab 创建过快而丢失事件。
        with self.page.expect_popup() as popup_info:
            self.image_editor_entry.click()

        return popup_info.value
