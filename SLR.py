"""
带不确定度的一元线性回归
"""

from .utils import *
from AB_uncert import 不确定度合成


class 一元线性回归:
    """
    一元线性回归类
    """

    class 回归结果:
        """
        回归结果类
        属性:
            a: 截距，带不确定度
            b: 斜率，带不确定度
            表达式: 回归表达式
            SSE: 残差平方和
            RR(R²): 决定系数
        可计算
        """

        def __init__(self, a, b, 残差平方和, 决定系数):
            self.a = a
            self.b = b
            self.SSE = self.残差平方和 = 残差平方和
            self.RR = self.决定系数 = 决定系数
            self.计算 = lambda x: a + b * x

        def __str__(self):
            return f"y={self.a} + {self.b} * x"

        def __call__(self, x):
            return self.计算(x)

        __repr__ = __str__

    @classmethod
    def 拟合(cls, x, y):
        """
        一元线性回归拟合 y=a+b*x，可处理不确定度
        输入:
            x: 自变量数据
            y: 因变量数据
        输出:
            a,b: 拟合参数，带不确定度
        """
        n = len(x)
        if n != len(y):
            raise ValueError("x和y的长度必须相等")
        b = (x.sum() * y.sum() - n * (x * y).sum()) / (x.sum() ** 2 - n * (x**2).sum())
        a = ((x * y).sum() * x.sum() - y.sum() * (x**2).sum()) / (
            x.sum() ** 2 - n * (x**2).sum()
        )
        残差平方和 = ((y - (a + b * x)) ** 2).sum()
        决定系数 = 1 - 残差平方和 / (((y - y.mean()) ** 2).sum())
        结果 = cls.回归结果(a, b, 残差平方和, 决定系数)
        return 结果

    fit = 拟合

    @staticmethod
    def 相关系数(x, y):
        """
        计算相关系数r
        输入:
            x: 自变量数据
            y: 因变量数据
        输出:
            r: 相关系数
        """
        if len(x) != len(y):
            raise ValueError("x和y的长度必须相等")
        r = ((x - x.mean()) * (y - y.mean())).sum() / (
            (((x - x.mean()) ** 2).sum() * ((y - y.mean()) ** 2).sum()) ** 0.5
        )
        return r

    @classmethod
    def 求A类不确定度(cls, x, y, 结果=None):
        """
        计算因变量y的A类不确定度
        输出:
            y的A类不确定度
        """
        if 结果 is None:
            结果 = cls.拟合(x, y)
        n = len(x)
        if n != len(y):
            raise ValueError("x和y的长度必须相等")
        标准偏差 = (结果.残差平方和 / (n - 2)) ** 0.5

        return 标准偏差

    def __init__(self, x, y, 名称=None):
        if 名称 is None:
            self.名称 = f"{y.名称}-{x.名称}线性回归"
        self.x = x
        self.y = y
        self.回归 = self.拟合(x, y)
        self.y.A不确定度 = self.求A类不确定度(x, y, self.回归)

    def predict(self, x):
        """
        预测函数值
        输入:
            x: 自变量数据
        输出:
            y: 预测的因变量数据
        """
        return self.a + self.b * x
