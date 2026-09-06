"""pytest、pytest-playwright 与 Allure results 的测试项级集成。"""

from __future__ import annotations

import platform
from pathlib import Path
import warnings

import allure
import pytest

from autoui.core.config.settings import Settings


_OUTPUT_PATH = pytest.StashKey[Path]()
_REPORTS = pytest.StashKey[dict[str, pytest.TestReport]]()


def _is_web_test(item: pytest.Item) -> bool:
    """判断测试项是否通过 pytest-playwright 请求浏览器能力。"""
    return bool({"page", "context", "browser"}.intersection(item.fixturenames))


@pytest.fixture(autouse=True)
def allure_web_test_context(request: pytest.FixtureRequest) -> None:
    """为 Web 测试写入运行 labels 并记录其独立产物目录。

    依赖通过 ``request`` 按需获取，避免让普通单元测试隐式依赖浏览器
    fixture。业务分类 labels 仍由具体产品测试套件声明。
    """
    if not _is_web_test(request.node):
        return

    settings: Settings = request.getfixturevalue("settings")
    browser_name: str = request.getfixturevalue("browser_name")
    output_path: str = request.getfixturevalue("output_path")

    request.node.stash[_OUTPUT_PATH] = Path(output_path)
    request.node.stash[_REPORTS] = {}

    allure.dynamic.label("testTarget", "desktop-web")
    allure.dynamic.label("site", settings.site)
    allure.dynamic.label("deployment", settings.deployment)
    allure.dynamic.label("browser", browser_name)
    allure.dynamic.label("os", platform.system())


def _failure_artifacts(
    output_dir: Path,
) -> list[tuple[Path, str, object, str | None]]:
    """返回当前测试项中 Allure 应展示的失败诊断产物。"""
    artifacts: list[tuple[Path, str, object, str | None]] = []

    artifacts.extend(
        (
            path,
            f"Playwright Trace：{path.name}",
            "application/vnd.allure.playwright-trace",
            "zip",
        )
        for path in sorted(output_dir.rglob("trace*.zip"))
    )
    artifacts.extend(
        (
            path,
            f"失败截图：{path.name}",
            allure.attachment_type.PNG,
            None,
        )
        for path in sorted(output_dir.rglob("test-failed-*.png"))
    )
    artifacts.extend(
        (
            path,
            f"失败录屏：{path.name}",
            "video/webm",
            "webm",
        )
        for path in sorted(output_dir.rglob("*.webm"))
    )
    return artifacts


def _attach_failure_artifacts(item: pytest.Item) -> None:
    """将失败 Web 测试的原生产物附加到当前 Allure 测试项。

    附件失败会产生明确的 pytest warning，但不会覆盖原始 Test Outcome。
    """
    output_dir = item.stash.get(_OUTPUT_PATH, None)
    reports = item.stash.get(_REPORTS, None)
    if output_dir is None or reports is None:
        return
    if not any(report.failed for report in reports.values()):
        return

    for path, name, attachment_type, extension in _failure_artifacts(output_dir):
        try:
            allure.attach.file(
                str(path),
                name=name,
                attachment_type=attachment_type,
                extension=extension,
            )
        except Exception as error:  # 报告故障不能改写原始测试结果。
            warnings.warn(
                f"无法将测试产物附加到 Allure：{path}：{error}",
                pytest.PytestWarning,
                stacklevel=2,
            )


@pytest.hookimpl(wrapper=True, tryfirst=True)
def pytest_runtest_makereport(
    item: pytest.Item,
    call: pytest.CallInfo[object],
):
    """记录 pytest 原始阶段结果，并在 teardown 后附加失败产物。"""
    report = yield

    reports = item.stash.get(_REPORTS, None)
    if reports is not None:
        reports[report.when] = report

    # pytest-playwright 在 fixture teardown 中归档 Trace 和截图；此时 Allure
    # 测试生命周期仍打开，可以把文件关联到同一个测试项。
    if report.when == "teardown":
        _attach_failure_artifacts(item)

    return report
