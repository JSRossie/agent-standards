# Fragment — Cowork sandbox git/file recovery

**Import this only if** the project runs in a **Cowork sandbox**. Everything here addresses
sandbox-specific failure modes (delete permissions, background-maintenance lock rot) that do not
exist on a host machine. Host repos should not import it.

Import the same way as baseline: in Cowork, inline it between sync markers (Cowork's CLAUDE.md
loader doesn't honor `@<path>` imports).

## Sandbox file-delete recovery

In Cowork sandboxes, `rm` and other delete operations may fail with **"Operation not permitted"** —
most commonly when stale `.git/HEAD.lock` or `.git/index.lock` files block a commit after an aborted
git operation. **Do not tell the user deletion is impossible and do not ask them to delete files
manually.** The correct recovery is:

1. Call the MCP tool `mcp__cowork__allow_cowork_file_delete` with the VM path of the file to delete
   (e.g. `/sessions/<session>/mnt/<folder>/.git/index.lock`). This grants the sandbox permission to
   delete files in that folder for the remainder of the session.
2. Re-run the `rm -f` in bash.
3. Retry the original operation (e.g. `git commit`).

This pattern applies to any sandboxed delete that fails with "Operation not permitted" — reach for
`mcp__cowork__allow_cowork_file_delete` first, not a workaround.

## Disable background git maintenance

- Set `gc.auto=0` and `maintenance.auto=false` in the project's `.git/config`. This disables git's
  built-in background auto-gc/maintenance, which is the source of the recurring
  `.git/objects/maintenance.lock` problem — the backgrounded process gets killed when the sandbox
  session ends, leaving the lock behind to silently suppress all future maintenance.
- With auto-gc disabled, run `git gc --prune=now` manually when loose objects accumulate (it runs in
  1–2 seconds on small/medium repos and is safe to re-run). Projects using the
  [`commit-review-helper`](commit-review-helper.md) fragment get a `gc` advisory from the helper that
  replaces the disabled auto-gc — it trips when loose objects exceed 500, when no pack files exist,
  or when the newest pack is more than 14 days old.
- **Never bundle a commit and `git gc` into the same bash call.** Each belongs in its own invocation
  so the sandbox's 45-second timeout on one can't kill the other.

## Stale-lock / debris handling

Interrupted git operations leave `*.lock` or `tmp_obj_*` debris that silently blocks later commits
and maintenance. Treat debris as something to surface and clear immediately rather than let it rot:

```bash
find .git -name '*.lock' -delete
find .git/objects -name 'tmp_obj_*' -delete
```

If a delete fails with "Operation not permitted", run `mcp__cowork__allow_cowork_file_delete` on the
file first (see *Sandbox file-delete recovery* above), then re-run. Projects using the
[`commit-review-helper`](commit-review-helper.md) fragment have this surfaced as a HARD warning so a
stale lock blocks the commit instead of rotting silently for days.
