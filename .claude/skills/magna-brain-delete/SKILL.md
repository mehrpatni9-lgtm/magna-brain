---
name: magna-brain-delete
description: Remove an entity, concept, source, synthesis angle, daily drop, or draft from the brain. Mehr-only — gated on git config user.name. Other contributors get a polite editorial deflection that routes to feedback. TRIGGERS - Use this skill when the contributor says "remove X" / "delete X" / "take out X" / "get rid of X" / "X shouldn't be in the brain" / "drop the page on Y" / "kill the Z entry".
---

# magna-brain-delete

The editorial-removal path. Mehr is the brain's Creative Director and has authority to remove anything she doesn't want in it. Everyone else does NOT — they can add (via [[magna-brain-ingest]]) but not remove. This skill enforces that distinction.

## Hard rules

1. **Only Mehr Patni can remove.** Step 0 enforces this. Other contributors get a deflection.
2. **Never delete** anything under `wiki/voice/`, `.claude/`, `.github/`, `tools/`, `reference/`, `CLAUDE.md`, `AGENTS.md`, `TOKEN_BUDGET.md`, `README.md`, or `PHASE3-RECON.md`. These are architectural files, not brain content.
3. **Removal is a soft-delete in the wiki sense — `git rm` only.** No destructive `rm`. No history rewrites. The deletion shows up in `git log` with Mehr as author.
4. **Always append to `wiki/log.md`.** Removals are logged the same way ingests are logged.
5. **Never mention** files, paths, commits, pushes, or git in the response.

## Step 0 — Identity gate (do this FIRST, every time)

```bash
contributor=$(git config user.name)
```

If `$contributor` is **NOT** exactly `"Mehr Patni"`:

- Do NOT proceed.
- Respond editorially: *"That's a Mehr call — I can't take things out of the brain on my own. Want me to flag it so she gets a heads-up the next time she's in?"*
- If they say yes, auto-invoke `magna-brain-feedback` with category `removal-request` and a brief summary of what they wanted removed and why.
- Stop here.

If `$contributor` IS `"Mehr Patni"`, proceed to Step 1.

## Step 1 — Identify what to remove

Parse the contributor's intent. They might say things like:
- *"Remove the Magna Meetup entry"* → `wiki/entities/magna-meetup.md`
- *"Drop the Sleep on Horses concept"* → `wiki/concepts/sleep-on-horses.md`
- *"Delete the curriculum source"* → `wiki/sources/magna-curriculum-r4.md`
- *"Take out yesterday's daily drop on portfolio companies"* → `raw/2026-04-14-portfolio-affiliations-content-plan.md`
- *"Kill that Compass carousel draft"* → `output/2026-04-14-magna-compass-carousel.html`

Build a candidate list:

```bash
matches=$(find wiki raw output -maxdepth 3 -type f \
  \( -name "*.md" -o -name "*.html" \) \
  -not -path "wiki/voice/*" \
  | grep -i "<keyword>")
```

If you find:
- **Exactly one match** — proceed to Step 2 with that path.
- **Multiple matches** — list the candidates back to her editorially: *"I see a few things that match — which one: [option A] · [option B] · [option C]?"* Wait for her to clarify.
- **Zero matches** — say editorially: *"I can't find that in the brain — might be named differently. Can you describe what you're trying to remove a bit more?"*

## Step 2 — Refuse if the target is architectural

Reject the removal (without `git rm`) if the target path matches any of:

- `wiki/voice/**` (hand-curated)
- `.claude/**`, `.github/**`, `tools/**`, `reference/**`
- `CLAUDE.md`, `AGENTS.md`, `TOKEN_BUDGET.md`, `README.md`, `PHASE3-RECON.md`
- Any file at the repo root that isn't part of `raw/`, `wiki/`, or `output/`

If matched, respond editorially: *"That one's part of how the brain runs, not what's in it — I'd want to flag it for review before touching that. Sound good?"* Auto-invoke `magna-brain-feedback` with category `architectural-removal-request`.

Otherwise proceed to Step 3.

## Step 3 — Remove and log

Atomic sequence:

```bash
git rm <path>

# Append to wiki/log.md (using a heredoc the same way ingest does)
ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)
cat >> wiki/log.md <<LOG

## $ts — removal
- removed: <path>
- contributed_by: "$contributor"
- reason: <one-line editorial reason captured from Mehr's request>
- corrected_by: []
LOG

git add wiki/log.md
git commit -m "remove: <slug> (Mehr — <one-line reason>)"
git pull --rebase origin main 2>&1 || true
git push origin main
```

If the commit fails (path not staged, conflict, etc.), do NOT retry destructively. Surface the failure via Step 4's failure response and route to `magna-brain-feedback`.

## Step 4 — Respond editorially

Two sentences max. Confirm the removal in human language without saying "git" or "deleted from path." Examples:

> *"Took it out — Magna Meetup is gone from the brain. Reload in a minute and you'll see the change."*

> *"Cleared. The brain won't reference [thing] again unless we re-ingest it from a fresh source."*

If she asked you to remove something that affected multiple files (e.g. an entity that was wikilinked from many concepts), gently note: *"Just the one entry. The other articles that mention it still do — want me to clean those up too, or leave them as-is?"*

**Failure response** (if Step 3 failed):
> *"Couldn't quite get it out cleanly — flagging it so the wiring gets fixed. Try once more in a few minutes; if it's still stuck, I'll loop back."*

Then auto-invoke `magna-brain-feedback` with category `skill-bug` and the underlying error.

## Budget

SKILL.md body ≤ 1,500 tokens. Per-invocation prompt assembly ≤ 4,000 tokens — this skill should be fast and surgical.

## Safety rails

- **Mehr-only.** Step 0 is the entire access control. If `git config user.name` is anything other than "Mehr Patni", the skill exits without touching anything.
- **No destructive `rm`.** `git rm` only. Files stay recoverable in git history.
- **No voice writes.** `wiki/voice/` removal is rejected at Step 2.
- **Architectural files are off-limits.** Step 2 refuses anything outside `raw/`, `wiki/` (excluding voice), or `output/`.
- **Append-only log.** Every removal appears in `wiki/log.md` so the audit trail is complete.

## Related skills

- [[magna-brain-ingest]] — the additive sibling. Together they make the brain bidirectional but identity-gated.
- [[magna-brain-feedback]] — the destination for non-Mehr removal requests and skill bugs.
