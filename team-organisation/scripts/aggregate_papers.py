#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from datetime import datetime
from pathlib import Path


TITLE_RE = re.compile(r"^(###)\s+(?:\d+\.\s+)?(.+)$")


def number_papers(section: str) -> str:
    """Add stable numbering to paper headings under each second-level section."""
    lines = section.splitlines()
    if not lines:
        return section

    count = 0
    numbered: list[str] = []
    for line in lines:
        if line.startswith("## "):
            count = 0
            numbered.append(line)
            continue

        match = TITLE_RE.match(line)
        if match:
            count += 1
            numbered.append(f"### {count}. {match.group(2)}")
        else:
            numbered.append(line)
    return "\n".join(numbered)


def read_category_files(categories_dir: Path) -> list[tuple[str, str]]:
    files = sorted(categories_dir.glob("*.md"))
    sections: list[tuple[str, str]] = []
    for path in files:
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            continue
        text = number_papers(text)
        sections.append((path.stem, text))
    return sections


def main() -> int:
    parser = argparse.ArgumentParser(description="Aggregate per-category paper markdown files.")
    parser.add_argument("--categories-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--title", default="论文分类归纳整理")
    args = parser.parse_args()

    sections = read_category_files(args.categories_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        f"# {args.title}",
        "",
        "<!-- 自动生成：请修改 workspace/paper_organisation/categories/ 下的分类 md 后重新运行聚合脚本；用户面向文件位于 Base/Paper_Aggregation/。 -->",
        f"<!-- 更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M')} -->",
        "",
    ]
    if not sections:
        lines.append("暂无分类内容。")
    else:
        for _, section in sections:
            lines.append(section)
            lines.append("")

    args.output.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
