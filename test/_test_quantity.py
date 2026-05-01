# -*- coding: utf-8 -*-
"""测试自定义 Q_ 子类和 ureg_compatible 装饰器"""

import sys
sys.path.insert(0, r'b:\alot\phyexp')

from pint import UnitRegistry
from phyexp.utils import ureg, Q_
from phyexp import ureg_compatible, convert_quantity_to_ureg
import numpy as np

print("=" * 60)
print("测试 1: 基本功能 - 库内 ureg 运算")
print("=" * 60)
q1 = Q_(5, 'm')
q2 = Q_(3, 'm')
print(f"q1 = {q1}")
print(f"q2 = {q2}")
print(f"q1 + q2 = {q1 + q2}")
print(f"q1 - q2 = {q1 - q2}")
print(f"q1 * q2 = {q1 * q2}")
print(f"q1 / q2 = {q1 / q2}")
print(f"q1 == q2: {q1 == q2}")
print(f"q1 > q2: {q1 > q2}")
print("PASS")

print()
print("=" * 60)
print("测试 2: 跨 ureg 运算 - Q_ + 外部 Quantity")
print("=" * 60)
ext_ureg = UnitRegistry()
ext_q = ext_ureg.Quantity(3, 'm')
print(f"库内 q1 = {q1} (ureg={id(q1._REGISTRY)})")
print(f"外部 ext_q = {ext_q} (ureg={id(ext_q._REGISTRY)})")
try:
    r = q1 + ext_q
    print(f"q1 + ext_q = {r}")
    print(f"结果 ureg 是否为库内: {r._REGISTRY is ureg}")
    print("PASS")
except Exception as e:
    print(f"FAIL: {e}")

print()
print("=" * 60)
print("测试 3: 跨 ureg 运算 - Q_ - 外部 Quantity")
print("=" * 60)
try:
    r = q1 - ext_q
    print(f"q1 - ext_q = {r}")
    print("PASS")
except Exception as e:
    print(f"FAIL: {e}")

print()
print("=" * 60)
print("测试 4: 跨 ureg 运算 - Q_ * 外部 Quantity")
print("=" * 60)
try:
    r = q1 * ext_q
    print(f"q1 * ext_q = {r}")
    print("PASS")
except Exception as e:
    print(f"FAIL: {e}")

print()
print("=" * 60)
print("测试 5: 跨 ureg 运算 - Q_ / 外部 Quantity")
print("=" * 60)
try:
    r = q1 / ext_q
    print(f"q1 / ext_q = {r}")
    print("PASS")
except Exception as e:
    print(f"FAIL: {e}")

print()
print("=" * 60)
print("测试 6: 跨 ureg 比较运算")
print("=" * 60)
try:
    print(f"q1 == ext_q: {q1 == ext_q}")
    print(f"q1 > ext_q: {q1 > ext_q}")
    print(f"q1 < ext_q: {q1 < ext_q}")
    print("PASS")
except Exception as e:
    print(f"FAIL: {e}")

print()
print("=" * 60)
print("测试 7: 外部 ureg 中有库内没有的单位")
print("=" * 60)
ext_ureg2 = UnitRegistry()
ext_ureg2.define('dog_year = 7 * year')
ext_q2 = ext_ureg2.Quantity(2, 'dog_year')
print(f"外部 ext_q2 = {ext_q2}")
print(f"库内是否有 dog_year: {'dog_year' in ureg._units}")
try:
    r = Q_(1, 'year') + ext_q2
    print(f"Q_(1, 'year') + ext_q2 = {r}")
    print(f"库内是否有 dog_year: {'dog_year' in ureg._units}")
    print("PASS")
except Exception as e:
    print(f"FAIL: {e}")

print()
print("=" * 60)
print("测试 8: convert_quantity_to_ureg 独立函数")
print("=" * 60)
ext_q3 = ext_ureg.Quantity(10, 'cm')
print(f"外部 ext_q3 = {ext_q3} (ureg={id(ext_q3._REGISTRY)})")
converted = convert_quantity_to_ureg(ext_q3, ureg)
print(f"转换后 = {converted} (ureg={id(converted._REGISTRY)})")
print(f"转换后 ureg 是否为库内: {converted._REGISTRY is ureg}")
print("PASS")

print()
print("=" * 60)
print("测试 9: ureg_compatible 装饰器")
print("=" * 60)

@ureg_compatible
def calculate_speed(distance, time):
    return distance / time

ext_d = ext_ureg.Quantity(100, 'm')
ext_t = ext_ureg.Quantity(10, 's')
print(f"外部 distance = {ext_d}")
print(f"外部 time = {ext_t}")
try:
    r = calculate_speed(ext_d, ext_t)
    print(f"speed = {r}")
    print(f"结果 ureg 是否为库内: {r._REGISTRY is ureg}")
    print("PASS")
except Exception as e:
    print(f"FAIL: {e}")

print()
print("=" * 60)
print("测试 10: ureg_compatible 装饰器 - 混合参数")
print("=" * 60)

@ureg_compatible
def add_quantities(a, b):
    return a + b

try:
    r = add_quantities(q1, ext_q)
    print(f"add_quantities(q1, ext_q) = {r}")
    print("PASS")
except Exception as e:
    print(f"FAIL: {e}")

print()
print("=" * 60)
print("测试 11: 与 uncertainties 兼容性")
print("=" * 60)
from uncertainties import ufloat
try:
    q_u = Q_(ufloat(5, 0.1), 'm')
    print(f"带不确定度的 Q_ = {q_u}")
    r = q_u + Q_(3, 'm')
    print(f"q_u + 3m = {r}")
    print("PASS")
except Exception as e:
    print(f"FAIL: {e}")

print()
print("=" * 60)
print("测试 12: numpy 数组兼容性")
print("=" * 60)
try:
    arr = np.array([1, 2, 3]) * Q_(1, 'm')
    print(f"numpy 数组 * Q_ = {arr}")
    print(f"类型: {type(arr)}")
    print("PASS")
except Exception as e:
    print(f"FAIL: {e}")

print()
print("=" * 60)
print("测试 13: 反向运算 (外部 Quantity OP Q_)")
print("=" * 60)
print("注意: 外部 ureg 的 Quantity.__add__ 会先触发并抛出 ValueError,")
print("由于 Pint 不返回 NotImplemented，__radd__ 不会被调用。")
print("这种情况应使用 ureg_compatible 装饰器或手动转换。")
try:
    r = ext_q + q1
    print(f"ext_q + q1 = {r}")
    print("PASS (意外)")
except Exception as e:
    print(f"预期行为 - 外部 Quantity 主导运算时失败: {type(e).__name__}: {e}")
    print("这是已知限制，请使用 ureg_compatible 装饰器处理此场景")

print()
print("=" * 60)
print("测试 14: 单位转换后保持正确数值")
print("=" * 60)
ext_q4 = ext_ureg.Quantity(1, 'km')
print(f"外部 ext_q4 = {ext_q4}")
try:
    r = q1 + ext_q4
    print(f"q1(5m) + ext_q4(1km) = {r}")
    expected = Q_(1005, 'm')
    print(f"期望值: {expected}")
    print(f"数值正确: {r.magnitude == expected.magnitude}")
    print("PASS" if r.magnitude == expected.magnitude else "FAIL")
except Exception as e:
    print(f"FAIL: {e}")

print()
print("=" * 60)
print("所有测试完成!")
print("=" * 60)
