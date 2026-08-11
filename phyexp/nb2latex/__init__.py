# -*- coding: utf-8 -*-
"""
phyexp.nb2latex — notebook → 可排版 LaTeX 报告生成工具

把实验报告 notebook 转成干净、可继续手改的 LaTeX 文件夹
（report.tex + figures/），配合 xelatex 编译中文 PDF。

用法：
    python -m phyexp.nb2latex 实验报告.ipynb --execute --compile
或：
    from phyexp.nb2latex import convert
    convert("实验报告.ipynb", execute=True, compile_tex=True)
"""

from .convert import convert

__all__ = ["convert"]
__version__ = "0.1.0"
