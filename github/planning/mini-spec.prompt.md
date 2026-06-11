---
mode: 'agent'
description: 'Pick a planning rung and draft the artifact (cross-project planning-protocol standard)'
---
<!-- source: skills/planning-protocol/SKILL.md (agent-standards). Render — keep thin; see dotClaude ADR-0014. -->

You are running the **planning-protocol**. Follow the planning section of `AGENTS.md`
in this repo for the ladder and parameters. Defaults: `decisions_root` =
`docs/decisions/`, `max_rung` = `3`.

For the work the user describes:

1. **Pick a rung and say which and why in one line.** Default to rung 2 (mini-spec);
   rung 1 only for single-sitting work, rung 3 when the decision is the hard part,
   rung 4 only if this repo declares `max_rung: 4`.
2. **Draft the artifact.** Rung 2: a `SPEC.md` co-located with the work, five sections
   — Goal / Constraints / Approach / Tasks / Done-when — one screen, concrete checkable
   tasks. Rung 3: a numbered, dated ADR under `decisions_root` (context, options, the
   call, why, consequences), then a mini-spec or task list to drive the build.
3. **Flag step-up signals** instead of absorbing them: a mini-spec that wants research,
   contracts, or a data model is heavier work; a design fork inside an Approach section
   is an ADR, not a bullet.
