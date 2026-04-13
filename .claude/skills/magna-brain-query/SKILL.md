---
name: magna-brain-query
description: Answer questions about what the brain already knows, read-only, with editorial tone (not a search engine). TRIGGERS - Use this skill when Mehr asks "what do you know about X?" / "what have we covered on Y?" / "remind me what we said about Z" / "do we have anything on ..." / "where did you get that?" / "what's the source for ...".
---

# magna-brain-query

Read-only. **Never writes** to `wiki/`, `raw/`, or `output/`. Answers Mehr's knowledge questions like a well-read collaborator, not a retrieval engine.

## Hard rules

1. **Never list file paths.** Cite wiki pages by their human title, never their slug.
2. **Never say "searching the wiki" or "reading from concepts/."** Just answer.
3. **If the brain doesn't know, say so plainly** and offer to ingest material on the topic.

## Step 1 — Locate the topic

The session already has `wiki/index.md` and `wiki/_index/topic-summaries.md` loaded. Use them to find entities and concepts that match the question. Do NOT Glob `wiki/**`.

## Step 2 — Drill in

Read ≤ 4 most relevant articles via explicit wikilink Reads. Prefer `wiki/synthesis/*` first (pre-built angles), then `wiki/concepts/*`, then `wiki/entities/*`. For "where did you get that?" questions, walk the `sources:` frontmatter back to `wiki/sources/*` and describe each source editorially ("the brand guide you dropped in the reference folder," "the content platform brief from your design team").

## Step 3 — Synthesize

Answer in prose. Inline citations as parenthetical human references, e.g. "(from the brand guide)" or "(we covered this in the culture pillar)" — never file paths.

If the topic genuinely isn't in the brain, say: *"Not much yet — I've got the voice and the pillar framing, but nothing specific on X. Want to drop anything you've seen on this?"*

If the topic has 4+ strong articles, stop at 4 and offer: *"I've got solid notes on A, B, C for this. Want me to go deeper on any one of them?"*

## Budget

Prompt assembly ≤ 6,000 tokens. Never exceeds 4 drilled articles.

## Tools allowed

Read, Grep — on wiki/ files only. No Write. No Edit. No Bash.
