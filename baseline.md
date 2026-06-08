# Agent Baseline Standards

Always-on operational rules that apply to **every** project, in any environment. This file is
the portable nucleus: import it whole and it never contradicts a sane project. Environment- and
project-specific machinery (the auto-split commit helper, Cowork sandbox recovery) is **not**
here — it lives in opt-in fragments under [`fragments/`](fragments/) that a project references by
name only if it applies. See *Opt-in fragments* at the end.

Project-specific rules (commit-type vocabulary, pipeline details, data model, terminology) are
added inline by each project's `CLAUDE.md` after this import. The git rules below — commit format,
end-of-turn posture, hard rules, and concurrent/multi-agent worktree discipline — are the
canonical, portable source: import them from here rather than re-deriving them per repo, which is
how they drift.

## Recovery from accidental overwrites

With Git in place, recovery is straightforward:

```bash
git diff <path>                # See what changed
git checkout -- <path>         # Revert to last commit
git log --oneline <path>       # See history
```

## Commit message format

Commits follow **Conventional Commits with an optional scope**: `type(scope): subject`.

- Lowercase, imperative mood, no trailing period (`fix(auth): handle expired token`, not
  `Fixed the auth bug.`).
- Scope is the area touched, not the file (`docs(architecture)`, `tools(unifi-mcp)`); it is
  optional for cross-cutting changes (`chore: bootstrap repo conventions`).
- Body and footer are optional — add them only when the context isn't obvious from the subject.

Baseline fixes the *shape*. The **type vocabulary** (`feat`/`fix`/`docs`/`chore`/…) and what each
**scope** means are per-project — each project's `CLAUDE.md` lists the types in use and their
scopes. Don't invent types ad hoc; use the project's set.

## End-of-turn commit posture

Any turn that produces a coherent deliverable ends by committing it. The repository exists to track
changes and enable backing out unexpected behavior — that purpose is served by **making the
commit**, not by asking before each one.

- **Commit the coherent unit, not the session.** Three unrelated deliverables in one turn (an ADR
  + a briefing + a tool tweak) are three commits. Don't batch unrelated edits into one commit.
- **Default is to commit; opt out inline.** To skip, the user says so inline ("don't commit this
  turn", "leave this uncommitted"). Without an explicit opt-out, the end-of-turn commit fires.
- **Undo is cheap.** `git reset --soft HEAD~N` reverses the last N commits and leaves the changes
  staged so they can be re-edited; `git reset --hard HEAD~N` discards them entirely.

Projects with a commit-review helper that auto-splits a turn's changes into grouped commits follow
the [`commit-review-helper`](fragments/commit-review-helper.md) fragment for the mechanics; the
posture above is unchanged by it.

## Hard rules

These are non-negotiable in every project:

- **Never force-push** (`git push --force`, `--force-with-lease`), regardless of branch.
- **Never rewrite published history.** No `--amend`, rebase, or `reset` on commits that have been
  pushed. A new commit to correct a mistake is always preferred over rewriting one that others may
  have.
- **Non-force push is a per-project posture, not a baseline ban.** Some projects have no remote and
  never push; others push routinely. Baseline does not forbid `git push` — it forbids only the two
  rules above. Default to ask-first on a first push unless the project says otherwise.
- **Never use `git add .` or `git add -A`.** Stage explicit file paths. This keeps `.DS_Store`,
  editor cruft, secrets, and unrelated in-progress work out of the commit.
- **Never skip hooks** (`--no-verify`, `--no-gpg-sign`) without an explicit user instruction.
- **Never operate on nested git repositories from outside their root.**

## Concurrent & multi-agent git hygiene

These rules apply when **more than one session or agent works the same repo at once** — parallel
Claude sessions, or background agents spawned with `isolation: "worktree"`. Serial single-operator
work is unaffected: it lands on the working branch directly, as usual. The failure mode they prevent
is two workers colliding on one checkout — a commit landing on whichever branch happens to be
checked out, or one agent's `git add` sweeping in another's half-done work.

- **Branch per task, named for the work.** Each concurrent session/agent branches off its stated
  base as `<type>/<short-topic>`, with `<type>` drawn from the commit-type vocabulary
  (`feat`/`fix`/`docs`/`chore`/…): `feat/dns-secondary`, `fix/boot-leg`. Never land work on a
  branch named for a different task; never invent an opaque name unrelated to the work.
- **Isolated worktrees, never a shared checkout.** The foreground session owns the primary
  checkout; parallel/background agents each run in their own `git worktree` (the Agent tool's
  `isolation: "worktree"`). Two agents mutating one working tree corrupt each other's index and
  files.
- **Confirm your branch immediately before every commit.** Run `git branch --show-current` and
  abort if it isn't the branch you created for this task. This is the check that catches a commit
  about to land on someone else's branch.
- **Stage explicit paths (the no-`git add .` rule, sharpened).** In a shared tree, `git add .` /
  `-A` sweeps another agent's uncommitted work into your commit. Stage only the paths you changed.
- **Don't touch a branch or checkout you don't own.** Don't switch the primary checkout while
  another session is using it; don't `git branch -f`, `reset --hard`, or delete a branch you didn't
  create. History rewrites stay ask-first whichever branch they target.
- **Wrong-branch recovery: prefer the lossless move.** If a commit lands on the wrong branch and the
  intended branch is an ancestor of it (so fast-forwarding loses nothing), point the intended branch
  at the commit and switch to it — then leave the wrong branch as you found it for its owner:

  ```
  git branch -f <intended-branch> <commit>
  git switch <intended-branch>
  ```

  Ask the operator before rewinding anything that is not a clean fast-forward.

## Deterministic checks over prose

If an invariant can be expressed as a check, encode it — in a hook (see *One-time hooks setup per
clone* below) or CI — rather than as a paragraph every agent has to remember to follow. Prose is for
genuine judgment (when to branch, how to write a good commit message); mechanical invariants (branch
guards, single-writer file ownership, regenerating a derived file) belong in enforcement. The
corollary for shared "hot" files that nearly every session edits — status logs, indexes, lockfiles —
is structural: make the file single-owner or generated from per-session fragments, so two agents
never open the same file, instead of asking everyone to "edit only their own section." A convention
is the first thing concurrent work violates; structure can't be.

## One-time hooks setup per clone

If the project uses git hooks (timestamp footers, branch/STATUS guards, derived-file regenerators),
each clone must wire them up — commits otherwise succeed without the hooks firing. The mechanism is
per-project (the project's `CLAUDE.md` or hooks README names it); common forms:

```bash
git config core.hooksPath .githooks        # or a project make target, e.g. `make install-hooks`
```

---

## What this file doesn't include

The following are project-specific and live in each project's own `CLAUDE.md`:

- **Commit-type vocabulary and scopes** — which `type`s exist in this project and what each scope
  names (see *Commit message format* above for the portable shape).
- **Commit-group taxonomy** — for helper-driven projects, what categories of files exist, how they
  split into commits, and in what order.
- **Pipeline-integrity specifics** — which scripts must have run, which invariants must pass, what
  counts as a HARD vs WARN.
- **Project paths, data model, naming conventions, terminology.**
- **Branching/remote model** — whether there's a remote, PR-vs-direct-push, the push posture.
- **Skill and fragment installations** — which skills from `~/Local/agent-standards/skills/` and
  which fragments below are in scope.

## Opt-in fragments

Environment- and project-specific machinery that used to live in this file now sits in
[`fragments/`](fragments/). A project imports a fragment **only if it applies** — the same way it
imports this file (`@<path>` in Claude Code, or inlined between sync markers in environments that
don't honor imports, e.g. Cowork):

- **[`fragments/commit-review-helper.md`](fragments/commit-review-helper.md)** — the auto-split
  commit procedure for projects with a `commit_review.py`-style helper (JSON-mode invocation,
  HARD-warning gating, per-group staging, post-commit follow-ups). Projects without the helper don't
  import it.
- **[`fragments/cowork-sandbox.md`](fragments/cowork-sandbox.md)** — Cowork-sandbox-only recovery:
  file-delete via `mcp__cowork__allow_cowork_file_delete`, `gc.auto=0`/`maintenance.auto=false`,
  and stale-lock/debris handling. Irrelevant to host repos; import it only in a Cowork sandbox.
