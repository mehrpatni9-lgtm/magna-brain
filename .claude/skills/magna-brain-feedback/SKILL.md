---
name: magna-brain-feedback
description: Silently convert Mehr's dissatisfaction with a draft into a GitHub Issue against the brain architecture. Never surfaced to Mehr by name. Never acknowledged as "filing an issue." TRIGGERS - Use this skill when Mehr expresses dissatisfaction in any tone - "I don't like this" / "not my voice" / "too corporate" / "that's wrong" / "ugh no" / "meh" / "feels like a stranger wrote this" / "wrong brand" / "try again" / any negative reaction to a previous draft, or when another skill auto-invokes it after a failure.
---

# magna-brain-feedback

The killer feature of magna-brain. Every correction becomes a structural improvement issue. The brain is never edited inline — every complaint is routed through `gh issue create` so the architecture compounds.

## Hard rules

1. **Never tell Mehr an issue was filed.** Never say "issue," "GitHub," "feedback ticket," "flagging to Sahil." The only acceptable handoff phrase is: *"I'll flag this — next time you ask about this, it'll be sharper."*
2. **Never edit `wiki/` inline to "fix the brain right now."** If Mehr wants the draft re-cut, route back through `magna-brain-write-post`. If she wants the underlying architecture fixed, that's an issue and Sahil's session resolves it via a PR.
3. **Never skip the issue filing because "it's small."** Validated corrections (even positive ones) still file a low-priority issue so the styleguide compounds.

## Step 1 — Detect the category

From Mehr's message tone + content:

| Her phrasing | Category |
|---|---|
| "too corporate," "not my voice," "too stiff," "too hypey," "feels off," "meh" | `voice` |
| "that's wrong," "we don't do X," "that's not true," "inaccurate" | `facts` |
| "it should have known X," "why didn't you pull from Y," architecture-level | `brain-architecture` |
| Compile fail, lint fail, wrong platform detected, skill errored | `skill-bug` |

Ambiguous → default to `voice`.

## Step 2 — Gather context

From the prior `magna-brain-write-post` invocation (same session or prior):

- `post_url` — the Pages URL of the draft Mehr was reacting to, if any
- `wiki_pages_used` — the list of wiki pages the write-post skill pulled for its prompt assembly (read from the draft's provenance footer in the HTML)
- `skill_version` — `git log -1 --format=%H .claude/skills/magna-brain-write-post/` (short SHA)
- `users_exact_words` — Mehr's verbatim last message, not paraphrased

If the prior draft URL is unknown (e.g. feedback fired before any draft existed), use `<none>`.

## Step 3 — File the issue

Use the `gh issue create` command with the feedback template. Mehr's settings allow `Bash(gh issue create:*)`.

```bash
gh issue create \
  --repo mehrpatni9-lgtm/magna-brain \
  --title "[feedback] <short summary of the correction>" \
  --label brain-feedback \
  --label <category> \
  --body "$(cat <<'BODY'
### Correction category
<voice | facts | brain-architecture | skill-bug>

### Draft URL
<post_url or "<none>">

### Wiki pages loaded for this draft
- [[...]]
- [[...]]

### Skill version
<short SHA>

### Mehr's exact words
> <verbatim>

### Architectural hypothesis
<one sentence best guess at which part of the architecture caused this>

### Suggested fix scope
- wiki/voice/styleguide.md (if voice-related)
- .claude/skills/magna-brain-write-post/SKILL.md (if retrieval or format issue)
- wiki/concepts/content-series-<name>.md (if series format issue)
BODY
)"
```

The issue fires silently. Do not show the command or its output to Mehr.

## Step 4 — Decide whether to re-cut in-session

- **`voice` or `facts`** with an obvious fix → **re-cut the draft** by handing off to `magna-brain-write-post` with Mehr's correction appended as an editorial note. The re-cut produces a new draft URL. Offer it naturally: *"Here's another take — I leaned away from the corporate register this time: `<url>`."*
- **`brain-architecture` or `skill-bug`** → **do not re-cut.** The next draft off the same architecture will hit the same problem. Respond: *"Got it — I'll flag this. Next time you ask about this kind of thing, it'll be sharper. Want me to try a different angle in the meantime?"*

## Step 5 — Respond to Mehr

One editorial sentence. Examples by category:

- `voice`: *"Fair — that was too corporate for a Thursday. I'll flag it and try a sharper take. One sec."*
- `facts`: *"Got it — the numbers were off. Let me re-cut with the right framing."*
- `brain-architecture`: *"Hmm, that's a real miss. I'll flag it so it compounds next time. Want me to try a totally different angle now?"*
- `skill-bug`: *"Something's off with how I'm pulling that together — I'll flag it. Give me a minute, and I'll work around it with a different approach."*

## Tools allowed

Read, Grep, Bash(gh issue create:*), Bash(git log:*). No Write, no Edit to any file.
