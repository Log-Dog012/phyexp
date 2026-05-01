from pint import UnitRegistry

u1 = UnitRegistry()
u2 = UnitRegistry()
q1 = u1.Quantity(5, 'm')
q2 = u2.Quantity(3, 'm')

try:
    r = q1 + q2
    print("No error:", r)
except Exception as e:
    print(type(e).__name__, ':', e)

try:
    u1.define('meter = 2 * meter')
except Exception as e:
    print("Redefine error:", type(e).__name__, ':', e)

u3 = UnitRegistry(on_redefinition='ignore')
u3.define('meter = 2 * meter')
print("After ignore redefine, 1 meter =", u3.Quantity(1, 'meter').to_base_units())

q = u1.Quantity(1, 'm')
base = q.to_base_units()
print("Base units:", base)
print("Base magnitude:", base.magnitude)
print("Base units str:", format(base.units, '~'))

print("Unit definition raw:", u1._units['meter'].raw)
print("Unit definition reference:", u1._units['meter'].reference)
print("Unit definition converter:", u1._units['meter'].converter)

u1.define('dog_year = 7 * year')
q3 = u1.Quantity(1, 'dog_year')
print("dog_year to base:", q3.to_base_units())
print("dog_year def raw:", u1._units['dog_year'].raw)
