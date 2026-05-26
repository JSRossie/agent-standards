---
name: handoff-protocol
description: Cross-project standard for session-handoff documents — the context dumps a Claude session writes so the next session can pick up cold after /clear or a fresh conversation. Use when the user says "prepare a handoff", "write a handoff", "resume from the latest handoff", "pick up where we left off", or similar; when ending a long session before /clear; or when asked to set up or normalize a project's handoff system. Reads per-project parameters (handoffs_root, git_posture) from the project's CLAUDE.md. Triggers on phrases like "handoff", "hand off", "resume the session", "where did we leave off", "carry this over".
---

# Handoff Protocol

A **handoff** is a self-contained context dump one session writes so the next
session can resume cold — after `/clear`, a fresh conversation, or a gap of days
— without the prior chat history. It captures what's true now, what to do next,
and the traps to avoid, in a form the resuming agent can act on directly.

This skill is the single source of truth for the format. It is **parameterized**:
posture and location come from the project, the structure comes from here.

## Per-project parameters

Read these from the project's `CLAUDE.md` (under its `## Handoffs` section). If a
project hasn't set them, use the defaults and say so.

| Parameter | Default | Meaning |
|---|---|---|
| **`handoffs_root`** | `.claude/handoffs/` | Where this project's handoffs live. |
| **`git_posture`** | `tracked` | `tracked` = committed durable record (INDEX, timestamped, predecessor chain). `ephemeral` = gitignored scaffolding, discarded when its state lands in a durable doc. |
| **`naming`** | `YYYY-MM-DDTHHMM-<slug>.md` | Filename pattern. `ephemeral` projects may drop the time: `YYYY-MM-DD-<slug>.md`. |

The two postures are both legitimate and deliberately opposite:

- **`tracked`** (e.g. vrt): handoffs are part of the permanent record. Commit each
  one, keep an `INDEX.md`, chain predecessors. Requires a `.gitignore` exception so
  the rest of `.claude/` stays ignored — see "Git posture" below.
- **`ephemeral`** (e.g. r-net): handoffs are throwaway scaffolding. Gitignored, never
  committed, no INDEX. **Rule:** if the state belongs in a durable artifact (WORKLOG,
  ADR, briefing, spec), update *that* instead — only write a handoff for context that
  has nowhere durable to live and that the next session needs.

## When to write one

- Before a planned `/clear`, or when the user asks to "prepare a handoff" / "pick
  up where we left off".
- When a long session has accumulated context the next session needs and that
  isn't already captured in a durable artifact.

Do **not** write a handoff to restate what's already in a committed doc. For an
`ephemeral` project especially, prefer updating the durable artifact.

## Anatomy

Every handoff is one markdown file: YAML frontmatter, then the core sections.

### Frontmatter

```yaml
---
created: 2026-05-25T14:30        # ISO 8601, minute precision
slug: <kebab-case-topic>          # matches the filename slug
status: open                      # open until superseded by the next handoff in the chain
topic: <one sentence — what this handoff is about>
related:                          # files the resuming agent will touch or must know about
  - path/to/relevant/file.md
  - CLAUDE.md
---
```

### Core sections (always)

```markdown
# Goal
One or two sentences: what this handoff exists to get done.

# State
Bulleted current conditions — what's committed, what's in flight, branch/tree
state, data shape, anything the next session would otherwise have to rediscover.
Note intentional oddities ("James edited X post-commit — leave it").

# Next
The specific instructions for the next session. Concrete and ordered. Where there
are real alternatives, lay out Path A / Path B with the tradeoff.

# Don't
Negative constraints and anti-patterns — the traps. Things that look reasonable
but are wrong here, claimed names not to reuse, work not to bundle into commits.

# Open for <user>
Decision points that need the user's input before or during the next session.
(Header uses the user's name, e.g. "Open for James".)

# Read first
The prioritized reading list — files/sections to open before doing anything, each
with a one-line why.
```

### Extended sections (larger handoffs, as needed, `##` level)

`What shipped` · `Critical findings` · `Where things stand right now` ·
`Open follow-on items` · `Pattern observations` · `Standards reminders` ·
`Close-out actions`. Use only the ones that earn their place.

### Predecessor chain (`tracked` projects)

When a handoff continues a prior one, name it explicitly so the chain is
followable:

```markdown
**Predecessor.** Picked up from `.claude/handoffs/<earlier-file>.md` (<what it left done>).
```

A full template lives in `reference/handoff-template.md`.

## INDEX (`tracked` projects only)

Maintain `<handoffs_root>/INDEX.md` as a hand-curated digest of the **last 5**
handoffs, newest first. `ephemeral` projects skip this — `ls` is the index.

```markdown
# Handoffs — last 5

_Updated 2026-05-25T14:30_

- [2026-05-25 · <2–3 sentence executive summary of the handoff>](2026-05-25T1430-<slug>.md)
```

Update the INDEX in the same step as writing the handoff.

## Git posture

**`tracked`:** the handoffs dir must be exempted from a broad `.claude/` ignore.
The convention:

```gitignore
# Claude project config: handoffs are tracked, the rest of .claude/ isn't
.claude/*
!.claude/handoffs/
```

Commit handoffs on their own, with subject `handoffs: <short description>`. They
persist permanently; there is no archival step. A handoff stays `status: open`
until the next one in the chain supersedes it.

**`ephemeral`:** the dir is gitignored. Never commit handoffs and never propose
committing them. They remain on disk until manually cleared; re-reading an old one
is a deliberate choice.

## Resume workflow

When the user says "resume from the latest handoff" / "pick up where we left off":

1. List `<handoffs_root>`, newest by filename timestamp (for `tracked`, consult
   `INDEX.md` first).
2. Read the latest handoff in full; follow its `Read first` list before acting.
3. If it names a predecessor and you lack that context, read it too.
4. Act on `Next`. Surface anything under `Open for <user>` before proceeding past it.

## Setting up a project

To adopt this standard in a project that doesn't have it:

1. Add a `## Handoffs` section to the project's `CLAUDE.md` declaring `handoffs_root`
   and `git_posture` (see "Per-project parameters").
2. Create `<handoffs_root>/`. For `tracked`, add the `.gitignore` exception above and
   seed an empty `INDEX.md`.
3. Ensure writes to `<handoffs_root>` don't prompt — the per-project permission seed
   should allow `Write`/`Edit` on that path (it's a permissive rule, so it belongs in
   the project seed, never in global settings).
