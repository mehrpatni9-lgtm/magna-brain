# AGENTS.md — compile-step schema

This file is read by the **compile subprocess** (Sahil-side Claude Agent
SDK call) to turn daily dumps in `raw/` into structured wiki articles under
`wiki/`. It is the contract between the ingest layer and the brain.

> Mehr's session never reads this file. Only the compile subprocess and
> Sahil's terminal session do.

---

## 1. When the compile step runs

- **Trigger:** automatically, immediately after any `magna-brain-ingest`
  invocation that writes to `raw/<YYYY-MM-DD>.md`.
- **Gate:** the `state.json` SHA-256 hash of the daily log must have
  changed since the last run. Unchanged logs are no-ops.
- **Runtime:** Python subprocess using the Claude Agent SDK.
- **Permissions:**
  - `permission_mode: "acceptEdits"`
  - `max_turns: 30`
  - `tools: [Read, Write, Edit, Glob, Grep]` — **no Bash**. Prompt-injection
    blast radius must stay off the shell.
- **Inputs the agent reads:**
  - `raw/<YYYY-MM-DD>.md` (today's dump)
  - `wiki/index.md` (current master index)
  - `wiki/_index/topic-summaries.md`
  - `wiki/log.md` (recent change log, tail 200 lines)
  - Any existing wiki article reachable by wikilink from the above
- **Outputs the agent may write:**
  - New or updated files under `wiki/sources/`, `wiki/entities/`,
    `wiki/concepts/`, `wiki/synthesis/`
  - `wiki/index.md` (refreshed)
  - `wiki/_index/topic-summaries.md` (refreshed only when topic clusters shift)
  - `wiki/log.md` (append-only)
- **Outputs the agent must NOT touch:**
  - `wiki/voice/**` — voice layer is hand-curated; only explicit voice-update
    skills touch it
  - `skills/**`, `.claude/**`, `.github/**`, `CLAUDE.md`, `AGENTS.md`,
    `TOKEN_BUDGET.md`

---

## 2. Article types

The compile step emits exactly four article types. Every wiki file belongs
to one of them. No new types may be introduced without an architectural PR.

### 2.1 `sources/`

One file per ingested source (PDF, URL, transcript, image caption, note).
Faithful record of the origin material. No interpretation.

**Filename:** `wiki/sources/<slug>.md`
**Frontmatter:**
```yaml
---
type: source
title: "<human title>"
kind: pdf | url | image | voice | note | spreadsheet
origin: <path in raw/ or URL>
ingested: 2026-04-13
tags: [brand-guide, content-calendar, ...]
sources: []              # sources always have an empty sources list
corrected_by: []         # filled in if a feedback issue reshapes this file
---
```
**Body:** faithful extraction. No synthesis. No editorializing.

### 2.2 `entities/`

One file per distinct named thing: person, product, brand, campaign,
audience segment.

**Filename:** `wiki/entities/<kebab-name>.md`
**Frontmatter:**
```yaml
---
type: entity
name: "<canonical name>"
kind: person | brand | product | campaign | audience | channel
aliases: ["<other names>"]
tags: []
sources: [[source-slug-1]], [[source-slug-2]]
created: 2026-04-13
updated: 2026-04-13
corrected_by: []
---
```
**Body sections (fixed order):**
1. **One-line definition** — who/what this is in ≤140 chars.
2. **Key facts** — bulleted, every bullet cites `[[source-slug]]`.
3. **Relationships** — wikilinks to other entities, each with a one-line
   relation description.
4. **Open questions** — bullets of what's unknown or contradictory.

### 2.3 `concepts/`

One file per idea, framework, claim, or recurring theme. This is where the
brain *thinks*, not where it records.

**Filename:** `wiki/concepts/<kebab-name>.md`
**Frontmatter:** same shape as entities, with `type: concept`.
**Body sections:**
1. **TL;DR** — one paragraph, ≤80 words.
2. **Why it matters for Magna** — one paragraph tying to brand goals.
3. **Supporting sources** — bulleted wikilinks to `[[sources/...]]`.
4. **Related concepts** — wikilinks to `[[concepts/...]]`.
5. **Contradictions / open threads** — explicit list of conflicts with
   other wiki pages. Do not resolve silently.

### 2.4 `synthesis/`

Cross-cutting insights that connect multiple concepts and entities into a
reusable angle for a post. This is the layer `write-post` preferentially
reads from.

**Filename:** `wiki/synthesis/<kebab-name>.md`
**Frontmatter:** same shape as concepts, with `type: synthesis`, plus
`draws_on: [[concept-a]], [[concept-b]], [[entity-c]]`.
**Body sections:**
1. **The angle** — one paragraph. A POV Magna can credibly hold.
2. **Evidence trail** — bulleted wikilinks through the brain that back the
   angle.
3. **Counter-angle** — one paragraph of the strongest objection.
4. **Post hooks** — 3–5 bullets of concrete post openers using this angle.

---

## 3. Wikilink discipline

- Every cross-reference uses Obsidian `[[wikilinks]]` syntax. Never raw
  paths, never markdown links.
- Every claim in `entities/`, `concepts/`, `synthesis/` cites at least one
  `[[sources/...]]`. Uncited claims are a lint failure.
- No article may link to itself.
- Orphans (files not reachable from `wiki/index.md`) are a lint failure.
- Broken wikilinks are a lint failure.

---

## 4. Index and topic-summaries

### `wiki/index.md`

Single master index. Auto-injected at every session start. Budget ≤ 1,500
tokens (see `TOKEN_BUDGET.md`).

Sections:
- **Entities** — one line per entity: `[[entity]] — <one-line definition>`
- **Concepts** — one line per concept: `[[concept]] — <TL;DR first
  sentence>`
- **Synthesis angles** — one line per synthesis file
- **Recent sources (last 30 days)** — one line per source
- **Compiled from** — a table mapping compiled articles to their source
  provenance, adapted from Cole Medin's pattern

If the budget would be exceeded, the compile step collapses older sources
into `wiki/_index/topic-summaries.md` and links them there.

### `wiki/_index/topic-summaries.md`

Graphrag-style community summaries. One paragraph per topic cluster.
Budget ≤ 1,500 tokens. Regenerated only when the compile step detects
topic drift (new concepts added or relationships shifted).

---

## 5. Provenance and correction traceability

Every wiki file carries:

- `sources: [[s1]], [[s2]]` — where the claims came from
- `corrected_by: [issue-42, issue-57]` — which GitHub feedback issues
  reshaped this file

When the feedback skill files an issue that touches a wiki page, and
Sahil's session merges the architectural fix, the PR must append the issue
number to `corrected_by` on every file it touches. This is how the brain
stays auditable across corrections.

`wiki/index.md` carries a "Compiled From" table listing every compiled
article with its source provenance, so Mehr (via query skill) can always
answer "where did we learn this?" without Sahil in the loop.

---

## 6. Log discipline

`wiki/log.md` is append-only. Every compile run appends a block:

```
## 2026-04-13T14:22:08Z
- ingest: raw/2026-04-13.md (3 new sources)
- created: entities/nike-air-max-90.md
- updated: concepts/nostalgia-marketing.md
- refreshed: index.md
- corrected_by: []
```

Lint fails if any edit to `log.md` is not a pure append.

---

## 7. Compile-step prompt skeleton

The Agent SDK subprocess receives a prompt structured as:

1. This `AGENTS.md` file (the schema contract)
2. Current `wiki/index.md`
3. Current `wiki/_index/topic-summaries.md`
4. Today's `raw/<date>.md`
5. The instruction: *"Update the wiki to reflect the new material. Obey
   the schema in AGENTS.md. Do not touch `wiki/voice/`. Do not rewrite
   articles unless the new material contradicts or meaningfully extends
   them. Prefer creating new concept/synthesis files over bloating existing
   ones."*

Implementation lives in Sahil-side Python (Phase 2). This file is the spec
the implementation must satisfy.

---

## 8. Non-goals for the compile step

- No embedding generation. No vector index. No similarity search.
- No Bash access. No network calls beyond what the Agent SDK exposes.
- No writes outside `wiki/`. The output path is `output/`, handled by
  `magna-brain-write-post`, not by compile.
- No touching of `wiki/voice/`. That layer is hand-curated and only updated
  via explicit voice-update skills or Sahil-merged PRs.
