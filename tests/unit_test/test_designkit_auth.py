"""DesignKit 登录态配置 Interface 测试。"""

from pathlib import Path

import pytest

from autoui.core.config.settings import Settings, Viewport
from tests.web.designkit.auth import (
    STORAGE_STATE_ENV,
    resolve_designkit_storage_state,
)


def _settings(*, site: str = "cn", deployment: str = "release") -> Settings:
    """构造登录态路径解析需要的最小不可变 Settings。"""
    return Settings(
        site=site,
        deployment=deployment,
        base_url="https://www.designkit.cn/",
        viewport=Viewport(width=1920, height=1080),
        locale="zh-CN",
        timezone_id="Asia/Shanghai",
    )


def test_storage_state_defaults_to_current_target(tmp_path: Path) -> None:
    """未显式配置时应使用 site 与 deployment 组成默认文件名。"""
    expected = tmp_path / ".auth" / "designkit-com-beta.json"
    expected.parent.mkdir()
    expected.write_text("{}", encoding="utf-8")

    actual = resolve_designkit_storage_state(
        _settings(site="com", deployment="beta"),
        project_root=tmp_path,
        environment={},
    )

    assert actual == expected.resolve()


def test_storage_state_environment_override_accepts_relative_path(
    tmp_path: Path,
) -> None:
    """环境变量相对路径应以项目根目录为基准。"""
    expected = tmp_path / "local-auth" / "member.json"
    expected.parent.mkdir()
    expected.write_text("{}", encoding="utf-8")

    actual = resolve_designkit_storage_state(
        _settings(),
        project_root=tmp_path,
        environment={STORAGE_STATE_ENV: "local-auth/member.json"},
    )

    assert actual == expected.resolve()


def test_missing_storage_state_stops_before_context_creation(
    tmp_path: Path,
) -> None:
    """登录态缺失时应返回明确配置错误，而不是运行到下载阶段。"""
    with pytest.raises(pytest.UsageError, match="DesignKit 登录态不存在"):
        resolve_designkit_storage_state(
            _settings(),
            project_root=tmp_path,
            environment={},
        )
