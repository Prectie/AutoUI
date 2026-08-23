"""
Playwright 底层日志桥接模块。

本模块负责为 Playwright 操作提供当前测试项的 AutoUILogger，
并将具体动作统一交给 AutoUILogger.operation() 执行。

本模块不负责：
    1. 创建 nb_log logger；
    2. 配置日志 handler；
    3. 序列化 JSONL；
    4. 修改 Page Object；
    5. 推断业务语义。
"""
from functools import wraps
import uuid
from contextvars import ContextVar
from collections.abc import Callable, Mapping
from typing import Any, Iterator

import pytest
from nb_log import get_logger
from playwright.sync_api import Locator, Page

from autoui.core.logging.autoui_logger import AutoUILogger
from autoui.core.runtime import ExecutionIdentity

# Playwright 方法本身不会接收 pytest fixture，
# 因此通过 ContextVar 让底层包装器能够取得当前测试的 logger。
_current_autoui_logger: ContextVar[AutoUILogger | None] = ContextVar(
    "current_autoui_logger",
    default=None,
)

_original_locator_click: Callable[..., Any] | None = None
_original_locator_fill: Callable[..., Any] | None = None
_original_page_goto: Callable[..., Any] | None = None

def run_logged_action(
    *,
    action_name: str,
    action: Callable[[], Any],
    data: Mapping[str, Any] | None = None
) -> Any:
    """
    执行一个 Playwright 底层动作，并自动记录其执行生命周期。

    参数：
        action_name:
            底层动作名称，例如 Locator.click、Locator.fill
            或 Page.goto。

        action:
            延迟执行的原始 Playwright 调用。
            该函数只有在日志 started 事件记录后才会执行。

        data:
            当前动作的参数和上下文数据。
            例如 locator 描述、输入值、URL 和操作选项。

    返回：
        原始 Playwright 动作的返回值。

    异常：
        原始 Playwright 异常会继续向上抛出。
        AutoUILogger.operation() 会先记录 failed 事件。

    设计说明：
        当当前执行上下文没有绑定 AutoUILogger 时，
        直接执行原始动作，避免日志基础设施影响 Playwright 行为。
    """
    logger = _current_autoui_logger.get()

    # 没有绑定 logger 时保持 Playwright 原始行为，
    # 防止日志初始化问题改变被测操作的执行结果。
    if logger is None:
        return action()

    # 将底层动作交给统一的 operation()，
    # 由它负责 started、finished、failed 和耗时记录。
    with logger.operation(
        action_name,
        event_type="playwright_action",
        data=data,
    ):
        return action()


def _wrap_locator_click(
    original_click: Callable[..., Any],
) -> Callable[..., Any]:
    """为 Locator.click 增加统一的操作日志生命周期。

    参数：
        original_click:
            Playwright 原始的 Locator.click 方法。

    返回：
        包装后的 click 方法。

    设计说明：
        包装函数保留 *args 和 **kwargs，确保 Playwright 原有的
        modifiers、position、timeout、force 等参数继续透传。
        实际点击通过 lambda 延迟执行，保证 started 事件先于点击发生。
    """

    @wraps(original_click)
    def logged_click(
        locator: Locator,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        return run_logged_action(
            action_name="Locator.click",
            action=lambda: original_click(
                locator,
                *args,
                **kwargs,
            ),
            data={
                "target": repr(locator),
                "args": list(args),
                "options": dict(kwargs),
            },
        )

    return logged_click


def _wrap_locator_fill(
    original_fill: Callable[..., Any],
) -> Callable[..., Any]:
    """为 Locator.fill 增加统一的操作日志生命周期。"""

    @wraps(original_fill)
    def logged_fill(
        locator: Locator,
        value: str,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        return run_logged_action(
            action_name="Locator.fill",
            action=lambda: original_fill(
                locator,
                value,
                *args,
                **kwargs,
            ),
            data={
                "target": repr(locator),
                "value": value,
                "args": list(args),
                "options": dict(kwargs),
            },
        )

    return logged_fill


def _wrap_page_goto(
    original_goto: Callable[..., Any],
) -> Callable[..., Any]:
    """为 Page.goto 增加统一的操作日志生命周期。"""

    @wraps(original_goto)
    def logged_goto(
        page: Page,
        url: str,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        return run_logged_action(
            action_name="Page.goto",
            action=lambda: original_goto(
                page,
                url,
                *args,
                **kwargs,
            ),
            data={
                "url": url,
                "args": list(args),
                "options": dict(kwargs),
            },
        )

    return logged_goto


def install_playwright_logging() -> None:
    """安装 Playwright 动作日志包装。

    该函数在每个 pytest 进程中只执行一次，避免重复包装导致同一个
    click 动作产生多组重复日志。
    """
    global _original_locator_click, _original_locator_fill, _original_page_goto

    if _original_locator_click is not None:
        return

    _original_locator_click = Locator.click
    _original_locator_fill = Locator.fill
    _original_page_goto = Page.goto
    setattr(
        Locator,
        "click",
        _wrap_locator_click(_original_locator_click),
    )
    setattr(
        Locator,
        "fill",
        _wrap_locator_fill(_original_locator_fill),
    )
    setattr(
        Page,
        "goto",
        _wrap_page_goto(_original_page_goto),
    )


def restore_playwright_logging() -> None:
    """恢复 Playwright 原始方法，避免测试进程状态泄漏。"""
    global _original_locator_click, _original_locator_fill, _original_page_goto

    if _original_locator_click is None:
        return

    setattr(Locator, "click", _original_locator_click)
    setattr(Locator, "fill", _original_locator_fill)
    setattr(Page, "goto", _original_page_goto)
    _original_locator_click = None
    _original_locator_fill = None
    _original_page_goto = None


@pytest.fixture(scope="session", autouse=True)
def playwright_action_logging() -> Iterator[None]:
    """在 pytest 会话期间安装并恢复 Playwright 动作日志包装。

    生命周期：
        pytest session 开始时安装一次；
        pytest session 结束时恢复 Locator.click 原始方法。

    设计边界：
        本 fixture 只负责修改 Playwright 方法的生命周期。
        每条测试的 AutoUILogger 仍由 autoui_logger fixture 负责创建和绑定。
    """
    install_playwright_logging()

    try:
        yield
    finally:
        restore_playwright_logging()


@pytest.fixture(scope="function", autouse=True)
def autoui_logger(
    execution_identity: ExecutionIdentity,
    output_path: str
) -> Iterator[AutoUILogger]:
    """
    为当前 pytest 测试项创建并绑定 AutoUILogger。

    参数：
       execution_identity:
           当前测试项的统一运行身份。
           用于将日志与 testrun_uid、worker_id 和 nodeid 关联。

       output_path:
           pytest-playwright 为当前测试项提供的独立产物目录。
           当前测试的日志文件会写入该目录。

    返回：
       当前测试项使用的 AutoUILogger。

    生命周期：
       fixture setup 阶段创建 logger 并绑定 ContextVar；
       测试结束后恢复 ContextVar，并关闭当前 logger 的 handler。

    异常：
       logger 创建或 handler 初始化失败时，
       fixture setup 会失败，pytest 将测试标记为基础设施失败。
    """
    # 为每个测试项创建独立 logger 名称，
    # 避免 nb_log 缓存或复用其他测试的 handler。
    logger_name = (
        f"autoui.{execution_identity.worker_id}."
        f"{uuid.uuid4().hex}"
    )

    # nb_log 负责创建底层 logging.Logger 和文件 handler。
    # 当前阶段先完成生命周期绑定，JSON formatter 后续单独配置。
    native_logger = get_logger(
        logger_name,
        log_path=output_path,
        log_filename="autoui-events.jsonl",
        error_log_filename="autoui-errors.jsonl",
        log_file_handler_type=3,
        is_add_stream_handler=False
    )

    # 防止日志记录继续传播到 root logger，
    # 避免控制台重复输出或被其他全局 handler 再次处理。
    native_logger.propagate = False

    logger = AutoUILogger(
        logger=native_logger,
        identity=execution_identity,
    )

    # ContextVar.set() 返回恢复令牌，
    # 测试结束时必须使用同一个 token 恢复之前的上下文。
    token = _current_autoui_logger.set(logger)

    try:
        # 将 AutoUILogger 提供给依赖该 fixture 的其他 fixture。
        yield logger

    finally:
        # 防止当前测试的 logger 泄漏到后续测试。
        _current_autoui_logger.reset(token)

        # 当前 logger 是每个测试项独立创建的，
        # 测试结束后关闭 handler，避免文件句柄和 handler 累积。
        for handler in list(native_logger.handlers):
            handler.flush()
            handler.close()
            native_logger.removeHandler(handler)
