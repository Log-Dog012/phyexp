# -*- coding: utf-8 -*-

"""
测量量
"""

from .utils import ureg, Q_, ufloat
from typing import Sequence
from .AB_uncert import 求A类不确定度, 不确定度合成
from uncertainties.core import UFloat, AffineScalarFunc
import numpy as np


def 一次测量结果(数值, 单位: str = "", B类不确定度: float = 0.0, 名称: str = ""):
    # 一次测量结果的不确定度等于其B类不确定度
    带不确定度的数值 = ufloat(数值, B类不确定度, tag=名称 if 名称 else None)
    obj = Q_(带不确定度的数值, 单位)
    return obj


def 多次测量结果(数值列表, 单位: str = "", B类不确定度: float = 0.0, 名称: str = ""):
    # 多次测量结果的不确定度等于A类不确定度与B类不确定度合成
    数值列表 = 数值列表.magnitude if isinstance(数值列表, Q_) else np.array(数值列表)
    A类不确定度 = 求A类不确定度(数值列表)
    不确定度 = 不确定度合成(A类不确定度, B类不确定度)
    平均值 = 数值列表.mean()
    带不确定度的数值 = ufloat(平均值, 不确定度, tag=名称 if 名称 else None)
    obj = Q_(带不确定度的数值, 单位)
    return obj
