# Project Structure

The initialized workspace must live at:

```text
<Project-Root>/Codex-Paper/
```

Target structure:

```text
Codex-Paper/
├── Paper/
│   ├── main.tex
│   ├── sections/
│   │   ├── abstract.tex
│   │   ├── introduction.tex
│   │   ├── related_work.tex
│   │   ├── method.tex
│   │   ├── experiments.tex
│   │   ├── conclusion.tex
│   │   └── appendix.tex
│   ├── figures/
│   ├── tables/
│   └── refs.bib
├── User-Interaction/
│   ├── Abstract/
│   │   ├── Abstract-Interaction.md
│   │   └── Abstract-Note.md
│   ├── Introduction/
│   │   ├── Introduction-Interaction.md
│   │   └── Introduction-Note.md
│   ├── RelatedWork/
│   │   ├── RelatedWork-Interaction.md
│   │   └── RelatedWork-Note.md
│   ├── Method/
│   │   ├── Method-Interaction.md
│   │   └── Method-Note.md
│   ├── Experiments/
│   │   ├── Experiments-Interaction.md
│   │   └── Experiments-Note.md
│   ├── Conclusion/
│   │   ├── Conclusion-Interaction.md
│   │   └── Conclusion-Note.md
│   ├── Appendix/
│   │   ├── Appendix-Interaction.md
│   │   └── Appendix-Note.md
│   └── Citation/
│       ├── Citation-Interaction.md
│       └── Citation-Note.md
└── Codex-Notes/
    └── Core-Understanding.md
```

All names are case-sensitive by convention. Preserve this spelling exactly even on case-insensitive filesystems.

## Core-Understanding

`Codex-Notes/Core-Understanding.md` must be Chinese and contain only these three level-1 headings:

```md
# 我们的几大贡献是什么

# 我们要解决的问题是什么

# 我们的方法是什么
```

During initialization, write `待用户确认。` under each heading unless the user explicitly provided paper-level contributions, problem, or method information in the initialization request. Do not infer missing content.
