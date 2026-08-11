# -*- coding: utf-8 -*-
"""
convert.py — notebook → 可排版 LaTeX 的主转换器

用途：把实验报告 notebook（.ipynb）转成「干净、可继续手改」的 LaTeX 文件夹，
包含 report.tex + figures/（图片目录），配合 xelatex 编译成中文 PDF。

CLI：python -m phyexp.nb2latex notebook.ipynb [选项]
API：from phyexp.nb2latex import convert; convert("nb.ipynb")

对比 jupyter nbconvert --to latex 的改进：
- preamble 干净（ctexart + 少量宏包），没有 pandoc/nbconvert 模板噪音
- markdown 的公式、表格、图片按报告习惯排版（公式用 LaTeX、表格用 booktabs）
- 代码 cell 用 listings（可整体隐藏，公式计分靠 LaTeX 公式而不是代码）
- 输出图片自动提取到 figures/；执行输出按 verbatim 呈现
- 核心转换零第三方依赖（标准库 json + re），--execute 才需要 nbclient
"""

import base64
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

try:
    from .markdown_latex import md_to_latex
except ImportError:  # 直接运行脚本时
    from markdown_latex import md_to_latex

__all__ = ["convert"]

# ---------------------------------------------------------------------------
# preamble 模板：干净、聚焦实验报告
# ---------------------------------------------------------------------------

PREAMBLE = r"""\documentclass[11pt]{ctexart}

% ---- 数学 ----
\usepackage{amsmath, amssymb}

% ---- 表格 ----
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{array}    % \arraybackslash（pandoc longtable 需要）

% ---- 图片 ----
\usepackage{graphicx}
\usepackage{float}

% ---- 页面 ----
\usepackage{geometry}
\geometry{a4paper, top=2.5cm, bottom=2.5cm, left=2.5cm, right=2.5cm}

% ---- 代码 ----
\usepackage{xcolor}
\usepackage{listings}
\lstset{
  basicstyle=\heiti\ttfamily\footnotesize, % \heiti 保证代码内中文（注释/字符串）正常显示
  frame=single,
  breaklines=true,
  numbers=left,
  numberstyle=\tiny\color{gray},
  numbersep=5pt,
  keywordstyle=\color{blue},
  commentstyle=\color{green!50!black},
  stringstyle=\color{red},
  aboveskip=0.8em,
  belowskip=0.8em,
  captionpos=b,
}

% ---- 超链接 ----
\usepackage{hyperref}
\hypersetup{colorlinks=true, linkcolor=blue, urlcolor=blue}

% ---- pandoc 输出兼容 ----
% pandoc 用 \pandocbounded 包裹图片、\tightlist 控制紧凑列表、
% \real 表示比例数值，这些宏在 pandoc 模板的 preamble 中定义，这里补齐
\providecommand{\pandocbounded}[1]{\begingroup\centering #1\endgroup}
\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
\providecommand{\passthrough}[1]{#1}
\providecommand{\real}[1]{#1}
\def\labelenumi{\arabic{enumi}.}
\def\labelenumii{\alph{enumii}.}
\def\labelenumiii{\roman{enumiii}.}
"""

BODY_OPEN = r"""
\begin{document}
"""

BODY_CLOSE = r"""
\end{document}
"""


def _preamble(title=None, author=None):
    out = [PREAMBLE]
    if title or author:
        out.append("\\title{" + (title or "") + "}")
        out.append("\\author{" + (author or "") + "}")
        out.append("\\date{\\today}")
        out.append("\\maketitle")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# notebook 读取与执行
# ---------------------------------------------------------------------------

def _load_nb(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _execute_nb(nb, kernel="python3", timeout=600):
    """用 nbclient 执行 notebook，返回带输出的 notebook dict。"""
    try:
        import nbformat
        from nbclient import NotebookClient
    except ImportError:
        raise RuntimeError("--execute 需要 nbclient 与 nbformat，请先：pip install nbclient nbformat")
    nbf = nbformat.from_dict(nb)
    client = NotebookClient(nbf, timeout=timeout, kernel_name=kernel)
    client.execute()
    return json.loads(nbformat.writes(nbf))


# ---------------------------------------------------------------------------
# cell 渲染
# ---------------------------------------------------------------------------

def _sanitize_md(src):
    """pandoc 预处理：
    1. 独立的 `---` 行（水平线）会被误判为 simple table 边界 → 换成 `***`；
    2. pipe table 前若无空行，pandoc 不识别表格 → 自动补空行；
    3. 表格分隔行（--- 且含 |）不受影响。"""
    lines = src.splitlines()
    out = []
    for ln in lines:
        if re.match(r"^\s*\|", ln) and out and out[-1].strip() \
                and not re.match(r"^\s*\|", out[-1]):
            out.append("")          # 表格块开始前补空行
        if re.match(r"^\s*---\s*$", ln):
            ln = "***"              # 水平线无歧义写法
        out.append(ln)
    return "\n".join(out)


def _fix_inline_display(s):
    """pandoc 有时把多行数学（含 \\\\ 或 \\begin{aligned} 等）输出成
    行内 \\(...\\)，这在 LaTeX 中非法；检测到则提升为 \\[...\\]
    并删除块内空行（display math 中不允许空段落）。"""
    def _repl(m):
        body = m.group(1)
        if "\\\\" in body or "\\begin{" in body or "\\begin{align" in body:
            body = re.sub(r"\n\s*\n", "\n", body)
            return "\\[" + body + "\\]"
        return m.group(0)
    return re.sub(r"\\\((.*?)\\\)", _repl, s, flags=re.S)


def _render_markdown(src, backend="pandoc"):
    """markdown → LaTeX。

    默认走 pandoc JSON AST + 自写渲染器（ast_to_latex）：
    - 输出干净 LaTeX，无 pandoc 专属宏（\real/\pandocbounded 等）
    - 表格 → 简单 booktabs tabular（不用 longtable+minipage）
    不可用时回退内置渲染器（markdown_latex）。
    """
    if not src.strip():
        return ""
    if backend == "pandoc":
        try:
            import json
            import pypandoc
            from .ast_to_latex import render_blocks
            ast = json.loads(pypandoc.convert_text(
                _sanitize_md(src), "json", format="markdown"))
            return render_blocks(ast.get("blocks", []))
        except (ImportError, OSError, RuntimeError, ValueError) as e:
            print(f"[警告] pandoc AST 渲染失败（{e}），回退到内置渲染器。", file=sys.stderr)
    return md_to_latex(src)


def _as_text(t):
    """nbformat 的文本字段可能是 str 或 list[str]，统一成 str。"""
    if isinstance(t, list):
        return "".join(t)
    return str(t)


def _render_outputs(outputs, out_dir, cell_idx):
    """输出 cell → LaTeX：文本走 verbatim，图片提取到 figures/。"""
    lines = []
    for oi, out in enumerate(outputs):
        otype = out.get("output_type")
        if otype == "stream":
            text = _as_text(out.get("text", ""))
            lines.append("\\begin{verbatim}" + text.rstrip("\n") + "\n\\end{verbatim}")
        elif otype in ("execute_result", "display_data"):
            data = out.get("data", {})
            if "image/png" in data:
                fig = f"output_{cell_idx}_{oi}.png"
                (out_dir / "img" / fig).write_bytes(base64.b64decode(data["image/png"]))
                lines.append(
                    "\\begin{figure}[H]\n\\centering\n"
                    f"\\includegraphics[width=0.85\\linewidth]{{img/{fig}}}\n"
                    "\\end{figure}")
            elif "text/plain" in data:
                text = _as_text(data["text/plain"])
                lines.append("\\begin{verbatim}" + text.rstrip("\n") + "\n\\end{verbatim}")
            # text/html（如 DataFrame）暂不转换，需要时可用 pandoc 后端
        elif otype == "error":
            ename = out.get("ename", "Error")
            evalue = _as_text(out.get("evalue", ""))
            lines.append(f"\\begin{{verbatim}}{ename}: {evalue}\n\\end{{verbatim}}")
    return lines


_MD_IMG_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")


def _svg_to_png(src, dst):
    """把 svg 转 png（依次尝试系统工具与 python 库），成功返回 True。"""
    for tool, args in [
        ("rsvg-convert", ["-w", "1200", "-o"]),
        ("magick", ["-density", "150"]),
        ("inkscape", ["-z", "-w", "1200", "-o"]),
    ]:
        if shutil.which(tool):
            try:
                if tool == "magick":
                    subprocess.run([tool, *args, str(src), str(dst)], check=True,
                                   capture_output=True, timeout=120)
                else:
                    subprocess.run([tool, *args, str(dst), str(src)], check=True,
                                   capture_output=True, timeout=120)
                return dst.exists()
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                continue
    # 最后试 python 库 cairosvg（pip install cairosvg）
    try:
        import cairosvg
        cairosvg.svg2png(url=str(src), write_to=str(dst), output_width=1200)
        return dst.exists()
    except Exception:
        return False


def _copy_md_images(nb, nb_dir, out_dir):
    """把 markdown cell 引用的本地图片复制到 out_dir/img/（保留相对结构），
    svg 尝试转 png。返回路径映射 {markdown 引用路径: 输出路径}，
    供 tex 中 \\includegraphics 路径改写。"""
    mapping = {}
    img_dir = out_dir / "img"
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "markdown":
            continue
        src = cell.get("source", "")
        if isinstance(src, list):
            src = "".join(src)
        for m in _MD_IMG_RE.finditer(src):
            p = m.group(1).split()[0].replace("\\", "/")
            if p.startswith(("http://", "https://", "data:")):
                continue
            cand = nb_dir / p
            if not cand.exists():
                print(f"[警告] markdown 引用的图片不存在：{cand}", file=sys.stderr)
                continue
            rel = cand.relative_to(nb_dir)
            if cand.suffix.lower() == ".svg":
                png_rel = rel.with_suffix(".png")
                dest = img_dir / png_rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                if not dest.exists():
                    if _svg_to_png(cand, dest):
                        print(f"[转换] svg → png：{rel} → img/{png_rel}", file=sys.stderr)
                        mapping[p] = f"img/{png_rel.as_posix()}"
                    else:
                        print(f"[警告] svg 转换失败（rsvg-convert/magick/inkscape/cairosvg 均不可用），"
                              f"tex 将直接引用 svg：{rel}", file=sys.stderr)
                        dest = img_dir / rel
                        mapping[p] = f"img/{rel.as_posix()}"
                else:
                    mapping[p] = f"img/{png_rel.as_posix()}"
            else:
                dest = img_dir / rel
                if not dest.exists():
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(cand, dest)
                mapping[p] = f"img/{rel.as_posix()}"
    return mapping


_IMGINC_RE = re.compile(r"\\includegraphics(\[[^\]]*\])?\{([^}]+)\}")


def _rewrite_img_paths(tex_body, mapping):
    """把 tex 中 \\includegraphics{...} 的路径按映射改写为 img/ 下路径。"""
    def repl(m):
        opts, path = m.group(1) or "", m.group(2)
        newpath = mapping.get(path, path)
        return f"\\includegraphics{opts}{{{newpath}}}"
    return _IMGINC_RE.sub(repl, tex_body)


# ---------------------------------------------------------------------------
# 主转换
# ---------------------------------------------------------------------------

def convert(notebook_path, out_dir=None, execute=False, hide_code=False,
            title=None, author=None, md_backend="self", compile_tex=False,
            kernel="python3", timeout=600):
    """把 notebook 转成可排版的 LaTeX，输出到 notebook 同目录。

    输出结构（默认，可 --out 覆盖）：
        <notebook 名>.tex   # 成品：可拖到 Overleaf 或本地 xelatex 编译
        <notebook 名>.pdf   # --compile 时的编译产物
        img/                # 全部图片（markdown 引用原图 + 代码输出图）
        build.bat/sh        # 一键编译脚本

    参数：
        notebook_path: .ipynb 文件路径
        out_dir: 输出目录（默认 notebook 所在目录）
        execute: 是否用 nbclient 重新执行 notebook（需要 nbclient）
        hide_code: 隐藏全部代码 cell（只留输出，适合最终报告）
        title / author: 文档标题 / 作者（可选，默认不生成标题页）
        md_backend: "pandoc"（默认，需 pypandoc）或 "self"（内置渲染器）
        compile_tex: 转换后立即用 latexmk/xelatex 编译 PDF
        kernel: 执行 notebook 的 kernel 名
        timeout: 执行超时（秒）

    返回：
        生成的 .tex 路径（Path）。
    """
    nb_path = Path(notebook_path)
    if not nb_path.exists():
        raise FileNotFoundError(f"notebook 不存在：{nb_path}")

    nb = _load_nb(nb_path)
    if execute:
        print(f"[1/4] 执行 notebook（kernel={kernel}）…", file=sys.stderr)
        nb = _execute_nb(nb, kernel=kernel, timeout=timeout)

    if out_dir is None:
        out_dir = nb_path.parent
    out_dir = Path(out_dir)
    (out_dir / "img").mkdir(parents=True, exist_ok=True)

    # markdown 引用的本地图片 → 复制到 img/（svg 转 png），返回路径映射
    img_map = _copy_md_images(nb, nb_path.parent, out_dir)

    print(f"[2/4] 渲染 cell → LaTeX（markdown 后端：{md_backend}）…", file=sys.stderr)
    body = []
    for idx, cell in enumerate(nb.get("cells", [])):
        ctype = cell.get("cell_type")
        src = cell.get("source", "")
        if isinstance(src, list):
            src = "".join(src)

        if ctype == "markdown":
            latex = _render_markdown(src, md_backend)
            if latex.strip():
                body.append(latex)
        elif ctype == "code":
            if not hide_code:
                body.append("\\begin{lstlisting}")
                body.append(src.rstrip("\n"))
                body.append("\\end{lstlisting}")
            body.extend(_render_outputs(cell.get("outputs", []), out_dir, idx))

    body_tex = _rewrite_img_paths("\n\n".join(body), img_map)
    tex = (_preamble(title, author) + BODY_OPEN + "\n\n"
           + body_tex + "\n\n" + BODY_CLOSE)
    tex_path = out_dir / (nb_path.stem + ".tex")
    tex_path.write_text(tex, encoding="utf-8")

    # 编译脚本（方便用户手动改完再编译）
    _write_build_script(out_dir, nb_path.stem)

    print(f"[3/4] 已生成：{tex_path}", file=sys.stderr)
    if compile_tex:
        print("[4/4] 编译 PDF…", file=sys.stderr)
        ok = _compile(tex_path)
        if not ok:
            print("[警告] PDF 编译失败，请检查 LaTeX 日志。", file=sys.stderr)
    return tex_path


def _write_build_script(out_dir, stem):
    """生成 build.sh / build.bat，用户改完 tex 后可一键编译。"""
    if sys.platform == "win32":
        script = out_dir / "build.bat"
        script.write_text(
            f"@echo off\r\nlatexmk -xelatex -interaction=nonstopmode {stem}.tex\r\n",
            encoding="utf-8")
    else:
        script = out_dir / "build.sh"
        script.write_text(f"#!/bin/sh\nlatexmk -xelatex -interaction=nonstopmode {stem}.tex\n",
                          encoding="utf-8")
        script.chmod(0o755)


def _compile(tex_path):
    cwd = tex_path.parent
    stem = tex_path.stem
    candidates = [
        ["latexmk", "-f", "-xelatex", "-interaction=nonstopmode", tex_path.name],
        ["xelatex", "-interaction=nonstopmode", tex_path.name],
    ]
    for cmd in candidates:
        try:
            r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=300)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
        if r.returncode == 0 and (cwd / (stem + ".pdf")).exists():
            return True
    return False


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(
        description="notebook → 可排版 LaTeX（phyexp 报告生成工具）")
    ap.add_argument("notebook", help=".ipynb 文件路径")
    ap.add_argument("--out", default=None, help="输出目录（默认 <名字>_report/）")
    ap.add_argument("--execute", action="store_true", help="重新执行 notebook（需 nbclient）")
    ap.add_argument("--hide-code", action="store_true", help="隐藏代码 cell，只留输出")
    ap.add_argument("--title", default=None, help="报告标题")
    ap.add_argument("--author", default=None, help="作者")
    ap.add_argument("--md-backend", default="pandoc", choices=["pandoc", "self"],
                    help="markdown 渲染后端（默认 pandoc，需 pypandoc）")
    ap.add_argument("--compile", action="store_true", help="转换后编译 PDF")
    ap.add_argument("--kernel", default="python3", help="执行 notebook 的 kernel")
    args = ap.parse_args()

    tex = convert(args.notebook, out_dir=args.out, execute=args.execute,
                  hide_code=args.hide_code, title=args.title, author=args.author,
                  md_backend=args.md_backend, compile_tex=args.compile,
                  kernel=args.kernel)
    print(f"\n完成：{tex}\n可用 build.bat / build.sh 编译，或直接 xelatex report.tex")
