from pint import UnitRegistry

ureg = UnitRegistry(auto_reduce_dimensions=True)
Q_ = ureg.Quantity

# pint的Measurements不具备误差传播能力
from uncertainties import ufloat
from uncertainties.unumpy import uarray
