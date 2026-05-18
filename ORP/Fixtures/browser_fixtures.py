# -*- coding:utf-8 -*-
import os
import pytest

from Page.pages_entry import PageEntry

from Utils.driver_utils import open_browser


def pytest_addoption(parser):
    # 控制使用哪个浏览器进行自动化, 现在仅支持 chrome
    parser.addoption(
        "--mybrowser",
        action='store',
        default='chrome',
        help="Browser to run tests against: chrome, firefox"
    )

    # 配置 url
    parser.addoption(
        "--env",
        action="store",
        default=None,  # 不在命令行阶段设置默认值, 走配置文件
        help="选择运行环境: test / prod"
    )
    parser.addini(
        "env",
        default="test",
        help="默认运行环境名(命令/配置未传 --env 时使用), 默认 test 环境"
    )

    parser.addini(
        "env_urls",
        type="linelist",
        help="环境到 URL 的映射"
    )


def _resolve_env_name(config) -> str:
    """
      解析当前首先使用的环境名, 优先从命令行中取, 其次是配置文件
    :param config: pytest内置对象
    :return: 环境
    """
    return (config.getoption("--env") or config.getini("env")).strip()


def _parse_env_urls(config) -> dict[str, str]:
    """
      把 env_urls(list[str]) 解析为: dict: {env: url}
      env_urls的期望格式为:
      [
        "dev=http://xxx.com"
      ]
    :param config: pytest内置对象
    :return: 解析后的 dict 格式
    """
    items = config.getini("env_urls")
    mapping: dict[str, str] = {}

    for line in items:
        # 统一处理, 将 url 转为字符串以及去掉首位空格
        line = str(line).strip()

        # 空行直接跳过, 允许在配置文件中留空行
        if not line:
            continue

        # 允许注释行: 以 # 开头就忽略
        if line.startswith('#'):
            continue

        # 格式校验, 仅允许 env=url 的格式
        if "=" not in line:
            raise pytest.UsageError(
                f"env_urls 配置格式错误: 应为 env=url, 实际为:{line}"
            )

        # 把第一个 = 分开, 即 dev, http://xxx.com
        # 即使后续 url 的 query 中存在 = 也不会被切分
        k, v = line.split('=', 1)

        # 再次去掉前后空格, 避免 dev = http... 的情况
        k = k.strip()
        v = v.strip()

        # 再次校验, env 或 url 是否为空
        if not k or not v:
            raise pytest.UsageError(
                f"env_urls 配置格式错误: env 和 url 不能为空, 实际为: {line}"
            )

        # 写入字典
        # 可重复, 但后写会覆盖先写
        mapping[k] = v

    return mapping


def resolve_url(config) -> str:
    """
      根据当前环境名, 返回对应的 URL
    :param config: pytest内置对象
    :return: 环境名对应的 URL 字符串
    """
    env_name = _resolve_env_name(config)
    mapping = _parse_env_urls(config)

    if env_name not in mapping:
        available = ",".join(sorted(mapping.keys())) if mapping else "(空)"
        raise pytest.UsageError(
            f"未找到环境 '{env_name}' 的 URL, 请在配置文件中的 env_urls 中进行设置: '{env_name}=http(s)://...'"
            f"当前已配置的环境: {available}"
        )

    return mapping[env_name]


@pytest.fixture(scope="session")
def env_url(request):
    """
      提供给测试/页面对象使用的环境 URL
      session 级别: 整次只运行一次
    :param request: pytest内置对象
    :return: 环境对应的URL
    """
    return resolve_url(request.config)


@pytest.fixture(scope="module")
def download_dir(request):
    test_file = str(request.node.fspath)
    test_dir = os.path.dirname(test_file)
    d = os.path.join(test_dir, "Downloads")
    os.makedirs(d, exist_ok=True)
    return d


@pytest.fixture(scope="module")
def driver(request, download_dir):
    # 1.从命令行获取 --browser 参数
    browser_name = request.config.getoption("--mybrowser")

    # 2.获取 driver
    drv = open_browser(browser_name, download_dir=str(download_dir))
    # CDP 允许下载
    drv.execute_cdp_cmd(
        "Page.setDownloadBehavior",
        {"behavior": "allow", "downloadPath": download_dir}
    )
    drv.maximize_window()
    yield drv
    drv.quit()


# 页面入口 PageEntry
@pytest.fixture(scope="function", name="entry")
def page_entry(driver, download_dir, env_url):
    yield PageEntry(driver, download_dir, env_url)
