import numpy as np

y1 = np.array(
    [
        7.548,
        7.349,
        7.131,
        6.883,
        6.661,
        6.462,
        6.250,
        6.002,
        5.830,
        5.600,
    ]
)

y2 = np.array(
    [
        7.569,
        7.340,
        7.121,
        6.891,
        6.678,
        6.463,
        6.270,
        6.039,
        5.822,
        5.590,
    ]
)

y = (y1 + y2) / 2
print(y)

x = np.array(range(1, 11))

k = len(x)

sx = np.sum(x)
sy = np.sum(y)
sxx = np.sum(x * x)
sxy = np.sum(x * y)
syy = np.sum(y * y)

# y=a+bx
# b=(sx*sy-k*sxy)/(sx*sx-k*sxx)
# a=(sxy*sx-sy*sxx)/(sx*sx-k*sxx)
# print(a*k+b*sx-sy)
b, a = np.polyfit(x, y, 1)
# print(f'y={a}+{b}x')

r = np.corrcoef(x, y)[0, 1]

ssy = np.sqrt(np.sum((y - (a + b * x)) ** 2) / (k - 2))

uab = b * np.sqrt((1 / r**2 - 1) / (k - 2))
uaa = uab * np.sqrt(sxx / k)

# uby=0.00005/np.sqrt(3)
uby = 0
ubb = uby / np.sqrt(sxx - sx * sx / k)
uba = ubb * np.sqrt(sxx / k)

ua = np.sqrt(uaa * uaa + uba * uba)
ub = np.sqrt(uab * uab + ubb * ubb)

print(f"a={a}±{ua}, b={b}±{ub}")

from uncertainties import unumpy as unp

uy = np.sqrt(ssy * ssy + uby * uby)
y = unp.uarray(y, uy)

sx = x.sum()
sy = y.sum()
sxx = (x * x).sum()
sxy = (x * y).sum()
syy = (y * y).sum()

b = (sx * sy - k * sxy) / (sx * sx - k * sxx)
a = (sxy * sx - sy * sxx) / (sx * sx - k * sxx)
print(f"{a=},{b=}")
