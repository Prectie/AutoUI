"""DesignKit Playwright 登录态解析。"""

from __future__ import annotations

from collections.abc import Mapping
import os
from pathlib import Path

import pytest

from autoui.core.config.settings import Settings


STORAGE_STATE_ENV = "DESIGNKIT_STORAGE_STATE"


def resolve_designkit_storage_state(
    settings: Settings,
    *,
    project_root: Path,
    environment: Mapping[str, str] | None = None,
) -> Path:
    """解析并校验当前 DesignKit 目标使用的登录态文件。

    配置优先级：
        1. ``DESIGNKIT_STORAGE_STATE`` 环境变量；
        2. ``.auth/designkit-{site}-{deployment}.json`` 默认路径。

    参数：
        settings: 当前测试会话的站点和部署环境配置。
        project_root: AutoUI 项目根目录，用于解析默认路径和相对路径。
        environment: 环境变量映射；默认读取当前进程环境。测试可传入替代映射。

    返回：
        已存在的 Playwright storage state 文件绝对路径。

    异常：
        pytest.UsageError: 登录态文件不存在，测试不应继续创建 BrowserContext。
    """
    environment = os.environ if environment is None else environment
    configured_path = environment.get(STORAGE_STATE_ENV)

    storage_state = (
        Path(configured_path).expanduser()
        if configured_path
        else project_root
        / ".auth"
        / f"designkit-{settings.site}-{settings.deployment}.json"
    )
    if not storage_state.is_absolute():
        storage_state = project_root / storage_state

    storage_state = storage_state.resolve()
    if not storage_state.is_file():
        raise pytest.UsageError(
            "DesignKit 登录态不存在："
            f"{storage_state}。请先生成登录态，或设置 {STORAGE_STATE_ENV}。"
        )

    return storage_state
