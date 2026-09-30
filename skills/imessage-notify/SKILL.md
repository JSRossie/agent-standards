---
name: imessage-notify
description: Use when the principal asks to be texted, messaged on his phone, or notified when work finishes ("text me when done", "send me an iMessage", "ping my phone"). Sends one line to his iMessage thread over the Hermes Photon adapter via a one-shot cron job, then verifies delivery in the log. Works from any conversation platform, including a Zulip DM. Supersedes the bundled `imessage` skill (imsg CLI) and any Messages.app / osascript route for notifications.
---

# iMessage notify (Photon)

A notification is one line to the principal's phone saying what finished and
where to look. It goes over the **Photon** adapter, a Hermes gateway platform
that relays iMessage through Photon's cloud. It does not go through this Mac's
Messages app.

## Preconditions (check once per session, names only)

1. The profile's `config.yaml` has `platforms.photon.enabled: true`.
2. The profile's `.env` defines `PHOTON_PROJECT_ID`, `PHOTON_PROJECT_SECRET` and
   `PHOTON_HOME_CHANNEL`. Check that the names exist with a non-empty value
   (`grep -cE '^PHOTON_PROJECT_ID=.+' .env`). Never print a value.
3. The gateway is running (`cronjob_manage` returns `gateway_running: true`).

If any fails, the profile has no phone route: say so in the current
conversation and deliver the notice there instead. Do not configure Photon
yourself; enabling it is the principal's decision (a third party in the path).

## Send

Create a one-shot cron job. A cron run's final response is what gets delivered,
so the prompt asks for the exact text and nothing else, with no tools:

```
cronjob_manage(
  action="create",
  name="notify-<slug>",
  schedule="in 1m",
  deliver="photon",
  enabled_toolsets=[],
  prompt="Reply with exactly this text and nothing else: <agent name>: <what finished>. <where to look>.",
)
```

`deliver="photon"` resolves to the profile's `PHOTON_HOME_CHANNEL`, which is the
principal's thread. It reaches his phone even when the conversation you are in
is on Zulip or another platform.

## Verify before reporting it sent

About 90 seconds after the scheduled time:

1. `cronjob_manage(action="list")`: the job shows `last_status: ok` and
   `last_delivery_error: null`.
2. The profile's `logs/agent.log` has
   `Job '<job_id>': delivered to photon:<masked number> via live adapter ... message_id=spc-msg-...`.

Only with both may you say "sent". Say "accepted by Photon" rather than
"received": the log proves hand-off to Photon, not arrival on the phone. The
principal's reply in the thread is the only proof of arrival.

## What to write

- One line, under about 200 characters, starting with the agent's name.
- What finished, the outcome (done, failed, needs you), and where to look (a
  URL, a Zulip topic, a commit).
- Nothing that needs a reply unless it is a real ask.

## Never in a text

- Secrets, tokens, keys, passwords, or anything credential-shaped. Photon is a
  third-party relay.
- Material outside the agent's remit, or another agent's domain.
- Anything the principal would not want on a lock screen: explicit content,
  health, finance, employer detail. Send "done, details in Zulip" instead.

## Failure handling

- Delivery error or no `delivered to photon` line: retry once with a new job.
  If that fails, report the failure in the current conversation with the job
  id and the log line, and stop.
- Never fall back to Messages.app, `osascript` or the `imsg` CLI. On james-mini
  the AppleScript send hangs (a pending Automation consent is the likely cause,
  unconfirmed) and `imsg` is not installed.
- Remove nothing: one-shot jobs complete and disable themselves.

## Notes

- Tested 2026-09-29 from the `quinn` profile during a Zulip DM: job
  `df86df88b2ea`, delivered in about 4 s, message id returned. Arrival on the
  phone confirmed by the principal the same evening ("got it" in the thread).
- Not checked: whether each profile (quinn, morgan, laura) texts from its own
  line or shares one thread. Each profile has its own Photon project
  credentials. If it matters, send a test from the new profile and ask.
- A profile loads this skill only if its `skills.external_dirs` includes
  `~/Local/agent-standards/skills`.
