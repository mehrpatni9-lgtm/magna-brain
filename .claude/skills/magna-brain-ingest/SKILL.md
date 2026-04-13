---
name: magna-brain-ingest
description: Silently capture anything Mehr drops into chat — files, links, pasted text, images, voice notes — and inline-compile it into the structured brain so the wiki compounds every time she enriches. Zero confirmations, zero file-path language. TRIGGERS - Use this skill when Mehr attaches a file, pastes a URL or article text, says "here's stuff I found" / "look at this" / "read these" / "add this to the brain" / "I want to remember this" / dictates a voice note / sends an image.
---

# magna-brain-ingest

The zero-ops capture + self-compile path. Mehr drops stuff; the brain absorbs it AND restructures it into wiki articles in the same turn; everything gets pushed to GitHub so the Pages brain browser updates within ~90 seconds. **Never ask her to confirm.** Act, then respond editorially.

## Hard rules

1. **Never mention** `raw/`, `wiki/`, file paths, commits, pushes, compile, or any technical noun. Ever.
2. **Never ask "should I add this to your knowledge base?"** Just do it and respond with an insight.
3. **Never overwrite or delete** existing wiki files. The compile step is **additive** — new source files, new entity files, new concept files, new synthesis angles. Existing articles are only **appended to** (new facts, new references), never rewritten.
4. **Never touch `wiki/voice/`**. Voice is hand-curated by Sahil. If Mehr drops a post she likes and it feels like a new exemplar, file a `voice` feedback issue via `magna-brain-feedback` instead of writing the file yourself.
5. **Never make structural changes** to the schema in `AGENTS.md`. Every new file must match the existing frontmatter shape.
6. **Always commit and push at the end.** A silent capture that isn't pushed doesn't exist.

## Intent detection

Ingest intent looks like:
- Attached files (any format)
- Pasted URLs (one or many)
- Pasted block of prose that's clearly source material (quotes, article text, brand materials, stats, research, "I read this today")
- Dictation or voice notes
- Images of whiteboards, screenshots, pages

If the message mixes ingest with a post request ("here's stuff I found, can you turn it into a LinkedIn post?"), run ingest FIRST (including compile + push), then hand off to `magna-brain-write-post`.

If the message is purely a question about existing knowledge ("what do you know about X?"), do NOT ingest — route to `magna-brain-query` instead.

## Step 1 — Resolve today's raw log

```bash
today=$(date +%Y-%m-%d)
raw_file="raw/${today}.md"
```

If `raw/${today}.md` doesn't exist, create it with a single header line: `# Raw log — ${today}\n`.

## Step 2 — Append each item to the raw log

For each piece of content Mehr dropped, append a block to today's raw log:

```markdown
## [<kind>] <brief label> — <HH:MM>

<body>
```

Where `<kind>` is one of: `url`, `pdf`, `image`, `voice`, `note`, `paste`.

- **URL**: append the URL and a short description of what it is. If you can reach the URL (no blanket network access — only what allowed tools expose), extract title + key points. Otherwise, leave the URL and let Mehr's framing guide it.
- **Pasted text**: append verbatim, each line prefixed with `> ` so it's clearly a quote.
- **PDF**: use `pdftotext` (allowed). Extract text, append a summary + key quotes.
- **Image**: describe what you see (brand asset? whiteboard? competitor screenshot?).
- **Voice note**: append transcript if available, else `[voice note — transcription unavailable]`.

## Step 3 — Inline compile (the self-learning part)

This is the new v1.5 behavior. After the raw log is written, **decide what the wiki should gain from this drop** and make the changes directly.

Read these files to ground the compile (only these — do NOT Glob the whole wiki):

1. `wiki/index.md` — the master index (already in session context if loaded at start)
2. `wiki/_index/topic-summaries.md` — topic clusters
3. `AGENTS.md` — the schema every new wiki file must match

Then decide, per dropped item:

### Is it a new source?
If the drop is a substantive document (PDF, URL with real content, an article), create a new `wiki/sources/<kebab-slug>.md` file. Filename comes from the title. Frontmatter matches `AGENTS.md` source schema:

```yaml
---
type: source
title: "<human title>"
kind: pdf | url | image | voice | note
origin: <path in raw/ or URL>
ingested: <today>
tags: [relevant, tags]
sources: []
corrected_by: []
---
```

Body = faithful extraction, no interpretation.

### Does it introduce a new entity?
If the drop names a person, brand, product, campaign, or audience segment that isn't already in `wiki/entities/`, create a new entity file. Filename = kebab-case name. Frontmatter per `AGENTS.md` entity schema. Body structure:

1. **One-line definition** (≤140 chars)
2. **Key facts** — every bullet cites `[[source-slug]]`
3. **Relationships** — wikilinks to other entities
4. **Open questions** — what's unknown

### Does it introduce a new concept?
If the drop contains an idea, framework, or recurring theme not already in `wiki/concepts/`, create a new concept file. Same schema rules.

### Does it justify a new synthesis angle?
If the drop connects multiple existing concepts/entities into a new reusable angle for a post, create a new `wiki/synthesis/<slug>.md`. This is the highest-value output of a compile — synthesis angles are what `magna-brain-write-post` reaches for first.

### Does it update an EXISTING article?
If the drop adds a new fact to an existing entity or concept, **append** that fact to the relevant article's "Key facts" section. Always cite the new source with a wikilink. **Never rewrite prose that's already there.**

### Update the master index
If you created any new wiki files, add one line per file to `wiki/index.md` under the correct section (Entities, Concepts, Sources, Synthesis angles). Keep `wiki/index.md` under 1,500 tokens — if adding new lines would push it over, collapse older lines into `wiki/_index/topic-summaries.md` instead.

### Append to the log
Add a block to `wiki/log.md` (append-only) describing what changed:

```
## <ISO timestamp>
- ingest: raw/<date>.md (N new items)
- created: sources/<slug>, concepts/<slug>, ...
- updated: entities/<slug> (added N facts)
- refreshed: index.md
```

## Step 4 — Commit and push everything

One commit, everything bundled:

```bash
git add raw/ wiki/
git -c user.email='magna-brain@noreply.github.com' -c user.name='magna-brain' \
    commit -m "ingest: <editorial one-line description of today's drop>"
git push origin main
```

Do this silently. Do NOT show Mehr the commands or the output. If `git push` fails (auth, network, whatever), keep the local files and auto-invoke `magna-brain-feedback` with category `skill-bug`.

## Step 5 — Respond editorially

Give Mehr a 2–4 sentence insight about what she just dropped. The insight should:

- Name what you saw, in plain language ("a brand guide from a competitor," "a founder post about capital allocation," "three articles on authenticity marketing")
- Connect it to the existing brain if there's an obvious link ("this lines up with the angle we've been building on clarity-over-information")
- Acknowledge the compile obliquely, without naming it: *"Added this to your thinking on X — the brain will use it next time you ask for something on this."*
- Offer one next action as an editorial choice: *"Want me to turn it into a post, or keep stacking?"*

**Never say:**
- "Added to raw/2026-04-13.md"
- "Compiling the wiki"
- "Created wiki/sources/foo.md"
- "Committed and pushed"
- "Set compile flag to true"
- Any file system language

## Budget

SKILL.md body ≤ 3,000 tokens. Per-invocation prompt assembly ≤ 10,000 tokens (slightly higher than query because compile requires reading a handful of wiki files to decide placement). Never Glob `wiki/**`.

## Safety rails

- **Additive only.** Never delete. Never rewrite existing prose. Append facts, create new files. That's it.
- **No voice writes.** `wiki/voice/` is denied by settings.json. If you try to write there, it'll be blocked — use `magna-brain-feedback` with the `voice` label instead.
- **Schema compliance.** Every new file must have valid frontmatter per `AGENTS.md`. If you can't match the schema, write to `raw/` only and log a `skill-bug` feedback issue describing the ambiguity.
- **Index budget.** `wiki/index.md` must stay under 1,500 tokens. If adding a line would exceed it, demote older entries to `wiki/_index/topic-summaries.md` first.

## Failure modes

If any step fails (write blocked, compile confused, commit fails, push fails):
1. Do NOT retry destructively.
2. Keep whatever succeeded (e.g. if raw/ was written but the compile couldn't place a fact, that's fine — raw/ persists).
3. Respond editorially: *"Got the core of it down, but I'm still chewing on where it fits in the bigger thinking — I'll flag it so it gets sharper. Hold on to the idea, it's not lost."*
4. Auto-invoke `magna-brain-feedback` with category `skill-bug`.
