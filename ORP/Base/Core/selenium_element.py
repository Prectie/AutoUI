from dataclasses import dataclass
from typing import Literal, Callable, Any, Tuple, Optional, TypeVar, Dict, Union, List

from selenium.common import StaleElementReferenceException, ElementClickInterceptedException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from Base.Core import ec_extension as EC_ext
from Base.Core.locator_provider import LocatorMixin
from Enum.wait_strategy import WaitStrategy
from Utils.log_utils import LoggerManager

logger = LoggerManager().get_logger()

""" 限定返回类型 """
WaitMode = Literal["element", "elements", "bool"]

R = TypeVar("R")


@dataclass(frozen=True)
class WaitSpecification:
    """
    等待策略元数据
    - mode: 方法返回类型
    - binder: 把 locator(+必要参数) 绑定为 until 可用的 condition
    - required: 该等待类型必须提供的关键字参数 (严格校验)
    - timeout/poll/ignored: 此类型默认等待配置 (可被调用时参数覆盖)
    - msg: 文本描述(日志, 报错用)
    - needs_locator: 此策略的 binder 是否需要 locator 作为第一个参数
    """
    mode: WaitMode
    binder: Callable[..., Any]
    required: Tuple[str, ...] = ()
    timeout: Optional[int] = None
    poll: Optional[float] = None
    ignored: Optional[Tuple[type, ...]] = None
    msg: str = ""
    needs_locator: bool = True


# --- 等待 / 动作默认忽略的异常 ---
_DEFAULT_WAIT_IGNORED: Tuple[type, ...] = (StaleElementReferenceException,)
_DEFAULT_ACTION_IGNORED: Tuple[type, ...] = (
    StaleElementReferenceException,
    ElementClickInterceptedException,
)

WAIT_REGISTRY: Dict[WaitStrategy, WaitSpecification] = {
    # 返回值为 element
    WaitStrategy.VISIBLE: WaitSpecification(
        mode="element",
        binder=lambda locator: EC.visibility_of_element_located(locator),
        msg="element visible for user"
    ),
    WaitStrategy.VISIBLE_ALL: WaitSpecification(
        mode="elements",
        binder=lambda locator: EC.visibility_of_all_elements_located(locator),
        msg="all elements visible for user"
    ),
    WaitStrategy.CLICKABLE: WaitSpecification(
        mode="element",
        binder=lambda locator: EC.element_to_be_clickable(locator),
        msg="element clickable(visible and enable)"
    ),
    WaitStrategy.PRESENCE: WaitSpecification(
        mode="element",
        binder=lambda locator: EC.presence_of_element_located(locator),
        msg="element present in DOM"
    ),

    # 返回 bool
    WaitStrategy.INVISIBLE: WaitSpecification(
        mode="bool",
        binder=lambda locator: EC.invisibility_of_element_located(locator),
        msg="element invisible"
    ),
    WaitStrategy.PRESENT_TEXT_IN_ELEMENT: WaitSpecification(
        mode="bool",
        binder=lambda locator, *, text: EC.text_to_be_present_in_element(locator, text),
        required=("text",),
        msg="text present in element text"
    ),
    WaitStrategy.PRESENT_TEXT_IN_ELEMENT_ATTRIBUTE: WaitSpecification(
        mode="bool",
        binder=lambda locator, *, attribute, text: EC.text_to_be_present_in_element_attribute(locator, attribute, text),
        required=("attribute", "text"),
        msg="text present in element attribute"
    ),
    WaitStrategy.WAIT_STALENESS: WaitSpecification(
        mode="bool",
        binder=lambda *, element: EC.staleness_of(element),
        required=("element",),
        msg="element need stale",
        needs_locator=False
    ),
    WaitStrategy.IFRAME_SWITCH: WaitSpecification(
        mode="bool",
        binder=lambda locator: EC.frame_to_be_available_and_switch_to_it(locator),
        msg="switch to iframe"
    ),
    WaitStrategy.DEFAULT_IFRAME_SWITCH: WaitSpecification(
        mode="bool",
        binder=lambda _: EC_ext.default_frame_to_be_available_and_switch_to_it(),
        msg="switch to default iframe",
        needs_locator=False
    ),
    WaitStrategy.PARENT_IFRAME_SWITCH: WaitSpecification(
        mode="bool",
        binder=lambda _: EC_ext.parent_frame_to_be_available_and_switch_to_it(),
        msg="switch to parent iframe",
        needs_locator=False
    ),
    WaitStrategy.NUMBER_OF_WINDOWS_TO_BE: WaitSpecification(
        mode="bool",
        binder=lambda num_window: EC.number_of_windows_to_be(num_window),
        required=("num_window",),
        msg="窗口数未达到预期",
        needs_locator=False
    ),
    WaitStrategy.NEW_WINDOW_IS_OPENED: WaitSpecification(
        mode="bool",
        binder=lambda current_handles: EC.new_window_is_opened(current_handles),
        required=("current_handles",),
        msg="未检测到新窗口打开",
        needs_locator=False
    ),
}


# 从注册表里取策略
def _spec_of(find_type: WaitStrategy) -> WaitSpecification:
    try:
        return WAIT_REGISTRY[find_type]
    except KeyError:
        raise ValueError(f"没有对应策略：{find_type}")


class ElementMixin(LocatorMixin):
    """
    统一等待与动作重试的 Mixin (二次封装常用的EC模块以及webelement模块)
    依赖: self.driver (Selenium WebDriver 实例)
    """
    # 默认值
    default_timeout: int = 8  # 最大等待时间
    default_poll: float = 0.5  # 每轮轮询时间
    default_wait_ignored = _DEFAULT_WAIT_IGNORED  # wait() 默认忽略的异常
    default_action_ignored = _DEFAULT_ACTION_IGNORED  # action() 默认忽略的异常

    def __init__(self, driver: WebDriver, locators: Dict[str, str]):
        # 初始化 locator 与 driver
        super().__init__(locators)
        # 由 ElementMixin 管理 driver
        self._driver = driver

    # ================================ 入口 ================================
    def wait(self,
             locator: Union[Tuple[str, str], WaitStrategy],
             wait_strategy: WaitStrategy = WaitStrategy.VISIBLE,
             *,
             timeout: Optional[int] = None,
             poll_frequency: Optional[float] = None,
             ignored_exceptions: Optional[Tuple[type, ...]] = None,
             **cond_kwargs,
             ) -> Union[WebElement, List[WebElement], bool]:
        """ 等待所选择的策略条件成立

        :param locator: 元素定位器
        :param wait_strategy: 选择等待策略(具体见 Enum/wait_strategy.py)
        :param timeout: 最大等待时间, 单位为秒
        :param poll_frequency: 每轮轮询时间
        :param ignored_exceptions: 轮询过程中需要忽略的异常
        :param cond_kwargs: 条件参数(例如 text/attribute) 与 locator 格式化无关
        :return: 元素类返回 WebElement / List[WebElement]; 布尔类返回 bool; GET_ALL 直接返回一组元素(不等待)
        """
        # 专门处理 GET_ALL 不需要等待, 直接取元素
        if wait_strategy == WaitStrategy.GET_ALL:
            if cond_kwargs:
                raise TypeError(f"[wait] GET_ALL 不接受额外参数, 收到: {sorted(cond_kwargs.keys())}")
            return self._driver.find_elements(*locator)

        # 取策略
        spec = _spec_of(wait_strategy)

        # 参数校验
        provided = set(cond_kwargs.keys())
        required = set(spec.required)
        missing = required - provided
        if missing:
            raise TypeError(f"策略: '{wait_strategy}' —— 参数传递错误: 缺失参数 '{spec.msg}': {sorted(missing)}")
        extra = provided - required
        if extra:
            raise TypeError(f"策略: '{wait_strategy}' —— 参数传递错误: 多余参数传入 '{spec.msg}': {sorted(extra)}")

        # 更改默认值(若需要)
        eff_timeout = timeout if timeout is not None else (spec.timeout or self.default_timeout)
        eff_poll = poll_frequency if poll_frequency is not None else (spec.poll or self.default_poll)
        eff_ignored = ignored_exceptions or spec.ignored or self.default_wait_ignored

        # 绑定 EC 条件并等待
        if spec.needs_locator:
            condition = spec.binder(locator, **cond_kwargs)
            msg_tail = f": 定位器信息 '{locator}'"
        else:
            condition = spec.binder(**cond_kwargs)
            msg_tail = f": 该方法不需要定位器; 或出现其他错误, 请调试或检查日志"

        return WebDriverWait(
            driver=self._driver,
            timeout=eff_timeout,
            poll_frequency=eff_poll,
            ignored_exceptions=eff_ignored,
        ).until(condition, message=f"'{spec.msg}' 条件超时, 具体信息{msg_tail}")

    # ================================ 动作统一入口 ================================
    def _until_action(
        self,
        locator: Tuple[str, str],
        wait_strategy: WaitStrategy,
        action: Callable[[WebElement], None],
        *,
        timeout: Optional[int] = None,
        poll_frequency: Optional[float] = None,
        ignored_exceptions: Optional[Tuple[type, ...]] = None,
        **cond_kwargs,
    ) -> bool:
        """ 每次重试: 先 wait() 拿稳定元素, 再执行 action(element) 操作

        :param locator: 元素定位器
        :param wait_strategy: 选择等待策略(具体见 Enum/wait_strategy.py)
        :param action: 具体动作函数逻辑, 该函数需要传入 WebElement 参数, 返回值为 None
        :param timeout: 最大等待时间
        :param poll_frequency: 每轮轮询时间
        :param ignored_exceptions: 轮询过程中需要忽略的异常
        :param cond_kwargs: 条件参数(例如 text/attribute) 与 locator 格式化无关
        :return: boolean -> 返回 True 说明动作成功执行(失败抛出超时异常)
        """
        # 取策略
        spec = _spec_of(wait_strategy)
        # 更改默认值(若需要)
        eff_timeout = timeout if timeout is not None else (spec.timeout or self.default_timeout)
        eff_poll = poll_frequency if poll_frequency is not None else (spec.poll or self.default_poll)
        eff_ignored = ignored_exceptions or spec.ignored or self.default_wait_ignored

        # 内部函数, 执行 action
        def attempt(_driver: WebDriver) -> bool:
            el = self.wait(locator, wait_strategy, timeout=eff_timeout, poll_frequency=eff_poll, **cond_kwargs)
            try:
                action(el)
                return True
            except eff_ignored:
                return False

        return WebDriverWait(
            driver=self._driver,
            timeout=eff_timeout,
            poll_frequency=eff_poll,
            ignored_exceptions=eff_ignored,
        ).until(attempt, message=f"action 失败, 名称为: {action.__name__} (定位器信息：{locator}, 描述: {spec.msg})")

    def _until_action_return(
        self,
        locator: Tuple[str, str],
        wait_strategy: WaitStrategy,
        action: Callable[[WebElement], R],
        *,
        timeout: Optional[int] = None,
        poll_frequency: Optional[float] = None,
        ignored_exceptions: Optional[Tuple[type, ...]] = None,
        **cond_kwargs,
    ) -> R:
        """ 每次重试: 先 wait() 拿稳定元素, 再执行 action(element) 操作

        :param locator: 元素定位器
        :param wait_strategy: 选择等待策略(具体见 Enum/wait_strategy.py)
        :param action: 该函数需要传入 WebElement 参数, 带有返回值(如 text, attribute)
        :param timeout: 最大等待时间
        :param poll_frequency: 每轮轮询时间
        :param ignored_exceptions: 轮询过程中需要忽略的异常
        :param cond_kwargs: 条件参数(例如 text/attribute) 与 locator 格式化无关
        :return: R -> 返回 action() 的返回值(失败抛出超时异常)
        """
        # 取策略
        spec = _spec_of(wait_strategy)
        # 更改默认值(若需要)
        eff_timeout = timeout if timeout is not None else (spec.timeout or self.default_timeout)
        eff_poll = poll_frequency if poll_frequency is not None else (spec.poll or self.default_poll)
        eff_ignored = ignored_exceptions or spec.ignored or self.default_wait_ignored

        result = None

        # 内部函数, 执行 action
        def attempt(_driver: WebDriver) -> bool:
            nonlocal result
            el = self.wait(locator, wait_strategy, timeout=eff_timeout, poll_frequency=eff_poll, **cond_kwargs)
            try:
                result = action(el)
                return True
            except eff_ignored:
                return False

        WebDriverWait(
            driver=self._driver,
            timeout=eff_timeout,
            poll_frequency=eff_poll,
            ignored_exceptions=eff_ignored,
        ).until(attempt, message=f"action-return 失败, 名称为: {action.__name__} (定位器信息：{locator}, 描述: {spec.msg})")
        return result

    # ==================================== 对外基础动作(封装webelement模块) ====================================
    def click(
        self,
        locator: Tuple[str, str],
        *,
        wait_strategy: WaitStrategy = WaitStrategy.CLICKABLE,
        **kw
    ) -> bool:
        """ 执行点击操作

        :param locator: 元素定位器
        :param wait_strategy: 等待策略, 默认 CLICKABLE
        :param kw:
                1. 等待配置: timeout, poll_frequency, ignored_exceptions
                2. 条件参数(该方法不需要): 传递给 WAIT_REGISTRY[EC模块方法所需参数] 的 required 关键字, 如 text/attribute/element 等
        :return: boolean -> 操作成功返回 True, 超时抛 TimeoutException
        """
        return self._until_action(locator, wait_strategy, lambda el: el.click(), **kw)

    def send_keys(
        self,
        locator: Tuple[str, str],
        text: str,
        *,
        wait_strategy: WaitStrategy = WaitStrategy.CLICKABLE,
        **kw
    ) -> bool:
        """ 执行输入操作

        :param locator: 元素定位器
        :param text: 要输入的文本
        :param wait_strategy: 等待策略, 默认 CLICKABLE
        :param kw:
                1. 等待配置: timeout, poll_frequency, ignored_exceptions
                2. 条件参数(该方法不需要): 传递给 WAIT_REGISTRY[EC模块方法所需参数] 的 required 关键字, 如 text/attribute/element 等
        :return: boolean -> 操作成功返回 True, 超时抛 TimeoutException
        """
        # logger.info(f"[Core::selenium_element.py] send_keys 接收到的文本为: '{text}'")
        return self._until_action(locator, wait_strategy, lambda el: el.send_keys(text), **kw)

    def clear(
        self,
        locator: Tuple[str, str],
        *,
        wait_strategy: WaitStrategy = WaitStrategy.CLICKABLE,
        **kw
    ) -> bool:
        """ 执行清空输入框操作

        :param locator: 元素定位器
        :param wait_strategy: 等待策略, 默认 CLICKABLE
        :param kw:
                1. 等待配置: timeout, poll_frequency, ignored_exceptions
                2. 条件参数(该方法不需要): 传递给 WAIT_REGISTRY[EC模块方法所需参数] 的 required 关键字, 如 text/attribute/element 等
        :return: boolean -> 操作成功返回 True, 超时抛 TimeoutException
        """
        return self._until_action(locator, wait_strategy, lambda el: el.clear(), **kw)

    def get_text(
        self,
        locator: Tuple[str, str],
        *,
        wait_strategy: WaitStrategy = WaitStrategy.VISIBLE,
        **kw
    ) -> str:
        """ 获取元素的文本信息

        :param locator: 元素定位器
        :param wait_strategy: 等待策略, 默认 VISIBLE
        :param kw:
                1. 等待配置: timeout, poll_frequency, ignored_exceptions
                2. 条件参数(该方法不需要): 传递给 WAIT_REGISTRY[EC模块方法所需参数] 的 required 关键字, 如 text/attribute/element 等
        :return: str -> 元素的文本信息
        """
        return self._until_action_return(locator, wait_strategy, lambda el: el.text, **kw)

    def get_dom_attribute(
        self,
        locator: Tuple[str, str],
        attribute: str,
        *,
        wait_strategy: WaitStrategy = WaitStrategy.VISIBLE,
        **kw
    ) -> str:
        """ 获取 HTML 标签上声明的属性值，也就是 "源码里是什么就读什么"

        :param locator: 元素定位器
        :param attribute: 属性名, 如 <input style="display: none"> 中的 style 即属性名
        :param wait_strategy: 等待策略, 默认 VISIBLE
        :param kw:
                1. 等待配置: timeout, poll_frequency, ignored_exceptions
                2. 条件参数(该方法不需要): 传递给 WAIT_REGISTRY[EC模块方法所需参数] 的 required 关键字, 如 text/attribute/element 等
        :return: str -> 属性名对应的属性值, 如获取 style 返回 "display: none"; 不存在时返回 None
        """
        return self._until_action_return(locator, wait_strategy, lambda el: el.get_dom_attribute(attribute), **kw)

    def get_property(
        self,
        locator: Tuple[str, str],
        property_name: str,
        *,
        wait_strategy: WaitStrategy = WaitStrategy.VISIBLE,
        **kw
    ) -> Union[str, bool, WebElement, dict]:
        """ 获取元素的 DOM property（运行时属性）对象

        :param locator: 元素定位器
        :param property_name: 属性名, 如 <input style="display: none"> 中的 style 即属性名
        :param wait_strategy: 等待策略, 默认 VISIBLE
        :param kw:
                1. 等待配置: timeout, poll_frequency, ignored_exceptions
                2. 条件参数(该方法不需要): 传递给 WAIT_REGISTRY[EC模块方法所需参数] 的 required 关键字, 如 text/attribute/element 等
        :return: str | bool | WebElement | dict -> 返回 property 的实时动态值; 不存在时返回 None
        """
        return self._until_action_return(locator, wait_strategy, lambda el: el.get_property(property_name), **kw)

    def get_value_of_css_property(
        self,
        locator: Tuple[str, str],
        css_property: str,
        *,
        wait_strategy: WaitStrategy = WaitStrategy.VISIBLE,
        **kw
    ) -> str:
        """ 返回元素指定 CSS 属性的 "计算后样式" 值

        :param locator: 元素定位器
        :param css_property: CSS 属性名, 如 <input style="display: none"> 中的 display 即 CSS 属性名
        :param wait_strategy: 等待策略, 默认 VISIBLE
        :param kw:
                1. 等待配置: timeout, poll_frequency, ignored_exceptions
                2. 条件参数(该方法不需要): 传递给 WAIT_REGISTRY[EC模块方法所需参数] 的 required 关键字, 如 text/attribute/element 等
        :return: str -> 返回 CSS 属性值, 如获取 display 返回 "none"; 不存在时返回空字符串: ''
        """
        return self._until_action_return(locator, wait_strategy, lambda el: el.value_of_css_property(css_property), **kw)

    def scrolled_into_view_and_get_location(
        self,
        locator: Tuple[str, str],
        *,
        wait_strategy: WaitStrategy = WaitStrategy.VISIBLE,
        **kw
    ) -> dict:
        """ 先将元素滚到可视区，然后返回元素外接矩形左上角坐标

        :param locator: 元素定位器
        :param wait_strategy: 等待策略, 默认 VISIBLE
        :param kw:
                1. 等待配置: timeout, poll_frequency, ignored_exceptions
                2. 条件参数(该方法不需要): 传递给 WAIT_REGISTRY[EC模块方法所需参数] 的 required 关键字, 如 text/attribute/element 等
        :return: dict -> {"x": int, "y": int} (CSS像素)
        """
        return self._until_action_return(locator, wait_strategy, lambda el: el.location_once_scrolled_into_view, **kw)

    def get_rect(
        self,
        locator: Tuple[str, str],
        *,
        wait_strategy: WaitStrategy = WaitStrategy.VISIBLE,
        **kw
    ) -> dict:
        """ 元素的几何信息(坐标, 尺寸)一次性返回

        :param locator: 元素定位器
        :param wait_strategy: 等待策略, 默认 VISIBLE
        :param kw:
                1. 等待配置: timeout, poll_frequency, ignored_exceptions
                2. 条件参数(该方法不需要): 传递给 WAIT_REGISTRY[EC模块方法所需参数] 的 required 关键字, 如 text/attribute/element 等
        :return: dict：{"x": int, "y": int, "width": int, "height": int} (CSS像素)
        """
        return self._until_action_return(locator, wait_strategy, lambda el: el.rect, **kw)

    def screenshot_element(
        self,
        locator: Tuple[str, str],
        filename: str,
        *,
        wait_strategy: WaitStrategy = WaitStrategy.VISIBLE,
        **kw
    ) -> bool:
        """ 把 该元素可视区域 的 PNG 截图直接保存到文件

        :param locator: 元素定位器
        :param filename: 文件保存路径
        :param wait_strategy: 等待策略, 默认 VISIBLE
        :param kw:
                1. 等待配置: timeout, poll_frequency, ignored_exceptions
                2. 条件参数(该方法不需要): 传递给 WAIT_REGISTRY[EC模块方法所需参数] 的 required 关键字, 如 text/attribute/element 等
        :return: bool -> 成功返回 True; 反之返回 False
        """
        return self._until_action_return(locator, wait_strategy, lambda el: el.screenshot(filename), **kw)




