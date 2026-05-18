from Page.base_page import BasePage


class ModuleLibraryPage(BasePage):
    """ 模型库页面
    """
    _locators = {
        "action_搜索": "//input[contains(@id, 'qqfield')]",
    }

    def search_module(self, text):
        self.base.element_op.input_by_keyword('action_搜索', value=text)
