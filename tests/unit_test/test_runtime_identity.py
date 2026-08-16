"""
AutoUI 测试运行身份的框架契约测试。

这些测试不访问真实页面，
只验证 runtime plugin 是否正确注册并提供 ExecutionIdentity。
"""


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
