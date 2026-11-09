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

## The Nod: details + hold-to-approve for big actions

Anything big (a payment, a message to a customer, a deleted file) can wait for a deliberate
long-press. Add these optional fields to a `kind: approval` alert (or to `POST /buddy/request`):

    {"kind":"approval","source":"bank","title":"Pay Acme","body":"Invoice 1042",
     "nod":true,"category":"payment","amount":"£42.00","recipient":"Acme Ltd"}

| field | rule |
|---|---|
| `amount` | string, e.g. "£42.00"; cut to 16 chars |
| `recipient` | string; cut to 40 chars |
| `category` | `payment` `send` `delete` `post` `share` `other`; anything else becomes `other` |
| `nod` | `true` = the device needs Y/Enter HELD about 0.8 s (a filling bar shows); a short press only shows "hold Y to approve". N/Esc still stops at once |

On `/buddy/summary` the device gets `nod` plus `summary` rewritten as three lines (head, amount, "to recipient"); the original `body` stays in `/buddy/pending`.
Too-long values are cut, not rejected. Without the fields an approval looks and works exactly as before.
Unanswered still means stopped (60 s timeout, Halt, fail closed), and the only way to approve is still `/buddy/decide`.

`GET /buddy/nods?limit=20` (token required) is the nod log: newest first, each with `id`, `title`, `amount`,
`recipient`, `category`, `nod`, `outcome` (`approved` | `stopped` | `expired`), `requested_at`, `decided_at`.
It reads the in-memory approval queue (last 50), so it is cleared when Core restarts. Pending asks are not listed.
Follow-up, not built: per-source limits ("under £10 needs no nod") and "ask me in 10 minutes".

Demo: `MAZ_TOKEN=... python scripts/demo-alerts.py --only nod`

## Device (src/core/alerts.cpp, firmware/nod/include/alert_policy.h)

| priority | sound (original tones) | edge flash | Buddy |
|---|---|---|---|
| low | 1 note | none | idle |
| normal | 2 notes | 2 pulses | needs attention |
| high | 3 notes | 4 pulses | needs attention |
| urgent | 4 notes | until answered | needs attention |

`task_done` always shows Buddy celebrating. Quiet drops low/normal sounds; Silent leaves only
urgent (forced, like the Focus alarm). The approval chime is unchanged and never muted.
Keys: ENT/A ack, S snooze, ESC hide locally; every other key (Fn shortcuts included) still reaches the normal UI. The approval overlay always sits above alerts (nod approvals: see above). Only high/urgent alerts wake the screen.

Demo: `MAZ_TOKEN=... python scripts/demo-alerts.py`

## Known limits
- `/buddy/events` is paged (about 4.8 KB per poll, oldest first); the device continues from `last`.
- At most 50 alert records are kept. Answered or expired ones are evicted first; if all 50 are still
  pending, `POST /buddy/alert` answers 429 `alert_table_full` (approvals are unaffected).
- Delivery is "device polls Core": an alert that fired while the device was offline is delivered only if it
  is still inside the 20-event ring when the device reconnects; there is no replay of older unacked alerts yet.
- The device answer (ack/snooze) is fire-and-forget on the shared worker; if it fails, Core keeps the alert open.
- Tone playback blocks the UI loop for up to about 0.4 s (same pattern as the approval chime).
- `kind: approval` cannot be delayed (`delay_seconds` is rejected with 400).
