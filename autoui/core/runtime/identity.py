"""
AutoUI 测试运行身份模型。

本模块负责描述单个 pytest 测试项在一次测试运行中的身份信息。

测试身份由以下字段组成：
    1. testrun_uid：整次 pytest 运行的唯一标识；
    2. worker_id：执行当前测试的 worker 标识；
    3. nodeid：pytest 为当前测试项生成的唯一标识。

本模块只保存运行身份数据，不依赖 pytest、pytest-xdist、
Playwright 或具体平台实现。
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutionIdentity:
    """
    描述单个 pytest 测试项的运行身份。

    参数：
        testrun_uid:
            整次 pytest 测试运行的唯一标识。
            同一次并行运行中的所有 worker 应共享该值。

        worker_id:
            当前测试所在的执行进程标识。
            串行执行时通常为 master，并行执行时通常为 gw0、gw1 等。

        nodeid:
            pytest 测试项的唯一标识。
            对参数化测试来说，不同参数通常对应不同的 nodeid。

    该对象使用 frozen=True，创建后不可修改，
    避免测试执行过程中身份信息发生变化。
    """

    testrun_uid: str
    worker_id: str
    nodeid: str

    def __post_init__(self) -> None:
        """
        校验测试用例身份字段

        测试身份后续会用于日志关联、artifact 目录生成和失败证据定位。
        如果字段为空，后续可能产生无法定位或互相覆盖的产物路径，因此在对象创建时提前失败
        """
        # 逐个校验身份字段，避免空字符串进入日志和 artifact 路径
        for field_name, value in (
            ("testrun_uid", self.testrun_uid),
            ("worker_id", self.worker_id),
            ("nodeid", self.nodeid),
        ):
            # 当前模型要求所有身份字段都是非空字符串
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} 不能为空")
