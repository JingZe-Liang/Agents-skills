---
name: codex-paper-workflow
description: Controlled long-term collaboration workflow for deep learning and computer vision papers. Use when Codex must initialize or operate a project-local Codex-Paper workspace, execute explicit module-level Markdown paper tasks, safely update LaTeX in an Overleaf-backed Paper subrepository, or handle explicitly requested citation passes without autonomous planning, repository scanning, or ghostwriting.
---

# Codex Paper Workflow

Use this skill to help a user write a deep learning / computer vision paper through explicit, module-level tasks. Treat it as a controlled collaboration protocol, not an automatic paper writer.

## Non-Negotiable Rules

- Place `Codex-Paper/` only in the current research project root, beside project folders such as `code/`, `configs/`, `outputs/`, or `datasets/`. Never create it inside this skill, a Codex config directory, or another hidden location.
- On every invocation, first check whether the project root contains `Codex-Paper/Paper/`, `Codex-Paper/User-Interaction/`, and `Codex-Paper/Codex-Notes/`.
- If required directories or starter files are missing, enter initialization mode: create only missing structure and missing starter files, do not write paper content, do not scan code, do not add citation, do not commit or push, then stop and report created/skipped items.
- Treat `Paper/` as the only formal paper output area. It may contain LaTeX, figures, tables, `refs.bib`, templates, styles, macros, and compile resources only.
- Treat `User-Interaction/` as the user-led module task area. Do not edit user task text or add logs/status markers to `Interaction` files.
- Do not read `*-Note.md` files by default. Read or modify a Note only when the user explicitly names it.
- Do not read `Codex-Notes/Core-Understanding.md` by default. Read or update it only when the user explicitly asks.
- Do not use `Codex-Notes/` by default. Create notes only when the user explicitly asks for planning, notes, cross-module work, large revision planning, citation planning, or reviewer-response planning.
- In early module writing, do not handle citation or cross-module coupling unless the task explicitly asks.
- Start citation work only through an explicit Citation task such as `执行 Citation Task 2`.
- Never fabricate experiments, data, figures, tables, citations, code behavior, author information, claims, or paper conclusions.
- After formal `Paper/` edits, compile successfully before committing or pushing. If local LaTeX tools are unavailable, say so and do not commit/push unless the user explicitly authorizes skipping local compile.
- Never automatically expand the task scope because a broader rewrite seems useful.

## Workflow

1. Determine the current research project root from the working directory and the user's request.
2. Check the project-local workspace:
   - `Codex-Paper/Paper/`
   - `Codex-Paper/User-Interaction/`
   - `Codex-Paper/Codex-Notes/`
3. If the workspace is missing or incomplete, run initialization mode. Prefer:

```bash
python path/to/codex-paper-workflow/scripts/init_codex_paper.py <project-root>
```

4. If the workspace is complete and the user asks to execute a module task, enter task execution mode.
5. If the request is only discussion, planning, checking, or "do not modify Paper", obey that boundary and do not edit formal LaTeX.

Read [references/initialization.md](references/initialization.md) for initialization details and [references/project-structure.md](references/project-structure.md) for the exact expected tree.

## Task Execution

Recognize module tasks of the form `执行 <Module> Task <n>` or equivalent. Supported modules:

`Abstract`, `Introduction`, `RelatedWork`, `Method`, `Experiments`, `Conclusion`, `Appendix`, `Citation`.

For a non-Citation module task:

1. Open only `Codex-Paper/User-Interaction/<Module>/<Module>-Interaction.md`.
2. Extract only the requested task block. A task boundary is a level-1 heading matching `# Task n` or `#task n`, case-insensitive and tolerant of spacing.
3. Treat that task block as the highest-priority instruction for this turn.
4. Read only files explicitly authorized by the task, plus the mapped LaTeX file when formal modification is allowed, and `Paper/main.tex` only when needed for location or compilation.
5. If the task does not exist, report that and do not execute another task.

Default module-to-LaTeX mapping:

```text
Abstract      -> Paper/sections/abstract.tex
Introduction  -> Paper/sections/introduction.tex
RelatedWork   -> Paper/sections/related_work.tex
Method        -> Paper/sections/method.tex
Experiments   -> Paper/sections/experiments.tex
Conclusion    -> Paper/sections/conclusion.tex
Appendix      -> Paper/sections/appendix.tex
Citation      -> target file and passage specified by the task
```

If the user's `Paper/` template uses different files, use the actual template structure. Do not create parallel paper content or guess a target section when unclear.

Read [references/task-protocol.md](references/task-protocol.md) before executing task blocks with ambiguity, cross-module instructions, note access, or planning requests.

## Paper Boundaries

Never place discussion, uncertain ideas, temporary notes, workflow explanations, internal planning, intermediate drafts, task logs, `Interaction` files, or `Note` files inside `Paper/`.

If `Paper/` already contains an Overleaf template or Git repository, preserve it. Do not overwrite `main.tex`, delete style files, restructure the template, or split a single-file paper unless a user task explicitly asks.

Read [references/paper-boundaries.md](references/paper-boundaries.md) before modifying `Paper/`.

## Citation

Citation work is off by default. Only execute it for explicit `Citation Task n` requests.

For Citation tasks, use only papers, cite keys, BibTeX entries, or article materials explicitly provided or allowed by that task. You may open `Paper/refs.bib` to verify cite keys. Make minimal changes, do not rewrite the paragraph's main logic, do not alter contributions, methods, or experimental conclusions, and do not hard-fill citations when the provided paper does not support the claim.

Read [references/citation-pass.md](references/citation-pass.md) before Citation tasks.

## Compile, Commit, Push

For formal Paper edits:

1. Modify only files required by the task.
2. Do not run `git add .`.
3. Add only explicit changed formal-paper paths.
4. Compile `Paper/main.tex` using the template's existing build method when available; otherwise try `latexmk` or an appropriate LaTeX command.
5. Commit only after successful compile from inside `Codex-Paper/Paper/`.
6. Use commit message `codex-paper: <Module> Task <n>`.
7. Push only if a remote exists and compile/commit succeeded.
8. Report changed files, compile result, commit result, push result, and unresolved issues.

If compile fails, do not push. Try reasonable fixes within the task scope; otherwise report the exact failure and next step.

Read [references/git-overleaf.md](references/git-overleaf.md) before committing or pushing.

## Self-Check

After updating this skill, verify:

```bash
python path/to/skill-creator/scripts/quick_validate.py path/to/codex-paper-workflow
python path/to/codex-paper-workflow/scripts/init_codex_paper.py <empty-existing-test-project>
python path/to/codex-paper-workflow/scripts/init_codex_paper.py <same-test-project>
```

Confirm the first initialization creates `Paper/`, `User-Interaction/`, `Codex-Notes/`, all eight module folders, each module's `Interaction` and `Note`, and `Core-Understanding.md`; confirm the second run reports no new creations. Also test a project whose `Codex-Paper/Paper/main.tex` already exists and confirm it is preserved.
