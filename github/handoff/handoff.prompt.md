---
mode: 'agent'
description: 'Write or resume a session handoff (cross-project handoff-protocol standard)'
---
<!-- source: skills/handoff-protocol/SKILL.md (agent-standards). Render — keep thin; see dotClaude ADR-0014. -->

You are running the **handoff-protocol**. Follow the handoff section of `AGENTS.md` in
this repo for the full format and parameters. Defaults: `handoffs_root` =
`.claude-handoffs/`, `git_posture` = `tracked`, `root_pointer` = `HANDOFF.md`.

Decide intent from the user's message:

- **Write** ("prepare/write a handoff", ending a session): create
  `<handoffs_root>/YYYY-MM-DDTHHMM-<slug>.md` with the frontmatter and the core sections
  (Goal, State, Next, Don't, Open for <user>, Read first). Then refresh `INDEX.md`,
  `git mv` anything past the newest 5 into `archive/`, and re-point `HANDOFF.md`
  (tracked repos).
- **Resume** ("pick up where we left off", "resume"): open the latest handoff (via
  `HANDOFF.md` → `INDEX.md` → newest filename), read it fully, follow its **Read first**
  list, then act on **Next**. Surface anything under **Open for <user>** first.

Keep it self-contained: capture what the next session can't rediscover, not what a
committed doc already says.
