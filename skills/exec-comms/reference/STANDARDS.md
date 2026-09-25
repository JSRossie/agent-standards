# Source standards

The standards `exec-comms` draws on, with origin, what each is for, where it breaks, and
what it produces. Use this to pick a format deliberately, and for your own writing.

## Core output formats

### BLUF — Bottom Line Up Front
**Origin:** US Army, AR 25-50 *Preparing and Managing Correspondence* (Army writing standard).
**What:** the conclusion, decision, or ask is the first sentence. Everything after is
support the reader may skip.
**Pros:** universal; works inside any other format; fastest reading time.
**Cons:** a rule, not a structure. Says nothing about what follows the first line.
**Use when:** always. Every other format below opens with a BLUF line.
**Sample:** "Recommend we drop vendor A; contract lapses Friday and B is 20% cheaper at equal SLA."

### Action Memo
**Origin:** US State Department correspondence handbook (5 FAH-1), the Action Memorandum:
decision requested, recommendation, options, approve/disapprove lines.
**What:** a one-page decision request. Decision and deadline, recommendation with reason,
the options considered, and a signature line.
**Pros:** forces a single recommendation; makes deferral cost visible; approve-with-a-word.
**Cons:** heavy for small calls; tempts agents to invent options for form's sake.
**Use when:** the reader must decide something with consequences.
**Sample:**
```
DECISION: approve moving the lab to the new subnet by Oct 3.
RECOMMEND: cut over Saturday 02:00 — lowest traffic, full rollback window.
OPTIONS: A Sat 02:00 · B weekday evening (shorter window) · C defer to Q4 (blocks VPN work)
RISK IF DEFERRED: VPN rollout slips two weeks.
APPROVE / DISAPPROVE / DISCUSS
```

### SBAR — Situation, Background, Assessment, Recommendation
**Origin:** Kaiser Permanente patient-safety work (Leonard, Graham, Bonacum, 2004),
spread by the Institute for Healthcare Improvement. Often attributed to US Navy submarine
crews; that origin is unverified folklore, so cite Kaiser/IHI.
**What:** four labelled lines for escalating a problem under time pressure.
**Pros:** built for interruptions; the reader can act on S and R alone; separates fact (S, B)
from judgment (A).
**Cons:** wrong for good news or routine status; B tempts over-explanation.
**Use when:** something is wrong and the reader needs to act or decide soon.
**Sample:**
```
S  Nightly backup to NAS-2 has failed three nights running.
B  Started after the firmware update on the 21st; disk is at 91%.
A  Likely the update changed the SMB auth default; disk space is a secondary risk.
R  Roll firmware back tonight; I need the admin credential to do it.
```

### Minto Pyramid / SCQA
**Origin:** Barbara Minto, McKinsey, *The Pyramid Principle* (1978). SCQA is its
opening: Situation, Complication, Question, Answer.
**What:** answer first, then grouped supporting arguments, each of which is itself a
mini-pyramid. Groupings should be MECE (mutually exclusive, collectively exhaustive).
**Pros:** the strongest structure for a recommendation; readers can stop at any depth.
**Cons:** the "three points" cap is a heuristic, not Minto's rule; SCQA opening can
become the very throat-clearing BLUF forbids. Keep S and C to one line each, or drop them.
**Use when:** the reader asked a question or for a recommendation.
**Sample:** "Use Postgres. It is already in the stack, the team knows it, and the write load is a tenth of its ceiling."

### 3P — Progress, Plans, Problems
**Origin:** software-management practice; used in Anthropic's own internal-comms formats.
**What:** three short lists. Problems is the only mandatory-when-present section.
**Pros:** lightest routine status; trivially scannable; empty sections vanish.
**Cons:** no room for a decision ask beyond "Problems"; no explicit RAG.
**Use when:** routine progress on one task or project.

### SITREP — Situation Report
**Origin:** military reporting; the doctrinal form is a fixed-field message. The agent
form here is the civilian adaptation: status, done, next, blocked, need.
**What:** periodic status across several workstreams with a single RAG at the top.
**Pros:** consistent across reports, so change is visible by diff; RAG gives a one-glance read.
**Cons:** overkill for one task; invites "Green, nothing to report" noise unless exception
rule is enforced.
**Use when:** a long-running operation with more than one moving part.

### Smart Brevity
**Origin:** Axios; VandeHei, Allen, Schwartz, *Smart Brevity* (2022). Trademarked term.
**What:** headline, one-line lede, "why it matters", then optional "go deeper". Bulleted,
bold lead-ins.
**Pros:** best for several unrelated items; optimized for skimming on a phone.
**Cons:** flattens argument; can read as glib for hard problems; heavy bold.
**Use when:** a digest of several items, none of which needs its own memo.

### Completed Staff Work
**Origin:** memo attributed to Provost Marshal General Archer Lerch, US Army, 1942.
**What:** doctrine, not a format. Staff studies the problem, works out every alternative,
and presents one finished recommendation the chief can approve by signing. Never
"what do you want me to do?"
**Pros:** the single best statement of the intent behind this skill.
**Cons:** can over-shoot into acting without authority; pair with closed-loop confirmation.
**Use when:** always, as posture.

### Decision brief vs information brief
**Origin:** US Army staff practice (ATP 5-0.1 / FM 6-0 briefing types).
**What:** name which one you are giving. A decision brief ends in a recommendation and asks
for a decision; an information brief ends when the information is delivered.
**Use when:** the first line should make the type obvious. If it does not, fix the first line.

## Supplementary disciplines

### Commander's Intent
**Origin:** US Army mission command (ADP 6-0): purpose, key tasks, end state.
**Use when:** *tasking* an agent. Give the why and the end state; leave the how open.

### RFC 2119 requirement keywords
**Origin:** IETF RFC 2119 (1997), clarified by RFC 8174 (uppercase only).
**What:** MUST, MUST NOT, SHOULD, SHOULD NOT, MAY with fixed meanings.
**Caveat:** evidence that capitalized keywords improve agent compliance is weak. Optional.

### Closed-loop communication
**Origin:** air-traffic read-back; crew resource management; TeamSTEPPS in healthcare.
**What:** receiver restates the instruction; sender confirms. Here: one line before a
costly or irreversible action.

### Words of Estimative Probability / ICD 203
**Origin:** Sherman Kent, CIA, 1964; codified in Intelligence Community Directive 203
(2015) as seven bands from *almost no chance* to *almost certain*.
**What:** fixed term-to-probability mapping; confidence in the evidence is reported
separately from probability of the judgment.

### Management by exception
**Origin:** classical management (Taylor); formalized in PRINCE2 tolerances.
**What:** report only deviations from plan. Silence is a signal.

### RAG status
**Origin:** UK project-management practice; PRINCE2, MSP.
**What:** Red / Amber / Green per item. Here, only Amber and Red get detail.

### Architecture Decision Record
**Origin:** Michael Nygard, 2011.
**What:** context, decision, consequences. Here, the one-line decision log is the
lightweight form; full ADRs are for durable design decisions.

### Amazon six-pager / PR-FAQ
**Origin:** Amazon, Bezos-era meeting culture.
**What:** narrative deep dive read in silence. Only on explicit request; never the default.

## Choosing, in one line each

- Decide → Action Memo. Fire → SBAR. Question → Answer + support. Routine → 3P.
- Many streams → SITREP. Many items → Smart Brevity. About to act → closed-loop line.
- Acted already → decision log line. Deep dive → only if asked, six-pager.
