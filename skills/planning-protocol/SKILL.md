---
name: planning-protocol
description: Cross-project standard for matching the planning artifact to the weight of the work — a four-rung ladder from plan-mode-only, through a co-located mini-spec (the default) and briefing→ADR, up to a full spec toolkit. Use before starting any non-trivial piece of work to pick and name the rung; when the user asks "do we need a spec for this?", "write a mini-spec", "should this be an ADR?", or asks to plan a feature; or when setting up a project's planning conventions. Reads per-project parameters (decisions_root, briefings_root, max_rung, status_doc) from the project's CLAUDE.md. A repo whose CLAUDE.md carries its own more specific planning doctrine (e.g. an inline ladder) wins where the two differ.
---

# Planning Protocol

Planning produces **durable artifacts that survive `/clear`, compaction, and
review** — that is the requirement. The *weight* of those artifacts should match
the work: a full spec toolkit is the heaviest rung, not the default, and
plan-mode-only loses the durability a multi-session repo depends on. This skill
is the single source of truth for the ladder; which rungs a project has
apparatus for comes from the project.

Derived from r-net's planning-weight ladder, where it was proven across
concurrent agents, three full-toolkit features, and a 20+ ADR design record.

## Per-project parameters

Read these from the project's `CLAUDE.md` (under its `## Planning` section). If
a project hasn't set them, use the defaults and say so.

| Parameter | Default | Meaning |
|---|---|---|
| **`decisions_root`** | `docs/decisions/` | Where ADRs live (rung 3). |
| **`briefings_root`** | `none` | Where exploration briefings live. `none` = fold the options analysis into the ADR itself (its Options/Why section) rather than a separate doc. |
| **`max_rung`** | `3` | The highest rung this repo has apparatus for. `4` only when a full spec toolkit (e.g. GitHub Spec Kit) is actually installed in the repo. |
| **`status_doc`** | `none` | A living worklog/status file (e.g. `WORKLOG.md`) to link new planning artifacts from, if the repo keeps one. |

## The ladder, lightest to heaviest

1. **Plan mode, no artifact** — trivial, single-sitting changes: a bugfix, one
   config option, a one-file tweak. The plan evaporates at `/clear`, which is
   fine when the work finishes before then. If it spills across sessions, you
   picked the wrong rung — step up.

2. **One-page mini-spec** (the default for most work) — a single `SPEC.md`
   **co-located with the work** (next to the tool, module, or config it
   describes — not under `docs/`), from the template at
   `reference/mini-spec-template.md`: Goal / Constraints / Approach / Tasks /
   Done-when. ~10 minutes to write, one file to read cold. Check tasks off
   inline; if the project declares a `status_doc`, link the spec from it.

3. **Briefing → ADR** — when the hard part is the *decision*, not the build
   (which tool, which topology, which architecture). Explore the options in a
   briefing under `briefings_root` (or directly in the ADR's Options/Why
   section when `briefings_root` is `none`), record the call as an ADR under
   `decisions_root`, then drive the build with a mini-spec or a task list.
   Don't use this rung to drive implementation — it records choices, not tasks.

4. **Full spec toolkit** (e.g. GitHub Spec Kit: specify → plan → tasks →
   implement) — multi-cycle features with sequenced work and genuine
   cross-cutting impact: multiple call sites, contracts between components.
   Only in repos that declare `max_rung: 4`; never bootstrap a spec toolkit
   into a repo just to plan one feature.

**Why this shape:** a spec toolkit's value is the durable artifacts, not the
ceremony — for most work a single file captures the same durability without the
tax. Matching weight to work keeps both the overhead and the context cost
proportionate.

## Picking a rung

Before starting non-trivial work, **pick a rung and say which and why in one
line** (e.g. "Rung 2 — multi-file change, single feature, no open design
fork"). Default to rung 2. Don't silently default to the heaviest rung because
it's the incumbent, or the lightest because it's faster.

Step-up and step-down signals:

- Plan-mode work **spills across sessions** → it needed at least rung 2.
- A mini-spec **wants a research section, contracts, or a data model** → that's
  the signal it's rung-4 work (or rung 3 + several mini-specs, in a
  `max_rung: 3` repo).
- A real fork shows up in a mini-spec's Approach (which tool, which topology)
  → that bullet is a briefing/ADR, not a bullet — step sideways to rung 3,
  decide, then come back.
- A rung-4 ceremony is producing artifacts nobody will reread → the work was
  rung 2; step down and fold what's useful into the mini-spec.

Other methodologies are fine when better suited — briefly justify when
proposing one.

## Rung 2: the mini-spec

- **Placement:** co-located with the work it describes (`tools/<tool>/SPEC.md`,
  next to the module, etc.). It is not a catalogued doc class — keep it next to
  the code, not under `docs/`.
- **Size:** five sections, one screen, ~10 minutes. If it wants to grow past
  that, see the step-up signals.
- **Lifecycle:** check Tasks off inline as you go. When the work ships, the
  spec **stays as the design record** (or folds into an ADR/ops doc if one is
  warranted). Update its `Status:` line; don't delete it.
- **Template:** `reference/mini-spec-template.md`.

## Rung 3: briefing → ADR

- A **briefing** records the *exploration* — options, pros/cons, open
  questions. An **ADR** records the *decision* — context, the call, why, and
  consequences. In repos with no `briefings_root`, the ADR's Options/Why
  section carries the exploration and a separate briefing is not required.
- ADRs are one file per decision, numbered and dated, under `decisions_root`.
  Follow the repo's existing ADR format; don't introduce a new one.
- The ADR is **immutable history**: when the decision changes, write a dated
  update or a superseding ADR rather than rewriting the record.

## Rung 4: full spec toolkit

Only in repos that declare `max_rung: 4`. The toolkit's own workflow governs;
this skill adds the discipline that makes it survive long sessions:

- **Delegate research to subagents** — the main thread gets the summary, not
  the search trail.
- **Read artifacts narrowly** — grep first, then read the slice the current
  task touches, not whole contract/data-model files.
- **Phase-boundary status** — at the end of each phase, write a one-paragraph
  status to the `status_doc` (or the feature's own tracking file) and treat the
  boundary as a natural place to `/clear`; the on-disk artifacts are the state.

The reference implementation is r-net's customized GitHub Spec Kit (a
constitution-check gate in the plan phase; `data-model.md`, `contracts/`, and
`quickstart.md` beyond stock) — consult it before installing a toolkit
elsewhere, and adapt rather than re-derive.

## Relationship to handoffs and worklogs

Planning artifacts are **durable design records**; handoffs
(`handoff-protocol`) are **session-terminal context dumps**. If state belongs
in a spec, ADR, or the repo's `status_doc`, update *that* — write a handoff
only for context that has nowhere durable to live. A repo that plans at the
right rung needs smaller handoffs.

## Setting up a project

To adopt this standard in a project that doesn't have it:

1. Add a `## Planning` section to the project's `CLAUDE.md` declaring at least
   `decisions_root` and `max_rung` (see "Per-project parameters"). Defaults
   suit most repos; declare `max_rung: 4` only where a spec toolkit is actually
   installed.
2. Don't pre-create directories — `decisions_root` comes into being with the
   first ADR.
3. If the repo already carries its own planning doctrine in `CLAUDE.md`, the
   repo's version wins where more specific; converge it to this standard's
   parameter block when it's next touched rather than forking the prose.
