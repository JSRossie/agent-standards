<!--
source: skills/planning-protocol/SKILL.md (agent-standards)
render: web-consumable (AGENTS.md), agent-agnostic. Canonical detail lives in the skill.
Keep thin; reconcile when the skill changes. See dotClaude ADR-0014.
-->

# Planning protocol (agent instructions)

Planning produces **durable artifacts that survive a cleared chat** — that is the
requirement. The *weight* of the artifact should match the work. This file is the
portable rendering of the cross-project `planning-protocol` standard, for agents that
don't read Claude Code skills (e.g. GitHub Copilot).

## Parameters (this repo)
- **decisions_root:** `docs/decisions/` — where ADRs live.
- **briefings_root:** `none` — options analysis goes in the ADR itself.
- **max_rung:** `3` — no full spec toolkit installed here.
- **status_doc:** `none` — no living worklog file to link specs from.

If a repo declares different values (in its `CLAUDE.md` / `AGENTS.md` / README), those win.

## The ladder, lightest to heaviest
1. **Plan only, no artifact** — trivial, single-sitting changes. If the work spills
   across sessions, you picked the wrong rung — step up.
2. **One-page mini-spec** (default) — a single `SPEC.md` co-located with the work
   (next to the code, not under `docs/`): Goal / Constraints / Approach / Tasks /
   Done-when. ~10 minutes, one file to read cold. Check tasks off inline.
3. **Briefing → ADR** — when the hard part is the *decision*, not the build. Record
   the call as a numbered, dated ADR under `decisions_root`; drive the build with a
   mini-spec or task list. ADRs record choices, not tasks, and are immutable history.
4. **Full spec toolkit** (e.g. GitHub Spec Kit) — multi-cycle, cross-cutting features.
   Only in repos that declare `max_rung: 4`; never bootstrap a toolkit for one feature.

## How to apply
Before starting non-trivial work, **pick a rung and say which and why in one line**.
Default to rung 2. Step up when a mini-spec wants research/contracts/data-model
sections; step sideways to rung 3 when a real fork (which tool, which topology) shows
up in the Approach; step down when ceremony is producing artifacts nobody will reread.

When the work ships, the mini-spec stays as the design record — update its `Status:`
line, don't delete it.

---
Canonical, full detail (parameters, mini-spec template, rung mechanics):
`skills/planning-protocol/SKILL.md` in `agent-standards`.
