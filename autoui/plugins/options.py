def pytest_addoption(parser):
    group = parser.getgroup("autoui")

    group.addoption(
        "--env",
        action="store",
        dest="autoui_env",
        default=None,
        help="选择 AutoUI 环境 profile"
    )

    group.addoption(
        "--site",
        action="store",
        dest="autoui_site",
        default=None,
        help="选择 AutoUI 站点（cn、com、zawa） "
    )

def pytest_sessionstart(session):
    pass