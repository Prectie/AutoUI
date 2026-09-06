"""DesignKit 测试套件 fixture。"""

from pathlib import Path

import pytest
from playwright.sync_api import Page

from autoui.core.config.settings import Settings
from tests.web.designkit.auth import resolve_designkit_storage_state
from tests.web.designkit.flows import ImageEditorFlow
from tests.web.designkit.pages import HomePage


_PROJECT_ROOT = Path(__file__).resolve().parents[3]


@pytest.fixture(scope="session")
def designkit_storage_state(settings: Settings) -> Path:
    """提供当前 DesignKit 目标对应的有效登录态文件。"""
    return resolve_designkit_storage_state(
        settings,
        project_root=_PROJECT_ROOT,
    )


@pytest.fixture(scope="session")
def browser_context_args(
    browser_context_args: dict[str, object],
    designkit_storage_state: Path,
) -> dict[str, object]:
    """在 AutoUI Web Context 配置之上注入 DesignKit 登录态。

    pytest 会先解析上层同名 fixture。本 fixture 只增加产品专属的
    ``storage_state``，BrowserContext 和 Page 生命周期仍由
    pytest-playwright 管理。
    """
    return {
        **browser_context_args,
        "storage_state": str(designkit_storage_state),
    }


@pytest.fixture
def image_editor_flow(page: Page) -> ImageEditorFlow:
    """为当前测试项提供绑定独立 ``Page`` 的图片编辑业务流程。"""
    return ImageEditorFlow(HomePage(page))
