from enum import Enum


class AttributeValue(Enum):
    """ HTML 属性名中存在的属性值 一般用于判断属性值中是否存在期望值 """
    SELECTED = 'selected'  # 元素被选中时出现的属性值
