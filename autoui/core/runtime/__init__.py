"""
AutoUI 测试运行时公共模型。

本包负责提供测试执行期间共享的运行时信息，
例如测试身份、worker 信息和测试项关联信息。

具体实现放在独立模块中，
本文件只暴露 runtime 包对外提供的公共对象。
"""

from autoui.core.runtime.identity import ExecutionIdentity


__all__ = [
    "ExecutionIdentity",
]
