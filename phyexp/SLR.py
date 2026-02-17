# -*- coding: utf-8 -*-

"""
带不确定度的一元线性回归
"""

from .utils import ureg, Q_
from .AB_uncert import 不确定度合成
from functools import wraps
import numpy as np
from . import plt
from .error import 提取标称值

def 提取不确定度(带不确定度的数值):
    """提取带不确定度的数值的不确定度。"""
    if hasattr(带不确定度的数值, "magnitude") and hasattr(带不确定度的数值, "units"):
        if hasattr(带不确定度的数值.magnitude, "nominal_value") and hasattr(带不确定度的数值.magnitude, "std_dev"):
            return Q_(带不确定度的数值.magnitude.std_dev, 带不确定度的数值.units)
    elif hasattr(带不确定度的数值, "nominal_value") and hasattr(带不确定度的数值, "std_dev"):
        return 带不确定度的数值.std_dev
    raise ValueError("输入的数值不包含不确定度信息。")

def 一元线性回归(x, y):
    """
    带不确定度的一元线性回归
    参数:
        x: 自变量数组，元素可以是带不确定度的数值。
        y: 因变量数组，元素必须是带不确定度的数值。
    返回:
        截距 a 和斜率 b，与输入同种类。
    备注:
        使用加权最小二乘法进行回归，权重为因变量的不确定度的倒数。
    """
    if len(x) != len(y):
        raise ValueError("x 和 y 的长度必须相等。")
    
    w=np.array([1/提取不确定度(yi) for yi in y],dtype=object)

    a=((w*y).sum()*(w*x**2).sum()-(w*x).sum()*(w*x*y).sum())/(w.sum()*(w*x**2).sum()-((w*x).sum())**2)
    b=(w.sum()*(w*x*y).sum()-(w*y).sum()*(w*x).sum())/(w.sum()*(w*x**2).sum()-((w*x).sum())**2)

    return a,b

def 绘制回归图(x:Q_, y:Q_, title=None, xlabel=None, ylabel=None):
    """
    绘制带不确定度的一元线性回归图
    参数:
        x: 自变量数组，元素可以是带不确定度的数值。
        y: 因变量数组，元素必须是带不确定度的数值。
    """
    a, b = 一元线性回归(x, y)

    if title is None:
        title = "带不确定度的一元线性回归图"
    if xlabel is None:
        xlabel = "自变量"
    if ylabel is None:
        ylabel = "因变量"

    x_vals = np.linspace(min(x).magnitude, max(x).magnitude, 100)
    y_vals = a.n + b.n * x_vals

    plt.errorbar(
        [xi.magnitude for xi in x],
        [提取标称值(yi).magnitude for yi in y],
        yerr=[提取不确定度(yi).magnitude for yi in y],
        fmt='o', label='数据点'
    )
    plt.plot(x_vals, y_vals, 'r-', label='回归线')
    plt.xlabel(f'{xlabel}/{x.units}')
    y=Q_([yi.magnitude for yi in y],y[0].units)
    plt.ylabel(f'{ylabel}/{y.units}')
    plt.title(title)
    plt.legend()
    plt.show()