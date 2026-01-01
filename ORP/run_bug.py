import os
import sys
from pathlib import Path

import pytest
import Fixtures.browser_fixtures
import Fixtures.func_fixtures
from Utils import analyze_utils, path_utils


def run_tests():
    # 需要测试的文件路径
    test_dir = 'Tests/ApplicationPortal/test_armament_search.py::TestArmamentSearch::test_orp_core_0001'

    pytest_args = [
        test_dir,
        "-vs",
        "-o", "addopts=",
    ]
    print("即将执行 pytest: ")
    # 执行测试并生成 Allure 结果
    pytest.main(pytest_args)


if __name__ == "__main__":
    run_tests()
