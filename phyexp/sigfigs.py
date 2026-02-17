# -*- coding: utf-8 -*-

from uncertainties import UFloat
from uncertainties import ufloat
from math import log10, floor


def 修约(带不确定度数值: UFloat, 字符串形式=True):
    """修约一个不确定度数值到其有效数字位数。

    参数:
        带不确定度数值 (UFloat): 需要修约的不确定度数值。

    返回:
        UFloat: 修约后的不确定度数值。
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
