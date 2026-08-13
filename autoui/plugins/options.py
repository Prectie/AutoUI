import os

import pytest

from autoui.core.config.settings import resolve_settings

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
    config = session.config

    settings = resolve_settings(
        cli_site=config.getoption("autoui_site"),
        cli_env=config.getoption("autoui_env"),
        cli_base_url=config.getoption("base_url"),
        env_vars=os.environ
    )

    config.autoui_settings = settings

@pytest.fixture(scope="session")
def settings(request):
    return request.config.autoui_settings
