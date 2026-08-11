# -*- coding: utf-8 -*-
r"""
markdown_latex.py — 实验报告 notebook 的 Markdown 子集 → LaTeX 渲染器

只处理实验报告实际会用到的元素，刻意保持小而可预测：

- 标题 `#` / `##` / `###`  →  \section / \subsection / \subsubsection
- 段落、**粗体**、*斜体*、`行内代码`、[链接](url)
- 行内公式 `$...$`、块级公式 `$$...$$`（原样传给 LaTeX）
- GFM 表格 → booktabs 的 tabular
- 图片 `![说明](路径)` → figure 环境
- 无序/有序列表
- 围栏代码块 → lstlisting
- 分隔线、引用块、HTML 注释 → 忽略/精简处理

设计原则：
- 公式片段（$...$、$$...$$）原样透传，不转义；
- 普通文本中的 LaTeX 特殊字符统一转义；
- 输出是「干净、可继续手改」的 LaTeX，不引入 pandoc/nbconvert 模板噪音。
"""

import re

__all__ = ["md_to_latex", "escape_latex"]


# ---------- 转义 ----------

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


def _escape_plain(s: str) -> str:
    for ch, rep in _ESCAPE_MAP:
        s = s.replace(ch, rep)
    return s


def escape_latex(s: str) -> str:
    """转义普通文本；`$...$` 行内公式片段保持原样。"""
    parts = re.split(r"(\$[^$\n]+\$)", s)
    return "".join(p if (p.startswith("$") and p.endswith("$") and len(p) > 1)
                   else _escape_plain(p) for p in parts)


_INLINE_PATTERNS = [
    # 行内代码（先处理，避免与粗体冲突）
    (re.compile(r"`([^`]+)`"), lambda m: r"\texttt{" + m.group(1) + "}"),
    # **粗体**
    (re.compile(r"\*\*([^*]+)\*\*"), lambda m: r"\textbf{" + m.group(1) + "}"),
    # *斜体*
    (re.compile(r"(?<!\*)\*([^*\n]+)\*(?!\*)"), lambda m: r"\textit{" + m.group(1) + "}"),
    # [文字](url) → 保留文字（报告里链接少见）
    (re.compile(r"\[([^\]]+)\]\([^)]+\)"), lambda m: m.group(1)),
]

_PLACEHOLDER_RE = re.compile(r"\x00F(\d+)\x00")


def _inline_and_escape(s: str) -> str:
    """普通文本 → LaTeX：先保护行内公式（占位符），转义普通字符，
    再做行内标记替换，最后恢复公式。顺序保证标记产生的 \\textbf 等不被破坏。"""
    formulas = []

    def _save(m):
        formulas.append(m.group(0))
        return "\x00F%d\x00" % (len(formulas) - 1)

    s = re.sub(r"\$[^$\n]+\$", _save, s)
    s = _escape_plain(s)
    for pat, rep in _INLINE_PATTERNS:
        s = pat.sub(rep, s)

    def _restore(m):
        return formulas[int(m.group(1))]

    return _PLACEHOLDER_RE.sub(_restore, s)


# ---------- 块级元素 ----------

_TITLE_RE = re.compile(r"^(#{1,6})\s+(.*)$")
_UL_RE = re.compile(r"^\s*[-*+]\s+(.*)$")
_OL_RE = re.compile(r"^\s*\d+[.)]\s+(.*)$")
_IMG_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
_FENCE_RE = re.compile(r"^```(\w*)\s*$")
_HR_RE = re.compile(r"^\s*([-*_])\1{2,}\s*$")


def _table(lines):
    """解析 GFM 表格（从分隔行开始）：
    | a | b |
    |---|---|
    | 1 | 2 |
    返回 (table_latex, 剩余行)。
    """
    header = lines[0]
    sep = lines[1]
    cols = [c.strip() for c in header.strip().strip("|").split("|")]
    # 对齐：左 :--- / 中 :---: / 右 ---:
    aligns = []
    for c in sep.strip().strip("|").split("|"):
        c = c.strip()
        if c.startswith(":") and c.endswith(":"):
            aligns.append("c")
        elif c.endswith(":"):
            aligns.append("r")
        elif c.startswith(":"):
            aligns.append("l")
        else:
            aligns.append("c")
    spec = "".join(aligns) if len(aligns) == len(cols) else "c" * len(cols)

    rows = []
    i = 2
    while i < len(lines):
        line = lines[i]
        if "|" not in line:
            break
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < len(cols):
            cells += [""] * (len(cols) - len(cells))
        rows.append(cells[:len(cols)])
        i += 1

    out = ["\\begin{table}[H]", "\\centering",
           "\\begin{tabular}{" + spec + "}",
           "\\toprule"]
    out.append(" & ".join(_inline_and_escape(c) for c in cols) + " \\\\")
    out.append("\\midrule")
    for r in rows:
        out.append(" & ".join(_inline_and_escape(c) for c in r) + " \\\\")
    out.append("\\bottomrule")
    out.append("\\end{tabular}")
    out.append("\\end{table}")
    return "\n".join(out), lines[i:]


def _image_to_latex(alt, path):
    alt_l = escape_latex(alt) if alt else ""
    p = path.replace("\\", "/")
    cap = "\\caption{" + alt_l + "}" if alt_l else "% no caption"
    return ("\\begin{figure}[H]\n\\centering\n"
            "\\includegraphics[width=0.85\\linewidth]{" + p + "}\n"
            + cap + "\n\\end{figure}")


def md_to_latex(md: str, fig_prefix: str = "") -> str:
    """把一段 Markdown 文本渲染为 LaTeX。

    fig_prefix: 图片路径前可加前缀（例如输出目录里图片被拷贝到 figures/）。
    返回 LaTeX 源码字符串。
    """
    lines = md.splitlines()
    out = []
    i = 0
    n = len(lines)
    in_list_ul = False
    in_list_ol = False

    def close_list():
        nonlocal in_list_ul, in_list_ol
        if in_list_ul:
            out.append("\\end{itemize}")
            in_list_ul = False
        if in_list_ol:
            out.append("\\end{enumerate}")
            in_list_ol = False

    while i < n:
        line = lines[i]
        stripped = line.strip()

        # 空行：段落分隔
        if not stripped:
            close_list()
            out.append("")
            i += 1
            continue

        # 围栏代码块
        m = _FENCE_RE.match(stripped)
        if m:
            close_list()
            lang = m.group(1) or "python"
            i += 1
            code = []
            while i < n and not _FENCE_RE.match(lines[i].strip()):
                code.append(lines[i])
                i += 1
            i += 1  # 跳过结束围栏
            out.append("\\begin{lstlisting}[language=" + lang + "]")
            out.extend(code)
            out.append("\\end{lstlisting}")
            continue

        # 块级公式 $$...$$（单行或多行）
        if stripped.startswith("$$"):
            close_list()
            if stripped.endswith("$$") and len(stripped) > 4:
                out.append("\\[" + stripped[2:-2].strip() + "\\]")
                i += 1
                continue
            body = []
            i += 1
            if stripped[2:].strip():
                body.append(stripped[2:].strip())
            while i < n and "$$" not in lines[i]:
                body.append(lines[i])
                i += 1
            if i < n:
                tail = lines[i].split("$$")[0].strip()
                if tail:
                    body.append(tail)
                i += 1
            out.append("\\begin{equation*}")
            out.extend(body)
            out.append("\\end{equation*}")
            continue

        # 表格（当前行含 | 且下一行是分隔行）
        if "|" in line and i + 1 < n and re.match(r"^\s*\|?[\s:\-|]+\|?\s*$", lines[i + 1]) \
                and "-" in lines[i + 1]:
            close_list()
            tbl, rest = _table(lines[i:])
            out.append(tbl)
            i = n - len(rest)
            continue

        # 标题
        m = _TITLE_RE.match(stripped)
        if m:
            close_list()
            level = len(m.group(1))
            cmd = {1: "section", 2: "subsection", 3: "subsubsection",
                   4: "paragraph", 5: "subparagraph", 6: "subparagraph"}[level]
            out.append("\\" + cmd + "{" + _inline_and_escape(m.group(2)) + "}")
            i += 1
            continue

        # 分隔线
        if _HR_RE.match(stripped):
            close_list()
            out.append("\\medskip\\hrule\\medskip")
            i += 1
            continue

        # 列表项
        m = _UL_RE.match(line)
        if m:
            if not in_list_ul:
                close_list()
                out.append("\\begin{itemize}")
                in_list_ul = True
            out.append("\\item " + _inline_and_escape(m.group(1)))
            i += 1
            continue
        m = _OL_RE.match(line)
        if m:
            if not in_list_ol:
                close_list()
                out.append("\\begin{enumerate}")
                in_list_ol = True
            out.append("\\item " + _inline_and_escape(m.group(1)))
            i += 1
            continue

        # 普通段落（可能含图片）
        close_list()
        text = _inline_and_escape(line)
        # 图片：整行只有图片 → 独立 figure；行内混排 → 直接 includegraphics
        if _IMG_RE.search(line):
            segs = re.split(r"(!\[[^\]]*\]\([^)]+\))", line)
            pieces = []
            for seg in segs:
                mm = _IMG_RE.match(seg)
                if mm:
                    pieces.append("\\includegraphics[width=0.85\\linewidth]{"
                                  + fig_prefix + mm.group(2).replace("\\", "/") + "}")
                elif seg:
                    pieces.append(_inline_and_escape(seg))
            out.append(" ".join(pieces))
        elif text:
            out.append(text)
        i += 1

    close_list()
    return "\n".join(out)


if __name__ == "__main__":
    import sys
    demo = """# 标题测试

这是**粗体**和*斜体*，还有 `行内代码`，行内公式 $e = mc^2$。

$$\\frac{1}{2}mv^2$$

| 次数 | 时间 $t$/s |
|------|-----------|
| 1    | 10.61     |
| 2    | 10.57     |

- 第一项
- 第二项

```python
x = 1 + 2
print(x)
```
"""
    print(md_to_latex(demo))
