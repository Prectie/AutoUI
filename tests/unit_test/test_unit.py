"""
AutoUI 测试运行身份的框架契约测试。

这些测试不访问真实页面，
验证 runtime plugin 提供的 ExecutionIdentity 和测试项级结构化日志闭环。
"""
import json
import logging
from pathlib import Path
import sys
from unittest.mock import MagicMock, patch
from typing import Any

import pytest

from autoui.core.logging.json_formatter import AutoUIJsonFormatter
from autoui.platforms.web.steps import WebStepRuntime, business_step


def test_execution_identity_is_available(execution_identity):
    """
    验证 pytest 测试项能够获取完整的 ExecutionIdentity。

    该测试用于保护框架基础设施，
    不属于具体业务功能回归测试。
    """
    # 验证整次测试运行的唯一标识存在。
    assert execution_identity.testrun_uid

    # 验证当前 worker 标识存在。
    assert execution_identity.worker_id

    # 验证当前测试项 nodeid 存在。
    assert execution_identity.nodeid

    # 验证 nodeid 确实指向当前测试，而不是其他测试。
    assert "test_execution_identity_is_available" in execution_identity.nodeid

def _make_record(
    event: dict[str, Any],
    *,
    level: int = logging.INFO,
    exc_info: Any = None,
) -> logging.LogRecord:
    """构造带有 autoui_event 的 LogRecord。"""
    record = logging.LogRecord(
        name="autoui.test",
        level=level,
        pathname=__file__,
        lineno=1,
        msg=event["message"],
        args=(),
        exc_info=exc_info,
    )
    record.autoui_event = event
    return record


def test_formatter_outputs_one_json_object_per_line() -> None:
    """普通事件应输出一行可解析 JSON。"""
    event = {
        "event_type": "business_step",
        "phase": "finished",
        "message": "搜索订单：订单管理",
        "testrun_uid": "run-001",
        "worker_id": "master",
        "nodeid": "tests/web/test_order.py::test_search",
        "step_id": "step-001",
        "data": {"keyword": "订单管理"},
        "duration_ms": 12.5,
        "error_type": None,
        "error_message": None,
        "traceback": None,
    }

    line = AutoUIJsonFormatter().format(
        _make_record(event)
    )

    assert "\n" not in line

    payload = json.loads(line)

    assert payload["schema_version"] == 1
    assert payload["level"] == "INFO"
    assert payload["event_type"] == "business_step"
    assert payload["phase"] == "finished"
    assert payload["message"] == "搜索订单：订单管理"
    assert payload["data"] == {"keyword": "订单管理"}
    assert payload["duration_ms"] == 12.5


def test_formatter_escapes_multiline_traceback() -> None:
    """异常堆栈应保留在 traceback 字段，但不能破坏单行 JSON。"""
    try:
        raise RuntimeError("搜索失败")
    except RuntimeError:
        exc_info = sys.exc_info()

    event = {
        "event_type": "business_step",
        "phase": "failed",
        "message": "搜索订单：订单管理",
        "testrun_uid": "run-001",
        "worker_id": "master",
        "nodeid": "tests/web/test_order.py::test_search",
        "step_id": "step-001",
        "data": {},
        "duration_ms": 20.0,
        "error_type": "RuntimeError",
        "error_message": "搜索失败",
        "traceback": None,
    }

    line = AutoUIJsonFormatter().format(
        _make_record(
            event,
            level=logging.ERROR,
            exc_info=exc_info,
        )
    )

    assert "\n" not in line

    payload = json.loads(line)

    assert payload["level"] == "ERROR"
    assert payload["error_type"] == "RuntimeError"
    assert payload["error_message"] == "搜索失败"
    assert "RuntimeError" in payload["traceback"]


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    """
    读取 JSONL 文件并解析其中的所有事件。

    参数：
        path:
            待读取的 JSONL 文件路径。

    返回：
        文件中每一行对应的 JSON 对象列表。
        空行会被忽略。

    异常：
        FileNotFoundError:
            日志文件不存在时抛出，说明 fixture 没有正确创建输出文件。

        json.JSONDecodeError:
            某一行不是合法 JSON 时抛出，说明 formatter 输出不符合契约。
    """
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_autoui_logger_writes_jsonl_files(
    autoui_logger,
    output_path: str,
) -> None:
    """
    验证每个测试项都能写入完整事件日志和错误日志。

    测试数据流：
        autoui_logger.operation()
            → AutoUILogger.emit()
            → logging.Logger
            → 两个 FileHandler
            → AutoUIJsonFormatter
            → 两个 JSONL 文件
    """
    # 成功操作应产生 started 和 finished 两条完整事件。
    with autoui_logger.operation("成功操作"):
        pass

    # 失败操作应原样抛出异常，同时产生 failed 事件。
    # pytest.raises 只负责验证业务异常仍然存在，
    # 不承担日志基础设施职责。
    with pytest.raises(RuntimeError):
        with autoui_logger.operation("失败操作"):
            raise RuntimeError("演示错误")

    output_dir = Path(output_path)

    event_entries = _read_jsonl(
        output_dir / "autoui-events.jsonl"
    )
    error_entries = _read_jsonl(
        output_dir / "autoui-errors.jsonl"
    )

    # 当前测试项还会由 pytest hook 追加 setup、call、teardown 结果；
    # 这里先筛选 operation，保持本测试对 AutoUILogger 操作协议的聚焦。
    event_entries = [
        entry
        for entry in event_entries
        if entry["event_type"] == "operation"
    ]
    error_entries = [
        entry
        for entry in error_entries
        if entry["event_type"] == "operation"
    ]

    # 完整事件日志应包含：
    # 成功操作 started、成功操作 finished、
    # 失败操作 started、失败操作 failed。
    assert len(event_entries) == 4
    assert [entry["phase"] for entry in event_entries] == [
        "started",
        "finished",
        "started",
        "failed",
    ]

    # 同一个 operation 的不同阶段必须共享 step_id，
    # 不同 operation 必须使用不同 step_id，平台才能正确聚合步骤。
    assert event_entries[0]["step_id"] == event_entries[1]["step_id"]
    assert event_entries[2]["step_id"] == event_entries[3]["step_id"]
    assert event_entries[0]["step_id"] != event_entries[2]["step_id"]

    # 耗时是事件协议字段，不应混入业务 data。
    assert event_entries[0]["duration_ms"] is None
    assert event_entries[1]["duration_ms"] is not None
    assert event_entries[1]["data"] == {}

    # 失败信息同样位于协议顶层，方便错误日志消费者直接读取。
    assert event_entries[3]["duration_ms"] is not None
    assert event_entries[3]["error_type"] == "RuntimeError"
    assert event_entries[3]["error_message"] == "演示错误"
    assert event_entries[3]["data"] == {}

    # 错误日志只接收 ERROR 事件，因此只应有一条失败事件。
    assert len(error_entries) == 1
    assert error_entries[0]["phase"] == "failed"
    assert "RuntimeError" in error_entries[0]["traceback"]

    # 同一个失败 LogRecord 会被两个 handler 分别写入，
    # 所以两个文件中的失败事件内容应保持一致。
    assert error_entries[0] == event_entries[3]


def _make_trace_page() -> MagicMock:
    """
    创建不启动真实浏览器的 Page 测试替身。

    测试只需要验证 WebStepRuntime 是否进入和退出 tracing.group，
    不需要依赖浏览器进程或本机 Playwright 浏览器缓存。
    """
    page = MagicMock(name="page")
    trace_group = page.context.tracing.group.return_value
    trace_group.__enter__.return_value = None
    trace_group.__exit__.return_value = False
    return page


def test_web_step_runtime_records_success(
    autoui_logger,
    output_path: str,
) -> None:
    """WebStepRuntime 的 with 层应记录成功业务步骤。"""
    page = _make_trace_page()
    runtime = WebStepRuntime(
        page=page,
        autoui_logger=autoui_logger,
    )

    with patch("autoui.platforms.web.steps.allure.step") as allure_step:
        allure_context = allure_step.return_value
        allure_context.__enter__.return_value = None
        allure_context.__exit__.return_value = False

        with runtime.step(
            "百度搜索：Playwright",
            data={"keyword": "Playwright"},
        ):
            pass

    entries = _read_jsonl(
        Path(output_path) / "autoui-events.jsonl"
    )
    entries = [
        entry
        for entry in entries
        if entry["event_type"] == "business_step"
    ]

    assert [entry["phase"] for entry in entries] == [
        "started",
        "finished",
    ]
    assert entries[0]["event_type"] == "business_step"
    assert entries[0]["message"] == "百度搜索：Playwright"
    assert entries[0]["data"] == {"keyword": "Playwright"}
    assert entries[0]["step_id"] == entries[1]["step_id"]
    assert entries[1]["duration_ms"] is not None
    page.context.tracing.group.assert_called_once_with(
        "百度搜索：Playwright"
    )
    page.context.tracing.group.return_value.__enter__.assert_called_once_with()
    page.context.tracing.group.return_value.__exit__.assert_called_once_with(
        None,
        None,
        None,
    )
    allure_step.assert_called_once_with("百度搜索：Playwright")
    allure_context.__enter__.assert_called_once_with()
    allure_context.__exit__.assert_called_once_with(
        None,
        None,
        None,
    )


def test_web_step_runtime_records_failure_and_reraises(
    autoui_logger,
    output_path: str,
) -> None:
    """WebStepRuntime 应记录失败事件并保留原始异常。"""
    page = _make_trace_page()
    runtime = WebStepRuntime(
        page=page,
        autoui_logger=autoui_logger,
    )

    with patch("autoui.platforms.web.steps.allure.step") as allure_step:
        allure_context = allure_step.return_value
        allure_context.__enter__.return_value = None
        allure_context.__exit__.return_value = False

        with pytest.raises(RuntimeError, match="演示错误"):
            with runtime.step(
                "百度搜索失败",
                data={"keyword": "Playwright"},
            ):
                raise RuntimeError("演示错误")

    entries = _read_jsonl(
        Path(output_path) / "autoui-events.jsonl"
    )
    entries = [
        entry
        for entry in entries
        if entry["event_type"] == "business_step"
    ]

    assert [entry["phase"] for entry in entries] == [
        "started",
        "failed",
    ]
    assert entries[1]["error_type"] == "RuntimeError"
    assert entries[1]["error_message"] == "演示错误"
    assert entries[1]["duration_ms"] is not None
    assert "RuntimeError" in entries[1]["traceback"]
    page.context.tracing.group.assert_called_once_with("百度搜索失败")
    page.context.tracing.group.return_value.__enter__.assert_called_once_with()
    page.context.tracing.group.return_value.__exit__.assert_called_once()
    allure_step.assert_called_once_with("百度搜索失败")
    allure_context.__enter__.assert_called_once_with()
    allure_context.__exit__.assert_called_once()


def test_business_step_formats_title_and_records_arguments(
    autoui_logger,
    output_path: str,
) -> None:
    """
    验证 business_step 能绑定参数、格式化标题并委托 runtime。

    测试用的 DemoPage 模拟真实 Page Object，
    只注入 WebStepRuntime，不直接创建日志对象或 handler。
    """

    class DemoPage:
        def __init__(self, runtime: WebStepRuntime) -> None:
            self._web_step_runtime = runtime

        @business_step("演示搜索：{keyword}")
        def search(self, keyword: str) -> str:
            """返回原始方法结果，验证装饰器不会改变返回值。"""
            return keyword.upper()

    result = DemoPage(
        WebStepRuntime(
            page=_make_trace_page(),
            autoui_logger=autoui_logger,
        )
    ).search("Playwright")

    assert result == "PLAYWRIGHT"

    entries = _read_jsonl(
        Path(output_path) / "autoui-events.jsonl"
    )
    entries = [
        entry
        for entry in entries
        if entry["event_type"] == "business_step"
    ]

    assert [entry["phase"] for entry in entries] == [
        "started",
        "finished",
    ]
    assert entries[0]["event_type"] == "business_step"
    assert entries[0]["message"] == "演示搜索：Playwright"
    assert entries[0]["data"] == {"keyword": "Playwright"}
    assert "self" not in entries[0]["data"]
    assert entries[0]["step_id"] == entries[1]["step_id"]


def test_business_step_records_failure_and_reraises(
    autoui_logger,
    output_path: str,
) -> None:
    """
    验证装饰后的业务方法失败时仍保留原始异常行为。

    失败事件由 WebStepRuntime 负责写入，
    装饰器本身不吞掉异常，pytest 仍能获得原始失败结果。
    """

    class DemoPage:
        def __init__(self, runtime: WebStepRuntime) -> None:
            self._web_step_runtime = runtime

        @business_step("演示失败：{keyword}")
        def search(self, keyword: str) -> None:
            """模拟一个抛出业务异常的页面方法。"""
            raise RuntimeError(f"搜索失败：{keyword}")

    with pytest.raises(RuntimeError, match="搜索失败：Playwright"):
        DemoPage(
            WebStepRuntime(
                page=_make_trace_page(),
                autoui_logger=autoui_logger,
            )
        ).search("Playwright")

    entries = _read_jsonl(
        Path(output_path) / "autoui-events.jsonl"
    )
    entries = [
        entry
        for entry in entries
        if entry["event_type"] == "business_step"
    ]

    assert [entry["phase"] for entry in entries] == [
        "started",
        "failed",
    ]
    assert entries[0]["message"] == "演示失败：Playwright"
    assert entries[1]["error_type"] == "RuntimeError"
    assert entries[1]["error_message"] == "搜索失败：Playwright"
    assert "RuntimeError" in entries[1]["traceback"]
    assert entries[0]["step_id"] == entries[1]["step_id"]
