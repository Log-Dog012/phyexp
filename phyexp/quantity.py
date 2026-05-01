# -*- coding: utf-8 -*-

"""
自定义 Pint Quantity 子类，处理跨 ureg 运算兼容性。

当库内 ureg 与用户传入的外部 ureg 的 Quantity 进行运算时，
Pint 默认会抛出 ValueError。本模块提供：
1. Q_ 子类：继承自 pint.Quantity，自动拦截 ureg 冲突并转换
2. ureg_compatible 装饰器：可独立用于装饰可能有 ureg 冲突的函数
"""

from pint import Quantity as _BaseQuantity
from pint.util import UnitsContainer
from functools import wraps
import warnings


_internal_ureg = None


def set_internal_ureg(ureg):
    global _internal_ureg
    _internal_ureg = ureg


def get_internal_ureg():
    return _internal_ureg


def _is_ureg_mismatch(error, other):
    if not isinstance(other, _BaseQuantity):
        return False
    if isinstance(error, ValueError):
        msg = str(error)
        if 'different registries' in msg:
            return True
    return False


def _get_unit_base_definition(source_ureg, unit_name):
    q = source_ureg.Quantity(1, unit_name)
    base_q = q.to_base_units()
    base_units_str = format(base_q.units, '~')
    return f"{unit_name} = {base_q.magnitude} * {base_units_str}"


def _compare_unit_defs(ureg1, ureg2, unit_name):
    try:
        q1 = ureg1.Quantity(1, unit_name).to_base_units()
        q2 = ureg2.Quantity(1, unit_name).to_base_units()
        return q1.magnitude == q2.magnitude and q1.units == q2.units
    except Exception:
        return False


def _sync_units(source_ureg, target_ureg):
    for unit_name in source_ureg._units:
        if unit_name.startswith('_'):
            continue
        if unit_name in target_ureg._units:
            continue
        try:
            def_str = _get_unit_base_definition(source_ureg, unit_name)
            target_ureg.define(def_str)
        except Exception:
            pass


def convert_quantity_to_ureg(q, target_ureg):
    if not isinstance(q, _BaseQuantity):
        return q
    if q._REGISTRY is target_ureg:
        return q

    _sync_units(q._REGISTRY, target_ureg)
    unit_str = format(q.units, '~')
    return target_ureg.Quantity(q.magnitude, unit_str)


def _build_q_class(internal_ureg):

    BaseQ = internal_ureg.Quantity

    class Q_(BaseQ):
        _internal_ureg = internal_ureg

        def _convert_to_internal(self):
            return convert_quantity_to_ureg(self, self._internal_ureg)

        @staticmethod
        def _try_convert_other(other):
            if isinstance(other, _BaseQuantity):
                if other._REGISTRY is not Q_._internal_ureg:
                    return convert_quantity_to_ureg(other, Q_._internal_ureg)
            return other

        def _binary_op(self, other, op_name):
            op = getattr(super(), op_name)
            try:
                return op(other)
            except ValueError as e:
                if _is_ureg_mismatch(e, other):
                    converted = self._try_convert_other(other)
                    if converted is not other:
                        return op(converted)
                raise

        def __add__(self, other):
            return self._binary_op(other, '__add__')

        def __sub__(self, other):
            return self._binary_op(other, '__sub__')

        def __mul__(self, other):
            return self._binary_op(other, '__mul__')

        def __truediv__(self, other):
            return self._binary_op(other, '__truediv__')

        def __floordiv__(self, other):
            return self._binary_op(other, '__floordiv__')

        def __mod__(self, other):
            return self._binary_op(other, '__mod__')

        def __pow__(self, other):
            return self._binary_op(other, '__pow__')

        def __radd__(self, other):
            return self._binary_op(other, '__radd__')

        def __rsub__(self, other):
            return self._binary_op(other, '__rsub__')

        def __rmul__(self, other):
            return self._binary_op(other, '__rmul__')

        def __rtruediv__(self, other):
            return self._binary_op(other, '__rtruediv__')

        def __rfloordiv__(self, other):
            return self._binary_op(other, '__rfloordiv__')

        def __rmod__(self, other):
            return self._binary_op(other, '__rmod__')

        def __rpow__(self, other):
            return self._binary_op(other, '__rpow__')

        def __eq__(self, other):
            return self._binary_op(other, '__eq__')

        def __ne__(self, other):
            return self._binary_op(other, '__ne__')

        def __lt__(self, other):
            return self._binary_op(other, '__lt__')

        def __le__(self, other):
            return self._binary_op(other, '__le__')

        def __gt__(self, other):
            return self._binary_op(other, '__gt__')

        def __ge__(self, other):
            return self._binary_op(other, '__ge__')

    return Q_


def ureg_compatible(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if _internal_ureg is None:
            return func(*args, **kwargs)

        new_args = [_convert_arg(a) for a in args]
        new_kwargs = {k: _convert_arg(v) for k, v in kwargs.items()}

        try:
            return func(*new_args, **new_kwargs)
        except ValueError as e:
            if 'different registries' in str(e):
                new_args = [_convert_arg_deep(a) for a in args]
                new_kwargs = {k: _convert_arg_deep(v) for k, v in kwargs.items()}
                return func(*new_args, **new_kwargs)
            raise

    return wrapper


def _convert_arg(arg):
    if isinstance(arg, _BaseQuantity):
        if arg._REGISTRY is not _internal_ureg:
            return convert_quantity_to_ureg(arg, _internal_ureg)
    return arg


def _convert_arg_deep(arg):
    if isinstance(arg, _BaseQuantity):
        if arg._REGISTRY is not _internal_ureg:
            return convert_quantity_to_ureg(arg, _internal_ureg)
    elif isinstance(arg, (list, tuple)):
        return type(arg)(_convert_arg_deep(a) for a in arg)
    elif isinstance(arg, dict):
        return {k: _convert_arg_deep(v) for k, v in arg.items()}
    return arg
