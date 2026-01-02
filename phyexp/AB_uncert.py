"""
物理实验中涉及的不确定度计算
"""

import numpy as np
import types
import warnings


def 可向量化(数字列表):
    """
    将不支持向量化的列表转换为numpy数组。

    参数:
    数字列表: 一组数字。

    返回:
    numpy数组(dtype可以为object)或原始输入。
    """
    attrs = [
        "__len__",
        "mean",
        "std",
    ]
    test = all(hasattr(数字列表, attr) for attr in attrs)
    if test:
        return 数字列表
    else:
        try:
            result = np.asarray(数字列表)
        except Exception as e:
            try:
                result = np.asarray(数字列表, dtype=object)
            except Exception:
                raise TypeError(f"无法将输入转换为numpy数组: {e}")

        return result


def 输入转换(func):
    """
    装饰器：将输入调整为不确定度合成所需类型。

    参数:
    func: 需要装饰的函数。

    返回:
    function: 装饰后的函数。
    """

    def wrapper(*分量):
        新分量 = [可向量化(i) for i in 分量]
        return func(*新分量)

    return wrapper


def generator_to_list_warning(func):
    """
    装饰器：如果输入是生成器，则转换为列表并发出警告。

    参数:
    func: 需要装饰的函数。

    返回:
    function: 装饰后的函数。
    """

    def wrapper(测量值列表):
        if isinstance(测量值列表, types.GeneratorType):
            测量值列表 = list(测量值列表)
            warnings.warn(
                "生成器已被迭代并转换为列表，后续无法再次使用此生成器（生成器是一次性迭代对象）。",
                UserWarning,  # 警告类型（用户级警告，最常用）
                stacklevel=2,  # 控制警告的栈层级，让用户看到自己的代码行（而非函数内部）
            )
        return func(测量值列表)

    return wrapper


@generator_to_list_warning
@输入转换
def 求A类不确定度(测量值列表):
    """
    计算A类不确定度，基于测量值均值的样本标准差（贝塞尔公式）。

    参数:
    测量值列表: 一组测量值（支持列表、元组、np数组、pint带单位量、pd.Series等可迭代对象）。

    返回:
    float/np.float64/pint.Quantity: A类不确定度（输入带单位则返回带单位结果）。
    """

    if len(测量值列表) < 2:
        raise ValueError("测量值列表至少应包含两个值以计算A类不确定度。")
    标准偏差 = 测量值列表.std(ddof=1) / (len(测量值列表) ** 0.5)

    return 标准偏差


A_uncert = 求A类不确定度

# 支持的分布及其对应的包含因子K
包含因子 = {
    "均匀": 3**0.5,
    "正态": 3,  # 3σ原则
}


# 这样的函数只是为了使用时更直观
def 仪器误差限转B类不确定度(仪器误差限, 分布="均匀", K=3**0.5):
    """
    将仪器误差限转换为B类不确定度。
    参数:
    仪器误差限: 仪器误差限值（正数）。
    分布: 仪器误差的分布类型，支持"均匀"和"正态"。默认值为"均匀"。
    K: 如果分布类型未知，可直接提供分布因子K（正数）。默认值为3的平方根（对应均匀分布）。
    返回:
    float: B类不确定度。
    """

    if 分布 in 包含因子:
        K = 包含因子[分布]
    elif 分布 is not None:
        现有分布类型 = list(包含因子.keys())
        raise ValueError(f"未知分布类型'{分布}'，目前只支持{现有分布类型}。")
    elif K <= 0:
        raise ValueError("分布因子K应为正数。")
    elif K > 0:
        pass
    else:
        raise ValueError("未知错误。")

    return 仪器误差限 / K


InstErr_to_B_uncert = 仪器误差限转B类不确定度


# 这个函数只是为了使用时更直观
def 不确定度合成(A分量, B分量):
    """
    计算不确定度合成，基于各分量的不确定度平方和的平方根。
    只能处理标量输入和数组输入。

    参数:
    分量: AB分量。

    返回:
    float: 合成不确定度。
    """
    return (A分量**2 + B分量**2) ** 0.5


uncert_comb = 不确定度合成
