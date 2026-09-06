"""
AutoUI pytest 运行时插件。

本模块负责将 pytest 和 pytest-xdist 提供的运行时信息，
组装成 AutoUI 统一的 ExecutionIdentity 对象。

本模块主要负责：
    1. 获取整次测试运行的 testrun_uid；
    2. 获取当前 worker_id；
    3. 获取当前测试项的 nodeid；
    4. 通过 execution_identity fixture 向测试和其他插件提供统一身份；
    5. 通过 autoui_logger fixture 创建当前测试项的结构化日志输出；
    6. 通过 pytest_runtest_makereport 记录 setup、call、teardown 结果。

配置解析由 autoui.plugins.options 负责；
浏览器上下文由 autoui.plugins.web 负责；
本模块负责测试运行身份和测试项级日志生命周期。
"""
import logging
import uuid
from collections.abc import Iterator
from pathlib import Path

import allure
import pytest

from autoui.core.logging.autoui_logger import AutoUILogger
from autoui.core.logging.json_formatter import AutoUIJsonFormatter
from autoui.core.runtime import ExecutionIdentity


_AUTOUI_LOGGER_KEY = pytest.StashKey[AutoUILogger]()
_LOGGER_STATE_KEY = pytest.StashKey[
    tuple[logging.Logger, list[logging.Handler]]
]()
_REPORTS_KEY = pytest.StashKey[dict[str, pytest.TestReport]]()
_OUTPUT_PATH_KEY = pytest.StashKey[Path]()


def _close_logger_state(
    native_logger: logging.Logger,
    handlers: list[logging.Handler],
) -> None:
    """
    关闭一个测试项专用 logger 的全部 handler。

    参数：
        native_logger:
            当前测试项专用的标准 logging.Logger。

        handlers:
            由 autoui_logger fixture 创建并挂载到 native_logger 的 handler。

    生命周期：
        该函数只在测试项完整的 setup、call、teardown 流程结束后调用，
        确保 teardown 结果仍能写入 JSONL 文件。
    """
    for handler in handlers:
        native_logger.removeHandler(handler)
        handler.flush()
        handler.close()


def _close_test_logger(item: pytest.Item) -> None:
    """
    清理当前测试项保存的 logger 状态。

    `pytest_runtest_protocol` 在整个测试项协议结束后调用本函数，
    因此 pytest 的 teardown 报告已经有机会通过
    `pytest_runtest_makereport` 写入日志。

    参数：
        item:
            当前 pytest 测试项，用于读取并删除 stash 中的 logger 状态。
    """
    logger_state = item.stash.get(_LOGGER_STATE_KEY, None)
    if logger_state is not None:
        del item.stash[_LOGGER_STATE_KEY]
        native_logger, handlers = logger_state
        _close_logger_state(native_logger, handlers)

    if item.stash.get(_AUTOUI_LOGGER_KEY, None) is not None:
        del item.stash[_AUTOUI_LOGGER_KEY]

    if item.stash.get(_REPORTS_KEY, None) is not None:
        del item.stash[_REPORTS_KEY]

    if item.stash.get(_OUTPUT_PATH_KEY, None) is not None:
        del item.stash[_OUTPUT_PATH_KEY]


def _emit_test_outcome(
    autoui_logger: AutoUILogger,
    report: pytest.TestReport,
    call: pytest.CallInfo[object],
) -> None:
    """
    将 pytest 某一个执行阶段的结果转换为 AutoUI 事件。

    参数：
        autoui_logger:
            当前测试项的 AutoUILogger，由 autoui_logger fixture 创建。

        report:
            pytest 根据当前阶段生成的 TestReport。
            `report.when` 标识 setup、call 或 teardown，
            `report.outcome` 标识 passed、failed 或 skipped。

        call:
            当前阶段的 CallInfo，用于取得耗时和原始异常信息。

    设计边界：
        本函数只记录 pytest 已经判定的阶段结果，不修改 report，
        也不吞掉或重新抛出测试异常。
    """
    error_type = None
    error_message = None
    exc_info = False

    # 只有 pytest 判定为 failed 时才把原始异常三元组传给 logging，
    # 这样 JSONL 中的 traceback 能与 pytest 的失败位置保持一致。
    if report.failed and call.excinfo is not None:
        error_type = call.excinfo.type.__name__
        error_message = str(call.excinfo.value)
        exc_info = (
            call.excinfo.type,
            call.excinfo.value,
            call.excinfo.tb,
        )

    autoui_logger.emit(
        event_type="test_outcome",
        phase=report.when,
        message=f"pytest {report.when}：{report.outcome}",
        data={"outcome": report.outcome},
        duration_ms=round(call.duration * 1000, 2),
        error_type=error_type,
        error_message=error_message,
        level=logging.ERROR if report.failed else logging.INFO,
        exc_info=exc_info,
    )


def _attach_failure_artifacts(item: pytest.Item) -> None:
    """将失败测试的框架产物附加到当前 Allure 测试结果。

    产物目录来自 pytest-playwright 的 ``output_path`` fixture；
    测试阶段状态来自 ``pytest_runtest_makereport`` 保存的报告。
    只有 setup、call 或 teardown 任一阶段失败时，才会添加失败证据。

    参数：
        item:
            当前 pytest 测试项，用于读取测试阶段报告和产物目录。

    返回：
        None。产物目录不存在或没有失败阶段时直接返回。

    异常：
        Allure 写入附件时产生的异常会向上抛出，避免静默隐藏框架集成问题。
    """
    output_dir = item.stash.get(_OUTPUT_PATH_KEY, None)
    reports = item.stash.get(_REPORTS_KEY, None)

    if output_dir is None or reports is None:
        return

    # setup、call、teardown 任一阶段失败，都需要保留完整失败证据。
    if not any(report.failed for report in reports.values()):
        return

    attachments = [
        (
            output_dir / "autoui-events.jsonl",
            "AutoUI 事件日志",
            "text/plain",
            "jsonl",
        ),
        (
            output_dir / "autoui-errors.jsonl",
            "AutoUI 错误日志",
            "text/plain",
            "jsonl",
        ),
    ]

    # pytest-playwright 可能生成多个失败截图，因此不能只查找一个固定文件名。
    attachments.extend(
        (
            path,
            f"失败截图：{path.name}",
            allure.attachment_type.PNG,
            None,
        )
        for path in sorted(output_dir.glob("test-failed-*.png"))
    )

    # Trace 文件名可能是 trace.zip、trace-1.zip 等形式。
    attachments.extend(
        (
            path,
            f"Playwright Trace：{path.name}",
            allure.attachment_type.ZIP,
            None,
        )
        for path in sorted(output_dir.glob("trace*.zip"))
    )

    for path, name, attachment_type, extension in attachments:
        if not path.is_file():
            continue

        # JSONL 使用 text/plain，并保留 jsonl 扩展名，方便下载后继续检索。
        allure.attach.file(
            str(path),
            name=name,
            attachment_type=attachment_type,
            extension=extension,
        )


@pytest.hookimpl(wrapper=True, tryfirst=True)
def pytest_runtest_makereport(
    item: pytest.Item,
    call: pytest.CallInfo[object],
):
    """
    在 pytest 生成 setup、call、teardown 报告后记录测试结果。

    该 hook 使用 pytest 的原生报告作为唯一结果来源，
    因此日志中的 outcome 与 pytest 最终判定保持一致。
    `yield` 前后不改变 pytest 返回的 TestReport。

    返回：
        pytest 原本生成的 TestReport，不做任何修改。
    """
    report = yield

    reports = item.stash.get(_REPORTS_KEY, None)
    if reports is not None:
        reports[report.when] = report

    autoui_logger = item.stash.get(_AUTOUI_LOGGER_KEY, None)
    if autoui_logger is not None:
        _emit_test_outcome(autoui_logger, report, call)

    # teardown 报告生成时，pytest-playwright 的截图和 Trace 已经完成归档；
    # 此时 Allure 测试仍处于打开状态，可以安全地追加附件。
    if report.when == "teardown":
        _attach_failure_artifacts(item)

    return report


@pytest.hookimpl(wrapper=True, tryfirst=True)
def pytest_runtest_protocol(
    item: pytest.Item,
    nextitem: pytest.Item | None,
):
    """
    在当前测试项的完整执行协议结束后关闭 JSONL handler。

    fixture finalizer 会在 teardown 阶段执行；本 hook 在整个
    runtest protocol 返回后才清理 handler，保证 teardown 报告能够落盘。

    参数：
        item:
            当前 pytest 测试项。

        nextitem:
            pytest 即将执行的下一个测试项；当前实现不需要使用它。

    返回：
        pytest runtest protocol 的原始返回值。
    """
    result = None
    try:
        result = yield
    finally:
        _close_test_logger(item)

    return result


@pytest.fixture()
def execution_identity(
    request,
    worker_id: str,
    testrun_uid: str,
) -> ExecutionIdentity:
    """
    为当前 pytest 测试项构造 ExecutionIdentity。

    参数：
        request:
            pytest 内置 fixture。
            通过 request.node.nodeid 获取当前测试项的唯一标识。

        worker_id:
            pytest-xdist 提供的 worker 标识。
            串行执行时通常为 master，并行执行时通常为 gw0、gw1 等。

        testrun_uid:
            pytest-xdist 提供的整次测试运行唯一标识。
            同一次并行测试中的所有 worker 应共享该值。

    返回：
        当前测试项对应的 ExecutionIdentity 实例。

    生命周期：
        该 fixture 默认使用 function scope，每个 pytest 测试项都会获得自己的身份对象。
    """
    # request.node.nodeid 能区分测试函数和参数化测试用例
    nodeid = request.node.nodeid

    return ExecutionIdentity(
        testrun_uid=testrun_uid,
        worker_id=worker_id,
        nodeid=nodeid
    )

@pytest.fixture(scope="function", autouse=True)
def autoui_logger(
    request: pytest.FixtureRequest,
    execution_identity: ExecutionIdentity,
    output_path: str,
) -> Iterator[AutoUILogger]:
    """
    为当前 pytest 测试项创建独立的 AutoUILogger 和 JSONL 文件输出。

    参数：
        request:
            pytest 内置 fixture。
            用于把当前测试项的 AutoUILogger 和 handler 生命周期状态
            保存到 item.stash，供结果 hook 和协议结束 hook 使用。

        execution_identity:
            由 execution_identity fixture 提供的当前测试项身份。
            来源于 pytest-xdist 的 testrun_uid、worker_id 和 pytest 当前测试项的 nodeid。
            该身份会被 AutoUILogger 自动写入每条事件。

        output_path:
            由 pytest-playwright 提供的当前测试项产物目录。
            同一个测试项的 JSONL、截图和 Trace 都应放在这个目录下。
            本 fixture 不自行计算测试目录，避免与 pytest-playwright
            的产物隔离规则重复。

    返回：
        当前测试项使用的 AutoUILogger 实例。
        测试用例或后续 WebStepRuntime 通过该对象提交 AutoUI 事件。

    生命周期：
        fixture setup 阶段创建 Logger、Formatter 和两个 FileHandler；
        测试执行期间由 AutoUILogger 向 Logger 提交事件；
        pytest_runtest_makereport 记录 setup、call、teardown 结果；
        整个测试项协议结束后，pytest_runtest_protocol 移除、flush
        并关闭当前测试项的 handler。

    异常：
        output_path 无法创建或日志文件无法打开时，
        FileHandler 会抛出文件系统异常，pytest 将当前测试标记为
        fixture setup 失败。
    """
    # output_path 是 pytest-playwright 为当前测试项提供的产物目录。
    # 这里仅确保目录存在，不重新设计测试项目录结构。
    output_dir = Path(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 这些属性属于测试项元数据，不属于业务步骤事件。
    # pytest 生成 setup、call、teardown 报告时会复制它们，
    # JUnit XML reporter 再将它们写入 testcase 的 properties。
    # 这样 CI 可以通过统一身份定位 JSONL 和其他测试产物。
    for property_name, property_value in (
        ("testrun_uid", execution_identity.testrun_uid),
        ("worker_id", execution_identity.worker_id),
        ("nodeid", execution_identity.nodeid),
        ("output_path", str(output_dir)),
    ):
        request.node.user_properties.append(
            (property_name, property_value)
        )

    # 报告和产物目录属于当前测试项的运行时状态，不写入业务事件，
    # 由结果 hook 在 teardown 阶段读取并关联到 Allure。
    request.node.stash[_REPORTS_KEY] = {}
    request.node.stash[_OUTPUT_PATH_KEY] = output_dir

    # logging.getLogger() 会按名称缓存 Logger。
    # 使用 worker_id 和随机值构造唯一名称，避免不同测试项复用
    # 旧 handler，导致日志串写或同一事件重复输出。
    logger_name = (
        f"autoui.{execution_identity.worker_id}."
        f"{uuid.uuid4().hex}"
    )
    native_logger = logging.getLogger(logger_name)

    # Logger 使用 DEBUG 作为最低级别。
    # 具体写入哪个文件由两个 handler 各自的 level 决定。
    native_logger.setLevel(logging.DEBUG)

    # 当前测试项的日志已经绑定到自己的文件。
    # 禁止继续传播到 root logger，避免控制台重复输出或被全局
    # logging 配置再次处理。
    native_logger.propagate = False

    # Formatter 只负责把 LogRecord 转换为 JSON 字符串。
    # 文件创建和写入仍由下面的 FileHandler 负责。
    formatter = AutoUIJsonFormatter()
    handlers: list[logging.Handler] = []

    try:
        # 完整事件文件接收 DEBUG 及以上的所有 AutoUI 事件。
        event_handler = logging.FileHandler(
            output_dir / "autoui-events.jsonl",
            mode="w",
            encoding="utf-8",
        )
        handlers.append(event_handler)
        event_handler.setLevel(logging.DEBUG)
        event_handler.setFormatter(formatter)
        native_logger.addHandler(event_handler)

        # 错误文件只接收 ERROR 及以上事件。
        # 失败事件因此会同时出现在完整事件文件和错误文件中，
        # 方便平台按需只读取错误日志。
        error_handler = logging.FileHandler(
            output_dir / "autoui-errors.jsonl",
            mode="w",
            encoding="utf-8",
        )
        handlers.append(error_handler)
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        native_logger.addHandler(error_handler)

        # AutoUILogger 只负责构造事件和提交 Logger，
        # 不负责创建 handler 或管理文件生命周期。
        logger = AutoUILogger(
            logger=native_logger,
            identity=execution_identity,
        )
    except BaseException:
        # 如果任一日志文件创建失败，先释放已经成功创建的 handler，
        # 再把原始异常交给 pytest，避免留下打开的文件句柄。
        _close_logger_state(native_logger, handlers)
        raise

    # handler 必须一直保持可用到 pytest_runtest_protocol 返回之后，
    # 因为 teardown 报告是在 fixture finalizer 之后仍可能被 hook 处理。
    request.node.stash[_AUTOUI_LOGGER_KEY] = logger
    request.node.stash[_LOGGER_STATE_KEY] = (native_logger, handlers)

    yield logger
