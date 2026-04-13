---
name: magna-brain-ingest
description: |
  Silently ingest whatever Mehr drops into chat — files, links, pasted text, images, voice notes — into the daily log, then trigger the compile step. Zero confirmations, zero file-path language.
  TRIGGERS - Use this skill when:
  - Mehr attaches a file of any format
  - Mehr pastes a URL or a block of raw text that is clearly source material, not a question
  - Mehr says "here's stuff I found" / "look at this" / "read these" / "add this to the brain" / similar
  - Mehr dictates a voice note or sends an image of a page/whiteboard/screenshot
---

# magna-brain-ingest

The zero-ops ingest path. Mehr never sees a file path, never confirms, never
waits. Everything she drops lands in today's daily log and then triggers
the compile subprocess that updates the wiki.

## Intent detection

Distinguish **ingest intent** from **write-post intent** and **query intent**
from tone and content, not keywords:

- If the message contains attached files or a URL with no explicit "write
  me a post" / "what do you know about," route here.
- If the message is prose with quotes, transcripts, article text, brand
  materials, stats, or "I found this," route here.
- If in genuine doubt, route to ingest by default — Mehr can always ask for
  a post next turn.

## What it does

1. Resolve today's date → `raw/<YYYY-MM-DD>.md`. Append-only.
2. For each piece of content:
   - **PDF:** extract text via Sahil-side helper. If vision is needed for
     diagrams, call vision on specific pages.
   - **Image:** caption + OCR via vision.
   - **URL:** fetch via the fetch subprocess. Strip boilerplate. Preserve
     the URL as the source of record.
   - **Voice:** transcribe via whisper.
   - **Pasted text:** append verbatim with a `>` quote marker so the compile
     step can distinguish dumped quotes from Mehr's own framing.
3. Each item gets a one-line header `## [<kind>] <brief label> — <timestamp>`
   in the daily log.
4. Compute SHA-256 of the updated `raw/<date>.md`; if different from
   `state.json`'s last value, trigger the compile subprocess.
5. Return to Mehr in plain chat: a 2–4 sentence *insight* about what she
   just dropped, phrased editorially. Example: *"Got it — this reads like
   a takedown of performative brand activism, and it lines up with the
   angle we've been building on authenticity. Want me to turn it into a
   post or keep stacking?"* No file paths. No "added to your knowledge base."

## Tools allowed

`[Read, Write, Edit, Glob, Grep]` — plus whatever subprocesses are needed
for PDF/image/voice/URL. **No inline `allowed-tools: Bash`** per the
explicit non-goal: prompt injection from clipped web content is the
highest-risk attack surface in this whole system.

## Compile-step invocation

After writing the daily log, the skill spawns the Sahil-side compile
subprocess defined in `AGENTS.md`. The subprocess runs with
`acceptEdits` and `max_turns: 30`. **Mehr's session does NOT run in
acceptEdits mode.** The subprocess is a *child process* with its own
permission scope.

If the compile subprocess fails or times out:
1. Keep the daily log in place (don't roll back — Mehr's input is
   persisted no matter what).
2. Emit a plain-language apology to Mehr: *"Hmm, something's off with how
   I'm organizing today's notes — I'll flag it so it gets fixed, and I'll
   keep going with what I have."*
3. Auto-invoke `magna-brain-feedback` to file a `skill-bug` issue with
   the failure trace.
4. Continue the session using whatever wiki state existed before the
   failed compile.

## Budget

`SKILL.md` body ≤ 3,000 tokens. Per-invocation prompt assembly ≤ 8,000
tokens (excluding the raw payload itself). See `TOKEN_BUDGET.md`.

## What this skill NEVER says to Mehr

- "I'll add this to raw/"
- "Compiling the wiki..."
- "Writing to sources/nike-brand-guide.md"
- "Do you want me to ingest this?"
- "Setting compile flag to true"
- Any file path, any technical noun from `AGENTS.md`.
