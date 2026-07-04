#!/usr/bin/env python3
"""Initialize a project-local Codex-Paper workspace safely and idempotently."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable


MODULES = [
    "Abstract",
    "Introduction",
    "RelatedWork",
    "Method",
    "Experiments",
    "Conclusion",
    "Appendix",
    "Citation",
]

SECTION_FILES = {
    "abstract": "abstract.tex",
    "introduction": "introduction.tex",
    "related_work": "related_work.tex",
    "method": "method.tex",
    "experiments": "experiments.tex",
    "conclusion": "conclusion.tex",
    "appendix": "appendix.tex",
}

MAIN_TEX = r"""\documentclass{article}

\begin{document}

\input{sections/abstract}
\input{sections/introduction}
\input{sections/related_work}
\input{sections/method}
\input{sections/experiments}
\input{sections/conclusion}
\input{sections/appendix}

\bibliographystyle{plain}
\bibliography{refs}

\end{document}
"""


def skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


def is_nonempty_file(path: Path) -> bool:
    return path.is_file() and path.stat().st_size > 0


def paper_has_template_content(path: Path) -> bool:
    if not path.exists():
        return False
    safe_empty_dirs = {"sections", "figures", "tables"}
    for child in path.iterdir():
        if child.name == ".git":
            return True
        if child.is_file():
            return True
        if child.is_dir() and child.name not in safe_empty_dirs:
            return True
        if child.is_dir() and any(child.rglob("*")):
            return True
    return False


def record_create(created: list[str], path: Path, root: Path) -> None:
    created.append(path.relative_to(root).as_posix())


def record_skip(skipped: list[str], path: Path, root: Path, reason: str) -> None:
    skipped.append(f"{path.relative_to(root).as_posix()} ({reason})")


def ensure_dir(path: Path, project_root: Path, created: list[str], skipped: list[str]) -> None:
    if path.exists():
        record_skip(skipped, path, project_root, "exists")
        return
    path.mkdir(parents=True, exist_ok=True)
    record_create(created, path, project_root)


def write_if_missing_or_empty(
    path: Path,
    content: str,
    project_root: Path,
    created: list[str],
    skipped: list[str],
) -> None:
    if is_nonempty_file(path):
        record_skip(skipped, path, project_root, "non-empty file preserved")
        return
    if path.exists() and path.is_file() and content == "":
        record_skip(skipped, path, project_root, "empty file exists")
        return
    if path.exists() and path.is_dir():
        record_skip(skipped, path, project_root, "path is directory")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    record_create(created, path, project_root)


def read_asset(name: str) -> str:
    return (skill_root() / "assets" / name).read_text(encoding="utf-8")


def module_note_content(module: str) -> str:
    if module == "Citation":
        return read_asset("Citation-Note.md")
    return read_asset("Module-Note.md").replace("<Module>", module)


def iter_required_dirs(codex_paper: Path) -> Iterable[Path]:
    yield codex_paper
    yield codex_paper / "Paper"
    yield codex_paper / "Paper" / "sections"
    yield codex_paper / "Paper" / "figures"
    yield codex_paper / "Paper" / "tables"
    yield codex_paper / "User-Interaction"
    for module in MODULES:
        yield codex_paper / "User-Interaction" / module
    yield codex_paper / "Codex-Notes"


def initialize(project_root: Path) -> tuple[list[str], list[str]]:
    project_root = project_root.resolve()
    if not project_root.exists() or not project_root.is_dir():
        raise SystemExit(f"Project root is not a directory: {project_root}")

    created: list[str] = []
    skipped: list[str] = []

    codex_paper = project_root / "Codex-Paper"
    paper = codex_paper / "Paper"
    paper_had_template_content = paper_has_template_content(paper)

    for directory in iter_required_dirs(codex_paper):
        ensure_dir(directory, project_root, created, skipped)

    for module in MODULES:
        module_dir = codex_paper / "User-Interaction" / module
        interaction_asset = "Citation-Interaction.md" if module == "Citation" else "Module-Interaction.md"
        write_if_missing_or_empty(
            module_dir / f"{module}-Interaction.md",
            read_asset(interaction_asset),
            project_root,
            created,
            skipped,
        )
        write_if_missing_or_empty(
            module_dir / f"{module}-Note.md",
            module_note_content(module),
            project_root,
            created,
            skipped,
        )

    write_if_missing_or_empty(
        codex_paper / "Codex-Notes" / "Core-Understanding.md",
        read_asset("Core-Understanding.md"),
        project_root,
        created,
        skipped,
    )

    if paper_had_template_content:
        for skeleton in [paper / "main.tex", paper / "refs.bib"]:
            record_skip(skipped, skeleton, project_root, "Paper already contained template content")
        for filename in SECTION_FILES.values():
            record_skip(skipped, paper / "sections" / filename, project_root, "Paper already contained template content")
    else:
        write_if_missing_or_empty(paper / "main.tex", MAIN_TEX, project_root, created, skipped)
        for filename in SECTION_FILES.values():
            write_if_missing_or_empty(
                paper / "sections" / filename,
                "",
                project_root,
                created,
                skipped,
            )
        write_if_missing_or_empty(paper / "refs.bib", "", project_root, created, skipped)

    return created, skipped


def print_report(created: list[str], skipped: list[str]) -> None:
    print("created:")
    if created:
        for item in created:
            print(f"  - {item}")
    else:
        print("  - none")

    print("skipped:")
    if skipped:
        for item in skipped:
            print(f"  - {item}")
    else:
        print("  - none")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Safely initialize a Codex-Paper workspace in a research project root."
    )
    parser.add_argument("project_root", help="Current research project root")
    args = parser.parse_args()

    created, skipped = initialize(Path(args.project_root))
    print_report(created, skipped)


if __name__ == "__main__":
    main()
