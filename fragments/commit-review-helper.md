# Fragment — commit-review helper (auto-split commits)

**Import this only if** the project has a `commit_review.py`-style helper that auto-splits a turn's
changes into grouped commits (the VRTNGM single-canonical-source-with-derived-artifacts model). It
extends — does not replace — the *End-of-turn commit posture* in
[`baseline.md`](../baseline.md): the default-to-commit, commit-the-coherent-unit, opt-out-inline
posture is unchanged; this fragment is only the mechanics of the split.

Import the same way as baseline: `@<path>` in Claude Code, or inlined between sync markers in
environments that don't honor imports (e.g. Cowork).

## End-of-turn auto-split commit

Any turn that modifies tracked files ends with an auto-split commit driven by the project's
commit-review helper. Git history is the safety net; `git reset --soft HEAD~N` reverses the last N
commits cleanly if anything looks wrong.

### Procedure

1. **Run the project's commit-review helper in JSON mode.** Typical invocation:

   ```bash
   python3 pipeline/commit_review.py --json
   ```

   The helper is read-only — it never writes, stages, commits, or pushes. It returns a structured
   payload describing: the auto-split commit groups, suggested per-group subjects, hard/soft
   warnings, stale-debris detection, gc-needed advisory, and any post-commit follow-ups.

2. **If `warnings.hard` is non-empty, STOP — do not commit.** HARD-warning families:

   - **Pipeline-integrity violation.** Source data changed but generated artifacts weren't
     regenerated, or invariant checks failed. Resolve by running the project's pipeline, then re-run
     the helper.
   - **Stale git debris.** Orphan `*.lock` files older than 5 minutes or orphan `tmp_obj_*` files in
     `.git/objects/`. Clean with `find .git -name '*.lock' -delete && find .git/objects -name
     'tmp_obj_*' -delete` (in a Cowork sandbox, use `mcp__cowork__allow_cowork_file_delete` first —
     see [`cowork-sandbox.md`](cowork-sandbox.md)), then re-run.

3. **Auto-split commit each non-empty group, in the order the helper emitted them.** For each group,
   run `git add` with the group's explicit file paths (never `git add .`) followed by
   `git commit -m "<subject>"`, **as its own bash call**. Keeping each commit in its own bash
   invocation respects the sandbox's 45-second timeout and ensures one commit's slowness can't kill
   another mid-flight.

   Override the helper's generic `suggested_subject` with one that names the actual change — Claude
   has the context from the turn that just produced the work, the helper does not. Report each commit
   hash inline as it lands.

4. **Post-commit follow-ups.** Run any follow-ups the helper flagged (changelog regeneration,
   `git gc --prune=now`, etc.), each in its own bash call.

### Helper-specific hard rules

These supplement the [`baseline.md`](../baseline.md) hard rules when the helper is in use:

- **Never commit while a HARD warning is outstanding** (debris or pipeline-integrity).
- **Stage the helper's explicit per-group file list**, never `git add .` / `-A`. (Baseline already
  bars `git add .`; this names where the path list comes from.)
- **Never bundle a commit and `git gc` into the same bash call.** Each belongs in its own invocation
  so neither can timeout-kill the other.

### Project-specific config that pairs with this fragment

These live in the project's own `CLAUDE.md`, not here:

- **Commit-group taxonomy** — what categories of files exist, how they split into commits, and in
  what order. The helper's group config lives per-project.
- **Pipeline-integrity specifics** — which scripts must have run, which invariants must pass, what
  counts as a HARD vs WARN.
