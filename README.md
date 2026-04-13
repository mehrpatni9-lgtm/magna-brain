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

## Handing this off to Mehr (Sahil, read this)

One command on her machine:

```bash
gh repo clone mehrpatni9-lgtm/magna-brain ~/magna-brain && cd ~/magna-brain && claude
```

That's everything. The `.claude/settings.json` contract locks her session
to read-only on the brain and write-only on `raw/` and `output/`. The six
`.claude/skills/magna-brain-*` skills auto-load when she opens Claude Code.
`CLAUDE.md` ensures her first "hi" returns a natural greeting, not a file
tree. She never sees a command or a path again.

### Before you hand off — admin toggles (one-time, Mehr must do)

Only a repo admin can flip these. Sahil has push/triage, not admin, so
Mehr needs to run through Settings once:

1. **Pages:** Settings → Pages → Source = `GitHub Actions`
2. **Actions permissions:** Settings → Actions → General → Workflow
   permissions = `Read and write permissions` (and allow PR creation)
3. Optional: grant Sahil `maintain` so future architectural PRs don't
   need a manual step.

Once those are on, the first draft Mehr asks for appears at
`https://mehrpatni9-lgtm.github.io/magna-brain/<date>-<slug>.html`
within ~60 seconds. The landing page at
`https://mehrpatni9-lgtm.github.io/magna-brain/` is already built and
lives under `output/index.html`.

---

## Status

**Phase 1 — Specification.** ✅ Complete. Architecture artifacts in
`CLAUDE.md`, `AGENTS.md`, `TOKEN_BUDGET.md`, `.claude/settings.json`,
and this README.

**Phase 2 — v1 implementation.** ✅ Complete for Mehr's first chat.
- Six executable skills at `.claude/skills/magna-brain-*/SKILL.md`
- Seeded `wiki/`: 8 entities, 14 concepts, 3 sources, 10 exemplars,
  1 synthesis angle, master index, topic summaries, append-only log
- `wiki/voice/styleguide.md` extracted from Magna's real brand guide
  and content platform
- Landing page at `output/index.html` with Magna brand shell
- GitHub Pages workflow publishing from `main` on any `output/` change
- 5 feedback labels created: `brain-architecture`, `voice`, `facts`,
  `skill-bug`, `brain-feedback`
- Feedback issue template auto-filled by `magna-brain-feedback` skill

**Phase 3 — autonomous compound loop (deferred).**
- Python compile subprocess (Agent SDK) that turns `raw/` dumps into
  structured `wiki/` articles. v1 instead lets `magna-brain-write-post`
  read recent `raw/` files as supplementary context — the brain "remembers"
  Mehr's dumps even without compile.
- XLSX parser for the content calendar (currently a stub in
  `wiki/sources/magna-content-calendar.md`).
- Multimodal ingest adapters (image vision, voice transcription, URL
  fetching). v1 handles PDFs via `pdftotext` and pasted prose natively.
- Lint CI wiring (the skill exists; the GitHub Actions job is TODO).
- Agentic swarm that auto-PRs architectural fixes for `brain-architecture`
  issues from Sahil's terminal.

---

## Reference material

`reference/` contains:
- `design/Magna Brand Guide.pdf` — seeded `wiki/sources/magna-brand-guide.md`
  and `wiki/voice/styleguide.md`
- `magna-content-platform.html` — the 2026 content strategy brief; seeded
  every content-series concept and entity file
- `Magna_Content_Calendar___Clean_v4.xlsx` — stub only, not yet parsed
- `design/` — logo assets, brand imagery

---

## License

TBD. Do not vendor code from the three reference repos
(`NicholasSpisak/second-brain`, `coleam00/second-brain-skills`,
`coleam00/claude-memory-compiler`) — all three are unlicensed. Re-implement
patterns only.
