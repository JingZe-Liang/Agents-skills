#!/usr/bin/env python3
"""Initialize an Exam_Helper review workspace."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
ASSET_ROOT = SKILL_ROOT / "assets" / "starter_files"

DIRS = [
    "input/diagnosis",
    "input/ppt",
    "input/past_papers",
    "input/homework",
    "input/textbook",
    "input/notes",
    "input/online_course",
    "input/teacher_hints",
    "work/internal_outputs/diagnosis",
    "work/internal_outputs/resource_routes",
    "work/internal_outputs/maps",
    "work/internal_outputs/plans",
    "work/internal_outputs/training",
    "work/assets",
    "output/00_overview",
    "output/01_daily",
    "output/02_question_types",
    "output/03_notes",
    "output/04_practice",
    "output/05_final",
]

FILES = {
    "README.md": "README.md",
    "exam_config.yaml": "exam_config.yaml",
    "input/diagnosis/00_课程诊断表.md": "00_课程诊断表.md",
    "work/internal_outputs/diagnosis/resource_inventory.md": "resource_inventory.md",
    "work/internal_outputs/diagnosis/exam_diagnosis.md": "exam_diagnosis.md",
    "work/internal_outputs/resource_routes/resource_router.md": "resource_router.md",
    "work/internal_outputs/resource_routes/learning_ladder.md": "learning_ladder.md",
    "work/internal_outputs/maps/knowledge_map.md": "knowledge_map.md",
    "work/internal_outputs/maps/question_type_map.md": "question_type_map.md",
    "work/internal_outputs/maps/active_recall_bank.md": "active_recall_bank.md",
    "work/internal_outputs/plans/strategy.md": "strategy.md",
    "work/internal_outputs/plans/daily_plan.md": "daily_plan.md",
    "work/internal_outputs/plans/review_log.md": "review_log.md",
    "work/internal_outputs/plans/sprint_plan.md": "sprint_plan.md",
    "work/internal_outputs/training/generated_questions.md": "generated_questions.md",
    "work/internal_outputs/training/mistake_log.md": "mistake_log.md",
    "output/README.md": "output_README.md",
    "output/00_overview/整体规划.md": "overall_plan.md",
    "output/00_overview/当前状态.md": "current_status.md",
    "output/00_overview/从零学习路线.md": "zero_baseline_route.md",
    "output/01_daily/README.md": "daily_README.md",
    "output/02_question_types/README.md": "question_types_README.md",
    "output/03_notes/README.md": "notes_README.md",
    "output/04_practice/README.md": "practice_README.md",
}


def copy_if_safe(src: Path, dst: Path) -> str:
    if dst.exists() and dst.stat().st_size > 0:
        return "skipped"
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)
    return "created"


def main() -> int:
    if len(sys.argv) > 2:
        print("Usage: init_exam_workspace.py [project-root]", file=sys.stderr)
        return 2

    root = Path(sys.argv[1]).resolve() if len(sys.argv) == 2 else Path.cwd()
    root.mkdir(parents=True, exist_ok=True)

    created_dirs = []
    for rel in DIRS:
        path = root / rel
        if not path.exists():
            path.mkdir(parents=True)
            created_dirs.append(rel)

    created_files = []
    skipped_files = []
    for rel, asset_name in FILES.items():
        status = copy_if_safe(ASSET_ROOT / asset_name, root / rel)
        if status == "created":
            created_files.append(rel)
        else:
            skipped_files.append(rel)

    print("Exam review workspace initialized.")
    if created_dirs:
        print("\nCreated directories:")
        for item in created_dirs:
            print(f"- {item}")
    if created_files:
        print("\nCreated files:")
        for item in created_files:
            print(f"- {item}")
    if skipped_files:
        print("\nSkipped non-empty files:")
        for item in skipped_files:
            print(f"- {item}")

    print(
        "\nNext steps:\n"
        "1. Fill input/diagnosis/00_课程诊断表.md.\n"
        "2. Put PPT files into input/ppt/.\n"
        "3. Put past papers and answers into input/past_papers/.\n"
        "4. Put homework, textbook, notes, online course materials, and teacher hints into matching folders.\n"
        "5. Invoke Exam_Helper again for diagnosis."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
