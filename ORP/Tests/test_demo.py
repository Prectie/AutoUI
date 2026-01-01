import time

import allure
import pytest
from nb_log import get_logger

from Utils.analyze_utils import combine_same_file_key
from Utils.log_utils import LoggerManager

logger = get_logger("lalala", log_path="D:/GitStore/AutoTest/Log")


# 注: allure注解在脚本中无实质性作用, 主要体现在生成测试报告时会根据注解中的内容标识每个脚本所属模块以及具体作用, 方便查看测试报告
class TestDemo:
    @pytest.mark.parametrize("data", combine_same_file_key(["common_admin_account", "demo_e"], "demo.yaml"))
    def test_(self, entry, image_snapshot, data):
        # 登录
        entry.LoginPage.login(data['username'], data['password'])
        # 截取
        # cropped_image = entry.DemoPage.action(data['tree_node'])

        # image_snapshot(cropped_image, "D:/orp-auto-test/ORP/Snapshots/test_image.png", threshold=0.1)
        assert 0


