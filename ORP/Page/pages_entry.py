from Page.CommonPage.login_page import LoginPage
from Page.CommonPage.module_run_page import ModuleRunPage
from Page.CommonPage.monitor_page import MonitorPage
from Page.TopMenuPage.module_library_page import ModuleLibraryPage
from Page.ApplicationPortalPage.app_portal_base_page import APPPortalBasePage
from Page.ApplicationPortalPage.armament_search_page import ArmamentSearchPage
from Page.base_page import BasePage
from Page.demo_page import DemoPage


class PageEntry:
    # 显式声明所有 page 属性, 增强IDE编写提示
    DemoPage: DemoPage
    BasePage: BasePage  # 所有页面的父类(抽象类)

    # ================= 通用页面 =================
    LoginPage: LoginPage
    ModuleRunPage: ModuleRunPage
    MonitorPage: MonitorPage

    # 顶层菜单页面
    ModuleLibraryPage: ModuleLibraryPage

    # ================= 应用门户 =================
    APPPortalBasePage: APPPortalBasePage
    ArmamentSearchPage: ArmamentSearchPage

    _map = {
        'DemoPage': DemoPage,

        'BasePage': BasePage,
        'LoginPage': LoginPage,
        'ModuleRunPage': ModuleRunPage,
        'MonitorPage': MonitorPage,

        'ModuleLibraryPage': ModuleLibraryPage,

        'APPPortalBasePage': APPPortalBasePage,
        'ArmamentSearchPage': ArmamentSearchPage,

    }

    def __init__(self, driver, download_dir: str = None):
        self.driver = driver
        self._download_dir = download_dir
        self._cache = {}

        # 本次运行环境相关的 url

    def __getattr__(self, name: str):
        # 懒加载, 用到对应页面才返回对应页面的实例
        if name in self._map:
            if name in self._cache:
                return self._cache[name]
            page = self._map[name](self.driver)
            # 注入 download_dir
            if hasattr(page, 'download_dir') and self._download_dir is not None:
                page.download_dir = self._download_dir
            self._cache[name] = page
            return page
        raise AttributeError(f"没有找到对应的页面: {name}")

    def __dir__(self):
        # 让 IDE 在补全时把 _map keys 也列出来
        return super().__dir__() + list(self._map.keys())
