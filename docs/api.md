# phyexp 说明文档

本文件由 `python tools/build_docs.py` 生成。

## 生成说明

- 文档来源是各模块的 docstring 和 `__all__`。
- 内部实现细节不会被收进正式文档。
- 重新生成后可直接覆盖本文件。

## 入口

### A_uncert(测量值列表)

计算A类不确定度，基于测量值均值的样本标准差（贝塞尔公式）。

参数:
测量值列表: 一组测量值（支持列表、元组、np数组、pint带单位量、pd.Series等可迭代对象）。

返回:
float/np.float64/pint.Quantity: A类不确定度（输入带单位则返回带单位结果）。

### uquantity(n: pint.registry.Quantity, u: pint.registry.Quantity, tag: str = None) -> pint.registry.Quantity

根据输入是标量还是数组，自动选择 `ufloat` 或 `uarray` 构造方式。

## phyexp.AB_uncert

物理实验中涉及的不确定度计算

### 公共符号

#### 可向量化(数字列表)

将非向量化输入尽量转换为可用于数值计算的数组。

#### 输入转换(func)

装饰器：把参数统一转换为适合不确定度计算的向量化输入。

#### generator_to_list_warning(func)

装饰器：如果输入是生成器，则先转成列表并提示一次性迭代风险。

#### 求A类不确定度(测量值列表)

计算A类不确定度，基于测量值均值的样本标准差（贝塞尔公式）。

参数:
测量值列表: 一组测量值（支持列表、元组、np数组、pint带单位量、pd.Series等可迭代对象）。

返回:
float/np.float64/pint.Quantity: A类不确定度（输入带单位则返回带单位结果）。

#### A_uncert(测量值列表)

计算A类不确定度，基于测量值均值的样本标准差（贝塞尔公式）。

参数:
测量值列表: 一组测量值（支持列表、元组、np数组、pint带单位量、pd.Series等可迭代对象）。

返回:
float/np.float64/pint.Quantity: A类不确定度（输入带单位则返回带单位结果）。

#### 仪器误差限转B类不确定度(仪器误差限, 分布='均匀', K=1.7320508075688772)

将仪器误差限转换为B类不确定度。
参数:
仪器误差限: 仪器误差限值（正数）。
分布: 仪器误差的分布类型，支持"均匀"和"正态"。默认值为"均匀"。
K: 如果分布类型未知，可直接提供分布因子K（正数）。默认值为3的平方根（对应均匀分布）。
返回:
float: B类不确定度。

#### InstErr_to_B_uncert(仪器误差限, 分布='均匀', K=1.7320508075688772)

将仪器误差限转换为B类不确定度。
参数:
仪器误差限: 仪器误差限值（正数）。
分布: 仪器误差的分布类型，支持"均匀"和"正态"。默认值为"均匀"。
K: 如果分布类型未知，可直接提供分布因子K（正数）。默认值为3的平方根（对应均匀分布）。
返回:
float: B类不确定度。

#### 不确定度合成(A分量或分量1, B分量或分量2, *更多分量)

计算不确定度合成，基于各分量的不确定度平方和的平方根。
只能处理标量输入和数组输入。

参数:
分量: AB分量。

返回:
float: 合成不确定度。

#### uncert_comb(A分量或分量1, B分量或分量2, *更多分量)

计算不确定度合成，基于各分量的不确定度平方和的平方根。
只能处理标量输入和数组输入。

参数:
分量: AB分量。

返回:
float: 合成不确定度。


## phyexp.error

实验误差

### 公共符号

#### 提取标称值(带不确定度的数值)

提取带不确定度数值的标称值。

参数：
    带不确定度的数值：可以是 `uncertainties` 数值对象，也可以是
        带单位的 `pint.Quantity`。

返回：
    对应的标称值；如果输入带单位，则保留单位。

#### 预处理(func)

装饰器：在调用前把参数中的不确定度对象替换成标称值。

#### 相对误差(测量值, 真值, str: bool = False, n=3)

计算测量值与真值之间的相对误差。

参数：
    测量值：实验测得值。
    真值：参考值或标准值。
    str：是否返回格式化字符串。为 `True` 时返回百分比文本。
    n：字符串模式下保留的小数位数。

返回：
    相对误差的数值或字符串。


## phyexp.meas

测量量

### 公共符号

#### 多次测量结果(数值列表, 单位: str = '', B类不确定度: float = 0.0, 名称: str = '')

根据多次测量值构造带不确定度的物理量。

参数：
    数值列表：测量值序列，或已经带单位的 `pint.Quantity`。
    单位：结果单位。
    B类不确定度：仪器引入的 B 类不确定度。
    名称：不确定度对象的标签。

返回：
    带不确定度的 `pint.Quantity`。

#### quantity_uarray(n: pint.registry.Quantity, u: pint.registry.Quantity) -> pint.registry.Quantity

把数组测量值和不确定度合成为 `uarray` 型 quantity。

#### quantity_ufloat(n: pint.registry.Quantity, u: pint.registry.Quantity, tag: str = None) -> pint.registry.Quantity

把标量测量值和不确定度合成为 `ufloat` 型 quantity。

#### uquantity(n: pint.registry.Quantity, u: pint.registry.Quantity, tag: str = None) -> pint.registry.Quantity

根据输入是标量还是数组，自动选择 `ufloat` 或 `uarray` 构造方式。


## phyexp.SLR

带不确定度的一元线性回归

### 公共符号

#### 提取不确定度(带不确定度的数值)

提取数值对象中的标准不确定度。

#### 一元线性回归(x, y)

带不确定度的一元线性回归
参数:
    x: 自变量数组，元素可以是带不确定度的数值。
    y: 因变量数组，元素必须是带不确定度的数值。

返回:
    截距 a 和斜率 b，与输入同种类。

备注:
    使用加权最小二乘法进行回归，权重为因变量不确定度的倒数。

#### 绘制回归图(x: phyexp.quantity._build_q_class.<locals>.Q_, y: phyexp.quantity._build_q_class.<locals>.Q_, title=None, xlabel=None, ylabel=None)

绘制带不确定度的一元线性回归图
参数:
    x: 自变量数组，元素可以是带不确定度的数值。
    y: 因变量数组，元素必须是带不确定度的数值。
    title: 图标题。
    xlabel: 横轴标签。
    ylabel: 纵轴标签。


## phyexp.sigfigs

### 公共符号

#### 修约(带不确定度数值: uncertainties.core.AffineScalarFunc, 字符串形式=True)

按不确定度的有效数字规则修约数值。

参数：
    带不确定度数值：`uncertainties.UFloat` 对象。
    字符串形式：为 `True` 时返回格式化字符串，否则返回修约后的对象。

返回：
    修约后的字符串或 `UFloat`。

#### u(representation, tag=None)

Create an uncertainties Variable from a string representation.
Several representation formats are supported.

Arguments:
----------
representation: string
    string representation of a value with uncertainty
tag:   string or `None`
    optional tag for tracing and organizing Variables ['None']

Returns:
--------
uncertainties Variable.

Notes:
--------
1. Invalid representations raise a ValueError.

2. Using the form "nominal(std)" where "std" is an integer creates
   a Variable with "std" giving the least significant digit(s).
   That is, "1.25(3)" is the same as `ufloat(1.25, 0.03)`,
   while "1.25(3.)" is the same as `ufloat(1.25, 3.)`

3. If the representation does not contain an uncertainty, an
   uncertainty of 1 in the least significant digit is assigned to
   the nominal value. For nominal values corresponding to "nan", an
   uncertainty of 1 is assigned.

Examples:
-----------

>>> from uncertainties import ufloat_fromstr
>>> x = ufloat_fromstr("12.58+/-0.23")  # = ufloat(12.58, 0.23)
>>> x = ufloat_fromstr("12.58 ± 0.23")  # = ufloat(12.58, 0.23)
>>> x = ufloat_fromstr("3.85e5 +/- 2.3e4")  # = ufloat(3.8e5, 2.3e4)
>>> x = ufloat_fromstr("(38.5 +/- 2.3)e4")  # = ufloat(3.8e5, 2.3e4)

>>> x = ufloat_fromstr("72.1(2.2)")  # = ufloat(72.1, 2.2)
>>> x = ufloat_fromstr("72.15(4)")  # = ufloat(72.15, 0.04)
>>> x = ufloat_fromstr("680(41)e-3")  # = ufloat(0.68, 0.041)
>>> x = ufloat_fromstr("23.2")  # = ufloat(23.2, 0.1)
>>> x = ufloat_fromstr("23.29")  # = ufloat(23.29, 0.01)
>>> x = ufloat_fromstr("nan")  # = ufloat(numpy.nan, 1.0)

>>> x = ufloat_fromstr("680.3(nan)") # = ufloat(680.3, numpy.nan)


## phyexp.notebook

### 公共符号

#### table(data: dict[str, pint.registry.Quantity], title: str = None, index: bool = True, caption: str = None, label: str = None, **kwargs) -> IPython.core.display.Markdown

把列式数据生成 Markdown 表格。

参数：
    data：字典，键为列名，值为列数据序列。
    title：表题。
    index：是否添加索引列。
    caption：表注。
    label：表标签，便于在导出文档中引用。
    kwargs：保留给后续扩展的额外参数。

返回：
    `IPython.display.Markdown` 对象。


## phyexp.quantity

自定义 Pint Quantity 子类，处理跨 ureg 运算兼容性。

当库内 ureg 与用户传入的外部 ureg 的 Quantity 进行运算时，
Pint 默认会抛出 ValueError。本模块提供：
1. Q_ 子类：继承自 pint.Quantity，自动拦截 ureg 冲突并转换
2. ureg_compatible 装饰器：可独立用于装饰可能有 ureg 冲突的函数

### 公共符号

#### set_internal_ureg(ureg)

设置库内部使用的 `ureg` 实例。

#### get_internal_ureg()

返回库内部当前使用的 `ureg` 实例。

#### convert_quantity_to_ureg(q, target_ureg)

把其他 registry 下的 quantity 转换到指定 registry。

#### ureg_compatible(func)

装饰器：尽量把参数转换到内部 `ureg` 后再调用函数。
