"""
实验误差
"""

from .utils import ureg, Q_
from functools import wraps


def 提取标称值(带不确定度的数值):
    """提取带不确定度的数值的标称值（即测量值）。"""
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
    """装饰器：预处理函数参数，提取带不确定度数值的标称值。"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        新args = [提取标称值(arg) for arg in args]
        新kwargs = {k: 提取标称值(v) for k, v in kwargs.items()}
        return func(*新args, **新kwargs)

    return wrapper


@预处理
def 相对误差(测量值, 真值, str: bool = False, n=3):
    """计算测量值与真值之间的误差。"""
    if str:
        tem = (测量值 - 真值) / 真值
        if hasattr(tem, "magnitude"):
            tem = tem.magnitude
        return f"{tem:.{n}%}"
    else:
        return (测量值 - 真值) / 真值
