"""AutoUI JSONL 日志格式化器。"""

from __future__ import annotations

import json
import logging
from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any


class AutoUIJsonFormatter(logging.Formatter):
    """
    将 LogRecord 中的 AutoUI 事件格式化为单行 JSON。

    输入：
        LogRecord.autoui_event。
        该字段由 AutoUILogger.emit() 注入。

    输出：
        一行完整、可被 json.loads() 解析的 JSON 字符串。

    设计边界：
        本类只负责事件序列化，不负责创建 Logger、Handler、文件
        或 pytest fixture 生命周期。
    """

    # 该版本标识 JSONL 字段结构；发生不兼容的协议变更时才递增。
    SCHEMA_VERSION = 1

    def format(self, record: logging.LogRecord) -> str:
        """
        将一条 LogRecord 转换为 JSONL 内容。

        参数：
            record:
                Python logging 创建的日志记录。

        返回：
            不包含真实换行符的 JSON 字符串。

        异常：
            ValueError:
                LogRecord 缺少 AutoUI 事件，或必填字段为空。

            TypeError:
                data 不是 Mapping，或事件中包含无法 JSON 序列化的值。
        """
        raw_event: object = getattr(record, "autoui_event", None)

        if not isinstance(raw_event, Mapping):
            raise ValueError(
                "LogRecord 缺少 autoui_event，"
                "AutoUIJsonFormatter 只能格式化 AutoUI 事件"
            )

        event = dict(raw_event)

        data = event.get("data")
        if data is None:
            data = {}

        if not isinstance(data, Mapping):
            raise TypeError("AutoUI 事件的 data 必须是 Mapping")

        # 事件字段优先取 AutoUILogger 提交的协议值；
        # timestamp 和 message 在事件未显式提供时分别回退到 LogRecord 的时间和文本。
        payload: dict[str, Any] = {
            "schema_version": event.get(
                "schema_version",
                self.SCHEMA_VERSION,
            ),
            "timestamp": event.get(
                "timestamp",
                self._format_timestamp(record.created),
            ),
            "level": record.levelname,
            "event_type": self._required_text(event, "event_type"),
            "phase": self._required_text(event, "phase"),
            "message": self._required_text(
                event,
                "message",
                fallback=record.getMessage(),
            ),
            "testrun_uid": event.get("testrun_uid"),
            "worker_id": event.get("worker_id"),
            "nodeid": event.get("nodeid"),
            "step_id": event.get("step_id"),
            "data": dict(data),
            "duration_ms": event.get("duration_ms"),
            "error_type": event.get("error_type"),
            "error_message": event.get("error_message"),
            "traceback": event.get("traceback"),
        }

        # 异常堆栈作为 JSON 字符串写入。
        # json.dumps() 会将其中的换行符转义，保证物理上仍是一行。
        if record.exc_info and not payload["traceback"]:
            payload["traceback"] = self.formatException(record.exc_info)

        return json.dumps(
            payload,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
        )

    @staticmethod
    def _required_text(
        event: Mapping[str, Any],
        field_name: str,
        fallback: str | None = None,
    ) -> str:
        """读取并校验事件中的必填文本字段。"""
        value = event.get(field_name)

        if (
            fallback is not None
            and (
                not isinstance(value, str)
                or not value.strip()
            )
        ):
            value = fallback

        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"AutoUI 事件字段不能为空：{field_name}")

        return value

    @staticmethod
    def _format_timestamp(timestamp: float) -> str:
        """将 LogRecord 时间转换为 UTC ISO 8601 字符串。"""
        return (
            datetime.fromtimestamp(
                timestamp,
                tz=timezone.utc,
            )
            .isoformat(timespec="milliseconds")
            .replace("+00:00", "Z")
        )
