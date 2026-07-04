# Task Protocol

Use this protocol for all module tasks.

## Extracting Tasks

Task files live at:

```text
Codex-Paper/User-Interaction/<Module>/<Module>-Interaction.md
```

Only level-1 headings of the following forms create task boundaries:

```md
# Task 3
#task 3
```

Matching must be case-insensitive and tolerant of spaces after `#` and between `Task` and the number.

When asked to execute `Method Task 3`, read only the content from the `Task 3` heading through the line before the next level-1 task heading. Do not read previous, later, or similar tasks.

If the requested task is missing, report it and stop.

## Interaction Files

Do not rewrite, annotate, status-mark, summarize into, or append logs to `*-Interaction.md`. The user owns these files.

## Note Files

`*-Note.md` files are user-maintained reminders. By default:

- do not read them;
- do not scan them;
- do not organize them;
- do not update them;
- do not synchronize their content into the paper;
- do not use them to trigger cross-module changes.

Only access a Note when the user explicitly says to read or modify that specific Note.

## Local Writing Default

For a normal module task, read only:

- the requested task block;
- the mapped `Paper/sections/*.tex` file when formal modification is allowed;
- `Paper/main.tex` only when needed for locating structure or compiling;
- files explicitly named by the task.

Do not proactively read other modules, inspect all terminology, design experiments, add citations, or perform global restructuring.

## Cross-Module Work

Cross-module work is allowed only when the task explicitly asks for it, for example by naming another module task, requesting coupling work, or asking for a plan in `Codex-Notes/`.

If creating a planning note is authorized, name it after the task, such as:

```text
Codex-Notes/Method-Task-7-Plan.md
Codex-Notes/Method-Introduction-Coupling-Plan.md
```

Do not create planning notes for simple local tasks.
