"""
AutoUI 结构化日志门面。

本模块只负责构造 AutoUI 统一的结构化事件，
不负责创建 logger、不负责文件写入，也不依赖 pytest、Playwright 或具体 Page Object。

底层 logger 的创建、handler 配置和 JSONL 输出由 pytest fixture 配置的标准 logging 负责。
"""

import logging
import uuid
from collections.abc import Mapping
from contextlib import contextmanager
from time import perf_counter
from types import TracebackType
from typing import Any, Iterator

from autoui.core.runtime import ExecutionIdentity


ExcInfo = tuple[
    type[BaseException],
    BaseException,
    TracebackType | None,
]


class AutoUILogger:
    """
    AutoUI 结构化事件日志门面。

    参数：
        logger:
            由外部提供的标准 logging.Logger。
            由 pytest fixture 创建并配置，负责实际的日志输出。

        identity:
            当前 pytest 测试项的 ExecutionIdentity。
            用于自动补充 testrun_uid、worker_id 和 nodeid。

    设计边界：
        AutoUILogger 只负责事件建模和事件提交。
        它不创建 logger、不管理 handler、不直接打开日志文件，
        也不理解具体的 pytest fixture 或 Playwright 对象。
    """
    def __init__(
        self,
        logger: logging.Logger,
        identity: ExecutionIdentity
    ) -> None:
        """
        创建 AutoUILogger。

        参数：
            logger:
                外部创建的标准 logging.Logger。

            identity:
                当前测试项的统一运行身份。

        异常：
            不主动校验 logger 和 identity。
            identity 自身已经通过 ExecutionIdentity 完成字段校验。
        """
        self._logger = logger
        self._identity = identity

    def emit(
        self,
        *,
        event_type: str,
        phase: str,
        message: str,
        data: Mapping[str, Any] | None = None,
        step_id: str | None = None,
        duration_ms: float | None = None,
        error_type: str | None = None,
        error_message: str | None = None,
        level: int = logging.INFO,
        exc_info: bool | ExcInfo = False
    ) -> None:
        """
        写入一条结构化测试事件。

        该方法负责把事件描述与当前测试项的运行身份合并，
        然后通过 logging.Logger 提交给后续 handler 和 JSON formatter。

        参数：
            event_type:
                事件类型，例如 operation、playwright_action。

            phase:
                事件阶段，例如 started、finished、failed。

            message:
                面向人的事件描述，例如 Locator.click 或 Page.goto。

            data:
                当前事件关联的业务或技术数据。
                数据应当由字符串、数字、布尔值、列表和字典等 JSON 友好的对象组成。

            step_id:
                同一次操作的关联标识。
                started、finished 和 failed 事件应当共享同一个值。
                独立生命周期事件可以不传入该参数。

            duration_ms:
                当前阶段对应的耗时，单位为毫秒。
                通常只在 finished 或 failed 事件中填写。

            error_type:
                失败事件的异常类型名称。
                非失败事件保持为 None。

            error_message:
                失败事件的异常消息。
                非失败事件保持为 None。

            level:
                Python logging 日志级别。
                普通事件通常使用 logging.INFO，
                失败事件通常使用 logging.ERROR。

            exc_info:
                是否记录异常 traceback。
                False 表示不记录，True 表示使用当前处理中的异常；
                pytest 的 CallInfo 异常也可以直接传入其异常三元组。

        异常：
            ValueError:
                event_type、phase 或 message 为空时抛出。
        """
        # 这些字段属于 AutoUI 事件协议的固定字段，
        # 如果允许空值，后续平台无法稳定筛选和聚合日志。
        for field_name, value in (
            ("event_type", event_type),
            ("phase", phase),
            ("message", message),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} 字段不能为空")

        # 复制 data，避免调用方在日志提交后继续修改原始字典，
        # 导致日志内容与实际执行参数不一致。
        event: dict[str, Any] = {
            "event_type": event_type,
            "phase": phase,
            "message": message,
            "testrun_uid": self._identity.testrun_uid,
            "worker_id": self._identity.worker_id,
            "nodeid": self._identity.nodeid,
            "step_id": step_id,
            # data 只承载业务或技术上下文；耗时和异常属于事件协议字段。
            "data": dict(data) if data is not None else {},
            "duration_ms": duration_ms,
            "error_type": error_type,
            "error_message": error_message,
        }

        # 使用 autoui_event 作为 AutoUI 事件载体，避免自定义字段直接覆盖 LogRecord 的内置属性。
        # JSON formatter 后续负责读取该字段并序列化。
        self._logger.log(
            level,
            message,
            extra={"autoui_event": event},
            exc_info=exc_info
        )

    @contextmanager
    def operation(
        self,
        message: str,
        *,
        event_type: str = "operation",
        data: Mapping[str, Any] | None = None,
    ) -> Iterator[None]:
        """
        自动记录一次操作的开始、成功或失败。

        该方法使用 context manager 包裹实际操作，
        调用方不需要手动分别发送 started、finished 和 failed 事件。

        参数：
            message:
                操作描述，例如 Locator.click 或 Page.goto。

            event_type:
                事件类型。
                默认使用 operation。
                后续 Playwright 底层包装器可以传入
                playwright_action。

            data:
                与当前操作相关的参数和上下文数据。

        返回：
            一个供 with 语句使用的上下文管理器。

        异常：
            实际操作抛出的 Exception 会先被记录为 failed，
            然后继续向上抛出，保证 pytest 能够正确判定测试失败。
        """
        # 同一次操作的所有阶段共享同一份关联 ID，
        # 这样平台才能把 started、finished 和 failed 合并展示。
        step_id = uuid.uuid4().hex

        # 复制基础数据，让三个阶段拥有一致的上下文。
        base_data = dict(data) if data is not None else {}

        # perf_counter 适合计算耗时，不受系统时间调整影响。
        started_at = perf_counter()

        self.emit(
            event_type=event_type,
            phase="started",
            message=message,
            data=base_data,
            step_id=step_id,
            level=logging.INFO
        )

        try:
            # 进入 with 代码块，执行真正的 Playwright 操作。
            yield
        except Exception as exc:
            # 失败事件保留原始操作数据；耗时和异常写入协议顶层字段，
            # 便于平台直接筛选失败原因和聚合耗时。
            duration_ms = round(
                (perf_counter() - started_at) * 1000,
                2
            )

            self.emit(
                event_type=event_type,
                phase="failed",
                message=message,
                data=base_data,
                step_id=step_id,
                duration_ms=duration_ms,
                error_type=type(exc).__name__,
                error_message=str(exc),
                level=logging.ERROR,
                exc_info=True
            )

            # 不能吞掉原始异常，否则 pytest 可能错误地认为测试成功。
            raise

        else:
            # 只有 with 代码块没有异常结束，
            # 才能记录 finished。
            duration_ms = round(
                (perf_counter() - started_at) * 1000,
                2
            )

            self.emit(
                event_type=event_type,
                phase="finished",
                message=message,
                data=base_data,
                step_id=step_id,
                duration_ms=duration_ms,
                level=logging.INFO,
            )

