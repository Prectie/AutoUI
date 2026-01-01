import math
from typing import Dict, Optional

from selenium.webdriver import ActionChains, Keys

from Base.Core.selenium_element import ElementMixin
from selenium.webdriver.chrome.webdriver import WebDriver

from Base.Facade.element_operator import KeywordMixin
from Enum.wait_strategy import WaitStrategy
from Utils.log_utils import LoggerManager

logger = LoggerManager().get_logger()


class MouseAction(ElementMixin):
    def __init__(self, driver: WebDriver, locators: Dict[str, str]):
        # 初始化 locator 与 driver
        super().__init__(driver, locators)
        self.el_ops = KeywordMixin(driver, locators)

    def hover_and_click_by_keyword(
        self,
        keyword: str,
        *args,
        wait_strategy: WaitStrategy = WaitStrategy.VISIBLE,
        hover_time: float = 0.2,
        click_time: float = 0.1,
        **kw
    ) -> bool:
        """ 鼠标悬停到元素上并点击

        :param keyword: 关键字名称, 定位器来源
        :param args: 用于格式化定位器字符串中的占位符 (如 "//div[text()='{}']")
        :param wait_strategy: 等待策略, 默认 VISIBLE(可见元素)
        :param hover_time: move_to_element 后的暂停时间(秒), 默认0.2s, 让浏览器有足够时间触发 hover 操作
        :param click_time: click 前的短暂暂停(秒), 默认0.1s, 确保元素准备好接受点击
        :param kw: 等待配置: timeout, poll_frequency, ignored_exceptions
        :return: bool -> 操作成功返回 True, 失败抛异常
        """
        # 1.定位到可见的目标元素
        elem = self.el_ops.get_element_by_keyword(keyword, *args, wait_strategy=wait_strategy, **kw)

        # 2.构造 ActionChains
        actions = ActionChains(self._driver)
        # 3.move_to_element(悬停) 并 pause 一段时间让 hover 效果生效
        actions.move_to_element(elem).pause(hover_time)
        # 4.click, 并 pause 以防连续操作太快
        actions.click(elem).pause(click_time)

        # 5.执行所有操作
        actions.perform()
        return True

    def ctrl_slice_select_by_keyword(
        self,
        keyword: str,
        *args,
        wait_strategy: WaitStrategy = WaitStrategy.VISIBLE_ALL,
        slice_str: str = ":",
        click_time: float = 0.1,
        **kw
    ) -> bool:
        """ 按住 Ctrl, 通过切片方式选择多个元素

        :param keyword: 关键字名称, 定位器来源
        :param args: 用于格式化定位器字符串中的占位符 (如 "//div[text()='{}']")
        :param wait_strategy: 等待策略, 默认 VISIBLE_ALL(所有可见元素)
        :param slice_str: Python 切片格式字符串(默认选中所有元素), 如
                          "1:5:2" -> 从索引 1 开始到 5 结束, 步长为 2
                          "::2" -> 所有元素, 步长为 2
                          "-3" -> 倒数第三个元素
                          ":" -> 所有元素
                          "5" -> 只选择索引为 5 的元素
        :param click_time: 每次点击的间隔
        :param kw: 等待配置: timeout, poll_frequency, ignored_exceptions
        :return: bool -> 操作成功返回 True, 失败返回 False
        """
        # 获取一组稳定的元素
        els = self.el_ops.get_elements_by_keyword(keyword, *args, wait_strategy=wait_strategy, **kw)
        length = len(els)

        if not els:
            logger.warning(f"未找到任何匹配的元素，关键字：{keyword}")
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

            # 组装 ActionChains 动作
            actions = ActionChains(self._driver)
            actions.key_down(Keys.CONTROL)

            # 遍历所有需要点击的下标, 依次点击
            for i in indices:
                try:
                    # 对 "单个下标" 进行负数修正(切片情况下, range不会产生负下标)
                    if i < 0:
                        i += length

                    # 边界检查
                    if 0 <= i < length:
                        element = els[i]
                        actions.click(element)
                        actions.pause(click_time)
                    else:
                        logger.warning(f"索引 {i} 超出范围 [0, {length - 1}]")
                except Exception as e:
                    logger.error(f"点击索引 {i} 的元素时出错: {str(e)}")
                    actions.key_up(Keys.CONTROL).perform()  # 执行已入队操作(确保释放键位)
                    raise

            # 循环结束, 执行所有动作
            actions.key_up(Keys.CONTROL).perform()
            return True

        except (ValueError, IndexError) as e:
            logger.error(f"切片字符串 '{slice_str}' 格式错误或索引超出范围: {str(e)}")
            raise ValueError(f"切片字符串 '{slice_str}' 格式错误") from e
        except Exception as e:
            # 其他未知异常, 透传给调用方
            logger.error(f"执行 Ctrl 多选操作时出错：{str(e)}")
            raise

    def double_left_click_by_keyword(
        self,
        keyword: str,
        *args,
        wait_strategy: WaitStrategy = WaitStrategy.VISIBLE,
        click_time: float = 0.1,
        **kw
    ) -> bool:
        """ 鼠标悬停到元素上并左键双击

        :param keyword: 关键字名称, 定位器来源
        :param args: 用于格式化定位器字符串中的占位符 (如 "//div[text()='{}']")
        :param wait_strategy: 等待策略, 默认 VISIBLE(可见元素)
        :param click_time: click 前的短暂暂停(秒), 默认0.1s, 确保元素准备好接受点击
        :param kw: 等待配置: timeout, poll_frequency, ignored_exceptions
        :return: bool -> 操作成功返回 True, 失败抛异常
        """
        el = self.el_ops.get_element_by_keyword(keyword, *args, wait_strategy=wait_strategy, **kw)

        actions = ActionChains(self._driver)

        # 双击
        actions.double_click(el).pause(click_time)
        actions.perform()
        return True

    def drag_and_drop_by_offset_by_keyword(
        self,
        keyword: str,
        *args,
        wait_strategy: WaitStrategy = WaitStrategy.VISIBLE,
        x_offset: Optional[int] = None,
        y_offset: Optional[int] = None,
        steps: int = 2,
        **kw
    ) -> bool:
        """ 根据关键字定位源元素, 按给定偏移量拖拽

        :param keyword: 关键字名称, 定位器来源
        :param args: 用于格式化定位器字符串中的占位符 (如 "//div[text()='{}']")
        :param wait_strategy: 等待策略, 默认 VISIBLE(可见元素)
        :param x_offset: 水平方向移动像素, 以右为正值
        :param y_offset: 垂直方向移动像素, 以下为正值
        :param steps: 拖拽步数, 默认为 2 步 (至少 2 步以上)
        :param kw: 等待配置: timeout, poll_frequency, ignored_exceptions
        :return: bool -> 操作成功返回 True, 失败抛异常
        """
        # 校验
        if x_offset is None or y_offset is None:
            logger.error("偏移量为 None")
            raise ValueError("偏移量不应为 None")

        el = self.el_ops.get_element_by_keyword(keyword, *args, wait_strategy=wait_strategy, **kw)

        # 按偏移量进行分布拖拽
        action = ActionChains(self._driver)
        action.click_and_hold(el)
        acc_x = acc_y = 0.0
        for _ in range(steps):
            acc_x += x_offset / steps
            acc_y += y_offset / steps

            move_x = math.floor(acc_x)
            move_y = math.floor(acc_y)

            action.move_by_offset(int(move_x), int(move_y))

            acc_x -= move_x
            acc_y -= move_y

        action.release().perform()
        return True

