# -*- coding: utf-8 -*-
r"""
ast_to_latex.py — pandoc JSON AST → 干净 LaTeX 渲染器

对比 pandoc 内置 LaTeX writer 的改进（都来自实践踩坑）：
- 表格 → 简单 booktabs tabular（p{列宽} 处理多行单元格），不用 longtable+minipage
- 数学 → 原样 \(...\) / \[...\]，不做多余包装
- 输出零 pandoc 专属宏（无 \pandocbounded / \tightlist / \real / \labelenumi）
- 图片 → \includegraphics{路径}，路径由调用方统一改写（img/ 目录）

用法：ast = json.loads(pypandoc.convert_text(src, "json", format="markdown"))
      latex = render_blocks(ast["blocks"])
"""

import re

__all__ = ["render_blocks", "render_inlines"]


# ---------------------------------------------------------------------------
# 文本转义（普通文本中的 LaTeX 特殊字符）
# ---------------------------------------------------------------------------

_ESCAPE_MAP = [
    ("\\", r"\textbackslash{}"),
    ("&", r"\&"),
    ("%", r"\%"),
    ("#", r"\#"),
    ("_", r"\_"),
    ("{", r"\{"),
    ("}", r"\}"),
    ("~", r"\textasciitilde{}"),
    ("^", r"\textasciicircum{}"),
]


def _escape(s):
    for ch, rep in _ESCAPE_MAP:
        s = s.replace(ch, rep)
    return s


# ---------------------------------------------------------------------------
# 内联节点
# ---------------------------------------------------------------------------

def render_inlines(inlines):
    """内联节点列表 → LaTeX（不含数学块级处理）。"""
    return "".join(_inline(i) for i in inlines)


def _inline(n):
    t, c = n["t"], n.get("c")
    if t == "Str":
        return _escape(c)
    if t == "Space":
        return " "
    if t == "SoftBreak":
        return " "
    if t == "LineBreak":
        return "\\\\\n"
    if t in ("Emph", "Underline"):
        return r"\emph{" + render_inlines(c) + "}"
    if t == "Strong":
        return r"\textbf{" + render_inlines(c) + "}"
    if t == "Strikeout":
        return r"\sout{" + render_inlines(c) + "}"   # 需要 ulem 包
    if t == "Code":
        return r"\texttt{" + _escape(c[1]) + "}"
    if t == "Math":
        kind, tex = c
        # 行内数学里嵌多行环境（split/aligned/cases/array）→ 提升为 display 块
        needs_display = any(env in tex for env in
                            ("\\begin{split}", "\\begin{aligned}", "\\begin{alignedat}",
                             "\\begin{cases}", "\\begin{matrix}", "\\begin{array}"))
        if kind == "DisplayMath" or needs_display:
            return "\n\n\\[\n" + tex + "\n\\]\n\n"
        return r"\(" + tex + r"\)"
    if t == "Link":
        return render_inlines(c[1])
    if t == "Image":
        # 内联图片：c = [attrs, caption, [src, title]]
        return r"\includegraphics[width=0.85\linewidth]{" + c[2][0] + "}"
    if t == "RawInline":
        fmt, text = c
        return text if fmt in ("latex", "tex") else ""
    if t == "Note":          # 脚注：渲染成普通文本
        return render_blocks(c[0])
    if t == "Span":
        return render_inlines(c[1])
    if t == "Cite":
        return render_inlines(c[1])
    return ""


# ---------------------------------------------------------------------------
# 块级节点
# ---------------------------------------------------------------------------

def render_blocks(blocks):
    """块级节点列表 → LaTeX 字符串。"""
    return "\n\n".join(_block(b) for b in blocks if _block(b).strip())


def _block(n):
    t, c = n["t"], n.get("c")
    if t == "Header":
        level, attrs, inlines = c
        cmd = {1: "section", 2: "subsection", 3: "subsubsection",
               4: "paragraph", 5: "subparagraph", 6: "subparagraph"}.get(level, "subsubsection")
        return "\\" + cmd + "{" + render_inlines(inlines) + "}"
    if t == "Para":
        return render_inlines(c)
    if t == "Plain":
        return render_inlines(c)
    if t == "CodeBlock":
        return "\\begin{lstlisting}\n" + c[1].rstrip("\n") + "\n\\end{lstlisting}"
    if t == "BulletList":
        items = "".join("\\item " + render_blocks(li).replace("\n", " ") + "\n" for li in c)
        return "\\begin{itemize}\n" + items + "\\end{itemize}"
    if t == "OrderedList":
        items = "".join("\\item " + render_blocks(li).replace("\n", " ") + "\n" for li in c[1])
        return "\\begin{enumerate}\n" + items + "\\end{enumerate}"
    if t == "BlockQuote":
        return "\\begin{quote}\n" + render_blocks(c) + "\n\\end{quote}"
    if t == "HorizontalRule":
        return "\\medskip\\hrule\\medskip"
    if t == "RawBlock":
        fmt, text = c
        return text if fmt in ("latex", "tex") else ""
    if t == "Div":
        return render_blocks(c[1])
    if t == "LineBlock":
        lines = "\\\\\n".join(render_inlines(li) for li in c)
        return lines
    if t == "Table":
        return _render_table(c)
    if t == "Figure":
        # pandoc 3.x：c = [attrs, caption, [blocks]]，内部是 Image
        attrs, caption, figblocks = c
        return render_blocks(figblocks)
    if t == "DefinitionList":
        out = []
        for term, defs in c:
            out.append("\\paragraph{" + render_inlines(term) + "}")
            for d in defs:
                out.append(render_blocks(d))
        return "\n".join(out)
    if t == "Null":
        return ""
    # 未知节点：递归尝试渲染内容
    if isinstance(c, list):
        try:
            return render_blocks(c) if all(isinstance(x, dict) and "t" in x for x in c) else render_inlines(c)
        except Exception:
            return ""
    return ""


def _render_table(c):
    """pandoc Table：c = [caption, aligns, widths, headers, rows] → booktabs tabular。

    用 p{列宽} 处理多行单元格（无需 longtable+minipage），
    单元格内的块级内容（如多段落）合并为单段。"""
    caption, aligns, widths, headers, rows = c

    ncols = len(headers)
    if ncols == 0:
        ncols = max((len(r) for r in rows), default=0)
    if ncols == 0:
        return ""

    # 列格式：有宽度 → p{宽度\linewidth}；否则按对齐
    specs = []
    for i in range(ncols):
        w = widths[i] if i < len(widths) else 0.0
        a = aligns[i] if i < len(aligns) else {"t": "AlignDefault"}
        align = "l" if a["t"] == "AlignLeft" else ("r" if a["t"] == "AlignRight" else "c")
        if w and w > 0:
            specs.append(f">{{\\raggedright\\arraybackslash}}p{{{w}\\linewidth}}")
        else:
            specs.append(align)

    out = ["\\begin{table}[H]", "\\centering",
           "\\begin{tabular}{" + "".join(specs) + "}", "\\toprule"]
    out.append(" & ".join(_cell(h) for h in headers) + " \\\\")
    out.append("\\midrule")
    for row in rows:
        cells = list(row[:ncols])
        while len(cells) < ncols:
            cells.append([{"t": "Str", "c": ""}])
        out.append(" & ".join(_cell(h) for h in cells) + " \\\\")
    out.append("\\bottomrule")
    out.append("\\end{tabular}")
    if caption and caption[1]:
        out.append("\\caption{" + render_inlines(caption[1]) + "}")
    out.append("\\end{table}")
    return "\n".join(out)


def _cell(inlines):
    """表格单元格：内联列表 → LaTeX；块级内容合并。"""
    return render_inlines(inlines)
