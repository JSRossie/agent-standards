# github/ — web-consumable renders

Agent-agnostic renderings of this repo's behaviors, for tools that don't read Claude Code
skills (e.g. GitHub Copilot). Each `<behavior>/` holds the portable form of a skill under
`../skills/`.

**Source of truth is the skill, not the render.** Renders are thin: they inline the
essentials and defer detail to the skill. Every render names its source in a header. When
the skill changes, reconcile the render in the same pass.

**Primary format: `AGENTS.md`** (read across agent tools). An optional `*.prompt.md` gives
VS Code Copilot an explicit `/`-trigger.

## Use on a Claude-less machine
1. Clone `agent-standards`.
2. Copy the render into your target repo: `AGENTS.md` to the repo root (merge if one
   already exists), and any `*.prompt.md` into `.github/prompts/`.
3. Commit them in that repo so they travel with it and work on github.com too.

## Renders
- `handoff/` — the cross-project session-handoff protocol. Source: `../skills/handoff-protocol/`.

See dotClaude ADR-0014 for the model (two-tier topology, dual rendering).
