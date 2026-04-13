# magna-brain

A token-efficient content engine brain for Magna — a Claude Code skill bundle
operating over a Git-tracked markdown vault. One brain, two sessions, one
compounding loop.

> **Audience for this README:** Sahil and future agents. Mehr never reads
> this file. Her interface is pure chat in Claude Code.

---

## What this is

magna-brain is the persistent memory behind every Magna post. It combines:

- **Karpathy's LLM-Wiki pattern** — a five-layer `sources / entities /
  concepts / synthesis / voice` hierarchy of markdown articles linked by
  `[[wikilinks]]`.
- **A compile-step persistence loop** — adapted from Cole Medin's
  `claude-memory-compiler`, where raw daily dumps are compiled into
  structured wiki articles by a Claude Agent SDK subprocess.
- **Anthropic Skills progressive-disclosure** — each capability is a
  `SKILL.md` bundle under `skills/`, loaded on trigger, not on session start.

Storage is markdown in Git. No database, no vector store, no daemon, no
embeddings in v1. Retrieval is index-first: only `wiki/index.md` and
`wiki/_index/topic-summaries.md` auto-load per prompt, and skills drill
into full articles on demand via wikilinks.

---

## Two sessions, one repo

magna-brain is designed around a **two-plan permission asymmetry**:

| | **Mehr** (Claude $20) | **Sahil** (Claude $200) |
|---|---|---|
| Role | Ideation + enrichment | Architecture |
| Interface | Chat only, zero ops | Terminal, agentic swarms |
| Can write to | `raw/`, `output/` | Everywhere |
| Cannot write to | `wiki/`, `skills/`, `.claude/` | — |
| Triggers | Natural language | Issues, PRs, CI |
| Fixes | Files issues (invisibly) | Merges issues as PRs |

The repo itself is the ops layer. Mehr is only the ideation layer. Every
dissatisfaction she expresses in chat becomes a structured GitHub Issue
against the brain architecture — not an inline edit — so the architecture
compounds instead of accumulating content patches.

---

## The loop

```
Mehr dumps stuff / asks for a post
           │
           ▼
   ┌───────────────┐
   │   raw/        │  (daily log, any format)
   └───────┬───────┘
           │  compile step (Sahil-side, Agent SDK subprocess)
           ▼
   ┌───────────────┐
   │   wiki/       │  5 layers, wikilinked, indexed
   └───────┬───────┘
           │  write-post skill reads, never writes
           ▼
   ┌───────────────┐
   │   output/     │  GitHub Pages draft on drafts/ branch
   └───────┬───────┘
           │
           ▼
     Mehr reviews
           │
   ┌───────┴───────┐
   │               │
   ▼               ▼
Loves it       Corrects it
   │               │
   │               ▼
   │       feedback skill fires
   │               │
   │               ▼
   │       GitHub Issue (invisibly)
   │               │
   │               ▼
   │       Sahil merges fix (architecture, not content)
   └───────────────┘
```

The brain is never edited inline. Every correction is a structural fix.

---

## Vault layout

```
raw/                            # daily dumps (any format) — Mehr's write-zone
wiki/
  sources/                      # one file per ingested source
  entities/                     # people, products, brands, campaigns
  concepts/                     # ideas, frameworks, claims
  synthesis/                    # cross-cutting insights
  voice/
    styleguide.md               # one compressed tone document
    exemplars/                  # 5–10 hand-picked posts, topic-tagged
  index.md                      # master index (auto-loaded on prompt)
  _index/
    topic-summaries.md          # graphrag-style community summaries
  log.md                        # append-only change log
output/                         # GitHub Pages drafts — Mehr's read-URL zone
reference/                      # brand guide, content calendar, exemplars
skills/                         # Claude Code skill bundles (6 in v1)
.claude/settings.json           # permission contract (Mehr-side)
.github/                        # issue templates, Pages workflow
CLAUDE.md                       # root instructions (Mehr's session)
AGENTS.md                       # compile-step schema (Sahil's subprocess)
TOKEN_BUDGET.md                 # budgets the lint skill enforces
```

Everything uses Obsidian `[[wikilinks]]`. Every wiki page carries
`tags / sources / created / updated / corrected_by` frontmatter.

---

## Skills shipped in v1

See `skills/<name>/SKILL.md` for each.

| Skill | Fires on | Writes to |
|---|---|---|
| `magna-brain-setup` | One-shot bootstrap | `CLAUDE.md`, `AGENTS.md`, `.claude/`, `skills/` |
| `magna-brain-ingest` | Mehr pastes/attaches anything | `raw/` (then triggers compile) |
| `magna-brain-write-post` | "write me a post about X" | `output/`, `drafts/` branch |
| `magna-brain-query` | "what do you know about X?" | Nothing (read-only) |
| `magna-brain-lint` | CI + pre-publish | Nothing (reports) |
| `magna-brain-feedback` | Mehr expresses dissatisfaction | GitHub Issue (invisible to Mehr) |

---

## Status

**Phase 1 — Specification (current).** The artifacts in this repo describe
the architecture only. No Python, Jekyll config, or hook scripts are
implemented yet. Review the spec; implementation follows from Sahil's
terminal session once the spec is locked.

**Phase 2 — Implementation.** Agent-SDK compile subprocess, ingest adapters
(PDF/image/voice/URL), Pages workflow, lint CI, GH Issue automation.

**Phase 3 — Mehr's first session.** She opens Claude Code in
`~/magna-brain`, types "hi," and the brain is loaded. If she ever has to
type a command or see a file path, the spec failed.

---

## Reference material

`reference/` is where Mehr has dropped brand assets, the content calendar,
and an exemplar content-platform HTML. The compile step will ingest these
in Phase 2 to seed `wiki/voice/` and `wiki/entities/`. Do not ingest from
the spec phase.

---

## License

TBD. Do not vendor code from the three reference repos
(`NicholasSpisak/second-brain`, `coleam00/second-brain-skills`,
`coleam00/claude-memory-compiler`) — all three are unlicensed. Re-implement
patterns only.
