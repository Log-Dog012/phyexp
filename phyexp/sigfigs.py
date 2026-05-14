# -*- coding: utf-8 -*-

from uncertainties import UFloat
from uncertainties import ufloat
from math import log10, floor

__all__ = ["修约", "u"]


def 修约(带不确定度数值: UFloat, 字符串形式=True):
    """按不确定度的有效数字规则修约数值。

    参数：
        带不确定度数值：`uncertainties.UFloat` 对象。
        字符串形式：为 `True` 时返回格式化字符串，否则返回修约后的对象。

    返回：
        修约后的字符串或 `UFloat`。
    """
    if 带不确定度数值.std_dev == 0:
        if 字符串形式:
            return f"{带不确定度数值:g}"
        else:
            return 带不确定度数值
    else:
        位 = -floor(log10(abs(带不确定度数值.std_dev)))
        修约值 = ufloat(
            round(带不确定度数值.nominal_value, 位), round(带不确定度数值.std_dev, 位)
        )
        if 字符串形式:
            return f"{修约值:g}"
        else:
            return 修约值


# 无法处理单位


from uncertainties import ufloat_fromstr as u
from uncertainties.umath import *

"""
用u来创建需考虑不确定度的数值，并直接使用数学函数进行计算
可以用dir()查看可用的函数
"""
