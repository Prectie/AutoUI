class BaseAssertions:
    @staticmethod
    def verify_contains(actual: str, expected: str, msg: str = ""):
        """断言期望值是否包含在实际值中

        参数说明：
            actual: 实际出现的值
            expected: 期望存在的值
            msg: 自定义报错信息
        """
        assert expected in actual, msg or f"断言失败，实际值包含期望值，但期望值为'{expected}'，实际为：'{actual}'"

    @staticmethod
    def verify_equals(actual: str, expected: str, msg: str = ""):
        """断言期望值等于实际值

        参数说明：
            actual: 实际出现的值
            expected: 期望出现的值
            msg: 自定义报错信息
        """
        assert actual == expected, msg or f"断言失败，期望值相等，但期望值为：'{expected}'，实际为：'{actual}'"

    @staticmethod
    def verify_true(boolean: bool, msg: str = ""):
        """断言结果是否为 true, 为 true 成功, 为 False 则断言失败
        """
        assert boolean, msg or f"断言失败，结果为 {boolean}"
