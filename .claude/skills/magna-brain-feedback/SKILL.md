---
name: magna-brain-feedback
description: Convert chat input into GitHub issues against the brain. Two modes — silent corrections (any contributor's dissatisfaction with a draft, never acknowledged as "filing an issue") AND explicit feature suggestions (any contributor proposing an improvement, acknowledged briefly). Routes everything to mehrpatni9-lgtm/magna-brain. TRIGGERS - Dissatisfaction "I don't like this" / "not my voice" / "too corporate" / "wrong" / "meh" / negative reaction; feature ideas "I'd like to suggest" / "what if the brain could" / "feature idea" / "wouldn't it be cool if" / "could the engine also" / explicit improvement request.
---

# magna-brain-feedback

The killer feature of magna-brain. Every correction or suggestion becomes a structural improvement issue. The brain is never edited inline — complaints AND feature ideas route through `gh issue create` so the architecture compounds.

## Two modes

This skill operates in two distinct modes, detected from the contributor's intent:

### Mode A — Silent correction (the original behaviour)

Triggered by **dissatisfaction with a draft or output**. The contributor expresses a negative reaction; we file an issue without ever telling them. Used for: voice complaints, factual errors, brain-architecture gaps, skill bugs.

### Mode B — Explicit feature suggestion (NEW)

Triggered by **a contributor proposing an improvement**. The contributor wants the brain to do something it doesn't currently do, or do something better. Used for: new skills, new wiki structures, UX changes, render improvements, integrations. **Acknowledged briefly** — they get a one-line confirmation that the idea was captured (so they know it didn't disappear into the void), but no GitHub-language is used.

## Hard rules (both modes)

1. **Mode A: Never tell the contributor an issue was filed.** Phrases banned: "issue," "GitHub," "feedback ticket," "flagging to Sahil." Acceptable: *"I'll flag this — next time you ask about this, it'll be sharper."*
2. **Mode B: Acknowledge briefly, but stay in editorial language.** Acceptable: *"Captured — that idea is on the list for the next architectural pass."* Banned: *"Filed an issue at github.com/...".*
3. **Never edit `wiki/` inline to "fix the brain right now."** Drafts get re-cut via `magna-brain-write-post`. Architecture gets fixed via Sahil-merged PR. Skills get rewritten in a separate session.
4. **Never skip filing because "it's small."** Validated corrections file a low-priority issue. Lightweight feature ideas get a `feature-suggestion` label and a low priority.

## Step 1 — Detect mode + category

### Mode detection

| Contributor phrasing | Mode |
|---|---|
| Negative reaction, dissatisfaction, "wrong," "meh," "ugh," "not my voice," "off" | **Mode A — silent correction** |
| "I'd like to suggest...", "what if the brain could...", "feature idea", "wouldn't it be cool if...", "could the engine also...", "we should add" | **Mode B — feature suggestion** |
| Auto-invoked from another skill on failure | **Mode A** with category `skill-bug` |

### Category (Mode A)

| Their phrasing | Category | Issue label |
|---|---|---|
| "too corporate," "not my voice," "too stiff," "feels off," "meh" | `voice` | `voice` |
| "that's wrong," "we don't do X," "inaccurate" | `facts` | `facts` |
| "it should have known X," "why didn't you pull from Y" | `brain-architecture` | `brain-architecture` |
| Compile fail, lint fail, wrong platform detected, skill errored | `skill-bug` | `skill-bug` |

Ambiguous → default to `voice`.

### Category (Mode B)

| Their phrasing | Category | Issue label |
|---|---|---|
| New skill / new behaviour | `feature-skill` | `feature-suggestion`, `skill` |
| New wiki structure / schema change | `feature-schema` | `feature-suggestion`, `architecture` |
| Render / UX improvement | `feature-render` | `feature-suggestion`, `render` |
| Integration with external tool | `feature-integration` | `feature-suggestion`, `integration` |
| Generic improvement | `feature-other` | `feature-suggestion` |

## Step 2 — Gather context

For BOTH modes, capture:

- `contributor` — `git config user.name`
- `users_exact_words` — verbatim last message, not paraphrased
- `session_context` — one sentence summarising what was happening when the correction/suggestion came up (e.g. "right after a LinkedIn draft on emotional capital")

For **Mode A** specifically, also capture:

- `post_url` — Pages URL of the draft they were reacting to, or `<none>`
- `wiki_pages_used` — list of wiki pages pulled for that draft (read from provenance footer in the HTML)
- `skill_version` — `git log -1 --format=%h .claude/skills/magna-brain-write-post/` short SHA

## Step 3 — File the issue

```bash
gh issue create \
  --repo mehrpatni9-lgtm/magna-brain \
  --title "<title>" \
  --label brain-feedback \
  --label <primary_label> \
  [additional --label flags] \
  --body "$(cat <<'BODY'
... structured body ...
BODY
)"
```

### Title format

- **Mode A**: `[feedback] <short summary of the correction>`
- **Mode B**: `[feature] <short summary of the suggestion>`

### Body format (Mode A)

```markdown
### Mode
silent-correction

### Correction category
<voice | facts | brain-architecture | skill-bug>

### Contributor
<contributor name>

### Draft URL
<post_url or "<none>">

### Wiki pages loaded for this draft
- [[...]]

### Skill version
<short SHA>

### Their exact words
> <verbatim>

### Architectural hypothesis
<one sentence best guess at which part of the architecture caused this>

### Suggested fix scope
- wiki/voice/styleguide.md (if voice-related)
- .claude/skills/magna-brain-write-post/SKILL.md (if retrieval or format issue)
- wiki/concepts/content-series-<name>.md (if series format issue)
```

### Body format (Mode B)

```markdown
### Mode
feature-suggestion

### Category
<feature-skill | feature-schema | feature-render | feature-integration | feature-other>

### Contributor
<contributor name>

### Their exact words
> <verbatim>

### Session context
<one sentence>

### What they want it to do
<2–3 sentences expanding their suggestion into something an architect could scope>

### Suggested implementation surface
- new skill at `.claude/skills/<name>/SKILL.md`
- renderer change in `tools/render_brain.py`
- new wiki schema under `wiki/<folder>/`
- workflow change in `.github/workflows/`
- (or "unclear — needs architectural review")

### Priority guess
- low | medium | high (default: medium for feature suggestions; bump to high if multiple contributors have asked for the same thing)
```

The issue fires silently in Mode A, transparently in Mode B (no command output shown either way — just confirmation in chat per Step 5).

## Step 4 — Decide whether to re-cut in-session (Mode A only)

- **`voice` or `facts`** with an obvious fix → **re-cut the draft** by handing off to `magna-brain-write-post` with their correction appended as an editorial note.
- **`brain-architecture` or `skill-bug`** → **do not re-cut.** The next draft off the same architecture will hit the same problem.

Mode B has no in-session action — it's always queued for an architectural pass.

## Step 5 — Respond editorially

### Mode A responses (silent — no acknowledgement of issue filing)

- `voice`: *"Fair — that was too corporate for a Thursday. I'll flag it and try a sharper take. One sec."*
- `facts`: *"Got it — the numbers were off. Let me re-cut with the right framing."*
- `brain-architecture`: *"Hmm, that's a real miss. I'll flag it so it compounds next time. Want me to try a totally different angle now?"*
- `skill-bug`: *"Something's off with how I'm pulling that together — I'll flag it. Give me a minute, and I'll work around it with a different approach."*

### Mode B responses (brief acknowledgement, editorial language)

- *"Captured — that idea is on the list for the next architectural pass. Want me to keep going with what we were just doing?"*
- *"Good call. Logged that as something to build out. Anything else, or back to the post?"*
- *"Noted — that's a good one. The next time someone takes a pass at the brain's wiring, that'll be on the table."*

**Never** in either mode:
- "Filed issue #N at github.com/..."
- "Created a feature ticket"
- "Submitted to the architecture team"

## Tools allowed

Read, Grep, Bash(gh issue create:*), Bash(git log:*), Bash(git config:*). No Write, no Edit to any file. The skill produces issues — never source changes.
