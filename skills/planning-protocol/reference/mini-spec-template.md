# Mini-spec template

The default planning artifact (rung 2 of the planning-protocol ladder) for work
that is more than a single-sitting tweak (plan mode would lose it) but less
than a multi-cycle, cross-cutting feature (which earns a full spec toolkit).

## How to use

1. Copy the template below into a `SPEC.md` **co-located with the work** —
   `tools/<tool>/SPEC.md` for a tool, alongside the module or config it
   describes. Not under `docs/`; it lives next to the code.
2. Fill the five sections. Aim for ~10 minutes and one screen. If it wants to
   grow a research section, contracts, or a data model, that's the signal to
   step up a rung.
3. If the project declares a `status_doc`, link the spec from it. Check tasks
   off inline as you go.
4. When the work ships, the spec stays as the design record (or folds into an
   ADR/ops doc if one is warranted). Update its `Status:` line; don't delete it.

---

```markdown
# <Thing> — mini-spec

**Status:** draft | building | shipped
**Updated:** YYYY-MM-DD

## Goal
One or two sentences: what this delivers and why. Answer "done means what?"
in plain terms before the Done-when checklist makes it testable.

## Constraints
The non-negotiables that shape the approach — existing ADRs/decisions this must
respect, interfaces it can't break, security/scope boundaries, the project's
runtime or tooling conventions. Cite ADRs by number where the repo has them. If
a constraint is an assumption rather than a known, mark it.

## Approach
How, at a glance — the shape of the solution, key decisions, and the ones
deliberately deferred. A few bullets or a short paragraph, not a design doc. If
a real fork shows up here (which tool, which topology), that's an ADR, not a
bullet — step sideways to rung 3.

## Tasks
- [ ] Concrete, ordered, checkable steps
- [ ] Each one a thing you'd actually commit
- [ ] Keep them small enough to check off in a sitting

## Done-when
- [ ] Observable acceptance criteria — the conditions that make this shippable
- [ ] Tests pass, run the way this repo runs them
- [ ] Docs / status_doc updated as the change warrants
```
