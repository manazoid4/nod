# Real footage shot list: the Cardputer-based prototype

Status: DRAFT plan. Nothing here has been filmed.

Why: Kickstarter hardware campaigns need a real prototype, and `docs/kickstarter/GATES.md` gates 1, 2 and 7 need uncut video. The current films are concept renders and one generated scene. This list is what replaces them with evidence.

## Rules

- Film what works. If a step fails, keep the failed take in a "bloopers and failures" folder. Honest failures are useful for updates.
- Uncut means one continuous take with no edit, no speed change and no cut-aways between press and result. Light grading and a trim at each end are fine.
- No CGI, no simulated screens, no voice-over that says something the video does not show.
- Show the PC screen and the device in the same frame wherever the PC is part of the claim.
- Show firmware and Core versions on screen or in a held-up note. Latest compile was reported as v1.0.2 on the owner's device (`docs/HANDOVER-COMPETITOR-NEXT-2026-11-07.md`). Check the actual version on the day.
- Do not show a location, address, Wi-Fi name, IP address, API key, or anyone's face you do not have written consent for. Hide the Wi-Fi name and secrets before filming. The repo is public.
- Say "Designed in the UK" at most. No town.

## Kit

- The real Cardputer ADV, charged, running the build you will describe.
- The Windows PC running Core, with the desktop in a clean state (no personal tabs or notifications).
- A phone on a tripod or stand (1080p or better, 30 fps, landscape and a vertical pass).
- A second camera angle or a screen recording of the PC if possible.
- Daylight or a soft lamp. Avoid glare on the 1.14 inch screen. Turn the screen brightness up.
- A plain surface in cream or oak, a mint or orange prop, nothing with text.
- A clapper or a visible clock for time reference.
- A lav mic or a quiet room for the speaker audio. Record the device speaker too, close to the phone.
- A notebook to log each take: date, firmware version, Core version, pass or fail.

## Priority 1: the three gate-1 workflows (uncut, one take each)

| # | Shot | What must be visible | Pass test |
|---|---|---|---|
| 1 | Hold-to-talk question, spoken reply | Hand, device, PC in frame. Hold key, speak a short question, release, hear the spoken reply | Reply is on topic and audible. Gate: reply latency noted (do not claim a figure unless measured) |
| 2 | Voice capture of a thought | Hold key, say a note, release. Then show where it was saved on the PC | The saved note text matches what was said |
| 3 | Agent approval (yes and no) | The PC shows an AI agent asking to do something harmless. The device shows the request. One take pressing yes, one take pressing no. One take with no answer | Yes runs it. No does not. No answer does not. All three on camera |

Use harmless test actions only (for example, open a folder you created for the test).

## Priority 2: proof the "Verified" claims

| # | Shot | What must be visible |
|---|---|---|
| 4 | Core answering with free cloud AI | PC screen showing the provider in use, a question and an answer |
| 5 | Provider failover | Turn one provider off (invalid key in a test profile) and show Core switching to the next. Show the log line |
| 6 | Device sync over Wi-Fi | Device and PC together, a change on one appearing on the other |
| 7 | Wireless firmware update | The update running from start to a reboot, with the version number before and after |
| 8 | Typed note | Type a short note on the device keys. Show where it appears. Only if the feature is confirmed on the device |
| 9 | Charging screen | Plug in USB-C at Home. Screen should change to Charging within about 90 seconds. Unplug and show it stop. Record both events with a clock. Charging is inferred from the battery voltage trend, so keep the failed takes too |

## Priority 3: the object itself

| # | Shot | Notes |
|---|---|---|
| 10 | Real device on a table, turned slowly by hand | Replaces turntable concept clips. Plain surface, soft light. Label as "Prototype" |
| 11 | Close-up of keys and screen, thumb typing | Macro, steady. Check legends are readable |
| 12 | Size in hand | Next to a coin or a ruler for scale. Published size is 84 x 54 x 19.6 mm |
| 13 | USB-C, speaker grille, microphone openings | Stills too |
| 14 | If printed: the case fitting around the device | Only when a real print exists. Show gaps, port access, key access honestly (`hardware/case/nod_case.scad` is CAD only today) |
| 15 | Real unboxing | Only if a real kit exists. Otherwise skip |

## Priority 4: outsider tests (gate 3)

- Film five people setting up Piblo from the written guide on their own Windows PC. Written consent for each, including that clips may be used publicly.
- Screen-record and film hands. No faces unless they agree.
- Log time to finish and where they got stuck. Fix the guide. Re-test.

## Priority 5: approval trials (gate 2)

- Log 100 approval runs in a spreadsheet: time, firmware version, Core version, result, any unapproved execution.
- Film at least five real runs and one of each failure mode (timeout, disconnect, duplicate request, stale request). The expected result for every one is "denied".
- Zero unapproved executions is the pass mark. One failure resets the count after the fix.

## Stills and audio to capture on the same day

- 10 stills: device from above, three-quarter, side, in hand, on a PC desk, charging, with cable.
- 30 seconds of room tone.
- Close recording of the device speaker reply.
- A screen capture of Core's window with settings and secrets hidden.

## Edit plan once footage exists

1. Cut a 60 to 90 second campaign video: 10 seconds of the problem, the three workflows in order, the honest status, the waitlist line. Use real footage only. Label anything that is not real.
2. Publish the uncut takes in full beside the edit (a playlist or a page link). This is the proof for Kickstarter review.
3. Cut ten-second vertical clips for social, one per workflow.
4. Swap the concept films on the site for real footage as each shot passes. Keep the concept films in a "Future ideas" area with their labels, or remove them.
5. Update the "In testing" rows in `campaign-page-draft.md` and `README.md` only when the matching take exists.

## Done check

- Each of the three gate-1 workflows has an uncut take with firmware and Core versions visible.
- Every "Verified" line on the page has a shot or a log behind it.
- No secrets, Wi-Fi names, IP addresses or place names in any frame or file name.
- The owner has watched every clip and signed it off.
