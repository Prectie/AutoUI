"""
AutoUI pytest 运行时插件。

本模块负责将 pytest 和 pytest-xdist 提供的运行时信息，
组装成 AutoUI 统一的 ExecutionIdentity 对象。

本模块主要负责：
    1. 获取整次测试运行的 testrun_uid；
    2. 获取当前 worker_id；
    3. 获取当前测试项的 nodeid；
    4. 通过 execution_identity fixture 向测试和其他插件提供统一身份。

配置解析由 autoui.plugins.options 负责；
浏览器上下文由 autoui.plugins.web 负责；
本模块只处理测试运行身份。
"""
import pytest

from autoui.core.runtime import ExecutionIdentity

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
