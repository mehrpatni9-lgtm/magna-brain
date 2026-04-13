---
name: magna-brain-setup
description: One-shot bootstrap for the magna-brain vault. Scaffolds missing directories, seeds index files if absent, verifies the .claude/settings.json permission contract. Sahil-only. Never fires in Mehr's session. TRIGGERS - Use this skill when Sahil says "scaffold magna-brain" / "bootstrap the vault" / when magna-brain-lint reports missing structural files and asks for a re-scaffold.
---

# magna-brain-setup

Idempotent bootstrap. Safe to re-run — never clobbers hand-curated content in `wiki/voice/` or `raw/`.

**This skill is never triggered by Mehr.** It writes to `CLAUDE.md`, `AGENTS.md`, `.claude/skills/`, `.claude/settings.json` — all of which Mehr's permission contract denies.

## Actions

1. Ensure these directories exist (create missing, skip existing):
   - `raw/`, `output/`
   - `wiki/{sources,entities,concepts,synthesis,voice/exemplars,_index}/`
   - `.claude/skills/magna-brain-{setup,ingest,write-post,query,lint,feedback}/`
   - `.github/{ISSUE_TEMPLATE,workflows}/`

2. Ensure these files exist (create missing with empty-but-valid stubs, skip existing):
   - `wiki/index.md` (with required frontmatter + empty sections)
   - `wiki/_index/topic-summaries.md` (stub)
   - `wiki/log.md` (single header, append-only marker)
   - `raw/.gitkeep`, `output/.gitkeep`
   - `.gitignore` (ignore `.DS_Store`, `*.swp`, `state.json` local state)

3. Verify presence of these root files. **Warn if missing, never overwrite:**
   - `CLAUDE.md`, `AGENTS.md`, `TOKEN_BUDGET.md`, `README.md`
   - `.claude/settings.json`
   - Every `.claude/skills/*/SKILL.md`

4. Run `magna-brain-lint` at the end and emit its report.

## What it does NOT touch

- `wiki/voice/styleguide.md` if it has content
- `wiki/voice/exemplars/*` ever (hand-curated)
- `raw/**` ever
- Existing compiled wiki articles
- Existing issue template or Pages workflow

## Tools allowed

Read, Write (new files only), Edit, Glob, Grep. No Bash.

## Output

A diff-style summary of what was created vs skipped, emitted to Sahil's session only.
