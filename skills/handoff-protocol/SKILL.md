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
| **`handoffs_root`** | `.claude-handoffs/` | Where this project's handoffs live. A repo-root dir kept **outside** `.claude/` so Claude Code's `.claude/` write guard never prompts on handoff writes. |
| **`git_posture`** | `tracked` | `tracked` = committed durable record (INDEX, timestamped, predecessor chain). `ephemeral` = gitignored scaffolding, discarded when its state lands in a durable doc. |
| **`naming`** | `YYYY-MM-DDTHHMM-<slug>.md` | Filename pattern. `ephemeral` projects may drop the time: `YYYY-MM-DD-<slug>.md`. |
| **`root_pointer`** | `HANDOFF.md` | A pointer at the **repo root** that always resolves to the newest handoff, for one-hop access. Set `none` to disable. |

The two postures are both legitimate and deliberately opposite:

- **`tracked`** (e.g. vrt): handoffs are part of the permanent record. Commit each
  one, keep an `INDEX.md`, chain predecessors. The dir is a normal repo-root folder, so
  it commits with no `.gitignore` handling — see "Git posture" below.
- **`ephemeral`** (e.g. r-net): handoffs are throwaway scaffolding. Gitignored, never
  committed, no INDEX or predecessor chain — but they **still archive** (newest 5 in the
  root, older into a gitignored `archive/`) so the folder stays scannable as they pile up;
  archival is independent of git posture. **Rule:** if the state belongs in a durable
  artifact (WORKLOG, ADR, briefing, spec), update *that* instead — only write a handoff for
  context that has nowhere durable to live and that the next session needs.

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
**Predecessor.** Picked up from `.claude-handoffs/<earlier-file>.md` (<what it left done>).
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

The INDEX's "last 5" deliberately matches what stays in `<handoffs_root>` after
archiving (below), so its links always point at files in the root — never into
`archive/`.

## On each write

When you write a handoff, do these in the same step (so they land in one commit):

1. **Write** the handoff file under `<handoffs_root>` per the naming pattern.
2. **INDEX** (`tracked`): refresh `INDEX.md` to the newest 5.
3. **Archive** (both postures): move any handoff past the newest 5 into `archive/`
   (below) — `git mv` for `tracked`, plain `mv` for `ephemeral`.
4. **Pointer**: refresh `<root_pointer>` to point at the file just written (below).

## Archiving (both postures)

Keep the **5 most recent** handoffs in `<handoffs_root>`; older ones move to
`<handoffs_root>/archive/`. For `tracked` this is the same 5 the INDEX lists, so the
visible files mirror the digest; for `ephemeral` it simply keeps the root scannable as
handoffs accumulate. Either way the root stays short and the archive holds the long tail.

The only difference is the move command — `git mv` when `tracked` (so history follows the
file and the move lands in the handoff's commit), plain `mv` when `ephemeral` (the dir is
gitignored, so `git mv` would error; nothing about the move is committed):

```bash
# from <handoffs_root>, after writing the new handoff.
# [0-9]*.md matches timestamped handoffs and skips INDEX.md; the loop no-ops
# when there's nothing to archive (portable across BSD/macOS and GNU).
mkdir -p archive
mover="git mv"; git check-ignore -q . && mover="mv"   # gitignored dir → plain mv
ls -1 [0-9]*.md 2>/dev/null | sort -r | tail -n +6 | while read -r f; do
  $mover "$f" archive/
done
```

- `archive/` needs no extra handling — `tracked` commits it like the rest of
  `<handoffs_root>`; `ephemeral` already ignores it under the `/<handoffs_root>` entry,
  so archived files stay on disk locally but never enter git.
- Archiving **relocates, never deletes** — the long tail remains recoverable. A repo that
  genuinely wants pruning can swap `mv` for `rm`, but the default keeps the files.
- **Links stay valid (`tracked`).** INDEX only ever lists the visible 5, so its links never
  reach into `archive/`. A predecessor link breaks only once that predecessor ages past the
  newest 5 — by which point its successor has also aged out of the active chain. The
  resume path (latest + its immediate predecessor) is always within the visible 5; for
  deeper history, look in `archive/`.
- `ephemeral` keeps no INDEX and no predecessor chain — `ls` of the (now-short) root is the
  index, and `archive/` holds older context if a resume needs to reach back.

## Latest pointer

Maintain `<root_pointer>` (default `HANDOFF.md`) at the **repo root** as a symlink to
the newest handoff, so the file you reach for most is one hop from the top of the tree:

```bash
ln -sf "<handoffs_root>/<newest>.md" HANDOFF.md   # target is relative to the repo root
```

Refresh it whenever you write a handoff. It is a **local convenience and gitignored**
(add `/HANDOFF.md` to `.gitignore`) — not part of the durable record, so it adds no
root-level churn to commits and simply regenerates on the next write. A fresh clone has
no pointer until the next handoff is written; that's fine. Set `root_pointer: none` in
the project's `CLAUDE.md` to opt out. Applies to **both** postures.

## Git posture

`<handoffs_root>` lives at the **repo root** (`.claude-handoffs/` by default), outside
`.claude/`. That keeps Claude Code's `.claude/` write guard off it — handoff writes
don't prompt — and it flips the default git behavior versus a path inside `.claude/`
(which consumer repos usually ignore wholesale): a top-level dir is tracked unless you
ignore it, so now `tracked` is free and `ephemeral` is the case that needs a rule.

**`tracked`:** nothing to ignore — the dir is a normal tracked folder. (The old
`.claude/*` + `!.claude/handoffs/` exception is no longer needed.) Commit handoffs on
their own, with subject `handoffs: <short description>`. They persist permanently —
archiving only **relocates** older ones into `archive/` (see "Archiving"), it never
deletes them. A handoff stays `status: open` until the next one in the chain supersedes it.

**`ephemeral`:** add the dir to `.gitignore` so scratch is never committed. At the repo
root it is no longer swept up by a `.claude/` ignore, so this entry is **required**:

```gitignore
# Session handoffs: ephemeral scaffolding, not committed
/.claude-handoffs/
```

Never commit handoffs and never propose committing them. They remain on disk until
manually cleared; re-reading an old one is a deliberate choice.

## Resume workflow

When the user says "resume from the latest handoff" / "pick up where we left off":

1. Go to the latest: follow `<root_pointer>` if present, else consult `INDEX.md`
   (`tracked`), else list `<handoffs_root>` newest by filename timestamp.
2. Read the latest handoff in full; follow its `Read first` list before acting.
3. If it names a predecessor and you lack that context, read it too — recent
   predecessors are in `<handoffs_root>`, older ones in `archive/`.
4. Act on `Next`. Surface anything under `Open for <user>` before proceeding past it.

## Setting up a project

To adopt this standard in a project that doesn't have it:

1. Add a `## Handoffs` section to the project's `CLAUDE.md` declaring `handoffs_root`
   and `git_posture` (see "Per-project parameters").
2. Create `<handoffs_root>/`. For `tracked`, seed an empty `INDEX.md` (nothing to
   gitignore — it's a top-level tracked dir). For `ephemeral`, add the `.gitignore`
   entry shown under "Git posture".
3. Unless `root_pointer: none`, add `/HANDOFF.md` (or the chosen pointer name) to the
   repo's `.gitignore` — the pointer is a local convenience, not committed.
4. Ensure writes to `<handoffs_root>` don't prompt — the per-project permission seed
   should allow `Write`/`Edit` on that path (it's a permissive rule, so it belongs in
   the project seed, never in global settings).
