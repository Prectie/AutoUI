from enum import Enum


class Attribute(Enum):
    """ 存放 HTML 标签里的各种属性名, property 与 attribute 均适用 """
    CLASS = 'class'
    STYLE = 'style'
    WIDTH = 'width'
    HEIGHT = 'height'
