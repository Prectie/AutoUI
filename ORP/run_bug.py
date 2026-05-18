

import pytest


def run_tests():
    # 需要测试的文件路径
    test_dir = ''

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
