# Piblo feature shortlist + build handover (9 Nov 2026)

Maz's cut of the top 10 from `FEATURE-IDEAS-50` (PR #57). Rule for every feature: **it must do something a phone, smartwatch, Alexa or Google Home does badly.** Piblo's edge is that Piblo Core sits on your own PC and knows what you were doing there; Piblo itself is a glanceable screen with real keys that the people around you can see.

Dropped by Maz: "What was I doing?", "Waiting on" tracker, Do-not-disturb sign, "Approve any agent" as a headline (too AI-centric; the approval system stays under the hood as part of The Nod).

## The shortlist

### 1. Phone-free mode
**Pitch:** "Put your phone in a drawer. Piblo lets through only the people who matter."
- **How it works:** a VIP list (up to 10 people) set in Piblo Core. Calls and messages from them show on Piblo with name + first line; everything else waits until you pick the phone up.
- **Better than a watch:** a watch still buzzes with everything unless you build focus filters on the phone; Piblo shows nothing else by design and has no apps to drift into. Timed sessions ("phone-free until 6pm") earn Buddy XP.
- **Keys:** A = "seen", S = "reply later" (Piblo reminds you at the session end), voice key = dictate a short reply, sent after you confirm.
- **Build route:** Windows Phone Link notifications on the PC (Core reads them), or a small Android companion app that forwards VIP notifications to Core. Start with Android forwarding; iPhone is harder (Phone Link is limited) and must be stated honestly.
- **Effort:** M. **First test:** VIP message arrives on Piblo within 5 s; a non-VIP message never shows.

### 2. The Nod (renamed from "Spending guard")
**Pitch:** "Anything big waits for your nod." Matches the brand line *Ask. Listen. Nod.*
- **What counts as big:** spending money, sending to a customer or a group, deleting files, posting publicly, sharing a document. Each shows on Piblo: what, who to, how much.
- **Keys:** a **long-press** on Y to approve (no accidental taps), N to stop, S to "ask me in 10 minutes". Unanswered = stopped (fails safe, already how the approval queue works).
- **Who it's for:** anyone who lets software or other people act for them: a family card used by a teenager, a shop's refunds, an automation that emails customers, and yes, AI agents.
- **Extras:** a daily "nod log" on the PC (everything approved or stopped, with times); per-source limits ("under £10 doesn't need a nod").
- **Build route:** extends the existing `kind: approval` alert path in Core (`docs/ALERTS.md`): add `amount`, `recipient`, `category`, and a long-press rule in firmware.
- **Effort:** S-M. **First test:** a webhook asking to "pay £42 to Acme" shows amount + payee; short press does nothing; long-press approves; timeout stops it.

### 3. A first device for kids, with a location module
**Pitch:** "A first device that isn't a phone."
- **Base (no module):** chore list with XP and Buddy rewards, reminders from parents, quick "I'm home" / "pick me up" keys that message a parent, no browser, no apps, no social feeds.
- **Location module (add-on):** a clip-on unit with GPS plus a mobile-data connection, because GPS alone only knows where it is; it needs a data link to tell a parent. M5Stack sells Grove units combining GNSS with Cat-M/NB-IoT (e.g. "Unit CatM+GNSS", SIM7080G) [price and Cardputer ADV fit not yet verified].
  - Parent sees the location on their own PC/Piblo only when: the child presses "pick me up", a scheduled check-in time ("at school by 9"), or a safe-zone exit (home, school).
  - Battery: GPS sampling every few minutes, not continuously; publish real battery hours.
- **Safeguarding rules (non-negotiable):** location goes only to the linked parent, never to us; visible "location on" icon on the child's screen; no hidden tracking mode; works only with a parent account set up on the family PC; clear UK GDPR wording for children's data.
- **Effort:** base M, module L (hardware + SIM plan). **First test:** "pick me up" sends the location to the parent within 30 s on mobile data.

### 4. Parent check-in (elderly relatives) — keep, improve later
**Pitch:** "One key that says I'm OK."
- **Now:** a daily "I'm OK" key and a "call me" key. If no "I'm OK" by a set time (e.g. 11am), the family gets a gentle alert. Big text, loud clear chime, no menus.
- **Later ideas (not committed):** medication "taken" key, spoken reminders from family in their own voice, a weekly "how's Mum doing" summary for the family.
- **Effort:** M. **First test:** missed check-in by 11:00 sends a family alert by 11:05.

### 5. Lead alerts with reply — keep (Maz didn't cut it)
- Website form, missed call or CRM lead shows on Piblo; voice reply "call back at 3" becomes a drafted message sent only after The Nod.
- **Effort:** M (webhook alerts already exist).

### 6. Privacy light + local-only switch — keep
- Visible recording light while the mic is on; one switch makes Core use only local models, so nothing leaves the PC.
- **Effort:** S.

### 7. NEW: "Follow me" screen handoff
**Pitch:** "Piblo knows what you were watching, and moves it to the right screen at the right moment."
- **Scene:** you're cooking, food's nearly done. You say to Piblo: "when the pasta's done, carry on my show on the TV." Piblo sets the timer; when it rings, Core finds what you were last watching on your laptop (the YouTube video and timestamp, or the next episode), pauses the laptop, and plays it on the Chromecast / smart TV from the same second.
- **Why Alexa/Google Home can't do this:** they can cast a named video, but they don't know what you were watching on your laptop, where you stopped, or what you were working on. Piblo Core is on your PC, so it does.
- **Also:** "send this to the TV" (whatever is playing on the PC now); "back to my laptop" (TV pauses, laptop resumes at the same second); "when I'm back at my desk, reopen what I had" (works with the PC's open windows).
- **Build route:** Core already runs on the PC. YouTube position from the browser (small extension or reading the active tab), casting via open-source Chromecast libraries (`pychromecast` or `catt`, both MIT/BSD-style licences, check before use), Android TV via ADB over Wi-Fi as a second step. Netflix/iPlayer: only "open the app on the TV" at first; no DRM tricks.
- **Effort:** M for YouTube + Chromecast; L for other services. **First test:** YouTube video on the laptop at 12:34 continues on the Chromecast within 3 s of 12:34, laptop paused.

## Build order (suggested)
1. The Nod (small, builds on existing code, protects every other feature).
2. Privacy light + local-only switch (small, needed for trust before launch).
3. Follow me (YouTube + Chromecast), the best demo video moment.
4. Phone-free mode (Android first).
5. Parent check-in.
6. Lead alerts with reply.
7. Kids' device base, then the location module after supplier quotes.

---

## Handover prompt (paste to Hermes or a coding agent)

> You are working on Piblo (repo manazoid4/piblo). Read `docs/kickstarter/FEATURE-SHORTLIST-2026-11-09.md` first, then `docs/ALERTS.md` and `FEATURE_INVENTORY.md`.
>
> Goal: make the shortlist real, one finished slice at a time, in the build order listed. Start with **The Nod**: extend the existing `kind: approval` alert in Core with `amount`, `recipient` and `category`; show them on the device; require a long-press on Y to approve; keep timeout = stopped. Add Core tests, run the existing test suite, and open a PR with before/after evidence. Do not mark anything done on the device until it has been seen working on the real Cardputer ADV; write the device test steps instead.
>
> Then draft (do not build yet) a one-page design for **Follow me** (YouTube + Chromecast): how Core reads the laptop's current video and time, which open-source casting library and licence, and a 3-step demo script for the Kickstarter video.
>
> Rules: one PR per feature; surgical changes; no new paid services; never print keys or tokens; no public posts, emails or DMs; no prices on the site; never mention any location beyond "UK". The kids' location module needs supplier quotes and a safeguarding review before any build: research only. Report back in 5 bullets: what changed, test results, PR link, blockers, next step.
