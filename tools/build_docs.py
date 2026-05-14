from __future__ import annotations

import argparse
import importlib
import inspect
import sys
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


DEFAULT_MODULES = [
    "phyexp",
    "phyexp.AB_uncert",
    "phyexp.error",
    "phyexp.meas",
    "phyexp.SLR",
    "phyexp.sigfigs",
    "phyexp.notebook",
    "phyexp.quantity",
]


def _get_doc(obj) -> str:
    doc = inspect.getdoc(obj)
    return doc if doc else "暂无说明。"


def _get_signature(obj) -> str:
    try:
        return str(inspect.signature(obj))
    except (TypeError, ValueError):
        return ""


def _public_names(module) -> list[str]:
    names = getattr(module, "__all__", None)
    if names is not None:
        return list(names)
    return [name for name in dir(module) if not name.startswith("_")]


def _render_module(module_name: str) -> str:
    try:
        module = importlib.import_module(module_name)
    except Exception as exc:
        return "\n".join(
            [
                f"## {module_name}",
                "",
                f"导入失败：{exc}",
                "",
            ]
        )

    lines: list[str] = [f"## {module_name}", ""]

    module_doc = inspect.getdoc(module)
    if module_doc:
        lines.extend([module_doc, ""])

    public_names = _public_names(module)
    if public_names:
        lines.extend(["### 公共符号", ""])

    for name in public_names:
        if not hasattr(module, name):
            continue

        obj = getattr(module, name)
        signature = _get_signature(obj)
        heading = f"#### {name}{signature}" if signature else f"#### {name}"
        lines.extend([heading, ""])
        lines.extend([_get_doc(obj), ""])

    return "\n".join(lines)


def _render_document(module_names: Iterable[str]) -> str:
    lines = [
        "# phyexp 说明文档",
        "",
        "本文件由 `python tools/build_docs.py` 生成。",
        "",
        "## 生成说明",
        "",
        "- 文档来源是各模块的 docstring 和 `__all__`。",
        "- 内部实现细节不会被收进正式文档。",
        "- 重新生成后可直接覆盖本文件。",
        "",
    ]

    try:
        package = importlib.import_module("phyexp")
    except Exception as exc:
        lines.extend(["## phyexp", "", f"导入失败：{exc}", ""])
    else:
        lines.extend(["## 入口", ""])
        for name in ("A_uncert", "uquantity"):
            if hasattr(package, name):
                obj = getattr(package, name)
                signature = _get_signature(obj)
                heading = f"### {name}{signature}" if signature else f"### {name}"
                lines.extend([heading, "", _get_doc(obj), ""])

    for module_name in module_names:
        lines.extend([_render_module(module_name), ""])

    return "\n".join(lines).rstrip() + "\n"


def build_docs(output_path: Path, module_names: Iterable[str]) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(_render_document(module_names), encoding="utf-8")
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Markdown docs for phyexp.")
    parser.add_argument(
        "-o",
        "--output",
        default="docs/api.md",
        help="输出文件路径，默认是 docs/api.md",
    )
    parser.add_argument(
        "modules",
        nargs="*",
        default=DEFAULT_MODULES[1:],
        help="要导出的模块名，默认覆盖当前公开模块。",
    )
    args = parser.parse_args()

    output_path = build_docs(Path(args.output), args.modules)
    print(f"generated {output_path.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())