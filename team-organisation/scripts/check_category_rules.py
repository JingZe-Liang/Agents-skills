#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Check whether paper classification rules changed.")
    parser.add_argument("--rules", type=Path, default=Path("workspace/paper_organisation/分类.md"))
    parser.add_argument("--state", type=Path, default=Path("workspace/paper_organisation/state/分类.sha256"))
    parser.add_argument("--update", action="store_true", help="write the current hash after reorganisation")
    args = parser.parse_args()

    if not args.rules.exists():
        print(f"missing: {args.rules}")
        return 2

    current = sha256_file(args.rules)
    previous = args.state.read_text(encoding="utf-8").strip() if args.state.exists() else ""

    if args.update:
        args.state.parent.mkdir(parents=True, exist_ok=True)
        args.state.write_text(current + "\n", encoding="utf-8")
        print(f"updated: {args.state} {current}")
        return 0

    if previous == current:
        print(f"unchanged: {args.rules} {current}")
        return 0

    if previous:
        print(f"changed: {args.rules}")
        print(f"previous: {previous}")
        print(f"current:  {current}")
    else:
        print(f"new: {args.rules} {current}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
