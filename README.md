# Agent Standards

Reusable, cross-tool rules and skills that apply to every project. Behaviors are defined
once here and consumed by multiple agent tools — Claude Code via skills, other agents
(e.g. GitHub Copilot) via web-consumable renders.

> Renamed from `claude-standards` — the behaviors aren't Claude-specific. See dotClaude
> ADR-0014 for the cross-tool model (two-tier topology, dual rendering).

## Layout

- `baseline.md` — always-on operational rules (commit hygiene, sandbox recovery, git posture). Designed to be imported into a project's `CLAUDE.md`.
- `skills/` — Claude-native skill source folders (the canonical definition of each behavior).
- `github/` — web-consumable renders of those skills (`AGENTS.md` + optional `*.prompt.md`) for agents that don't read Claude Code skills. See [github/README.md](github/README.md).

## Using a behavior in a new project

### Claude Code — reference the skill
Skills install globally via dotClaude's `.chezmoiexternal` (pulled into `~/.claude/skills/`),
or copy a skill folder into a project. The project's `CLAUDE.md` then references it by name.

### Other agents (e.g. Copilot) — copy the render
Clone this repo and copy the relevant `github/<behavior>/` render into your target repo:
`AGENTS.md` at the repo root (merge if one exists) and any `*.prompt.md` into
`.github/prompts/`. Commit them there so they travel with the repo.

### Baseline rules
`baseline.md` is imported into a project's `CLAUDE.md`. In environments that honor
`@<path>` imports (Claude Code), reference it directly:

```
@~/Local/agent-standards/baseline.md
```

Environments that don't expand imports (e.g. Cowork) **inline** the content between sync
markers instead:

```markdown
<!-- BEGIN: agent-standards/baseline.md -->
[paste current contents of ~/Local/agent-standards/baseline.md, stripping its H1]
<!-- END: agent-standards/baseline.md -->
```

Refresh by replacing everything between the markers with the latest file. A small
`sync-baseline.sh` (find the markers, splice in the latest file) is a reasonable addition
once there are more than two consumers.

## Distribution

This is a public git repo (`JSRossie/agent-standards`). Claude Code skills are pulled into
`~/.claude/skills/` via dotClaude's `.chezmoiexternal` (weekly, or
`chezmoi apply --refresh-externals`); the handoff distribution decision is recorded in
dotClaude ADR-0012. GitHub renders are copied per-repo (see above). Forked/inlined copies
stay frozen until manually re-synced.

## Shipped

| Behavior | Skill (Claude-native) | Render (cross-tool) |
|---|---|---|
| `citation-standards` | `skills/citation-standards/` | — |
| `handoff-protocol` | `skills/handoff-protocol/` | `github/handoff/` |

`handoff-protocol` is parameterized on `handoffs_root` / `git_posture` per project; derived
from VRT. See dotClaude ADR-0012 (the standard) and ADR-0014 (the cross-tool render).

## Not extracted yet

Remaining portable concerns (`document-conventions`, `document-timestamping`,
`commit-review-helper`, `research-citation-schema`) get pulled from VRT on demand as new
projects need them.
