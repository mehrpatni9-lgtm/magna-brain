---
name: magna-brain-lint
description: |
  Structural health check for the brain: token budgets, broken wikilinks, orphans, contradictions, stale claims, and index drift. Runs in CI and before any write-post publish. Never invoked by Mehr directly.
  TRIGGERS - Use this skill when:
  - Sahil says "lint the brain" / "check the brain" / "run magna-brain-lint"
  - CI runs on a PR touching wiki/, skills/, or index files
  - magna-brain-write-post is about to publish and needs a pre-flight check
---

# magna-brain-lint

Not a skill Mehr ever sees by name. Runs automatically:
- In CI on every PR that touches `wiki/`, `skills/`, `TOKEN_BUDGET.md`,
  `AGENTS.md`, or `CLAUDE.md`.
- As the final pre-publish step of `magna-brain-write-post`.
- Manually from Sahil's terminal.

## Checks

### 1. Token budgets (enforced from `TOKEN_BUDGET.md`)

- `wiki/index.md` ≤ 1,500 tokens
- `wiki/_index/topic-summaries.md` ≤ 1,500 tokens
- Combined SessionStart injection ≤ 3,000 tokens
- `wiki/voice/styleguide.md` ≤ 1,000 tokens
- Per-skill `SKILL.md` body ≤ 3,000 tokens
- Combined skill frontmatter (`name` + `description` across all 6 skills)
  ≤ 1,000 tokens
- Simulated `write-post` assembly (voice + 2 exemplars + top 6 articles +
  SessionStart + skill body + CLAUDE.md rules) ≤ 12,000 tokens

Any overflow is a CI failure, not a warning.

### 2. Broken wikilinks

- Every `[[target]]` must resolve to an existing file under `wiki/`.
- Anchors within wikilinks (e.g. `[[concept#section]]`) must resolve to a
  heading in the target file.

### 3. Orphans

- Every file under `wiki/{sources,entities,concepts,synthesis}/` must be
  reachable from `wiki/index.md` via ≤ 3 wikilink hops.
- Unreachable files are orphans. Fail.

### 4. Contradictions (soft)

- Parse every article's bullets. For any two bullets across articles that
  make mutually exclusive factual claims about the same entity (same
  `type: entity`, same `name`), flag a warning and require a
  `contradictions:` block resolving it in the concept that cites both.
- This check is heuristic — it fails loudly only when an `entity.facts`
  line directly contradicts another.

### 5. Stale claims

- For every article with `updated:` older than 180 days AND a
  `supporting_sources:` wikilink to a source marked `kind: url`, emit a
  warning. Long-lived URL-sourced claims need periodic revalidation.

### 6. Index drift

- Compare `wiki/index.md`'s enumerated entities/concepts/synthesis against
  the filesystem. Every file must appear in the index within its section;
  no section may list a file that doesn't exist.

### 7. Skill-path discipline

- No `SKILL.md` may reference `Glob(wiki/**/*.md)` in its body or tools.
- Only `magna-brain-write-post` may reference `wiki/voice/` in its body or
  tools.
- Only `magna-brain-ingest` may reference `raw/` in its tools.

### 8. Frontmatter schema

- Every wiki file has valid `type`, `tags`, `sources`, `created`,
  `updated`, `corrected_by` frontmatter per `AGENTS.md`.

## Outputs

- A plain-text report, one line per violation.
- CI job fails if any **error** is present (warnings don't fail).
- On pre-publish failure in `write-post`, the `write-post` skill surfaces
  to Mehr as *"Something's off with this draft — give me a sec to
  re-cut,"* and auto-files a feedback issue. Mehr never sees the lint
  report itself.

## Tools allowed

`[Read, Glob, Grep]` — **no Write, no Edit, no Bash**. The lint skill is
read-only by design.

## Budget

`SKILL.md` body ≤ 3,000 tokens. Per-invocation prompt ≤ 4,000 tokens
(the skill is deterministic in structure, so its prompt can stay small).
