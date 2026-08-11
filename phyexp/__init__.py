# -*- coding: utf-8 -*-

"""
phyexp — 大学物理实验数据处理库

公开 API：
- 物理量：`uquantity` / `一次测量结果` / `多次测量结果`（带单位 + 不确定度）
- 不确定度：`A_uncert`(求A类不确定度) / `仪器误差限转B类不确定度` / `不确定度合成`
- 误差：`相对误差` / `提取标称值`
- 拟合：`SLR.一元线性回归` / `SLR.绘制回归图`
- 报告：`nb2latex`（notebook → LaTeX）
"""

from .AB_uncert import (
    求A类不确定度 as A_uncert,
    仪器误差限转B类不确定度,
    不确定度合成,
)
from .meas import uquantity, 一次测量结果, 多次测量结果
from .error import 相对误差, 提取标称值

__all__ = [
    "A_uncert",
    "仪器误差限转B类不确定度",
    "不确定度合成",
    "uquantity",
    "一次测量结果",
    "多次测量结果",
    "相对误差",
    "提取标称值",
]
