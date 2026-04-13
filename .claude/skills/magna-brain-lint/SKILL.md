---
name: magna-brain-lint
description: Structural health check for the brain — token budgets, broken wikilinks, orphans, contradictions, stale claims, and index drift. Runs in CI and before any write-post publish. Never invoked by Mehr directly. TRIGGERS - Use this skill when Sahil says "lint the brain" / "check the brain" / "run magna-brain-lint" / after a magna-brain-write-post draft before publishing / CI runs on a PR touching wiki/, .claude/skills/, TOKEN_BUDGET.md, AGENTS.md, or CLAUDE.md.
---

# magna-brain-lint

Not a skill Mehr sees by name. Three invocation paths: manual from Sahil's terminal, auto-fired by `magna-brain-write-post` just before publish, and CI-triggered on relevant PRs.

## Checks performed (all read-only)

### 1. Token budgets

Cross-reference against `TOKEN_BUDGET.md`. Use a rough tokenizer (word_count × 1.3 is a workable approximation when `tiktoken` is unavailable). Fail if:

- `wiki/index.md` > 1,500 tokens
- `wiki/_index/topic-summaries.md` > 1,500 tokens
- Combined index + topic-summaries (SessionStart injection) > 3,000 tokens
- `wiki/voice/styleguide.md` > 1,000 tokens
- Any single `.claude/skills/*/SKILL.md` body > 3,000 tokens
- Combined skill frontmatter (name + description) across all 6 skills > 1,000 tokens

### 2. Broken wikilinks

Grep `wiki/**/*.md` and `.claude/skills/**/*.md` for `[[target]]` patterns. For each, verify a corresponding file exists under `wiki/` (wikilinks resolve against `wiki/` root, e.g. `[[magna]]` → `wiki/entities/magna.md` OR `wiki/concepts/magna.md` OR `wiki/sources/magna.md` — first match wins).

Fail on: no file matches the wikilink target.

### 3. Orphans

For every `.md` file under `wiki/{sources,entities,concepts,synthesis}/`, verify it is reachable from `wiki/index.md` via ≤ 3 wikilink hops (transitive closure). Fail on: unreachable files.

### 4. Skill-path discipline

Fail on:

- Any `.claude/skills/*/SKILL.md` body containing `Glob(wiki/**/*.md)` or equivalent full-wiki glob.
- Any skill other than `magna-brain-write-post` referencing `wiki/voice/` in its body or tool list.
- Any skill other than `magna-brain-ingest` referencing `raw/` as a write target.
- Any Bash pattern in a skill's allowed tools that grants blanket shell access.

### 5. Frontmatter schema

For every wiki file, verify required frontmatter keys exist:
- `sources/`: `type, title, kind, origin, ingested, tags, sources, corrected_by`
- `entities/`: `type, name, kind, tags, sources, created, updated, corrected_by`
- `concepts/`, `synthesis/`: `type, name, tags, sources, created, updated, corrected_by`
- `voice/exemplars/`: `type, platform, series, voice, topics, format, sources, created`

Warn (don't fail) if optional keys are missing. Fail if required keys are missing.

### 6. Log discipline

`wiki/log.md` must be append-only — compare against the previous commit's version. Fail if any existing line has been modified.

## Output

One-line-per-violation report, grouped by severity:

```
ERRORS (fail CI):
- wiki/index.md: 1,612 tokens (budget 1,500)
- wiki/concepts/foo.md: orphan (not reachable from index)
- .claude/skills/magna-brain-ingest/SKILL.md: references wiki/voice/ (restricted to write-post)

WARNINGS:
- wiki/concepts/bar.md: missing optional `updated:` frontmatter
```

When invoked by `magna-brain-write-post` pre-publish, only **errors** block. When invoked in CI, errors fail the workflow. When invoked manually by Sahil, report everything.

## Tools allowed

Read, Glob (scoped), Grep. No Write, no Edit, no Bash except `git log:*` and `git diff:*` for the log-discipline check.

## Budget

SKILL.md body ≤ 3,000 tokens. Per-invocation prompt ≤ 4,000 tokens.
