#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


PREFIX_RE = re.compile(r"^(\d{2,})_")


def slugify(text: str) -> str:
    text = re.sub(r"[^A-Za-z0-9]+", "_", text.strip())
    text = re.sub(r"_+", "_", text).strip("_")
    return text or "Paper_Search"


def existing_numbers(*roots: Path) -> list[int]:
    numbers: list[int] = []
    for root in roots:
        if not root.exists():
            continue
        for path in root.iterdir():
            match = PREFIX_RE.match(path.name)
            if match:
                numbers.append(int(match.group(1)))
    return numbers


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize a numbered paper-search workspace.")
    parser.add_argument("purpose", help="short purpose slug, e.g. Majiayi_InfraredFusion")
    parser.add_argument("--base-dir", type=Path, default=Path("Base/Paper_Search"))
    parser.add_argument("--workspace-dir", type=Path, default=Path("workspace/paper_search"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    next_number = max(existing_numbers(args.base_dir, args.workspace_dir), default=0) + 1
    name = f"{next_number:02d}_{slugify(args.purpose)}"
    output = args.base_dir / f"{name}.md"
    workspace = args.workspace_dir / name

    if not args.dry_run:
        args.base_dir.mkdir(parents=True, exist_ok=True)
        (workspace / "notes").mkdir(parents=True, exist_ok=True)
        (workspace / "metadata").mkdir(parents=True, exist_ok=True)
        for file_name in ("evidence.md",):
            path = workspace / file_name
            if not path.exists():
                path.write_text(f"# {file_name.removesuffix('.md')}\n", encoding="utf-8")

    print(json.dumps({"name": name, "output": str(output), "workspace": str(workspace)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
