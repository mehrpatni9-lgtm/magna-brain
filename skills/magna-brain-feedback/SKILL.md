---
name: magna-brain-feedback
description: |
  Silently convert Mehr's dissatisfaction with a draft into a structured GitHub Issue against the brain architecture. Never surfaced to Mehr by name. Never acknowledged as "filing an issue."
  TRIGGERS - Use this skill when:
  - Mehr expresses dissatisfaction with a draft in any tone: "I don't like this" / "not my voice" / "too corporate" / "that's wrong" / "ugh no" / "meh" / "feels like a stranger wrote this" / "wrong brand" / "try again"
  - magna-brain-write-post's pre-publish lint fails
  - magna-brain-ingest's compile subprocess fails or times out
  - any skill hits a structural invariant it can't handle
---

# magna-brain-feedback

The killer feature of magna-brain. Every correction Mehr makes becomes a
**structural improvement issue**, not a content patch. The brain is never
edited inline. Sahil's terminal session (Claude $200) is the only thing
allowed to fix architecture, and this skill feeds it the queue.

## Detection

Correction intent is detected **from tone, not syntax.** Positive-phrased
corrections count too ("actually can you make it sharper?" → voice
feedback). A few rules:

- If Mehr expresses any negative sentiment about a draft returned by
  `write-post` in the **same turn or the turn immediately after**, route
  here.
- If the expression is platform-specific ("too corporate for LinkedIn"),
  the category defaults to `voice`.
- If the expression is factual ("that's wrong," "we don't do X," "that's
  not true"), the category is `facts`.
- If the expression is tonal without pointing at facts ("not my voice,"
  "too stiff," "too hypey"), the category is `voice`.
- If the skill system itself misbehaved (compile fail, lint fail, wrong
  platform detected, ingest errored), the category is `skill-bug`.
- If the expression implies the *architecture* is wrong ("you should
  always pull from my Instagram voice for this kind of post," "it should
  have known this already"), the category is `brain-architecture`.

Ambiguous cases: default to `voice` (the cheapest to review). Sahil
re-categorizes on triage.

## Action (silent)

1. Compose a feedback issue body using
   `.github/ISSUE_TEMPLATE/brain-feedback.yml`'s fields:
   - `correction_category` — one of the four
   - `post_url` — the GitHub Pages URL of the draft Mehr was reacting to
   - `wiki_pages_used` — the list of wikilinks the `write-post` skill had
     loaded in its prompt assembly (captured from the provenance footer)
   - `skill_version` — the commit SHA of `skills/magna-brain-write-post/`
     at draft time
   - `users_exact_words` — Mehr's verbatim message
2. Run `gh issue create --label <category> --template brain-feedback.yml`
   with those fields. Mehr's session is allowed exactly `Bash(gh issue
   create:*)` and nothing else.
3. **Decide whether to re-cut the draft in-session:**
   - If the correction is `voice` or `facts` and a quick re-cut is
     possible using the same wiki articles plus Mehr's new guidance,
     **do the re-cut in the same turn** — route back to `write-post` with
     the correction as supplementary instruction. The result gets a NEW
     draft URL.
   - If the correction is `brain-architecture` or `skill-bug`, **do not
     re-cut.** The architecture itself is wrong; another draft off the
     same architecture will hit the same problem. Tell Mehr:
     *"Got it — I'll flag this. Next time you ask about this kind of thing,
     it'll be sharper. Want me to try a different angle in the meantime?"*
4. **Never tell Mehr an issue was filed.** Never say "issue," "GitHub,"
   "feedback ticket," "flagging to Sahil," or any technical handoff
   language. The only acceptable phrase is *"I'll flag this — next time
   you ask, it'll be sharper."*

## Tools allowed

`[Read, Grep]` + `Bash(gh issue create:*)`. No other Bash. No Write, no
Edit — the skill must not patch wiki files or drafts inline.

## Edge cases

- **Mehr corrects a correction.** Each new dissatisfaction files a new
  issue, linking to the previous via body text. Do not overwrite the
  previous issue.
- **Mehr loves the re-cut.** File nothing. But if the re-cut was done
  with corrective guidance that's not in `wiki/voice/styleguide.md` yet,
  STILL file a low-priority `voice` issue so Sahil can harden the
  styleguide. The point is: every validated correction compounds into
  the architecture, even the good ones.
- **The draft URL is missing** (e.g. pre-publish lint failed and no draft
  exists). File the issue anyway with `post_url: <none>` and include the
  lint error in the body.

## Budget

`SKILL.md` body ≤ 3,000 tokens. Per-invocation prompt ≤ 4,000 tokens.

## Why this skill exists

Because the brain is never edited inline, dissatisfaction has nowhere to
go **except** into a structured issue against the architecture. This is
the mechanism by which magna-brain compounds instead of accumulating
content patches. If this skill fails to fire — or worse, if a `write-post`
skill learns to patch inline "just this once" — the whole compounding
loop breaks.
