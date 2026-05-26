# Claude Standards

Reusable rules and skills that apply to every project, extracted from VRT's CLAUDE.md.

## Layout

- `baseline.md` — always-on operational rules (commit hygiene, sandbox recovery, git posture). Designed to be imported into a project's `CLAUDE.md`.
- `skills/` — skill source folders. Copy into a project's skills folder, or package into a local plugin via the `cowork-plugin-management:create-cowork-plugin` skill.

## Using this in a new project

### Option A — fork (default for Cowork projects): inline the baseline

Cowork's CLAUDE.md loader does not honor `@<path>` imports — the directive is left as literal text rather than expanded. So in Cowork projects, the canonical baseline content gets **copied** into the new project's `CLAUDE.md`, not referenced.

Surround the inlined block with sync markers so future refreshes are mechanical:

```markdown
<!-- BEGIN: claude-standards/baseline.md -->
[paste current contents of ~/Local/claude-standards/baseline.md, stripping its H1]
<!-- END: claude-standards/baseline.md -->
```

To refresh after the canonical baseline changes, replace everything between the markers with the new content. A small `sync-baseline.sh` script (find the markers, splice in the latest file) is a reasonable next addition once you have more than two consumers.

For skills, copy the skill folders you want directly into the project, or install them as a local plugin via `cowork-plugin-management:create-cowork-plugin`. Skill content (like `citation-standards/SKILL.md`) can also be referenced in prose from the project's CLAUDE.md and read on demand — that path doesn't require the import directive to work.

### Option B — reference (Claude Code projects only)

In environments that honor `@<path>` imports (Claude Code), the new project's `CLAUDE.md` can reference the canonical file directly:

```
@~/Local/claude-standards/baseline.md
```

This preserves single-source-of-truth — fix the canonical file once, every consumer picks up the change. Verify the import resolves before relying on it (a quick test prompt that asks for a specific detail from `baseline.md` will surface a silent failure).

## Updating

This is a regular git repo. Edit, commit, and the next project that imports `baseline.md` picks up the change. Forked copies stay frozen until manually re-synced.

## Shipped skills

- `citation-standards` — IEEE-with-business-extensions citations for authored markdown.
- `handoff-protocol` — the cross-project session-handoff standard (the context dump a
  session writes so the next can resume cold). Parameterized on `handoffs_root` /
  `git_posture` per project; derived from VRT. See `dotClaude` ADR-0012.

## What's not in here yet

The remaining portable concerns (`document-conventions`, `document-timestamping`, `commit-review-helper`, `research-citation-schema`) get extracted from VRT on demand as new projects need them.

**`handoff-protocol` distribution is not wired yet.** This repo has no git remote, so it can't be pulled via `.chezmoiexternal` (the mechanism used for design-system skills). The distribution decision is tracked in `dotClaude`'s handoff `2026-05-25T1928-handoff-protocol-distribution-and-migration.md`.
