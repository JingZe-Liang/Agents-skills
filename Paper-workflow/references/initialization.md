# Initialization

Use initialization mode whenever a project-local `Codex-Paper/` workspace is missing or incomplete.

## Required Behavior

- Accept the current research project root as the target.
- Create `Codex-Paper/` under that root only.
- Create missing required directories and starter files only.
- Never delete, move, rename, or overwrite user files.
- Never overwrite a non-empty file.
- Never scan repository code to infer the paper.
- Never write paper ideas, methods, results, claims, citations, or author data.
- Never initialize Git, add a remote, clone Overleaf, commit, or push.
- Stop after initialization and report what was created and skipped.

## Script

Prefer the bundled script:

```bash
python path/to/codex-paper-workflow/scripts/init_codex_paper.py <project-root>
```

The script is designed to be idempotent. It prints `created` and `skipped` lists.

## Template Preservation

If `Codex-Paper/Paper/` is missing or empty, the script may create a minimal LaTeX skeleton:

- `main.tex`
- `sections/abstract.tex`
- `sections/introduction.tex`
- `sections/related_work.tex`
- `sections/method.tex`
- `sections/experiments.tex`
- `sections/conclusion.tex`
- `sections/appendix.tex`
- `figures/`
- `tables/`
- `refs.bib`

If `Paper/` already contains any file, directory, or `.git`, treat it as an existing template/repository. Only create missing safe directories such as `sections/`, `figures/`, and `tables/`; do not create or overwrite `main.tex`, section files, or `refs.bib`.
