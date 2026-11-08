# Site round 2 — 8 Nov 2026

Screenshots: `before-390.png`, `before-1440.png` (start of round 2), `after-390.png`, `after-1440.png`, plus `*-fold.png` (first screen only). Served locally, reduced motion on.

| | Before | After |
|---|---|---|
| Mobile page height | 7,458 px | 7,312 px (with a new How-it-works section and 4 more FAQs) |
| Horizontal scroll at 390 / 1440 px | none | none |
| Site tests | 30 pass | 30 pass (2 count assertions lowered on purpose: one concept film instead of three) |

## What changed
- **Hero:** concept film replaced by the illustrated device showing the reminder screen with Buddy ("Bins out tonight · A done · S later"), labelled as an illustration. On mobile the device now shows on the first screen. Lede now says what it is and why not a phone ("small screen with real keys… No apps, no feeds").
- **How Piblo works:** new 3 steps (connect, it tells you, you answer) plus "What you need": a Windows PC running Piblo Core on the same Wi-Fi; internet only for spoken answers via a service you pick.
- **What it's for:** five uses (reminders, meetings, voice notes, alerts that matter, work alerts via webhook with approve/reject).
- **Piblo Buddy:** one character through a day (sleeping, calm, needs you, working, celebrating) with an "In testing" status: drawn by the firmware in the test build (PR #55), not yet checked on a device.
- **Ownership:** no subscription, open source, updates and add-ons (no unvalidated accessories), "not tied to us" (Core runs on your PC; outside services may change).
- **Editions:** £79/£149 removed from the page and FAQ. Prices go to the list first once supplier quotes are in. Founder's card has a brushed-aluminium look.
- **CTA:** every "Get launch-day price" replaced by "Join the launch list" (no launch-day offer exists).
- **Films:** three concept videos down to one, lower on the page, labelled "Concept film… the screen is simulated".
- **FAQ:** added Does it need a computer? Does it work offline? How is it different from my phone? and an evidence-based What works today?
- **Roadmap:** removed "Video vault, print-from-reel" (unrelated speculation) and "survives a restart" (no evidence). "Running on the actual device now" replaced with honest status from the test ledger. Footers now say "designed in the UK".

## Waitlist evidence (8 Nov, 13:xx)
Live endpoint `https://piblo.co.uk/api/waitlist` (code unchanged by this PR):
- bad email → 400 `invalid-email`; no consent → 400 `no-consent`; honeypot → 200 (not saved); 3 KB body → 413; GET → 405; no-JS bad email → 303 to `/?subscribed=0#waitlist`.
- Vercel env (names only): `RESEND_API_KEY`, `RESEND_SEGMENT_ID`, `SIGNUP_NOTIFY_EMAIL` set for production and preview.
- Resend segment "Piblo" exists (created 7 Nov) and has **0 contacts**. The success path (contact saved + owner alert) is **not yet proven**. Needs one approved test signup.
- The preview URL is behind Vercel Authentication, so strangers cannot test the preview form.

## Claims that still need real hardware evidence
1. Reminder chime + Buddy "needs you" + A/S keys (PR #55, untested on device).
2. Approve/reject a webhook or agent request with a key on the device.
3. Buddy's five moods rendering on the 240×135 screen.
4. Voice note saved to the PC inbox (ledger #5 passed once, Oct; re-check on current firmware).
5. Software updates over Wi-Fi from Core (code exists, device ⬜).
6. Battery: screen off when away (Buddy "sleeping").
7. Any real prototype photo or uncut video to replace the hero illustration.
