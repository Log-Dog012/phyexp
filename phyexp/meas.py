# -*- coding: utf-8 -*-

"""
测量量
"""

from .utils import ureg, Q_, ufloat, uarray
from typing import Sequence
from .AB_uncert import 求A类不确定度, 不确定度合成
from uncertainties.core import UFloat, AffineScalarFunc
import numpy as np

import pint # 用于标注类型

__all__ = [
    "一次测量结果",
    "多次测量结果",
    "quantity_uarray",
    "quantity_ufloat",
    "uquantity",
]

# 建议采用uquantity函数来创建带不确定度的quantity，输入时就应该含有单位信息

def 一次测量结果(数值, 单位: str = "", 不确定度: float = 0.0, 名称: str = None):
    """根据单次测量值及其不确定度构造带不确定度的物理量。

    参数：
        数值：单次测量值（数值或 `pint.Quantity`）。
        单位：结果单位。
        不确定度：该测量值的标准不确定度。
        名称：不确定度对象的标签。

    返回：
        带不确定度的 `pint.Quantity`。
    """
    if isinstance(数值, Q_):
        单位 = 数值.units
        数值 = 数值.magnitude
    return uquantity(Q_(数值, 单位), Q_(不确定度, 单位), tag=名称)

def 多次测量结果(数值列表, 单位: str = "", B类不确定度: float = 0.0, 名称: str = ""):
    """根据多次测量值构造带不确定度的物理量。

    参数：
        数值列表：测量值序列，或已经带单位的 `pint.Quantity`。
        单位：结果单位。
        B类不确定度：仪器引入的 B 类不确定度。
        名称：不确定度对象的标签。

    返回：
        带不确定度的 `pint.Quantity`。
    """
    # 多次测量结果的不确定度等于A类不确定度与B类不确定度合成
    数值列表 = 数值列表.magnitude if isinstance(数值列表, Q_) else np.array(数值列表)
    A类不确定度 = 求A类不确定度(数值列表)
    不确定度 = 不确定度合成(A类不确定度, B类不确定度)
    平均值 = 数值列表.mean()
    带不确定度的数值 = ufloat(平均值, 不确定度, tag=名称 if 名称 else None)
    obj = Q_(带不确定度的数值, 单位)
    return obj

def quantity_uarray(n: pint.Quantity, u: pint.Quantity) -> pint.Quantity:
    """把数组测量值和不确定度合成为 `uarray` 型 quantity。"""
    quantity = n._REGISTRY.Quantity
    return quantity(uarray(n.magnitude, 
                           (u.to(n.units)).magnitude), 
                    n.units)

def quantity_ufloat(n: pint.Quantity, u: pint.Quantity, tag: str = None) -> pint.Quantity:
    """把标量测量值和不确定度合成为 `ufloat` 型 quantity。"""
    quantity = n._REGISTRY.Quantity
    return quantity(ufloat(n.magnitude, 
                           (u.to(n.units)).magnitude, 
                           tag=tag), 
                    n.units)

# 自动判断是数组还是一个数，模仿uarray和ufloat的接口，返回一个带不确定度的quantity
def uquantity(n: pint.Quantity, u: pint.Quantity, tag: str = None) -> pint.Quantity:
    """根据输入是标量还是数组，自动选择 `ufloat` 或 `uarray` 构造方式。"""
    if isinstance(n.magnitude, np.ndarray):
        return quantity_uarray(n, u)
    else:
        return quantity_ufloat(n, u, tag=tag)