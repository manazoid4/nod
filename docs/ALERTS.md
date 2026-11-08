# Alerts + Piblo Buddy

One notification path for reminders, agent approvals and webhook alerts. Device column in
FEATURE_INVENTORY stays unchecked until it is tried on a real Cardputer ADV.

## Send an alert (token required, same Bearer token as every other Core route)

    POST /buddy/alert        Authorization: Bearer <MAZ_TOKEN>
    {"source":"ci","kind":"sla","title":"SLA breach: ticket #123","body":"...",
     "priority":"urgent","actions":["ack","snooze"],"delay_seconds":0,"expires_in":900}

- `kind`: reminder | meeting | deadline | sla | computer | task_done | approval | info
- `priority`: low | normal | high | urgent. `title` <= 60, `body` <= 200 chars.
- `actions`: `ack`, `snooze` (approve/reject are only valid for `kind: approval`).
- `kind: approval` is routed into the existing approval queue (`/buddy/request` path: 60 s
  timeout, Halt fails closed). The device answers with Y/N through `/buddy/decide` only.
- Alerts enter the `/buddy/events` ring (`kind: "alert"`, schema under `alert`). Older firmware
  ignores unknown kinds.
- `delay_seconds` schedules it (Core fires it when the device next polls after it is due).
- Device answers: `POST /buddy/alert/{id}/ack` or `/snooze` (`{"minutes": 10}`); Core stores the
  outcome (`GET /buddy/alerts`). An expired snooze fires the alert again; an ack never does.
- Voice "remind me in N minutes to X" creates a `reminder` alert automatically.

## Device (src/core/alerts.cpp, firmware/nod/include/alert_policy.h)

| priority | sound (original tones) | edge flash | repeats | Buddy |
|---|---|---|---|---|
| low | 1 note | none | no | idle |
| normal | 2 notes | 2 pulses | no | needs attention |
| high | 3 notes | 4 pulses | every 30 s | needs attention |
| urgent | 4 notes | until answered | every 8 s | needs attention |

`task_done` always shows Buddy celebrating. Quiet drops low/normal sounds; Silent leaves only
urgent (forced, like the Focus alarm). The approval chime is unchanged and never muted.
Keys: ENT/A ack, S snooze, ESC hide locally. The approval overlay always sits above alerts.

Demo: `MAZ_TOKEN=... python scripts/demo-alerts.py`
