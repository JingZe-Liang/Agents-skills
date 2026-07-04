# Git and Overleaf

Use this process only after a task formally modifies `Codex-Paper/Paper/`.

## Compile First

Compile `Paper/main.tex` before committing. Prefer the template's existing build system if present. Otherwise try a suitable local LaTeX command such as `latexmk`.

If LaTeX tools are unavailable, clearly report that local compile could not be performed and do not commit/push unless the user explicitly authorized skipping local compile.

If compile fails:

- do not claim success;
- do not push;
- attempt reasonable fixes only inside the task scope;
- if unresolved, report the error, affected files, and next step.

## Commit

Run Git commands inside:

```text
Codex-Paper/Paper/
```

Never use:

```bash
git add .
```

Add only the explicit formal files modified by this task, for example:

```bash
git add sections/method.tex
```

Use commit message:

```text
codex-paper: <Module> Task <n>
```

## Push

Push only after compile and commit succeed. If no remote exists, keep the local commit and report that Overleaf was not synced. If push fails, report the failure and do not pretend synchronization succeeded.

## Final Report

Include:

- changed files;
- compile result;
- commit result;
- push result;
- unresolved issues.
