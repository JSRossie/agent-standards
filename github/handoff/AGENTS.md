<!--
source: skills/handoff-protocol/SKILL.md (agent-standards)
render: web-consumable (AGENTS.md), agent-agnostic. Canonical detail lives in the skill.
Keep thin; reconcile when the skill changes. See dotClaude ADR-0014.
-->

# Handoff protocol (agent instructions)

A **handoff** is a self-contained context dump one session writes so the next can resume
cold — after a cleared chat, a new conversation, or a gap of days — without the prior
history. This file is the portable rendering of the cross-project `handoff-protocol`
standard, for agents that don't read Claude Code skills (e.g. GitHub Copilot).

## Parameters (this repo)
- **handoffs_root:** `.claude-handoffs/` — repo-root dir for handoffs.
- **git_posture:** `tracked` — committed durable record. (`ephemeral` = gitignored scratch.)
- **root_pointer:** `HANDOFF.md` — gitignored symlink at the repo root to the newest handoff.

If a repo declares different values (in its `CLAUDE.md` / `AGENTS.md` / README), those win.

## Write a handoff when
The user says "prepare/write a handoff" or "pick up where we left off", before a planned
context reset, or when a long session holds state the next session needs that isn't
already in a durable doc. Don't restate what a committed doc already captures.

## File
`<handoffs_root>/YYYY-MM-DDTHHMM-<slug>.md` — YAML frontmatter, then the core sections:

```yaml
---
created: 2026-06-02T14:30        # ISO 8601, minute precision
slug: <kebab-topic>              # matches the filename slug
status: open                     # open until the next handoff supersedes it
topic: <one sentence>
related:
  - path/to/relevant/file
---
```

Core sections (always):
- **# Goal** — one or two sentences: what this handoff exists to get done.
- **# State** — current conditions; what's committed / in flight; branch & tree state; intentional oddities to leave alone.
- **# Next** — concrete, ordered instructions for the next session; lay out Path A / Path B where there's a real choice.
- **# Don't** — traps and anti-patterns; names not to reuse; work not to bundle into commits.
- **# Open for <user>** — decisions that need the user before proceeding.
- **# Read first** — prioritized files/sections to open, each with a one-line why.

## On each write (tracked)
1. Write the file under `<handoffs_root>`.
2. Refresh `<handoffs_root>/INDEX.md` to the newest 5 (one line each, newest first).
3. Archive: `git mv` any handoff past the newest 5 into `<handoffs_root>/archive/`.
4. Re-point `<root_pointer>` at the file just written.

For an **ephemeral** repo: skip INDEX and the predecessor chain; gitignore
`<handoffs_root>`; archive with plain `mv` instead of `git mv`.

## Resume
1. Open the latest: follow `<root_pointer>`, else `INDEX.md`, else newest by filename timestamp.
2. Read it fully; follow its **Read first** list before acting.
3. If it names a predecessor you lack, read that too (recent in root, older in `archive/`).
4. Act on **Next**; surface anything under **Open for <user>** before proceeding past it.

---
Canonical, full detail (postures, archiving mechanics, setup): `skills/handoff-protocol/SKILL.md` in `agent-standards`.
