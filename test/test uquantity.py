import pint
ureg = pint.UnitRegistry()
quantity = ureg.Quantity
import numpy as np
from phyexp.meas import uquantity

try:
    n=quantity([1,2,3], 'm')
    u=quantity([0.1,0.2,0.3], 'm')
    result = uquantity(n, u)
    print(result)
except Exception as e:
    print(f"Error: {e}")

try:
    n=quantity(1, 'm')
    u=quantity(0.1, 'm')
    result = uquantity(n, u)
    print(result)
except Exception as e:
    print(f"Error: {e}")