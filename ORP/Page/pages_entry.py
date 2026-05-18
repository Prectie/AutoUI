from . import *
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
    ModuleLibraryPage: ModuleLibraryPage  # 模型库页面
    ConfigBusinessAndPublishAppPage: ConfigBusinessAndPublishAppPage  # 配置业务/发布应用页面
    APPPortalBasePage: APPPortalBasePage  # 应用门户页面
    AdminConsolePage: AdminConsolePage  # 后台管理页面

    # ================= 应用门户 =================
    ArmamentSearchPage: ArmamentSearchPage
    UnknownAirSituationPage: UnknownAirSituationPage  # 不明空情页面

    _map = {
        'DemoPage': DemoPage,

        'BasePage': BasePage,
        'LoginPage': LoginPage,
        'ModuleRunPage': ModuleRunPage,
        'MonitorPage': MonitorPage,

        'ModuleLibraryPage': ModuleLibraryPage,
        'ConfigBusinessAndPublishAppPage': ConfigBusinessAndPublishAppPage,
        'APPPortalBasePage': APPPortalBasePage,
        'AdminConsolePage': AdminConsolePage,

        'ArmamentSearchPage': ArmamentSearchPage,
        'UnknownAirSituationPage': UnknownAirSituationPage

    }

    def __init__(self, driver, download_dir: str = None, env_url: str = None):
        self.driver = driver
        self._download_dir = download_dir
        self._cache = {}
        self._env_url = env_url

        # 本次运行环境相关的 url

    def __getattr__(self, name: str):
        # 懒加载, 用到对应页面才返回对应页面的实例
        if name in self._map:
            if name in self._cache:
                return self._cache[name]
            page = self._map[name](self.driver, env_url=self._env_url)
            # 注入 download_dir
            if hasattr(page, 'download_dir') and self._download_dir is not None:
                page.download_dir = self._download_dir
            self._cache[name] = page
            return page
        raise AttributeError(f"没有找到对应的页面: {name}")

    def __dir__(self):
        # 让 IDE 在补全时把 _map keys 也列出来
        return super().__dir__() + list(self._map.keys())
