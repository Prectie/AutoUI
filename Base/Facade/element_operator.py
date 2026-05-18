import time
from typing import Dict, Tuple, List, Optional, Literal, Union

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from Base.Core.selenium_element import ElementMixin
from Enum.wait_strategy import WaitStrategy
from Utils.log_utils import LoggerManager

logger = LoggerManager().get_logger()


class KeywordMixin(ElementMixin):
    """ 关键字驱动(该模块的操作方法均需经过 element 模块, 否则容易出现元素过时异常) """
    def __init__(self, driver: WebDriver, locators: Dict[str, str]):
        # 初始化 locator 与 driver
        super().__init__(driver, locators)
        # self.mouse_op = MouseAction(driver, locators)

    # ================================ 工具：定位器索引化 ================================
    # noinspection PyMethodMayBeStatic
    def _index_locator(self, locator: Tuple[str, str], index: int) -> Tuple[str, str]:
        """ 根据基础 locator(一组) 生成 "指向第 index 个匹配项" 的新定位器

        :param locator: 形如 (By, value) 的定位器
        :param index: 目标索引 (下标从 0 开始)
        :return: Tuple[str, str] -> 新的 (By, value) 定位器, 指向第 index 个匹配元素
        """
        by, value = locator
        if index < 0:
            # 负索引需先知道长度, 但此处仅生成 locator, 不取 DOM 元素
            # 所以需要调用方先用 get_elements_by_keyword 拿长度再转正索引传进来
            raise ValueError("请传入非负数 index, 如需 -1, 需计算长度后再转换为正索引")
        # DOM元素下标从 1 开始, 而不是从 0 开始
        return By.XPATH, f"({value})[{index + 1}]"

    # ================================ 基础操作(获取元素、单级/多级点击、输入、获取文本) ================================
    def get_element_by_keyword(
        self,
        keyword: str,
        *args,
        wait_strategy: WaitStrategy = WaitStrategy.VISIBLE,
        **kw
    ) -> WebElement:
        """ 根据关键字获取单个稳定元素

        :param keyword: 关键字名称, 定位器来源; 到 _locator 中取定位器
        :param args: 用于格式化定位器字符串中的占位符 (如 "//div[text()='{}']")
        :param wait_strategy: 等待策略, 默认 VISIBLE(可见元素)
        :param kw:
                1. 等待配置: timeout, poll_frequency, ignored_exceptions
                2. 条件参数(该方法不需要): 传递给 WAIT_REGISTRY[EC模块方法所需参数] 的 required 关键字, 如 text/attribute/element 等
        :return: WebElement -> 返回所定位的元素, 超时抛 TimeoutException
        """
        locator_str = self._format_locator(keyword, *args)
        return self.wait(locator_str, wait_strategy, **kw)

    def get_elements_by_keyword(
        self, keyword: str,
        *args,
        wait_strategy: WaitStrategy = WaitStrategy.VISIBLE_ALL,
        **kw
    ) -> List[WebElement]:
        """ 获取一组符合 locator 的元素:
                1. 默认获取所有匹配元素是 可见的;
                2. 如需 "立即返回不等待", 不管是否可见, 用 GET_ALL 策略

        :param keyword: 关键字名称, 定位器来源
        :param args: 用于格式化定位器字符串中的占位符 (如 "//div[text()='{}']")
        :param wait_strategy: 等待策略, 默认 VISIBLE_ALL(可见元素)
        :param kw:
                1. 等待配置: timeout, poll_frequency, ignored_exceptions
                2. 条件参数(该方法不需要): 传递给 WAIT_REGISTRY[EC模块方法所需参数] 的 required 关键字, 如 text/attribute/element 等
        :return: List[WebElement] -> 返回一组所定位的元素, 超时抛 TimeoutException
        """
        locator_str = self._format_locator(keyword, *args)
        return self.wait(locator_str, wait_strategy, **kw)

    def get_elements_len(
        self,
        keyword: str,
        *args,
        wait_strategy: WaitStrategy = WaitStrategy.GET_ALL,
        **kw,
    ) -> int:
        """ 获取匹配元素的个数(不论是否可见)

        :param keyword: 关键字名称, 定位器来源
        :param args: 用于格式化定位器字符串中的占位符 (如 "//div[text()='{}']")
        :param wait_strategy: 等待策略, 默认 GET_ALL
        :param kw: 等待配置: timeout, poll_frequency, ignored_exceptions
        :return: int -> 返回定位器元素的个数, 若不存在则返回 0
        """
        return len(self.get_elements_by_keyword(keyword, *args, wait_strategy, **kw))

    def click_by_keyword(self, keyword: str, *args, **kw) -> bool:
        """ 根据关键字从映射中取出定位器, 支持单级和多级点击, 也支持参数化 (点击策略统一为 CLICKABLE)

        :param keyword: 关键字名称, 定位器来源
        :param args: 用于格式化定位器字符串中的占位符 (如 "//div[text()='{}']")
        :param kw:
                1. 等待配置: timeout, poll_frequency, ignored_exceptions
                2. 条件参数(该方法不需要): 传递给 WAIT_REGISTRY[EC模块方法所需参数] 的 required 关键字, 如 text/attribute/element 等
        :return: boolean -> 点击成功返回 True; 失败抛 TimeoutException
        """
        # 获取 keyword 映射的 value
        locator_str = self._format_locator(keyword, *args)

        if isinstance(locator_str, list):
            # 多级点击
            for locator in locator_str:
                self.click(locator, **kw)
            return True
        else:
            # 单级点击
            return self.click(locator_str, **kw)

    def click_each_variant_by_keyword(self, keyword: str, fmt_list: list, **kw):
        """ 针对同一个定位器, 根据不同的参数进行点击

        :param keyword: 关键字名称, 定位器来源
        :param fmt_list: 一组格式化参数
        :return:
        """
        for fmt in fmt_list:
            self.click_by_keyword(keyword, fmt, **kw)

    def click_slice_by_keyword(
        self,
        keyword: str,
        *args,
        get_wait_strategy: WaitStrategy = WaitStrategy.VISIBLE_ALL,
        click_wait_strategy: WaitStrategy = WaitStrategy.CLICKABLE,
        slice_str: str = ":",
        **kw
    ) -> bool:
        """ 按照 Python切片格式点击一组元素

        :param keyword: 关键字名称, 定位器来源
        :param args: 用于格式化定位器字符串中的占位符 (如 "//div[text()='{}']")
        :param get_wait_strategy: 获取元素等待策略, 默认 VISIBLE_ALL(所有可见元素)
        :param click_wait_strategy: 点击元素等待策略, 默认 CLICKABLE(可点击元素)
        :param slice_str: Python 切片格式字符串(默认选中所有元素), 如
                          "1:5:2" -> 从索引 1 开始到 5 结束, 步长为 2
                          "::2" -> 所有元素, 步长为 2
                          "-3" -> 倒数第三个元素
                          ":" -> 所有元素
                          "5" -> 只点击索引为 5 的元素
        :param kw: 等待配置: timeout, poll_frequency, ignored_exceptions
        :return: bool -> 操作成功返回 True, 失败返回 False
        """
        # 获取原始定位器, 若是一组匹配元素定位器, 后续根据下标来点击
        locator_str = self._format_locator(keyword, *args)

        # 获取所有匹配元素
        els = self.get_elements_by_keyword(keyword, *args, wait_strategy=get_wait_strategy, **kw)
        length = len(els)

        if not els:
            logger.warning(f"未找到任何匹配的元素, 定位器: {keyword}")
            return False

        try:
            # 解析字符串
            if ':' not in slice_str:
                # 单个索引情况
                index = int(slice_str)
                indices = [index]  # 统一成可迭代序列
            else:
                # 切片格式情况
                parts = slice_str.split(':')
                start = int(parts[0]) if parts[0] else None
                stop = int(parts[1]) if len(parts) > 1 and parts[1] else None
                step = int(parts[2]) if len(parts) > 2 and parts[2] else None
                slice_obj = slice(start, stop, step)

                # 用 range 先得到下标序列如: 0, 1, 2, ..., length-1, 再通过 slice_obj 对该序列进行切片
                # 注: 对 range 作切片依然返回 range 序列
                indices = range(length)[slice_obj]

            # 若切片为空, 或不符合格式(如: "10:5" 或 "::")
            if not indices:
                logger.warning(f"切片 {slice_str} 未选择任何元素")
                return False

            # 对选中的元素执行点击操作
            for i in indices:
                try:
                    if i < 0:
                        # 处理负索引
                        i += length
                    # 边界检查
                    if 0 <= i < length:
                        # 为每个索引位置创建新的定位器
                        indexed_locator = self._index_locator(locator_str, i)
                        self.click(indexed_locator, wait_strategy=click_wait_strategy, **kw)
                    else:
                        logger.warning(f"索引 {i} 超出范围 [0, {length - 1}]")
                except Exception as e:
                    logger.error(f"点击索引 {i} 的元素时出错: {str(e)}")
                    raise

            return True
        except (ValueError, IndexError) as e:
            logger.error(f"切片字符串 '{slice_str}' 格式错误或索引超出范围: {str(e)}")
            raise ValueError(f"切片字符串 '{slice_str}' 格式错误") from e
        except Exception as e:
            # 其他未知异常, 透传给调用方
            logger.error(f"执行切片点击操作时出错：{str(e)}")
            raise

    def click_times_by_keyword(
        self,
        keyword: str,
        *args,
        times: int,
        interval: float = 0.0,
        wait_strategy: WaitStrategy = WaitStrategy.CLICKABLE,
        **kw
    ) -> bool:
        """
          重复点击同一元素 times 次
        :param keyword: 关键字名称, 定位器来源
        :param args: 用于格式化定位器字符串中的占位符 (如 "//div[text()='{}']")
        :param times: 点击次数
        :param interval: 点击间隔
        :param wait_strategy: 点击元素等待策略, 默认 CLICKABLE(可点击元素)
        :param kw: 等待配置: timeout, poll_frequency, ignored_exceptions
        :return: boolean -> 点击成功返回 True; 失败抛 TimeoutException
        """
        if times <= 0:
            raise ValueError("times 需要合法")

        locator_str = self._format_locator(keyword, *args)
        for i in range(times):
            self.click(locator_str, wait_strategy=wait_strategy, **kw)

            if interval:
                time.sleep(interval)

        return True

    def input_by_keyword(
        self,
        keyword: str,
        *args,
        value: Optional[str] = None,
        **kw
    ) -> bool:
        """ 根据关键字对元素输入内容 或针对 <input type="file"> 上传文件

        :param keyword: 关键字名称, 定位器来源
        :param args: 用于格式化定位器字符串中的占位符 (如 "//div[text()='{}']")
        :param value: 输入的文本内容 或 需要上传的文件路径
        :param kw:
                1. 等待配置: timeout, poll_frequency, ignored_exceptions
                2. 条件参数(该方法不需要): 传递给 WAIT_REGISTRY[EC模块方法所需参数] 的 required 关键字, 如 text/attribute/element 等
        :return: boolean -> 输入成功返回 True; 失败抛 TimeoutException
        """
        locator_str = self._format_locator(keyword, *args)
        return self.send_keys(locator_str, value, **kw)

    def clear_and_input_by_keyword(
        self,
        keyword: str,
        *args,
        value: Optional[str] = None,
        **kw
    ) -> bool:
        """ 点击输入框, 清空输入框, 向输入框输入内容

        :param keyword: 关键字名称, 定位器来源
        :param args: 用于格式化定位器字符串中的占位符 (如 "//div[text()='{}']")
        :param value: 输入的文本内容
        :param kw:
                1. 等待配置: timeout, poll_frequency, ignored_exceptions
                2. 条件参数(该方法不需要): 传递给 WAIT_REGISTRY[EC模块方法所需参数] 的 required 关键字, 如 text/attribute/element 等
        :return: boolean -> 点击成功返回 True; 失败抛 TimeoutException
        """
        locator_str = self._format_locator(keyword, *args)
        self.click(locator_str, **kw)
        self.clear(locator_str, **kw)
        return self.send_keys(locator_str, value, **kw)

    def get_text_by_keyword(
        self,
        keyword: str,
        *args,
        mode: Literal['first', 'all'] = 'first',
        strip: bool = False,
        **kw
    ) -> Union[str, List[str]]:
        """ 根据关键字定位器获取元素的文本, 支持返回单个或文本列表

        :param keyword: 关键字名称, 定位器来源
        :param args: 用于格式化定位器字符串中的占位符 (如 "//div[text()='{}']")
        :param mode:
                - 'first': 只取一个文本(等待元素可见后获取)
                - 'all': 获取所有匹配元素文本(等待所有元素可见)
        :param strip: 是否对文本做 strip() 去首尾空白, 默认 False
        :param kw: 等待配置: timeout, poll_frequency, ignored_exceptions
        :return: Union[str, List[str]] -> 一个文本 或 一组文本
        """
        locator_str = self._format_locator(keyword, *args)

        if mode == 'first':
            txt = self.get_text(locator_str, **kw)
            return txt.strip() if strip else txt

        if mode == 'all':
            els = self.wait(locator_str, WaitStrategy.VISIBLE_ALL, **kw)
            return [el.text.strip() if strip else el.text for el in els]

    def get_dom_attribute_by_keyword(
        self,
        keyword: str,
        *args,
        wait_strategy: WaitStrategy = WaitStrategy.VISIBLE,
        attribute: Optional[str] = None,
        **kw
    ) -> str:
        """ 获取元素的 dom 属性值, 一般用于断言页面属性值发生变化

        :param keyword: 关键字名称, 定位器来源
        :param args: 用于格式化定位器字符串中的占位符 (如 "//div[text()='{}']")
        :param wait_strategy: 等待策略, 默认 VISIBLE(可见元素)
        :param attribute: 元素属性名 (如 <div id="u" type="text"> 中的 id、type)
        :param kw: 等待配置: timeout, poll_frequency, ignored_exceptions
        :return: str -> 元素 dom 属性名对应的值
        """
        locator_str = self._format_locator(keyword, *args)
        return self.get_dom_attribute(locator_str, attribute, wait_strategy=wait_strategy, **kw)

    def get_property_by_keyword(
        self,
        keyword: str,
        *args,
        wait_strategy: WaitStrategy = WaitStrategy.VISIBLE,
        property_name: Optional[str] = None,
        **kw
    ) -> Union[str, bool, WebElement, dict]:
        """ 获取元素的 DOM property（运行时属性）值, 本质是获取 CSSStyleDeclaration 对象

        :param keyword: 关键字名称, 定位器来源
        :param args: 用于格式化定位器字符串中的占位符 (如 "//div[text()='{}']")
        :param wait_strategy: 等待策略, 默认 VISIBLE(可见元素)
        :param property_name: 元素属性名 (如 <div id="u" type="text"> 中的 id、type)
        :param kw: 等待配置: timeout, poll_frequency, ignored_exceptions
        :return: Union[str, bool, WebElement, dict] -> 元素属性名对应的属性值
        """
        locator_str = self._format_locator(keyword, *args)
        return self.get_property(locator_str, property_name, wait_strategy=wait_strategy, **kw)

    def get_value_of_css_property_by_keyword(
        self,
        keyword: str,
        *args,
        wait_strategy: WaitStrategy = WaitStrategy.VISIBLE,
        css_property: Optional[str] = None,
        **kw
    ) -> str:
        """ 返回元素指定 CSS 属性的 "计算后样式" 值

        :param keyword: 关键字名称, 定位器来源
        :param args: 用于格式化定位器字符串中的占位符 (如 "//div[text()='{}']")
        :param wait_strategy: 等待策略, 默认 VISIBLE(可见元素)
        :param css_property: CSS属性名 (如 <div style="right: auto;display: block;"> style 中的 right、display)
        :param kw: 等待配置: timeout, poll_frequency, ignored_exceptions
        :return: str -> CSS 属性对应的值
        """
        locator_str = self._format_locator(keyword, *args)
        return self.get_value_of_css_property(locator_str, css_property, wait_strategy=wait_strategy, **kw)

    def scrolled_and_get_location_by_keyword(
        self,
        keyword: str,
        *args,
        **kw
    ) -> dict:
        """ 先将可见元素滚到可视区，然后返回可见元素外接矩形左上角坐标

        :param keyword: 关键字名称, 定位器来源
        :param args: 用于格式化定位器字符串中的占位符 (如 "//div[text()='{}']")
        :param kw: 等待配置: timeout, poll_frequency, ignored_exceptions
        :return: dict -> 元素左上角原点坐标 {"x": int, "y": int} (CSS像素)
        """
        locator_str = self._format_locator(keyword, *args)
        return self.scrolled_into_view_and_get_location(locator_str, **kw)

    def get_rect_by_keyword(
        self,
        keyword: str,
        *args,
        **kw
    ) -> dict:
        """ 一次性返回可见元素的几何信息(坐标, 尺寸)

        :param keyword: 关键字名称, 定位器来源
        :param args: 用于格式化定位器字符串中的占位符 (如 "//div[text()='{}']")
        :param kw: 等待配置: timeout, poll_frequency, ignored_exceptions
        :return: dict -> 元素左上角原点坐标(x, y), 尺寸(width, height) {"x": int, "y": int, "width": int, "height": int} (CSS像素)
        """
        locator_str = self._format_locator(keyword, *args)
        return self.get_rect(locator_str, **kw)

    def screenshot_element_by_keyword(
        self,
        keyword: str,
        *args,
        filename: Optional[str] = None,
        **kw
    ) -> bool:
        """ 把 该元素可视区域 的 PNG 截图直接保存到文件(注: 元素必须在可视区域, 若只有一部分可视则无法截取全貌)

        :param keyword: 关键字名称, 定位器来源
        :param args: 用于格式化定位器字符串中的占位符 (如 "//div[text()='{}']")
        :param filename: 文件保存路径
        :param kw: 等待配置: timeout, poll_frequency, ignored_exceptions
        :return: bool -> 成功返回 True; 反之返回 False
        """
        if filename is None:
            raise ValueError("无文件保存路径")
        locator_str = self._format_locator(keyword, *args)
        return self.screenshot_element(locator_str, filename, **kw)

    def switch_iframe_by_keyword(
        self,
        keyword: str,
        *args,
        wait_strategy: WaitStrategy = WaitStrategy.IFRAME_SWITCH,
        **kw
    ) -> bool:
        """ 切换iframe, 支持单级切换/多级连续切换

        :param keyword: 关键字名称, 定位器来源
        :param args: 用于格式化定位器字符串中的占位符 (如 "//div[text()='{}']")
        :param wait_strategy: 等待策略, 仅能使用 IFRAME_SWITCH
        :param kw: 等待配置: timeout, poll_frequency, ignored_exceptions
        :return: bool -> 成功返回 True; 超时抛 TimeoutException
        """
        locator_str = self._format_locator(keyword, *args)

        if isinstance(locator_str, list):
            # 多级切换
            for locator in locator_str:
                self.wait(locator, wait_strategy, **kw)
            return True
        else:
            # 单级切换
            return self.wait(locator_str, wait_strategy, **kw)

    def switch_default_iframe(
        self,
        wait_strategy: WaitStrategy = WaitStrategy.DEFAULT_IFRAME_SWITCH,
        **kw
    ) -> bool:
        """ 切换回默认iframe

        :param wait_strategy: 等待策略, 仅能使用 DEFAULT_IFRAME_SWITCH
        :param kw: 等待配置: timeout, poll_frequency, ignored_exceptions
        :return: bool -> 成功返回 True; 超时抛 TimeoutException
        """
        return self.wait(WaitStrategy.IGNORED_LOCATOR, wait_strategy, **kw)

    def switch_parent_iframe(
        self,
        wait_strategy: WaitStrategy = WaitStrategy.PARENT_IFRAME_SWITCH,
        **kw
    ) -> bool:
        """ 切换回父级iframe, 如果当前iframe为顶级, 则保持不变

        :param wait_strategy: 等待策略, 仅能使用 PARENT_IFRAME_SWITCH
        :param kw: 等待配置: timeout, poll_frequency, ignored_exceptions
        :return: bool -> 成功返回 True; 超时抛 TimeoutException
        """
        return self.wait(WaitStrategy.IGNORED_LOCATOR, wait_strategy, **kw)

    # ================================ 偏断言类操作 ================================
    def is_text_present_by_keyword(
        self,
        keyword: str,
        *args,
        wait_strategy: WaitStrategy = WaitStrategy.PRESENT_TEXT_IN_ELEMENT,
        expected_text: Optional[str] = None,
        **kw
    ) -> bool:
        """ 判断 expect_text 是否存在于匹配元素的 .text 中, 是返回 True, 否则返回 False

        :param keyword: 关键字名称, 定位器来源
        :param args: 用于格式化定位器字符串中的占位符 (如 "//div[text()='{}']")
        :param wait_strategy: 等待策略, 仅能使用 PRESENT_TEXT_IN_ELEMENT
        :param expected_text: 期望存在的文本
        :param kw: 等待配置: timeout, poll_frequency, ignored_exceptions
        :return: bool -> expect_text 存在于 locator.text 返回True, 反之返回False

        注: 该方法适用于前端先加载DOM再加载文本的场景
        """
        # 获取定位器并格式化
        locator_str = self._format_locator(keyword, *args)
        return self.wait(locator_str, wait_strategy, text=expected_text, **kw)

    def is_text_in_element_attribute_by_keyword(
        self,
        keyword: str,
        *args,
        wait_strategy: WaitStrategy = WaitStrategy.PRESENT_TEXT_IN_ELEMENT_ATTRIBUTE,
        attribute: str,
        text: str,
        **kw
    ) -> bool:
        """ 判断 text 是否存在于匹配元素的 attribute 中, 存在返回 True, 反之返回 False

        :param keyword: 关键字名称, 定位器来源
        :param args: 用于格式化定位器字符串中的占位符 (如 "//div[text()='{}']")
        :param wait_strategy: 等待策略, 仅能使用 PRESENT_TEXT_IN_ELEMENT_ATTRIBUTE
        :param attribute: 元素属性名
        :param text: 期望存在的属性值
        :param kw: 等待配置: timeout, poll_frequency, ignored_exceptions
        :return: bool -> text 存在于 attribute 中返回True, 反之返回False
        """
        locator_str = self._format_locator(keyword, *args)
        return self.wait(locator_str, wait_strategy, attribute=attribute, text=text, **kw)
