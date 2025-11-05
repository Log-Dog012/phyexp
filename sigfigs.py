from uncertainties import ufloat, ufloat_fromstr
from uncertainties.umath import *
from uncertainties import UFloat
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

import re

# 匹配所有数字的正则（支持：正负号、整数、小数、科学计数法e/E）
num_pattern = re.compile(
    # 整体结构：(可选括号包裹) + 核心内容 + (可选科学计数法后缀)
    r"(?:\(\s*)?"  # 可选左括号（带空格）
    # 核心内容：数值 [不确定度]
    r"((?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][-+]?\d+)?|nan)"  # 主数值（含纯nan）
    r"(?:"  # 不确定度（可选）
    r"(?:\s*[+-]/[+-]|[\s±]+)\s*"  # +/- 或 ±（合并空格处理）
    r"[-+]?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][-+]?\d+)?"  # 不确定度数值
    r"|"
    r"\(\s*(?:[-+]?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][-+]?\d+)?|nan)\s*\)"  # 括号形式
    r")?"
    r"(?:\s*\))?"  # 可选右括号（带空格）
    r"(?:[eE][-+]?\d+)?"  # 科学计数法后缀
)


def 有效数字计算(计算式: str):
    """
    解析带有效数字的计算式，自动处理不确定度并返回结果

    参数：
        计算式：字符串形式的表达式（如 "1.23±0.04 + 72.15(4) * 2"）

    返回：
        带不确定度的计算结果（ufloat对象）
    """

    def 替换为ufloat(匹配结果):
        """将匹配到的数值字符串替换为ufloat_fromstr调用"""
        数值字符串 = 匹配结果.group()
        # 生成安全的函数调用字符串（避免注入风险）
        return f"ufloat_fromstr('{数值字符串}')"

    try:
        # 1. 替换计算式中的所有数值为ufloat_fromstr调用
        处理后计算式 = num_pattern.sub(替换为ufloat, 计算式)

        # 2. 安全执行计算（限制命名空间，仅允许ufloat_fromstr）
        结果 = eval(处理后计算式, {"ufloat_fromstr": ufloat_fromstr})

        return 修约(结果, 字符串形式=False).nominal_value

    except Exception as e:
        raise ValueError(f"计算错误：{str(e)}，请检查计算式格式")
