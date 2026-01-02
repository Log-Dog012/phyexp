from phyexp import A_uncert
from phyexp.utils import ureg
import numpy as np

# 公式验证
# 上册P63 D,C
D = np.array(
    [0.803, 0.800, 0.801, 0.803, 0.800, 0.801, 0.803, 0.800, 0.799, 0.801]
) * ureg("mm")
print(f"答案0.8011000000000001 millimeter：{D.mean()}")
print(f"答案0.0004582575694955844 millimeter：{A_uncert(D)}")
C = np.array([1.590, 1.580, 1.570, 1.610, 1.580, 1.585, 1.595, 1.575]) * ureg("cm")
print(f"答案1.5856249999999998 centimeter：{C.mean()}")
print(f"答案0.004475877806962248 centimeter：{A_uncert(C)}")

# 边界情况
A_uncert(i for i in range(10))  # 生成器输入
A_uncert([1, 2, 3])  # 列表输入
