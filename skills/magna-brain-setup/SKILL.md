---
name: magna-brain-setup
description: |
  Scaffold or refresh the magna-brain vault inside the current repo.
  TRIGGERS - Use this skill when:
  - the repo has no wiki/ directory yet
  - the repo has no .claude/settings.json yet
  - Sahil says "scaffold magna-brain" or "bootstrap the vault"
  - the magna-brain-lint skill reports missing structural files and asks for a re-scaffold
---

# magna-brain-setup

One-shot bootstrap. Idempotent — safe to re-run to re-render scaffolding
without clobbering hand-curated content in `wiki/voice/` or `raw/`.

**Never fires in Mehr's session.** The setup skill's permissions require
writes to `CLAUDE.md`, `AGENTS.md`, `skills/`, and `.claude/` — all denied
for Mehr. This skill is Sahil-only.

## What it creates

- Directory skeleton per `README.md` vault layout:
  `raw/`, `wiki/{sources,entities,concepts,synthesis,voice/exemplars,_index}/`,
  `output/`, `skills/`, `.github/`, `.claude/`
- Seed `wiki/index.md` (empty sections, within token budget)
- Seed `wiki/_index/topic-summaries.md` (empty, within token budget)
- Seed `wiki/log.md` (single header, append-only marker)
- `.gitignore` for `output/` build artifacts and local state files
- `.claude/settings.json` if missing (copied from spec)
- `CLAUDE.md`, `AGENTS.md`, `TOKEN_BUDGET.md`, `README.md` if missing

## What it does NOT touch

- `wiki/voice/styleguide.md` if it already has content
- `wiki/voice/exemplars/*` ever
- `raw/**` ever
- Any existing compiled article under `wiki/{sources,entities,concepts,synthesis}/`
- `.github/ISSUE_TEMPLATE/brain-feedback.yml` if present
- `.github/workflows/pages.yml` if present

## Tools allowed

`[Read, Write, Edit, Glob, Grep]` — no Bash. The skill plans its writes,
shows the diff, then applies.

## Failure modes

- If a scaffold write would exceed a file's token budget from
  `TOKEN_BUDGET.md`, abort and file a `skill-bug` feedback issue.
- If the repo already has a file the skill was going to create, prefer the
  existing file and log the skip.

## Outputs

- A human-readable summary of what was created / skipped, emitted to the
  Sahil-side session only. Never surfaced to Mehr.
