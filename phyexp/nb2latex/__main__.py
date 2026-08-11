# -*- coding: utf-8 -*-
"""python -m phyexp.nb2latex 入口。"""

if __name__ == "__main__":
    from .convert import convert
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
