---
name: magna-brain-ingest
description: Silently capture anything dropped into chat — files, links, pasted text, images, voice notes — and inline-compile it into the structured brain so the wiki compounds every time the contributor enriches. Captures the contributor's name tag automatically. Zero confirmations, zero file-path language. TRIGGERS - Use this skill when the contributor attaches a file, pastes a URL or article text, says "here's stuff I found" / "look at this" / "read these" / "add this to the brain" / "I want to remember this" / dictates a voice note / sends an image.
---

# magna-brain-ingest

The zero-ops capture + self-compile path. The contributor drops stuff; the brain absorbs it AND restructures it into wiki articles in the same turn; everything gets pushed to GitHub so the auto-rendered brain page updates within ~90 seconds. **Never ask for confirmation.** Act, then respond editorially.

## Hard rules

1. **Never mention** `raw/`, `wiki/`, file paths, commits, pushes, compile, contributors, name tags, or any technical noun. Ever.
2. **Never ask "should I add this to your knowledge base?"** Just do it and respond with an insight.
3. **Never overwrite or delete** existing wiki files. The compile step is **additive** — new source files, new entity files, new concept files, new synthesis angles. Existing articles are only **appended to** (new facts, new references), never rewritten.
4. **Never touch `wiki/voice/`**. Voice is hand-curated by Sahil. If a contributor drops a post they like and it feels like a new exemplar, file a `voice` feedback issue via `magna-brain-feedback` instead of writing the file yourself.
5. **Never make structural changes** to the schema in `AGENTS.md`. Every new file must match the existing frontmatter shape.
6. **Always commit and push at the end** using the contributor's git identity. A silent capture that isn't pushed doesn't exist.

## Step 0 — Resolve the contributor's identity (do this FIRST, every time)

```bash
contributor=$(git config user.name)
```

If `git config user.name` is empty, fall back to the value of the `USER` environment variable, then default to `"Unknown"` only as a last resort. Use `$contributor` as the value of every `contributed_by:` frontmatter field you write in this session, and use the contributor's normal git identity for the commit author (do NOT pass `-c user.email=` or `-c user.name=` overrides — let git use the local config that the onboarding paste set).

This identity travels with everything the contributor adds today, so the brain page's contributor strip and every wiki article carry the right name tag.

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
slug=<a 2-4 word kebab-case label for this drop>
raw_file="raw/${today}-${slug}.md"
```

The repo convention is `raw/<YYYY-MM-DD>-<topic>.md` — multi-file-per-day is allowed. If a file with that exact name already exists, append a `-2` / `-3` suffix to the slug.

Write the raw file with frontmatter that includes `contributed_by: "$contributor"`:

```yaml
---
date: <YYYY-MM-DD>
source: <human description of where this came from>
contributed_by: "<contributor>"
---
```

Then write the body — see Step 2.

## Step 2 — Body of the raw file

For each piece of content the contributor dropped, append a block to the raw file body:

```markdown
## [<kind>] <brief label> — <HH:MM>

<body>
```

Where `<kind>` is one of: `url`, `pdf`, `image`, `voice`, `note`, `paste`.

- **URL**: append the URL and a short description of what it is. If you can reach the URL (no blanket network access — only what allowed tools expose), extract title + key points. Otherwise, leave the URL and let the contributor's framing guide it.
- **Pasted text**: append verbatim, each line prefixed with `> ` so it's clearly a quote.
- **PDF**: use `pdftotext` (allowed). Extract text, append a summary + key quotes.
- **Image**: describe what you see (brand asset? whiteboard? competitor screenshot?).
- **Voice note**: append transcript if available, else `[voice note — transcription unavailable]`.

## Step 3 — Inline compile (the self-learning part)

After the raw file is written, **decide what the wiki should gain from this drop** and make the changes directly. **Every new wiki file you create in this step MUST include `contributed_by: "$contributor"` in its frontmatter.**

Read these files to ground the compile (only these — do NOT Glob the whole wiki):

1. `wiki/index.md` — the master index
2. `wiki/_index/topic-summaries.md` — topic clusters (if exists)
3. `AGENTS.md` — the schema every new wiki file must match

Then decide, per dropped item:

### Is it a new source?
If the drop is a substantive document (PDF, URL with real content, an article), create a new `wiki/sources/<kebab-slug>.md` file. Filename comes from the title. Frontmatter:

```yaml
---
type: source
title: "<human title>"
kind: pdf | url | image | voice | note | spreadsheet | research | transcript
origin: <path in raw/ or URL>
ingested: <today>
contributed_by: "<contributor>"
tags: [relevant, tags]
sources: []
corrected_by: []
---
```

Body = faithful extraction, no interpretation.

### Does it introduce a new entity?
If the drop names a person, brand, product, campaign, or audience segment that isn't already in `wiki/entities/`, create a new entity file. Filename = kebab-case name. Frontmatter:

```yaml
---
type: entity
name: "<canonical name>"
kind: person | brand | product | campaign | audience | channel
aliases: ["<other names>"]
tags: []
sources: [[source-slug-1]]
created: <today>
updated: <today>
contributed_by: "<contributor>"
corrected_by: []
---
```

Body sections:
1. **One-line definition** (≤140 chars)
2. **Key facts** — every bullet cites `[[source-slug]]`
3. **Relationships** — wikilinks to other entities
4. **Open questions** — what's unknown

### Does it introduce a new concept?
Same shape as entity, with `type: concept`. Body: TL;DR · Why it matters for Magna · Supporting sources · Related concepts · Contradictions/open threads.

### Does it justify a new synthesis angle?
Create `wiki/synthesis/<slug>.md`. Same frontmatter shape with `type: synthesis` plus `draws_on: [[a]], [[b]]`. Body: The angle · Evidence trail · Counter-angle · Post hooks.

### Does it update an EXISTING article?
**Append only.** Add new facts to the relevant article's "Key facts" section with citations. Add a line to the "Contributors" section at the bottom: `- <date> — <contributor> (added <N> facts)`. Never rewrite prose that's already there.

### Update the master index
If you created any new wiki files, add one line per file to `wiki/index.md` under the correct section. Keep `wiki/index.md` under 1,500 tokens.

### Append to the log
Add a block to `wiki/log.md` (append-only) describing what changed:

```
## <ISO timestamp>
- ingest: raw/<file>.md (N new items)
- contributed_by: "<contributor>"
- created: sources/<slug>, concepts/<slug>, ...
- updated: entities/<slug> (added N facts)
- refreshed: index.md
- corrected_by: []
```

## Step 4 — Commit and push everything (using contributor identity)

One commit, everything bundled. **Do NOT pass `-c user.email=` or `-c user.name=` overrides** — let git use the contributor's local config:

```bash
git add raw/ wiki/
git commit -m "ingest: <editorial one-line description of today's drop>"
git pull --rebase origin main 2>&1 || true
git push origin main
```

The `pull --rebase` is important — multiple contributors push to main, so always rebase before pushing. If the rebase produces conflicts in append-only files (`wiki/log.md`, `wiki/index.md`), accept both sides; the schema is additive.

Do this silently. Do NOT show the contributor the commands or output.

## Step 5 — Post-condition check (NEW — guards against compile drift)

Run a quick verification:

```bash
last_diff=$(git show --stat HEAD)
```

Inspect `last_diff`. If it touched **only `raw/`** and not any path under `wiki/`, the compile step was silently skipped. **You must retry**:

1. Re-read the raw file you just wrote.
2. Re-do Step 3 (inline compile) — create the wiki files this time.
3. Stage `wiki/` and create a SECOND commit with message `ingest: compile — <same editorial description>`.
4. Pull-rebase and push again.

If after one retry the wiki/ commit STILL didn't happen, auto-invoke `magna-brain-feedback` with category `skill-bug` and note the failure. Then proceed to Step 6 anyway — the contributor still gets a response.

## Step 6 — Respond editorially

Give the contributor a 2–4 sentence insight about what they just dropped. The insight should:

- Name what you saw, in plain language ("a brand guide from a competitor," "a founder post about capital allocation," "three articles on authenticity marketing")
- Connect it to the existing brain if there's an obvious link
- Acknowledge the compile obliquely, without naming it
- Offer one next action as an editorial choice

**End your response with the visibility line** — one italic sentence + a link to the most salient compiled article (the entity/concept/synthesis the compile created or appended to). Format:

> *"Sharper next time you ask about strategy or capital — landed in the brain here: <https://mehrpatni9-lgtm.github.io/magna-brain/brain/article/<section>/<slug>.html>."*

If the compile produced multiple new articles, link to the brain page section anchor (e.g. `/brain/#concepts`) instead of any single article.

**Never say:**
- "Added to raw/2026-04-13.md"
- "Compiling the wiki"
- "Created wiki/sources/foo.md"
- "Committed and pushed"
- "Set compile flag to true"
- "Tagged you as contributor"
- Any file system language

## Budget

SKILL.md body ≤ 3,500 tokens. Per-invocation prompt assembly ≤ 10,000 tokens. Never Glob `wiki/**`.

## Safety rails

- **Additive only.** Never delete. Never rewrite existing prose. Append facts, create new files. That's it.
- **No voice writes.** `wiki/voice/` is denied by settings.json.
- **Schema compliance.** Every new file must have valid frontmatter per `AGENTS.md`, including `contributed_by`.
- **Identity preserved.** Always use `git config user.name` for both commit author and `contributed_by` frontmatter. Never hardcode an author.
- **Index budget.** `wiki/index.md` must stay under 1,500 tokens. Demote older entries to `wiki/_index/topic-summaries.md` if needed.

## Failure modes

If any step fails:
1. Do NOT retry destructively.
2. Keep whatever succeeded.
3. Respond editorially: *"Got the core of it down, but I'm still chewing on where it fits in the bigger thinking — I'll flag it so it gets sharper. Hold on to the idea, it's not lost."*
4. Auto-invoke `magna-brain-feedback` with category `skill-bug`.
