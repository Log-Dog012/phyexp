# -*- coding: utf-8 -*-

from pint import UnitRegistry
from .quantity import _build_q_class, set_internal_ureg, ureg_compatible, convert_quantity_to_ureg

ureg = UnitRegistry(auto_reduce_dimensions=True)
set_internal_ureg(ureg)
Q_ = _build_q_class(ureg)

# pint的Measurements不具备误差传播能力
from uncertainties import ufloat
from uncertainties.unumpy import uarray
