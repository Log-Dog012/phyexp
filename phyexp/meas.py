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

# 建议采用uquantity函数来创建带不确定度的quantity，输入时就应该含有单位信息

def 多次测量结果(数值列表, 单位: str = "", B类不确定度: float = 0.0, 名称: str = ""):
    # 多次测量结果的不确定度等于A类不确定度与B类不确定度合成
    数值列表 = 数值列表.magnitude if isinstance(数值列表, Q_) else np.array(数值列表)
    A类不确定度 = 求A类不确定度(数值列表)
    不确定度 = 不确定度合成(A类不确定度, B类不确定度)
    平均值 = 数值列表.mean()
    带不确定度的数值 = ufloat(平均值, 不确定度, tag=名称 if 名称 else None)
    obj = Q_(带不确定度的数值, 单位)
    return obj

def quantity_uarray(n: pint.Quantity, u: pint.Quantity) -> pint.Quantity:
    """
    n: 测量值数组quantity
    u: 不确定度数组quantity
    返回一个magnitude为uarray的quantity，单位与n相同
    注：返回的quantity的ureg与n相同
    """
    quantity = n._REGISTRY.Quantity
    return quantity(uarray(n.magnitude, 
                           (u.to(n.units)).magnitude), 
                    n.units)

def quantity_ufloat(n: pint.Quantity, u: pint.Quantity, tag: str = None) -> pint.Quantity:
    """
    n: 测量值quantity
    u: 不确定度quantity
    tag: 标签，可选
    返回一个magnitude为ufloat的quantity，单位与n相同
    注：返回的quantity的ureg与n相同
    """
    quantity = n._REGISTRY.Quantity
    return quantity(ufloat(n.magnitude, 
                           (u.to(n.units)).magnitude, 
                           tag=tag), 
                    n.units)

# 自动判断是数组还是一个数，模仿uarray和ufloat的接口，返回一个带不确定度的quantity
def uquantity(n: pint.Quantity, u: pint.Quantity, tag: str = None) -> pint.Quantity:
    """
    n: 测量值，quantity，可以是一个数或数组
    u: 不确定度，quantity
    tag: 标签，可选，uarray不支持
    返回一个带不确定度的quantity
    """
    if isinstance(n.magnitude, np.ndarray):
        return quantity_uarray(n, u)
    else:
        return quantity_ufloat(n, u, tag=tag)