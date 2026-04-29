# Onboarding paste — Magna brain contributors

This is the **single message** any new Magna contributor pastes into a fresh Claude Code chat to get fully set up. It walks them through gh CLI, GitHub auth, repo clone, local git identity, write-access verification, and reading CLAUDE.md — step by step, with debug fallbacks at every stage.

How to use it:

1. **Make sure the new contributor is a collaborator with WRITE access** on `mehrpatni9-lgtm/magna-brain`. (Settings → Collaborators on GitHub.) Without this, step 6 fails and they can't push.
2. Copy the **Slack/email template** below, paste it into iMessage / email / Slack to the new contributor.
3. They copy the **inner prompt block** and paste it into a fresh Claude Code chat on their laptop.
4. Claude walks them through every step. If anything fails, they paste the terminal error back into chat and Claude debugs it from there.

The same template self-serves for everyone — no per-person customisation needed.

---

## Slack / email template (what Sahil or Mehr sends)

> Hey,
>
> You're being onboarded to Magna's brain — the place where everything we know about Magna evolves in one URL, and where the content engine for what we publish lives in another. Both pages update automatically when anyone on the team adds something.
>
> To set up, do this once:
>
> 1. Open **Claude Code** on your laptop (download at <https://claude.com/download> if you don't have it). Open a fresh chat.
> 2. Copy and paste the entire prompt below into that chat. Claude will walk you through everything else from there.
> 3. If any step gets stuck, just paste the error or terminal output back into the chat — Claude will debug it with you in plain English.
>
> The brain is at <https://mehrpatni9-lgtm.github.io/magna-brain/brain/> — open it in a tab so you can watch it update in real time as you start contributing.
>
> ---
>
> ```
> Hi Claude — I'm onboarding myself into the Magna brain workflow.
> Walk me through setting up locally, one step at a time. After EACH
> step, confirm it worked before moving on. If any step fails, ASK me
> to paste the terminal output and help me debug it in plain English
> before continuing.
>
> Speak in normal English from step 8 onward (skip technical noun like
> "git," "directory," "config" once I'm onboarded). Steps 1–7 are
> setup-only and can use technical language as needed.
>
> Steps:
>
> 1. Verify gh CLI is installed by running `gh --version`.
>    - If installed, confirm and move on.
>    - If not, tell me the install command for my OS (`brew install gh`
>      on Mac, instructions for Windows / Linux otherwise) and stop.
>      I'll install it and tell you when I'm ready.
>
> 2. Verify GitHub authentication by running `gh auth status`.
>    - If authenticated, confirm and move on.
>    - If not, tell me to type `! gh auth login` (the `!` runs the
>      command in this chat session and shows me the browser flow) and
>      walk me through which options to pick (GitHub.com → HTTPS →
>      paste an auth token or browser).
>    - If anything looks off, ask me to paste the output back to you.
>
> 3. Ask me for my full name (e.g. "Shailu Tipparaju") and my email
>    (the one I want my Magna brain commits to be attributed to). Wait
>    for my response. These will be my git identity for everything I
>    contribute.
>
> 4. Clone the repo:
>    - If `~/magna-brain` does NOT exist, run:
>      `git clone https://github.com/mehrpatni9-lgtm/magna-brain.git ~/magna-brain`
>    - If it exists, run:
>      `cd ~/magna-brain && git pull --rebase origin main`
>    - If clone fails with a permission error, tell me to ask Sahil or
>      Mehr to add me as a collaborator with write access on
>      mehrpatni9-lgtm/magna-brain, then stop. I'll come back when
>      that's done.
>
> 5. From inside ~/magna-brain, set my git identity locally (scoped to
>    this repo only — won't affect my other projects):
>    - `cd ~/magna-brain`
>    - `git config --local user.name "<NAME from step 3>"`
>    - `git config --local user.email "<EMAIL from step 3>"`
>    - Verify with `git config user.name` and `git config user.email`.
>
> 6. Verify I have write access:
>    `gh repo view mehrpatni9-lgtm/magna-brain --json viewerPermission`
>    - If the result contains "WRITE" or "ADMIN", confirm and move on.
>    - If not, tell me to ask Sahil or Mehr for collaborator access and
>      stop here.
>
> 7. Read CLAUDE.md and AGENTS.md silently from ~/magna-brain. Do not
>    summarise them. Just read them so you know the rules of how to
>    behave from this point forward.
>
> 8. Greet me by name in plain English and say:
>    "Welcome <NAME>. The brain is loaded and your name tag is set.
>     Drop anything you found today — articles, PDFs, voice notes, or
>     pasted text — and I'll add it to the brain at
>     https://mehrpatni9-lgtm.github.io/magna-brain/brain/. Or tell me
>     what you want to write about and I'll draft it. If you ever want
>     to suggest a feature, just say 'I'd like to suggest...' and I'll
>     log it for you."
>
> Don't show me commands or paths after step 8. From step 8 forward,
> follow CLAUDE.md.
>
> DEBUG MODE: At any step, if I paste terminal output or an error
> back to you, diagnose what went wrong and tell me the next thing to
> try in plain English. If you can't fix it from chat alone, tell me
> to ask Sahil and explain what to ask him for in one sentence.
> ```

---

## Notes for Sahil / Mehr

- The prompt is **self-contained**. The contributor doesn't need to read this docs/onboarding.md file — only the inner prompt block.
- The prompt assumes the contributor has Claude Code installed. If they don't, step 1 of the email template tells them where to get it.
- The prompt does NOT bake in the contributor's name — Claude asks them in step 3 of the chat. So this template self-serves for everyone with no per-person edits.
- After onboarding, the contributor's session uses every skill in `.claude/skills/`. Specifically:
  - **`magna-brain-ingest`** captures anything they drop in chat and updates the brain.
  - **`magna-brain-write-post`** drafts posts in Magna's voice and publishes to Pages.
  - **`magna-brain-query`** answers questions about what the brain already knows.
  - **`magna-brain-feedback`** silently logs corrections AND explicitly logs feature suggestions as GitHub issues (the contributor can say "I'd like to suggest..." and Claude files it).
  - **`magna-brain-delete`** is **Mehr-only** (gated on `git config user.name == "Mehr Patni"`); other contributors get a polite deflection that routes to feedback.
- All commits push to `main` and trigger a Pages rebuild within ~90 seconds. Multi-contributor concurrent pushes are handled via `git pull --rebase` inside the ingest skill.

## When something goes wrong during onboarding

The prompt's DEBUG MODE clause means the contributor can paste any terminal output back to Claude and get help. Common failure modes Claude should be able to handle:

- **`gh: command not found`** → install via `brew install gh` (Mac), or pointed installation guide for Windows / Linux.
- **`gh auth status` says not authenticated** → walk them through `! gh auth login`.
- **`git clone` permission denied** → confirm they were added as a collaborator with write access; tell them to ping Sahil or Mehr.
- **`viewerPermission` is `READ` or `null`** → same — collaborator access not granted yet.
- **`git config --local` runs but later commits attribute to a different name** → check global config (`git config --global user.name`) is overriding; the `--local` config should win inside the repo.

If a failure can't be resolved from chat, the prompt's instruction is to tell the contributor to ask Sahil and to give them one-sentence wording for what to ask. That keeps the contributor unblocked and gives Sahil a precise question to answer.

## Suggesting features after onboarding

Once a contributor is onboarded, they can drop the brain feature ideas naturally in chat:

> *"I'd like to suggest the brain shows a sources-by-month chart on the homepage."*
>
> *"What if the engine could automatically schedule posts to Buffer?"*
>
> *"Could we have a Slack integration that posts the daily drop summary every morning?"*

Claude (via `magna-brain-feedback` Mode B) silently files these as `feature-suggestion` labelled issues on `mehrpatni9-lgtm/magna-brain` and gives the contributor a one-line acknowledgement. The architectural team sees them in the issue queue and prioritises them with the rest of the work.
