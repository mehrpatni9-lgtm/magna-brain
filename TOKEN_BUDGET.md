# TOKEN_BUDGET.md

Token budgets for magna-brain. The `magna-brain-lint` skill reads this file
and fails CI if any budget is exceeded. These numbers are **load-bearing**
for the whole design: the brain's differentiation from the reference repos
(`NicholasSpisak/second-brain`, `coleam00/second-brain-skills`,
`coleam00/claude-memory-compiler`) is that magna-brain publishes and
enforces a token budget.

All numbers are in tokens, counted with the `cl100k_base` tokenizer.

---

## Session-level budgets

| Surface | Budget | Source files |
|---|---:|---|
| **SessionStart auto-injection** | **≤ 3,000** | `wiki/index.md` + `wiki/_index/topic-summaries.md` |
| `wiki/index.md` | ≤ 1,500 | — |
| `wiki/_index/topic-summaries.md` | ≤ 1,500 | — |

Nothing else loads at session start. No `CLAUDE.md` expansions, no voice
layer, no individual articles.

---

## Skill-level budgets

| Surface | Budget | Notes |
|---|---:|---|
| **Skill metadata (all 6 skills combined)** | **≤ 1,000** | Frontmatter only — `name` + `description` of every `SKILL.md`. This is what Claude's matcher sees. |
| **SKILL.md body on trigger** | **≤ 3,000 each** | When a skill actually fires, its full body loads. Per-skill cap. |

---

## Voice-layer budget

Loaded **only** by `magna-brain-write-post`. No other skill touches it.

| Surface | Budget |
|---|---:|
| **Voice layer total (on write-post only)** | **≤ 2,000** |
| `wiki/voice/styleguide.md` | ≤ 1,000 |
| 2 best-matched exemplars from `wiki/voice/exemplars/` | ≤ 1,000 combined |

Exemplar selection is LLM-picked via a cheap prior call against exemplar
headers only (~500 tokens), not via embeddings. See
`skills/magna-brain-write-post/SKILL.md`.

---

## Prompt assembly budgets

| Path | Max assembled prompt |
|---|---:|
| **`magna-brain-write-post`** | **≤ 12,000 tokens** |
| `magna-brain-query` | ≤ 6,000 tokens |
| `magna-brain-ingest` | ≤ 8,000 tokens (excluding the raw payload itself) |

The `write-post` cap is the ceiling: CLAUDE.md rules + SessionStart
injection + SKILL.md body + voice layer + up to 6 drilled-in wiki articles
by wikilink + the post brief = ≤ 12,000 tokens total.

---

## Hard rules the lint skill enforces

1. **No skill may `Glob wiki/**/*.md` at prompt time.** Retrieval is
   strictly index-first, drill-down on demand via wikilinks. This is the
   single biggest lever on token efficiency.
2. **No skill may read `wiki/voice/**` unless it is `magna-brain-write-post`.**
3. **No skill may read the full `raw/` directory.** Only the specific
   daily-log file the ingest skill is processing.
4. **Per-file ceilings for index files are load-bearing.** If the compile
   step would push `wiki/index.md` above 1,500 tokens, it must collapse
   older entries into topic summaries instead.
5. **Skill metadata total across all skills ≤ 1,000 tokens.** Every word
   in a skill's `description` frontmatter is paid for on every user turn,
   because Claude's matcher sees all of them simultaneously.

---

## Why these numbers

- `3,000` for SessionStart is the inflection point below which
  conversation latency stays imperceptible on `claude-sonnet-4-6`.
- `1,000` for skill metadata total is Anthropic's recommended ceiling for
  skill frontmatter, taken from the public Skills docs.
- `12,000` for full `write-post` assembly is well below the Sonnet/Opus
  4.6 (1M) effective-context sweet spot (~32k for this kind of multi-hop
  task); the headroom absorbs long raw briefs without replanning.
- None of the three reference repos publish numbers. These are magna-brain's
  differentiator and they are enforced, not aspirational.

---

## Updating this file

Only Sahil's session may edit `TOKEN_BUDGET.md`, and only via a PR
referencing the issue that motivated the change (usually a
`brain-architecture` feedback issue from Mehr). The lint skill reads this
file on every CI run and on every `write-post` invocation.
