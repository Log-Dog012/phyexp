from phyexp.AB_uncert import 不确定度合成
from numpy import array as arr
from numpy import isclose

assert 不确定度合成(3,4)==5
assert isclose(不确定度合成(0.3,0.4),0.5)
assert all(isclose(不确定度合成(arr([0.3,0.4]),arr([0.4,0.3])),arr([0.5,0.5])))
assert all(isclose(不确定度合成(arr([3,3]),4,arr([12,12])),arr([13,13])))
assert all(isclose(不确定度合成(2,3,arr([4,5]),arr([5,4])),arr([54,54])**0.5)),不确定度合成(2,3,arr([4,5]),arr([5,4]))

print('All tests passed!')