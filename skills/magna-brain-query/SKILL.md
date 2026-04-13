---
name: magna-brain-query
description: |
  Answer read-only questions about what the brain already knows, without writing anything. Used when Mehr asks "what do you know about X?" or "remind me what we covered on Y?".
  TRIGGERS - Use this skill when:
  - Mehr asks a question about prior knowledge: "what do you know about X?" / "what have we covered on Y?" / "remind me what we said about Z?" / "do we have anything on X?"
  - Mehr asks where a claim came from ("where did you get that?" / "what's the source for X?")
---

# magna-brain-query

Read-only. Never writes to `wiki/`, never writes to `raw/`, never writes to
`output/`. Returns a natural-language answer with inline wikilink
citations, rendered to Mehr as plain prose (not bulleted paths).

## Retrieval plan

1. Use the SessionStart-injected `wiki/index.md` +
   `wiki/_index/topic-summaries.md` to locate the topic.
2. Drill into the ≤ 4 most relevant articles by wikilink.
3. Synthesize the answer in plain chat.
4. For "where did you get that" questions, walk the `sources:` frontmatter
   of the relevant article to produce a provenance trail. If the provenance
   points to a document in `reference/` or `raw/`, describe it editorially
   ("the brand guide you dropped last week"), never as a path.

## Budget

Prompt assembly ≤ 6,000 tokens. If the topic requires more articles than
that, the skill stops at 4 and says so in chat: *"I've got strong notes on
A, B, and C for this — want me to go deeper on any one of them?"*

## Tools allowed

`[Read, Glob, Grep]` — **no Write, no Edit, no Bash**.

The `Glob` permission is allowed *only* against `wiki/index.md` and
`wiki/_index/*`. Wiki article Reads are by explicit path, never globbed.
The lint skill enforces this.

## Chat rules

- Answer like a well-read collaborator, not a search engine.
- Cite wiki articles by their human title, not their file path.
- If the brain doesn't know, say so plainly and offer to ingest material:
  *"Not much yet — want to drop anything you've seen on this?"*
- Never mention "searching the wiki" or "reading from concepts/."
