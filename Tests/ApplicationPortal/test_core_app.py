import time

import pytest

from Utils.analyze_utils import read_yaml_combine, read_yaml_data
from Utils.log_utils import LoggerManager

logger = LoggerManager().get_logger()


class TestCoreApp:
    @pytest.fixture(scope="function", autouse=True)
    def login(self, entry, data):
        # 登陆测试账号
        entry.LoginPage.login(data['username'], data['password'])
        yield
        # 切换到管理运行实例页面
        entry.ModuleRunPage.goto_menu(data['admin_console'])
        # 删除任务
        entry.AdminConsolePage.perform_instance_action(
            data['manage_run_instances'],
            data['account_name'],
            data['unknown_air_situation'],
            data['delete']
        )

    @pytest.mark.parametrize(
        "data",
        read_yaml_combine(
            {
                ".6_test": "Common/accounts.yaml",
                "search_assistant": "Case/app_portal_data.yaml",
            }
        )
    )
    def test_orp_core_0001(self, entry, data):
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

    @pytest.mark.parametrize(
        "data",
        read_yaml_combine(
            {
                ".6_test": "Common/accounts.yaml",
                "page": "Common/navigate_to_page.yaml",
                "subpage": "Common/navigate_to_page.yaml",
                "unknown_air_situation": "Case/app_portal_data.yaml",
                "scenario_name": "Case/manage_run_app.yaml",
                "operation": "Case/manage_run_app.yaml",
            },
        )
    )
    def test_orp_core_0002(self, entry, data):
        # 进入 配置业务/发布应用 页面
        entry.ModuleRunPage.goto_menu(data['config_business'])
        # 启动不明空情业务
        entry.ConfigBusinessAndPublishAppPage.search(data['app_name'])
        entry.ConfigBusinessAndPublishAppPage.start_business(data['app_name'])

        # 设置不明空情
        entry.UnknownAirSituationPage.wait_unit_business_started()
        entry.UnknownAirSituationPage.set_air_situation_handling(
            data['air_situation_handling_tab'],
            data['height'],
            data['speed']
        )
        # 选择首波次飞机
        entry.UnknownAirSituationPage.select_first_wave_aircraft(
            data['first_wave_tab'],
            data['first_aircraft']
        )
        # 选择接续波次飞机
        entry.UnknownAirSituationPage.select_second_wave_aircraft(
            data['second_wave_tab'],
            data['second_aircraft']
        )
        # 加速仿真时间
        entry.UnknownAirSituationPage.control_panel_action(
            data['air_situation_handling_tab'],
            data['action_accelerate'],
            data['count']
        )
        # 进入态势页面
        entry.UnknownAirSituationPage.enter_menu(data['situation_tab'])
        entry.UnknownAirSituationPage.prepare_canvas_view()
        entry.UnknownAirSituationPage.monitor_module_running(data['situation_tab'], data['monitor_first_time'])

        # 发布射击命令
        entry.UnknownAirSituationPage.set_strike_status(data['air_situation_handling_tab'])
        entry.UnknownAirSituationPage.monitor_module_running(data['situation_tab'], data['monitor_second_time'])






