import time
from typing import Dict, Optional, List

from selenium.common import TimeoutException
from selenium.webdriver.chrome.webdriver import WebDriver


from Base.Core.selenium_element import ElementMixin, WaitStrategy
from Base.Facade.element_operator import KeywordMixin
from Utils.log_utils import LoggerManager

logger = LoggerManager().get_logger()


class WaitMixin(ElementMixin):
    """ 等待/同步相关 """
    def __init__(self, driver: WebDriver, locators: Dict[str, str]):
        # 初始化 locator 与 driver
        super().__init__(driver, locators)
        self.el_ops = KeywordMixin(driver, locators)

    # ================================ 通用等待操作 ================================
    def wait_attribute_value_presence_by_keyword(
        self,
        keyword: str,
        *arg,
        wait_strategy: WaitStrategy = WaitStrategy.PRESENT_TEXT_IN_ELEMENT_ATTRIBUTE,
        attribute: str,
        expected_value: str,
        **kw
    ) -> bool:
        """ 等待 属性值 出现在元素的 属性attribute 中

        :param keyword: 关键字名称, 定位器来源; 到 _locator 中取定位器
        :param arg: 用于格式化定位器字符串中的占位符 (如 "//div[text()='{}']")
        :param wait_strategy: 等待策略, 默认 PRESENT_TEXT_IN_ELEMENT_ATTRIBUTE (仅使用该策略)
        :param attribute: 属性
        :param expected_value: 期望存在于属性中的值
        :param kw: 等待配置: timeout, poll_frequency, ignored_exceptions
        :return: bool -> 操作成功返回 True, 失败返回 False
        """
        locator_str = self._format_locator(keyword, *arg)
        return self.wait(locator_str, wait_strategy, attribute=attribute, text=expected_value, **kw)

    def wait_element_stale_by_keyword(
        self,
        keyword: str,
        *args,
        wait_strategy: WaitStrategy = WaitStrategy.WAIT_STALENESS,
        **kw
    ):
        """ 等待元素从 DOM 中过时

        :param keyword: 关键字名称, 定位器来源
        :param args: 用于格式化定位器字符串中的占位符 (如 "//div[text()='{}']")
        :param wait_strategy: 等待策略, 默认 WAIT_STALENESS (仅使用该策略)
        :param kw: 等待配置: timeout, poll_frequency, ignored_exceptions
        :return: bool -> 操作成功返回 True, 失败返回 False
        """
        # 获取需要等待的元素
        stale_element = self.el_ops.get_element_by_keyword(keyword, *args)
        return self.wait(WaitStrategy.IGNORED_LOCATOR, wait_strategy, element=stale_element, **kw)

    def wait_new_window_is_opened(
        self,
        wait_strategy: WaitStrategy = WaitStrategy.NEW_WINDOW_IS_OPENED,
        current_handles: Optional[List[str]] = None,
        **kw
    ):
        """ 等待新窗口的打开

        :param wait_strategy: 等待策略, 默认 WAIT_STALENESS (仅使用该策略)
        :param current_handles: 当前窗口的所有句柄
        :param kw: 等待配置: timeout, poll_frequency, ignored_exceptions
        :return: bool -> 操作成功返回 True, 失败返回 False
        """
        return self.wait(WaitStrategy.IGNORED_LOCATOR, wait_strategy, current_handles=current_handles, **kw)

    # ================================ 偏业务等待操作 ================================
    def wait_until_result_stable(
        self,
        keyword: str,
        *args,
        wait_strategy: WaitStrategy = WaitStrategy.GET_ALL,
        wait_time: Optional[int] = 240,
        stable_duration: float = 3.0,
        interval: float = 1,
        **kw
    ):
        """
        等待结果文本在 N 秒内不再变化, 适用于大模型这种 streaming 输出场景

        :param keyword: 关键字名称, 定位器来源
        :param args: 用于格式化定位器字符串中的占位符 (如 "//div[text()='{}']")
        :param wait_strategy: 等待策略, 默认 VISIBLE_ALL (所有可见元素)
        :param wait_time: 最大等待时间, 单位为秒
        :param stable_duration: 判断 "稳定" 的持续时间, 默认 3 秒内无变化即认为稳定
        :param interval: 每轮检查的间隔时间, 单位为秒
        :param kw: 等待配置 timeout, poll_frequency, ignored_exceptions
        :return: bool -> 文本在 stable_duration 内未变化返回 True, 超时返回 False
        """
        end_time = time.time() + wait_time

        last_text = None  # 上一次采样到的文本
        last_change_ts = time.time()  # 上一次 文本发生变化 的时间

        while time.time() < end_time:
            # 每轮重新获取结果区域元素(支持多元素, 用 join 拼成一个整体文本)
            els = self.el_ops.get_elements_by_keyword(keyword, *args, wait_strategy=wait_strategy, **kw)

            if not els:
                logger.info(f"未找到关键字为 '{keyword}' 的元素, 等待下一轮")
                time.sleep(interval)
                continue

            current_text = "".join(el.text for el in els).strip()

            # 第一次 或 文本发生变化 -> 更新 last_text 和 last_change_ts
            if last_text is None or current_text != last_text:
                logger.info(f"'{keyword}' 文本发生变化, 长度 {len(current_text)}")
                last_text = current_text
                last_change_ts = time.time()
            else:
                # 文本和上次一样, 且持续 stable_duration 秒以上 -> 认为结果稳定
                if time.time() - last_change_ts >= stable_duration:
                    logger.info(f"关键字 '{keyword}' 文本在 {stable_duration}s 内未变化, 认为结果区域已稳定")
                    return True

            # 轮询间隔时间
            time.sleep(interval)

        logger.error(f"在 {wait_time}s 内, 关键字 '{keyword}' 文本始终未稳定")
        return False

    def wait_text_all_to_be_expected_text(
        self,
        keyword: str,
        *args,
        wait_strategy: WaitStrategy = WaitStrategy.VISIBLE_ALL,
        expected_text: str,
        wait_time: Optional[int] = 10,
        interval: Optional[float] = 0.4,
        **kw
    ) -> bool:
        """ 等待所有 keyword 对应的元素文本都变成 预期值

        :param keyword: 关键字名称, 定位器来源
        :param args: 用于格式化定位器字符串中的占位符 (如 "//div[text()='{}']")
        :param wait_strategy: 等待策略, 默认 VISIBLE_ALL (所有可见元素)
        :param expected_text: 预期值
        :param wait_time: 最大等待时间
        :param interval: 每次检查间隔时间
        :param kw: 等待配置: timeout, poll_frequency, ignored_exceptions
        :return: bool -> 操作成功返回 True, 失败返回 False
        """
        end_time = time.time() + wait_time

        while time.time() < end_time:
            # 1.每次都重新获取文件的状态
            els = self.el_ops.get_elements_by_keyword(keyword, *args, wait_strategy, **kw)
            if not els:
                # 如果列表还没渲染出来, 再等一轮
                time.sleep(interval)
                continue

            # 检查所有元素文本是否存在期望文本
            if all(el.text.strip() == expected_text for el in els):
                logger.info(f"所有元素文本都已变为预期值: {expected_text}")
                return True

            # 本轮检查未通过, 等待下一轮
            time.sleep(interval)

        error_msg = f"AssertionError: 在 {wait_time}s 内未检测到文件状态为完成"
        logger.error(error_msg)
        return False

