import time

import allure

from Page.base_page import BasePage


class UnknownAirSituationPage(BasePage):
    """ 不明空情页面
    """
    _locators = {
        # 通用
        "action_通用文本容器": "//span[text()='{}']",
        "query_正在运行提示": "//span[text()='任务状态:正在运行']",


        # 态势页面
        "query_画布": "//canvas[@aria-label]",


        # 空情设置
        "action_空情设置_高度": "(//textarea)[3]",
        "action_空情设置_速度": "(//textarea)[4]",
        "action_空情设置_空情": "(//span[@class='ant-select-selection-item'])[1]",
        "action_空情设置_发现目标": "//div[text()='发现目标' and @class]",  # 该模型一般都是要点击发现目标, 不需要点击未发现目标, 因此写死
        "action_空情设置_提交": "(//span[text()='提 交'])[1]",


        # 打击情况
        "action_打击情况_首波次飞机射击命令": "(//span[@class='ant-select-selection-item'])[2]",
        "action_打击情况_射击命令": "(//div[text()='射击' and @class])[1]",  # 该模型一般都是要点击射击, 不需要点击等待, 因此写死
        "action_打击情况_首波次飞机射击命令_提交": "(//span[text()='提 交'])[2]",


        # 首波次/接续波次计划清单
        "action_指定飞机波次选择": "//span[text()='{}']//parent::td//preceding-sibling::td"
                                                  "//div[not(contains(@class, 'selector'))]",
        "action_波次选择_是": "//div[@aria-selected='false' and not(@role)]",
        "action_波次计划_提交": "//span[text()='提 交']",


        "iframe_态势页面": "//iframe[contains(@src, 'tvGDNhCEZJgmzIRmfUV')]",
        "iframe_画布": "//*[@id='app']/div/div/div[2]/div/iframe",
        "iframe_空情处置": "//iframe[contains(@src, 'zQQymt7vc88NGHrYbAk')]",
        "iframe_首波次计划清单": "//iframe[contains(@src, 'dO3ODqIjtXHKd5h1WBo')]",
        "iframe_接续波次计划清单": "//iframe[contains(@src, 'lqj8hqaexzokiHRfR2g')]"

    }

    @allure.step("进入指定面板")
    def enter_menu(self, tab):
        """
          进入指定面板
        :param tab: 面板名称
        """
        # 点击进入面板
        self.base.element_op.click_by_keyword('action_通用文本容器', tab)

    @allure.step("等待业务启动成功")
    def wait_unit_business_started(self):
        # 调试用
        # self.driver.execute_script("debugger;")
        # 切换到提示所在的 iframe
        self.base.element_op.switch_iframe_by_keyword('iframe_态势页面')
        # 等待提示消失
        self.base.wait_op.wait_element_stale_by_keyword('query_正在运行提示')
        # 切回到顶层 iframe
        self.base.element_op.switch_default_iframe()

    @allure.step("设置空情处置")
    def set_air_situation_handling(self, tab, height, speed):
        """
          设置空情处置
        :param tab: 面板名称
        :param height: 空情高度
        :param speed: 空情速度
        """
        # 进入空情处置页面
        self.enter_menu(tab)
        # 切换到设置页面所在的 iframe
        self.base.element_op.switch_iframe_by_keyword('iframe_空情处置')
        # 高度设置
        self.base.element_op.clear_and_input_by_keyword('action_空情设置_高度', value=height)
        # 速度设置
        self.base.element_op.clear_and_input_by_keyword('action_空情设置_速度', value=speed)
        # 空情设置
        self.base.element_op.click_by_keyword('action_空情设置_空情')
        self.base.element_op.click_by_keyword('action_空情设置_发现目标')
        # 点击提交
        self.base.element_op.click_by_keyword('action_空情设置_提交')
        # 切回到顶层 iframe
        self.base.element_op.switch_default_iframe()

    @allure.step("选择首波次飞机")
    def select_first_wave_aircraft(self, tab, aircraft_name):
        """
          选择首波次飞机
        :param tab: 面板名称
        :param aircraft_name: 飞机名称
        """
        # 进入首波次飞机页面
        self.enter_menu(tab)
        # 切换到页面所在的 iframe
        self.base.element_op.switch_iframe_by_keyword('iframe_首波次计划清单')
        # 等待提示消失
        self.base.wait_op.wait_element_stale_by_keyword('query_正在运行提示')
        # 指定飞机波次选择是
        self.base.element_op.click_by_keyword('action_指定飞机波次选择', aircraft_name)
        self.base.element_op.click_by_keyword('action_波次选择_是')
        # 点击提交
        self.base.element_op.click_by_keyword('action_波次计划_提交')
        # 切回到顶层 iframe
        self.base.element_op.switch_default_iframe()

    @allure.step("选择接续波次飞机")
    def select_second_wave_aircraft(self, tab, aircraft_name):
        """
          选择接续波次飞机
        :param tab: 面板名称
        :param aircraft_name: 飞机名称
        """
        # 进入接续波次飞机页面
        self.enter_menu(tab)
        # 切换到页面所在的 iframe
        self.base.element_op.switch_iframe_by_keyword('iframe_接续波次计划清单')
        # 等待提示消失
        self.base.wait_op.wait_element_stale_by_keyword('query_正在运行提示')
        # 指定飞机波次选择是
        self.base.element_op.click_by_keyword('action_指定飞机波次选择', aircraft_name)
        self.base.element_op.click_by_keyword('action_波次选择_是')
        # 点击提交
        self.base.element_op.click_by_keyword('action_波次计划_提交')
        # 切回到顶层 iframe
        self.base.element_op.switch_default_iframe()

    @allure.step("点击空情处置控制面板选项")
    def control_panel_action(self, tab, action, count):
        """
          点击空情处置控制面板选项
        :param tab: 面板名称
        :param action: 控制选项
        :param count: 点击次数
        """
        # 进入空情处置页面
        self.enter_menu(tab)
        # 切换到设置页面所在的 iframe
        self.base.element_op.switch_iframe_by_keyword('iframe_空情处置')
        # 点击加速
        self.base.element_op.click_times_by_keyword('action_通用文本容器', action, times=count, interval=0.1)
        # 切回到顶层 iframe
        self.base.element_op.switch_default_iframe()

    @allure.step("持续检测模型运行情况")
    def monitor_module_running(self, tab, monitor_time: int):
        """
          持续检测模型运行情况
        :param tab: 面板名称
        :param monitor_time: 观察时间(秒)
        """
        # 进入态势页面
        self.enter_menu(tab)
        time.sleep(monitor_time)

    @allure.step("调整画布视图")
    def prepare_canvas_view(self):
        # 切换到画布所在的 iframe
        self.base.element_op.switch_iframe_by_keyword('iframe_态势页面')
        self.base.element_op.switch_iframe_by_keyword('iframe_画布')
        self.base.wait_op.wait_wheel_ready('query_画布')
        self.base.mouse_op.drag_and_drop_by_offset_by_keyword(
            'query_画布',
            x_offset=170,
            y_offset=0
        )
        self.base.mouse_op.scroll_from_origin_by_keyword('query_画布', delta_y=150, ctrl=True, ticks=3)
        # 切回到顶层 iframe
        self.base.element_op.switch_default_iframe()

    @allure.step("设置打击情况")
    def set_strike_status(self, tab):
        # 进入空情处置页面
        self.enter_menu(tab)
        # 切换到设置页面所在的 iframe
        self.base.element_op.switch_iframe_by_keyword('iframe_空情处置', timeout=180)
        # 点击首波次射击命令
        self.base.element_op.click_by_keyword('action_打击情况_首波次飞机射击命令')
        self.base.element_op.click_by_keyword('action_打击情况_射击命令')
        # 提交命令
        self.base.element_op.click_by_keyword('action_打击情况_首波次飞机射击命令_提交')
        # 切回到顶层 iframe
        self.base.element_op.switch_default_iframe()






