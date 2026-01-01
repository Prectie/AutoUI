import time

import allure

from Enum.attribute import Attribute
from Page.base_page import BasePage


class ArmamentSearchPage(BasePage):
    """ 武器装备智能检索助手页面, 负责询问助手、获取答案等一系列操作
    """
    _locators = {
        "iframe_检索助手": "//iframe[contains(@id, 'iframe-iframe-')]",
        "iframe_答案": "//iframe[@class='iframe-container']",

        "action_输入问题": "//div[@role='textbox']",
        "action_提交问题": "//button[@type='button']",

        "query_正在运行状态": "//span[text()='任务状态:正在运行']",
        "query_展示正在回答": "//span[contains(text(), '思考中')]",  # 用于判断是否在回答, 避免浪费时间
        "query_展示数据总结": "//body[@id='report-body']//div[@class='prose max-w-none']//p",  # 用于判断是否结束了回答
        "query_统计卡片标题": "//body[@id='report-body']//div[@class='stat-card']//p",
        "query_统计卡片数值": "//body[@id='report-body']//div[@class='stat-card']//h3",
        "query_柱状图": "//body[@id='report-body']//div[contains(@id, 'chart')]//canvas",

    }

    def _switch_assistant_iframe(self):
        """ 切换到 助手 所在的 iframe
        """
        self.base.element_op.switch_iframe_by_keyword('iframe_检索助手')

    @allure.step("等待回答结束")
    def _wait_for_answer_finished(self, timeout: int = 240):
        """ 等待回答结束

        :param timeout: 等待回答的最大时间, 默认 240s
        """
        # 切换到答案所在 iframe
        self.base.element_op.switch_iframe_by_keyword('iframe_答案', timeout=timeout)
        self.base.wait_op.wait_until_result_stable('query_展示数据总结')

    """ 业务逻辑 """
    @allure.step("对助手进行提问")
    def ask_question_and_commit(self, question: str):
        """
        对 武器装备检索助手 进行提问

        :param question: 问题
        """
        # 切换 iframe
        self._switch_assistant_iframe()
        # 等待出现 正在运行 提示
        self.base.wait_op.wait_element_stale_by_keyword('query_正在运行状态')
        # 输入问题 —— 这里有一个问题, 不知为何脚本输入会导致反串, 因此这里用反串进行输入
        self.base.element_op.input_by_keyword('action_输入问题', value=question[::-1])
        # 提交问题
        self.base.element_op.click_by_keyword('action_提交问题')
        # 如果没有正在回答, 说明大模型卡住了, 直接报错
        self.base.element_op.get_element_by_keyword('query_展示正在回答')
        # 等待回答结束
        self._wait_for_answer_finished()

    @allure.step("检查卡片是否被渲染")
    def assert_stat_grid_rendered(self):
        """ 断言统计卡片区域渲染成功
        """
        # 统计卡片标题
        titles = self.base.element_op.get_text_by_keyword('query_统计卡片标题', mode='all', strip=True)
        # 统计卡片数值
        values = self.base.element_op.get_text_by_keyword('query_统计卡片数值', mode='all', strip=True)

        assert titles, "卡片标题列表为空，统计区域未渲染"
        assert values, "卡片数值列表为空，统计区域未渲染"
        assert len(titles) == len(values), f"卡片标题数量 ({len(titles)}) 和数值数量 ({len(values)}) 不一致"
        assert all(titles), "存在标题文本为空的卡片"
        assert all(values), "存在数值文本为空的卡片"

    @allure.step("检查柱状图是否被渲染")
    def assert_bar_chart_rendered(self):
        """ 断言柱状图渲染成功
        """
        canvas = self.base.element_op.get_element_by_keyword('query_柱状图')

        # 再次确认柱状图是否显示
        assert canvas.is_displayed()

        # 获取柱状图的尺寸
        size = canvas.size
        assert size["width"] > 0 and size["height"] > 0, f"柱状图尺寸异常: {size}"

        # 获取柱状图的 width 和 height 属性, 再次判断
        w_pro = canvas.get_property(Attribute.WIDTH.value) or 0
        h_pro = canvas.get_property(Attribute.HEIGHT.value) or 0

        assert w_pro > 0 and h_pro > 0, f"柱状图属性宽高异常: width={w_pro}, height={h_pro}"



