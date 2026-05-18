import time

import pytest

from Utils.analyze_utils import read_yaml_combine
from Utils.log_utils import LoggerManager

logger = LoggerManager().get_logger()


class TestArmamentSearch:
    @pytest.mark.parametrize(
        "data",
        read_yaml_combine(
            {
                "auto_account": "Common/accounts.yaml",
                "search_assistant": "ApplicationPortalData/app_portal_data.yaml"
            },
        )
    )
    def test_orp_core_0001(self, entry, data):
        # 登陆测试账号
        entry.LoginPage.login(data['username'], data['password'])
        # 进入武器装备智能检索助手页面
        entry.APPPortalBasePage.enter_armament_search_page()
        # logger.info(f"脚本 test_orp_core_0001 输入的问题为：{data['question']}")
        # 输入问题并提交
        entry.ArmamentSearchPage.ask_question_and_commit(data['question'])

        # 断言表格成功渲染出来
        entry.ArmamentSearchPage.assert_stat_grid_rendered()
        entry.ArmamentSearchPage.assert_bar_chart_rendered()

        # 进入监控页面停止任务
        ret = entry.MonitorPage.stop_task(data['task'])
        assert ret == 0, f"监控页面上仍然存在处于正在运行状态的场景, 场景名为: {data['task']}"





