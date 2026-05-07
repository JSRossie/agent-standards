# Claude Standards

Reusable rules and skills that apply to every project, extracted from VRT's CLAUDE.md.

## Layout

- `baseline.md` — always-on operational rules (commit hygiene, sandbox recovery, git posture). Designed to be imported into a project's `CLAUDE.md`.
- `skills/` — skill source folders. Copy into a project's skills folder, or package into a local plugin via the `cowork-plugin-management:create-cowork-plugin` skill.

## Using this in a new project

### Option A — reference (recommended): one prompt to the new project

In the new project's `CLAUDE.md`, add the following line near the top:

```
@~/Local/claude-standards/baseline.md
```

Then copy the skill folders you want into the project's skills location, or install them as a local plugin.

The new project's own `CLAUDE.md` adds project-specific rules (data model, terminology, commit-group taxonomy) inline below the import.

### Option B — fork: copy the folders into the project

Copy `baseline.md` and any skill folders directly into the new project. Reference the local copy from `CLAUDE.md`:

```
@./baseline.md
```

This trades single-source-of-truth for self-containment. Use it when the new project will diverge significantly, or when `@<absolute-path>` imports aren't reliable in the target environment.

## Updating

This is a regular git repo. Edit, commit, and the next project that imports `baseline.md` picks up the change. Forked copies stay frozen until manually re-synced.

## What's not in here yet

Only `citation-standards` is shipped as a skill so far. The remaining portable concerns (`document-conventions`, `document-timestamping`, `commit-review-helper`, `research-citation-schema`) get extracted from VRT on demand as new projects need them.
