import io
import time

from PIL import Image

from Page.base_page import BasePage


class DemoPage(BasePage):
    """定位器命名规则说明

    操作器(Action): 所有可交互元素(点击/输入/提交), 如：按钮，输入框，可点击元素等
    读取器(Query): 仅用于获取信息(文本/属性/状态), 如：纯展示的元素
    导航器(Context): 需要切换上下文的容器, 如：下拉菜单等
    iframe: 单独为 iframe 列一个分类
    """
    _locators = {
        "action_工程分类_指定节点": "//div[@id='ORP_MODEL_jetreeview-body']//*[text()='{}']",
        "action_demo_查看": "//div[@data-qtip='查看']",
        "action_demo_组件1": "//*[text()='组件1']",
        "query_组件": "//*[@class='x6-graph-svg-stage']"
    }

    def action(self, tree_node):
        # 点击工程
        self.base.element_op.click_by_keyword('action_工程分类_指定节点', tree_node)
        # 点击查看
        self.base.element_op.click_by_keyword('action_demo_查看')
        # 切换到最新窗口
        self.base.browser_op.switch_to_new_window()
        # 点击组件
        self.base.element_op.click_by_keyword('action_demo_组件1')
        # 全页截图
        png = self.driver.get_screenshot_as_png()
        image = Image.open(io.BytesIO(png))
        # 获取元素
        el = self.base.element_op.get_element_by_keyword('query_组件')
        loc = el.location
        size = el.size
        left = loc['x']
        top = loc['y']
        right = left + size['width']
        bottom = top + size['height']
        return image.crop((left, top, right, bottom))




