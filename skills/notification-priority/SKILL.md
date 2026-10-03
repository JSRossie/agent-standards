---
name: notification-priority
description: Use when an agent decides how to reach the principal unprompted (alert, reminder, report, cron delivery). Maps P1/P2/P3 to iMessage, Zulip DM, or a channel.
---

# Notification priority

Every unprompted message to the principal carries a priority. The priority picks
the channel. Replies are not notifications: a reply goes back to wherever the
principal asked, so continuing a DM he started never counts as P2.

| Priority | Meaning | Channel |
|---|---|---|
| P1 | He must act within hours, or something is breaking or about to break in a way he would want to be woken for (data loss in progress, security event, outage he will notice) | iMessage via `imessage-notify`, plus the full detail in a Zulip DM |
| P2 | He must decide or act today, nothing on fire (blocked lane, reserved act awaiting his word) | Zulip DM to the principal |
| P3 | Everything else: status, completions, FYI, routine reports | The agent's home channel, one topic per task; routine reports roll into the daily digest |

## Rules

1. **P3 never goes to DM.**
2. **Reply where asked.** A conversation the principal opens stays in that
   thread, including follow-ups it spawns.
3. **P1 text is a pointer.** One line: what and where. The detail lives in the
   DM. Lock-screen rules from `imessage-notify` apply.
4. **One P1 per incident.** No repeats unless the incident gets materially worse.
5. **Failed P1 falls back to P2** and says the iMessage failed.
6. **Cron jobs declare their priority** in the job name or prompt and deliver to
   the matching target. A job whose outcome varies (healthy vs. failing) decides
   per run: P3 when routine, P2 or P1 when not. No job delivers to
   `zulip:dm:<principal>` for P3 output.
7. **Separation of spheres governs P3 placement.** A channel must not carry
   material its audience is not cleared for.

## Enforcement

Instruction only for now. If agents drift, add a `--priority` flag to a notify
helper that refuses a DM target for P3.

## Open Questions

- Quiet hours for P1 (none assumed).
- Whether an unacknowledged P1 or unanswered P2 escalates, and after how long.
