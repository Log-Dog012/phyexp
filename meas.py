"""
测量量
"""

from .utils import *
from typing import Union, List
from .AB_uncert import 求A类不确定度, 不确定度合成
from uncertainties.core import UFloat, AffineScalarFunc


class 数量(Q_):
    """
    带不确定度的数量类，继承自pint的Quantity类
    包含数值、单位、B类不确定度和名称属性
    也可以通过带不确定度的数值属性直接访问和修改
    例子:
        q = 数量(10, "m/s", 0.5, "速度")
        print(q.数值)  # 10
        print(q.单位)  # m/s
        print(q.B类不确定度)  # 0.5
        print(q.名称)  # 速度
        print(q.带不确定度的数值)  # 10.0 +/- 0.5
        q.数值 = 12
        q.B类不确定度 = 0.3
        q.名称 = "新速度"
        print(q.带不确定度的数值)  # 12.0 +/- 0.3
    """

    # @staticmethod
    # def 编号器():
    #    编号 = 0
    #    while True:
    #        编号 += 1
    #        yield 编号

    def __new__(cls, 数值, 单位: str = "", B类不确定度: float = 0.0, 名称: str = ""):
        # 一次测量结果的不确定度等于其B类不确定度
        if isinstance(数值, (UFloat, AffineScalarFunc)):
            # 处理非手动输入的构造
            带不确定度的数值 = 数值
        else:
            带不确定度的数值 = ufloat(数值, B类不确定度, tag=名称 if 名称 else None)
        obj = super().__new__(cls, 带不确定度的数值, 单位)
        return obj

    @property
    def 名称(self):
        if hasattr(self.magnitude, "tag"):
            return self.magnitude.tag
        else:
            return None

    @名称.setter
    def 名称(self, 新名称: str):
        self.magnitude.tag = 新名称

    @property
    def 数值(self):
        return self.magnitude.nominal_value

    @数值.setter
    def 数值(self, 新数值: float):
        self.magnitude.nominal_value = 新数值

    @property
    def 不确定度(self):
        return self.magnitude.std_dev

    @不确定度.setter
    def 不确定度(self, 新B类不确定度: float):
        self.magnitude.std_dev = 新B类不确定度

    @property
    def 相对不确定度(self):
        return abs(self.不确定度 / self.数值) if self.数值 != 0 else float("inf")

    @相对不确定度.setter
    def 相对不确定度(self, 新相对不确定度: float):
        self.不确定度 = abs(新相对不确定度 * self.数值)

    @property
    def 带不确定度的数值(self):
        return self.magnitude

    @带不确定度的数值.setter
    def 带不确定度的数值(self, 新带不确定度的数值: ufloat):
        self.magnitude = 新带不确定度的数值

    @property
    def 单位(self):
        return self.units

    @单位.setter
    def 单位(self, 新单位: str):
        self.units = ureg(新单位).units

    def __str__(self):
        if self.名称:
            return self.名称 + " : " + super().__str__()
        else:
            return super().__str__()

    def __repr__(self):
        if self.名称:
            return super().__repr__() + "--" + self.名称
        else:
            return super().__repr__()


class 数量组(Q_): ...
