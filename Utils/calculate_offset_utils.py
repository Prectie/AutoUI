from collections import namedtuple

from selenium.webdriver.remote.webelement import WebElement

Offsets = namedtuple("Offsets", ["dx", "dy", "ndx", "ndy"])


def calculate_offset_to_target_x_center(src: WebElement, tgt: WebElement):
    """
    计算从 scr 元素中心, 到 tgt 元素水平中心的偏移量(x, y), 以及回到原位的偏移量(-x, -y)
    """
    # 1.计算源元素的中心坐标
    src_location = src.location  # {'x', 'y'}
    src_size = src.size  # {'width', 'height'}
    src_center_x = src_location['x'] + src_size['width'] / 2
    src_center_y = src_location['y'] + src_size['height'] / 2

    # 2.计算目标元素水平中心坐标
    tgt_location = tgt.location
    tgt_size = tgt.size
    tgt_center_x = tgt_location['x'] + tgt_size['width'] / 2

    # 3.计算偏移量
    dx = tgt_center_x - src_center_x
    dy = tgt_location['y'] - src_center_y

    return Offsets(dx, dy, -dx, -dy)


def calculate_offset_to_target_center(src: WebElement, tgt: WebElement):
    """
    计算从 scr 元素中心, 到 tgt 元素中心的偏移量(x, y), 以及回到原位的偏移量(-x, -y)
    """
    # 1.计算源元素的中心坐标
    src_location = src.location  # {'x', 'y'}
    src_size = src.size  # {'width', 'height'}
    src_center_x = src_location['x'] + src_size['width'] / 2
    src_center_y = src_location['y'] + src_size['height'] / 2

    # 2.计算目标元素水平中心坐标
    tgt_location = tgt.location
    tgt_size = tgt.size
    tgt_center_x = tgt_location['x'] + tgt_size['width'] / 2
    tgt_center_y = tgt_location['y'] + tgt_size['height'] / 2

    # 3.计算偏移量
    dx = tgt_center_x - src_center_x
    dy = tgt_center_y - src_center_y

    return Offsets(dx, dy, -dx, -dy)