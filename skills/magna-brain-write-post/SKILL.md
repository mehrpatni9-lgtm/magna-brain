---
name: magna-brain-write-post
description: |
  Draft a platform-specific post (LinkedIn, Instagram, long-form, short-form) in Magna's established voice, using the wiki as the source of truth. Publishes a GitHub Pages draft and returns a clean URL.
  TRIGGERS - Use this skill when:
  - Mehr says "write me a post about X" / "give me a linkedin post on X" / "something for insta on X" / "draft a caption about X"
  - Mehr shares an idea and asks for it in Magna's voice
  - Mehr says "turn this into a post" after an ingest
---

# magna-brain-write-post

The only skill allowed to read `wiki/voice/`. The only skill allowed to
write to `output/` and push to the `drafts/` branch. Never writes to `wiki/`.

## Input

- A topical idea from Mehr, potentially one sentence, potentially a dump.
- The platform target (LinkedIn, Instagram, long-form, short-form). If
  ambiguous, default to LinkedIn and note the default choice editorially
  ("I'll take this as LinkedIn unless you tell me otherwise").

## Retrieval plan (index-first, drill-down)

1. **Read the SessionStart injection** already in context: `wiki/index.md`
   + `wiki/_index/topic-summaries.md`. Do NOT re-read them.
2. **Pick candidate articles** from the index that match the topic.
   Preferentially select from `wiki/synthesis/` — those are pre-built
   angles. Fall back to `wiki/concepts/`, then `wiki/entities/`. Never
   Glob, never scan sources directly.
3. **Drill into the ≤ 6 most relevant articles** by wikilink. Respect the
   `write-post` prompt assembly cap of 12,000 tokens total.
4. **Load the voice layer:**
   - `wiki/voice/styleguide.md` (≤ 1,000 tokens)
   - Run a cheap prior call against the headers of `wiki/voice/exemplars/`
     to pick the 2 best-matched exemplars for this topic / platform.
     Load only those 2 (≤ 1,000 tokens combined). No embeddings.
5. **Assemble the prompt** within the 12,000-token ceiling.

## Generation plan

1. Draft the post in one pass. Platform-specific length and structure
   (e.g. LinkedIn = hook + body + POV + CTA; Instagram = tighter, more
   evocative, with a line-break rhythm).
2. Verify every factual claim in the draft cites back to a wiki article
   loaded in this prompt. If a claim has no citation, rewrite to remove
   the claim or add a `[needs source]` marker that the lint skill will
   block on publish.
3. Append the **content idea** at the top of the draft output page,
   verbatim from Mehr's request, so reviewers see the brief alongside the
   result.
4. Append the **provenance footer** to the draft page:
   - List of wiki articles used (as wikilinks, rendered to anchors in the
     Pages build)
   - Skill version
   - Timestamp
   - A **"this doesn't feel right"** link that deep-links to
     `gh issue new` with the feedback template pre-filled (post URL,
     articles used, skill version). This is the path that turns
     dissatisfaction into a structured feedback issue WITHOUT requiring a
     separate action from Mehr.

## Publish plan

1. Write the draft to `output/<YYYY-MM-DD>-<slug>.md`.
2. Checkout / update the `drafts/<YYYY-MM-DD>-<slug>` branch (create if
   absent). `drafts/*` is the only branch namespace Mehr's session is
   allowed to push to.
3. Commit: `git add output/ && git commit -m "draft: <slug>"`.
4. Push: `git push origin drafts/<YYYY-MM-DD>-<slug>`.
5. The `.github/workflows/pages.yml` workflow publishes the `output/`
   directory to GitHub Pages on that branch.
6. Compute the Pages URL and return it to Mehr as plain chat:
   *"Here's your post — take a look: `<url>`. If any of it feels off, just
   tell me and I'll re-cut it."*

## Chat rules

- NEVER mention `output/`, `drafts/`, branches, commits, pushes, workflows,
  or skill versions in chat.
- NEVER enumerate which wiki articles were used. If Mehr asks "where did
  you get that from," route to `magna-brain-query` instead.
- If Mehr pushes back on the draft, **do not rewrite the post in chat**.
  Instead, route to `magna-brain-feedback` — the feedback skill decides
  whether to re-cut with a corrective instruction or to file an
  architectural issue against the voice/styleguide.
  Rewriting inline is the anti-pattern this whole system exists to avoid.

## Tools allowed

`[Read, Write, Edit, Glob, Grep]` + `Bash(git add:*)`, `Bash(git commit:*)`,
`Bash(git push:origin drafts/*)`, `Bash(git checkout:*)`. No other Bash.

## Budget

`SKILL.md` body ≤ 3,000 tokens. Prompt assembly ≤ 12,000 tokens.
Voice layer ≤ 2,000 tokens of that. Enforced by `magna-brain-lint`.
