# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository status

This repository is a fresh scaffold for an "education agents" project. At the time of writing it contains no source code, build system, tests, or documentation — only:

- `assets/books/ci_example.pdf` — a reference PDF (likely a textbook excerpt used as input/grounding material).
- `.claude/` — local Claude Code configuration (permissions + skills).

There is no README, no package manifest (`pyproject.toml` / `package.json` / etc.), no `.cursor/rules`, and no `.github/copilot-instructions.md`. When adding the first code, also add the corresponding build/test/lint commands to this file.

## Environment

Use the `education-env` conda environment for all Python commands in this repo. Prefix invocations with `conda run -n education-env ...` (or activate it first: `conda activate education-env`). Install new dependencies into this env, not base.

## Working in this repo

- Before assuming a command, language, or framework exists, verify — the project has not picked one yet. Ask the user which stack to use rather than guessing.
- The `assets/books/` directory holds source material (PDFs). The `pdf-handling`, `pdf-to-markdown`, and `pdf-to-latex` skills under `.claude/skills/` are available for extracting content from these PDFs.
- Several prompt-engineering and API skills are pre-installed under `.claude/skills/` (`prompt-engineering-claude`, `prompt-engineering-gemini`, `prompt-engineering-gpt5`, `structured-outputs`, `data-viz-plots`). Prefer invoking these skills over re-deriving their guidance when building LLM-facing code.
