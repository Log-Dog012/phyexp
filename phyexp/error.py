# -*- coding: utf-8 -*-

"""
实验误差
"""

from .utils import ureg, Q_
from functools import wraps

__all__ = ["提取标称值", "预处理", "相对误差"]


def 提取标称值(带不确定度的数值):
    """提取带不确定度数值的标称值。

    参数：
        带不确定度的数值：可以是 `uncertainties` 数值对象，也可以是
            带单位的 `pint.Quantity`。

    返回：
        对应的标称值；如果输入带单位，则保留单位。
    """
    if hasattr(带不确定度的数值, "magnitude") and hasattr(带不确定度的数值, "units"):
        if hasattr(带不确定度的数值.magnitude, "nominal_value") and hasattr(
            带不确定度的数值.magnitude, "std_dev"
        ):
            return Q_(带不确定度的数值.magnitude.nominal_value, 带不确定度的数值.units)
    elif hasattr(带不确定度的数值, "nominal_value") and hasattr(
        带不确定度的数值, "std_dev"
    ):
        return 带不确定度的数值.nominal_value
    return 带不确定度的数值


def 预处理(func):
    """装饰器：在调用前把参数中的不确定度对象替换成标称值。"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        新args = [提取标称值(arg) for arg in args]
        新kwargs = {k: 提取标称值(v) for k, v in kwargs.items()}
        return func(*新args, **新kwargs)

    return wrapper


@预处理
def 相对误差(测量值, 真值, str: bool = False, n=3):
    """计算测量值与真值之间的相对误差。

    参数：
        测量值：实验测得值。
        真值：参考值或标准值。
        str：是否返回格式化字符串。为 `True` 时返回百分比文本。
        n：字符串模式下保留的小数位数。

    返回：
        相对误差的数值或字符串。
    """
    if str:
        tem = (测量值 - 真值) / 真值
        if hasattr(tem, "magnitude"):
            tem = tem.magnitude
        return f"{tem:.{n}%}"
    else:
        return (测量值 - 真值) / 真值
