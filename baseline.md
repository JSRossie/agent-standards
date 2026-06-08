# Claude Baseline Standards

Always-on operational rules that apply to every project. Project-specific rules (commit-group taxonomy, pipeline details, data model, terminology) are added inline by each project's `CLAUDE.md` after this import. The git rules below — hard rules, commit hygiene, and concurrent/multi-agent worktree discipline — are the canonical, portable nucleus: import them from here rather than re-deriving them per repo, which is how they drift.

## Sandbox file-delete recovery (Cowork)

In Cowork sandboxes, `rm` and other delete operations may fail with **"Operation not permitted"** — most commonly when stale `.git/HEAD.lock` or `.git/index.lock` files block a commit after an aborted git operation. **Do not tell the user deletion is impossible and do not ask them to delete files manually.** The correct recovery is:

1. Call the MCP tool `mcp__cowork__allow_cowork_file_delete` with the VM path of the file to delete (e.g. `/sessions/<session>/mnt/<folder>/.git/index.lock`). This grants the sandbox permission to delete files in that folder for the remainder of the session.
2. Re-run the `rm -f` in bash.
3. Retry the original operation (e.g. `git commit`).

This pattern applies to any sandboxed delete that fails with "Operation not permitted" — reach for `mcp__cowork__allow_cowork_file_delete` first, not a workaround.

## Recovery from accidental overwrites

With Git in place, recovery is straightforward:

```bash
git diff <path>                # See what changed
git checkout -- <path>         # Revert to last commit
git log --oneline <path>       # See history
```

## End-of-turn auto-split commit

Any turn that modifies tracked files ends with an auto-split commit driven by the project's commit-review helper. The repository exists to track changes and enable backing out unexpected behavior — that purpose is served by **making the commit**, not by asking before each one. Git history is the safety net; `git reset --soft HEAD~N` reverses the last N commits cleanly if anything looks wrong.

### Procedure

1. **Run the project's commit-review helper in JSON mode.** Typical invocation:

   ```bash
   python3 pipeline/commit_review.py --json
   ```

   The helper is read-only — it never writes, stages, commits, or pushes. It returns a structured payload describing: the auto-split commit groups, suggested per-group subjects, hard/soft warnings, stale-debris detection, gc-needed advisory, and any post-commit follow-ups.

2. **If `warnings.hard` is non-empty, STOP — do not commit.** HARD-warning families:

   - **Pipeline-integrity violation.** Source data changed but generated artifacts weren't regenerated, or invariant checks failed. Resolve by running the project's pipeline, then re-run the helper.
   - **Stale git debris.** Orphan `*.lock` files older than 5 minutes or orphan `tmp_obj_*` files in `.git/objects/`. Clean with `find .git -name '*.lock' -delete && find .git/objects -name 'tmp_obj_*' -delete` (use `mcp__cowork__allow_cowork_file_delete` first if needed), then re-run.

3. **Auto-split commit each non-empty group, in the order the helper emitted them.** For each group, run `git add` with the group's explicit file paths (never `git add .`) followed by `git commit -m "<subject>"`, **as its own bash call**. Keeping each commit in its own bash invocation respects the sandbox's 45-second timeout and ensures one commit's slowness can't kill another mid-flight.

   Override the helper's generic `suggested_subject` with one that names the actual change — Claude has the context from the turn that just produced the work, the helper does not. Report each commit hash inline as it lands.

4. **Post-commit follow-ups.** Run any follow-ups the helper flagged (changelog regeneration, `git gc --prune=now`, etc.), each in its own bash call.

### Skipping commits

The default is to commit. To skip, the user says so inline ("don't commit this turn", "leave this uncommitted", "stash only"). Without an explicit opt-out, the auto-split commit fires.

To undo after the fact: `git reset --soft HEAD~N` reverses the last N commits and leaves the changes staged so they can be re-edited. `git reset --hard HEAD~N` discards them entirely.

### Hard rules

- Never run `git push`, `git push --force`, or any remote-modifying command.
- Never amend or rewrite existing commits.
- Never commit while a HARD warning is outstanding (debris or pipeline-integrity).
- Never use `git add .` or `git add -A`. Stage explicit file paths (in helper-driven projects, the helper's per-group file list).
- Never skip hooks (`--no-verify`, `--no-gpg-sign`) without an explicit user instruction.
- Never operate on nested git repositories from outside their root.
- Never bundle a commit and `git gc` into the same bash call. Each belongs in its own invocation so neither can timeout-kill the other.

## Concurrent & multi-agent git hygiene

These rules apply when **more than one session or agent works the same repo at once** — parallel Claude sessions, or background agents spawned with `isolation: "worktree"`. Serial single-operator work is unaffected: it lands on the working branch directly, as usual. The failure mode they prevent is two workers colliding on one checkout — a commit landing on whichever branch happens to be checked out, or one agent's `git add` sweeping in another's half-done work.

- **Branch per task, named for the work.** Each concurrent session/agent branches off its stated base as `<type>/<short-topic>`, with `<type>` drawn from the commit-type vocabulary (`feat`/`fix`/`docs`/`chore`/…): `feat/dns-secondary`, `fix/boot-leg`. Never land work on a branch named for a different task; never invent an opaque name unrelated to the work.
- **Isolated worktrees, never a shared checkout.** The foreground session owns the primary checkout; parallel/background agents each run in their own `git worktree` (the Agent tool's `isolation: "worktree"`). Two agents mutating one working tree corrupt each other's index and files.
- **Confirm your branch immediately before every commit.** Run `git branch --show-current` and abort if it isn't the branch you created for this task. This is the check that catches a commit about to land on someone else's branch.
- **Stage explicit paths (the no-`git add .` rule, sharpened).** In a shared tree, `git add .` / `-A` sweeps another agent's uncommitted work into your commit. Stage only the paths you changed.
- **Don't touch a branch or checkout you don't own.** Don't switch the primary checkout while another session is using it; don't `git branch -f`, `reset --hard`, or delete a branch you didn't create. History rewrites stay ask-first whichever branch they target.
- **Wrong-branch recovery: prefer the lossless move.** If a commit lands on the wrong branch and the intended branch is an ancestor of it (so fast-forwarding loses nothing), point the intended branch at the commit and switch to it — then leave the wrong branch as you found it for its owner:

  ```
  git branch -f <intended-branch> <commit>
  git switch <intended-branch>
  ```

  Ask the operator before rewinding anything that is not a clean fast-forward.

### Deterministic checks over prose

If an invariant can be expressed as a check, encode it — in a hook (see *One-time hooks setup per clone* below) or CI — rather than as a paragraph every agent has to remember to follow. Prose is for genuine judgment (when to branch, how to write a good commit message); mechanical invariants (branch guards, single-writer file ownership, regenerating a derived file) belong in enforcement. The corollary for shared "hot" files that nearly every session edits — status logs, indexes, lockfiles — is structural: make the file single-owner or generated from per-session fragments, so two agents never open the same file, instead of asking everyone to "edit only their own section." A convention is the first thing concurrent work violates; structure can't be.

## Git hygiene

- Set `gc.auto=0` and `maintenance.auto=false` in the project's `.git/config`. This disables git's built-in background auto-gc/maintenance, which is the source of the recurring `.git/objects/maintenance.lock` problem — the backgrounded process gets killed when the sandbox session ends, leaving the lock behind to silently suppress all future maintenance.
- The commit-review helper's `gc` advisory replaces the disabled auto-gc. It trips when loose objects exceed 500, when no pack files exist, or when the newest pack is more than 14 days old. `git gc --prune=now` runs in 1–2 seconds on small/medium repos and is safe to re-run.
- The debris check catches the symptom of interrupted git operations leaving `*.lock` or `tmp_obj_*` files. Treating debris as a HARD warning means a stale lock surfaces immediately rather than rotting silently for days.

## One-time hooks setup per clone

If the project uses git hooks (e.g., for timestamp footer maintenance), each clone must wire them up:

```bash
git config core.hooksPath .githooks
```

Without this, commits succeed but pre-commit hooks don't fire.

---

## What this fragment doesn't include

The following are project-specific and live in each project's own `CLAUDE.md`:

- **Commit-group taxonomy** — what categories of files exist in this project, how they split into commits, and in what order. The helper's group config lives per-project.
- **Pipeline-integrity specifics** — which scripts must have run, which invariants must pass, what counts as a HARD vs WARN.
- **Project paths, data model, naming conventions, terminology.**
- **Skill installations** — list which skills from `~/Local/agent-standards/skills/` (or elsewhere) are in scope.
