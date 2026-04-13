---
name: magna-brain-ingest
description: Silently capture anything Mehr drops into chat — files, links, pasted text, images, voice notes — into today's raw log so the brain "remembers" it for future posts. Zero confirmations, zero file-path language. TRIGGERS - Use this skill when Mehr attaches a file, pastes a URL or article text, says "here's stuff I found" / "look at this" / "read these" / "add this to the brain" / "I want to remember this" / dictates a voice note / sends an image.
---

# magna-brain-ingest

The zero-ops capture path. Mehr drops stuff; the brain absorbs it. **Never ask her to confirm.** If there's genuine ambiguity, proceed anyway and respond editorially about what you saw.

## Hard rules

1. **Never mention `raw/`, file paths, compilation, the wiki, or any technical noun.** Ever.
2. **Never ask "should I add this to your knowledge base?"** Just do it and respond with an insight.
3. **Never overwrite.** Today's raw log is append-only.

## Step 1 — Detect intent

Ingest intent looks like:
- Attached files (any format)
- Pasted URLs (one or many)
- Pasted block of prose that's clearly source material (quotes, article text, brand materials, stats, research, "I read this today")
- Dictation or voice notes
- Images of whiteboards, screenshots, pages

If the message mixes ingest with a post request ("here's stuff I found, can you turn it into a LinkedIn post?"), run ingest FIRST, then hand off to `magna-brain-write-post`.

If the message is purely a question about existing knowledge ("what do you know about X?"), do NOT ingest — route to `magna-brain-query` instead.

## Step 2 — Resolve today's raw log

```bash
today=$(date +%Y-%m-%d)
raw_file="raw/${today}.md"
```

If `raw/${today}.md` doesn't exist, create it with a single header line: `# Raw log — ${today}\n`.

## Step 3 — Append each item

For each piece of content Mehr dropped, append a block to today's raw log in this format:

```markdown
## [<kind>] <brief label> — <HH:MM>

<body>
```

Where `<kind>` is one of: `url`, `pdf`, `image`, `voice`, `note`, `paste`.

### Handling per kind

- **URL**: append the URL and a one-line description of what it is. If you can reach the URL with allowed tools, fetch title + a short excerpt; if not, leave the URL alone and ask editorially in chat what the piece is about.
- **Pasted text**: append verbatim, prefixed with `> ` on each line so it's clearly a quote, not Mehr's framing.
- **File attachment (any kind)**: Claude Code has already loaded the file content into the conversation. Write a short extracted summary + key quotes into the raw log. For PDFs, use `pdftotext` (allowed) if the tool is available and the file is local. For images, describe what you see (Magna brand logo? whiteboard notes? competitor post screenshot?).
- **Voice note**: if transcription is available via the client, append the transcript. If not, append `[voice note — transcription unavailable, Mehr should re-dictate if context is important]`.

## Step 4 — Write to `raw/`

Use the Write tool. Append to today's raw log. Never modify prior entries.

## Step 5 — Respond editorially in chat

Give Mehr a 2–4 sentence insight about what she just dropped. The insight should:

- Name what you saw, in plain language ("a brand guide from a competitor," "a founder post about capital allocation," "three articles on authenticity marketing")
- Connect it to the existing brain if there's an obvious link ("this lines up with the angle we've been building on clarity-over-information")
- Offer one next action as an editorial choice ("want me to turn it into a post or keep stacking?")

**Do not say:**
- "Added to raw/2026-04-13.md"
- "Compiling the wiki"
- "Ingest complete"
- "Set compile flag to true"
- Anything that references the file system

## v1 limitation — no compile step yet

In v1, ingest writes to `raw/` but does NOT automatically update the wiki layer. The wiki is seeded from `reference/` once, and subsequent raw logs are read by `magna-brain-write-post` directly as supplementary context (not as permanent brain content). This is invisible to Mehr — she experiences ingest as "the brain remembered" either way.

When the compile subprocess is built (Phase 3), this skill will gain a compile trigger at the end of Step 5. Until then, raw logs accumulate in `raw/` and are pulled into `write-post` prompts on demand.

## Failure mode

If a Write to `raw/` fails, respond editorially: *"Hmm, something's off with how I'm filing today's notes — I'll flag it so it gets fixed. Hold on to that thought for a sec, I still want to work with it."* Auto-invoke `magna-brain-feedback` with category `skill-bug`.
