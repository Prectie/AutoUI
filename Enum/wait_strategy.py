from enum import Enum
from typing import Tuple

from selenium.webdriver.common.by import By


class WaitStrategy(Enum):
    """等待类型统一枚举"""
    # locator 占位符
    IGNORED_LOCATOR: Tuple[str, str] = (By.XPATH, "")  # 会被 needs_locator=False 忽略, 仅作占位符

    # 返回 element
    PRESENCE = 'presence'  # 等待并查找 DOM 中至少出现一个符合定位器的元素（不保证元素可见）
    VISIBLE = 'visible'  # 等待 DOM 中出现且对用户可见的第一个符合定位器的元素
    VISIBLE_ALL = 'visible_all'  # 等待 DOM 中所有符合定位器的元素都加载且可见
    CLICKABLE = 'clickable'  # 检查元素可见且是 `enabled` 的，确保你可以点击它
    GET_ALL = 'get_all'  # 直接获取元素, 无需等待, 一般用于断言查找元素不存在

    # 返回 bool
    PRESENT_TEXT_IN_ELEMENT = 'present_text_in_element'  # 等待指定元素的 .text 包含 text, 即 .text in text, 成功返回 True
    PRESENT_TEXT_IN_ELEMENT_ATTRIBUTE = 'present_text_in_element_attribute'  # 等待 text信息 出现在元素属性 attribute 中
    INVISIBLE = 'invisible'  # 检查元素是不可见的或者不存在于DOM中的
    WAIT_STALENESS = 'wait_staleness'  # 检查给定的元素 WebElement 从 DOM 中过时
    IFRAME_SWITCH = 'iframe_switch'  # 切换指定 iframe
    DEFAULT_IFRAME_SWITCH = 'default_iframe_switch'  # 切换回默认 iframe
    PARENT_IFRAME_SWITCH = 'parent_iframe_switch'  # 切换回上一级 iframe
    NUMBER_OF_WINDOWS_TO_BE = 'number_of_windows_to_be'  # 窗口数是否达到预期
    NEW_WINDOW_IS_OPENED = 'new_window_is_opened'  # 是否有新窗口打开



