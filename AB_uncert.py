"""
物理实验中涉及的不确定度计算
"""

from . import *
from numpy import asarray

def 数字列表转arr(数字列表):
    """
    将数字列表转换为numpy数组。

    参数:
    数字列表: 一组数字。

    返回:
    numpy.ndarray: 转换后的数组。
    """
    if isinstance(数字列表, (list, tuple)) and all(isinstance(x, (int, float)) for x in 数字列表):
        return asarray(数字列表)
    else:
        return 数字列表
    
def 输入转换(func):
    """
    装饰器：将输入调整为不确定度合成所需类型。

    参数:
    func: 需要装饰的函数。

    返回:
    function: 装饰后的函数。
    """
    def wrapper(*分量):
        新分量 = [数字列表转arr(i) for i in 分量]
        return func(*新分量)
    return wrapper

@输入转换
def 求A类不确定度(测量值列表):
    """
    计算A类不确定度，基于测量值的标准偏差。

    参数:
    测量值列表: 一组测量值。

    返回:
    float: A类不确定度。
    """
    n = len(测量值列表)
    平均值 = 测量值列表.mean()
    标准偏差 = (((测量值列表 - 平均值) ** 2).sum() / (n - 1) / n) ** 0.5

    return 标准偏差


A_uncert = 求A类不确定度


def 仪器误差限转B类不确定度(仪器误差限, K=3**0.5):
    """
    将仪器误差限转换为B类不确定度，默认误差服从均匀分布。

    参数:
    仪器误差限: 仪器的误差限。
    K: 分布因子，默认为√3（均匀分布）。

    返回:
    float: B类不确定度。
    """
    return 仪器误差限 / K


InstErr_to_B_uncert = 仪器误差限转B类不确定度

@输入转换
def 不确定度合成(A分量, B分量):
    """
    计算不确定度合成，基于各分量的不确定度平方和的平方根。
    只能处理标量输入和数组输入。

    参数:
    分量: 各分量的不确定度列表。

    返回:
    float: 合成不确定度。
    """
    return (A分量**2+B分量**2) ** 0.5

uncert_comb = 不确定度合成
