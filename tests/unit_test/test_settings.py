"""AutoUI 配置解析的公开 Interface 测试。"""

from dataclasses import FrozenInstanceError

import pytest

from autoui.core.config.settings import resolve_settings


def test_cli_target_is_preserved_in_settings() -> None:
    """CLI 选择的站点和部署环境应进入不可变 Settings。"""
    settings = resolve_settings(cli_site="com", cli_env="beta")

    assert settings.site == "com"
    assert settings.deployment == "beta"
    assert settings.base_url == "https://beta.designkit.com/"


def test_cli_base_url_has_highest_priority() -> None:
    """显式 base URL 应覆盖目标配置，同时保留环境身份。"""
    settings = resolve_settings(
        cli_site="cn",
        cli_env="pre",
        cli_base_url="https://example.test/",
    )

    assert settings.site == "cn"
    assert settings.deployment == "pre"
    assert settings.base_url == "https://example.test/"


def test_unknown_target_fails_before_browser_start() -> None:
    """未知站点或环境必须在创建浏览器前给出明确错误。"""
    with pytest.raises(ValueError, match="未知站点或环境"):
        resolve_settings(cli_site="unknown", cli_env="beta")


def test_settings_are_immutable() -> None:
    """同一次运行中的配置不能被测试代码意外修改。"""
    settings = resolve_settings()

    with pytest.raises(FrozenInstanceError):
        settings.site = "com"  # type: ignore[misc]
