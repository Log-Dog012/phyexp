'''
带不确定度的一元线性回归
'''

from . import *

def SLR_fit(x,y):
    '''
    带不确定度的一元线性回归拟合 y=a+b*x
    输入:
        x: 自变量数据
        y: 因变量数据
    输出:
        a,b: 拟合参数，带不确定度
    '''
    n=len(x)
    if n!=len(y):
        raise ValueError("x和y的长度必须相等")
    b=(x.sum() * y.sum() - n * (x * y).sum()) / (x.sum() ** 2 - n * (x ** 2).sum())
    a=((x * y).sum() * x.sum() - y.sum() * (x ** 2).sum()) / (x.sum() ** 2 - n * (x ** 2).sum())
    return a,b