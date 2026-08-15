"""
AutoUI pytest 配置插件。

本模块负责：

1. 注册 --env 和 --site 命令行参数；
2. 在 pytest 测试会话开始时解析环境配置；
3. 通过 settings fixture 向测试用例提供统一的 Settings 对象。

它是 pytest 命令行配置和 AutoUI 项目运行时配置之间的连接层。
"""

import pytest

from autoui.core.config.settings import resolve_settings

def pytest_addoption(parser):
    """
    向 pytest 命令行注册 AutoUI 自定义参数。

    注册的参数包括：

    --env：
        选择运行环境，例如 dev、beta 等。

    --site：
        选择目标站点，例如 cn、com、zawa 等。

    参数值不会在这里直接解析，而是在 pytest_sessionstart() 中统一交给 resolve_settings() 处理。
    """
    # 创建名为 autoui 的 pytest 参数分组，使帮助信息中的自定义参数更容易区分。
    group = parser.getgroup("autoui", "AutoUI 运行配置")

    # 注册 --env 命令行参数
    group.addoption(
        "--env",
        action="store",
        dest="autoui_env",
        default=None,
        help="选择 AutoUI 环境 profile"
    )

    # 注册 --site 命令行参数
    group.addoption(
        "--site",
        action="store",
        dest="autoui_site",
        default=None,
        help="选择 AutoUI 站点（cn、com、zawa） "
    )

def pytest_sessionstart(session):
    """
    在 pytest 测试会话开始时解析并保存全局配置。

    配置来源包括：
        1. 命令行传入的 --site；
        2. 命令行传入的 --env；
        3. pytest-playwright 提供的 --base-url；
        4. 配置文件中的默认 site 和 environment；
        5. 对应站点和环境的目标配置。

    解析后的 Settings 对象会挂载到 pytest 配置对象上，后续可以通过 settings fixture 获取
    """
    # session.config 是当前 pytest 测试会话的配置对象
    config = session.config

    # 读取命令行参数，并交给统一的配置解析函数处理
    settings = resolve_settings(
        cli_site=config.getoption("autoui_site"),
        cli_env=config.getoption("autoui_env"),
        cli_base_url=config.getoption("base_url"),
    )

    # 将解析结果保存到 pytest 配置对象上
    config.autoui_settings = settings

@pytest.fixture(scope="session")
def settings(request):
    """
    提供整个 pytest 测试会话共享的 Settings 配置对象。

    参数：
        request: pytest 内置 fixture，用于访问当前测试会话的配置对象。

    返回：
        pytest_sessionstart() 中解析好的 Settings 实例。

    由于 scope 设置为 session，同一次测试运行期间只会创建并复用同一个配置对象。
    """
    # 从 pytest 配置对象中读取测试会话开始时保存的 Settings
    return request.config.autoui_settings
