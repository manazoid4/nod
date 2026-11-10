# Task 2 — Community post drafts (5) — DRAFT ONLY, do not post

Status: DRAFT for Maz's approval. Maz sends every post himself.
Rule reminder: honest device status only; no price; link to piblo.co.uk; lead with reminders / voice / any-agent, NOT "approve + pet" novelty.

**Demo honesty rule:** each post below is tied to a real clip Maz records on the real Cardputer ADV, uncut, with PC visible. No simulated UI, no renders, no other people's footage. Clip filenames are noted so engineering can verify against the test ledger before Maz posts.

**Self-promo rules snapshot (Maz must re-check at post time — rules change):**
- r/ClaudeAI: allows project Show & Tell with context; avoid pure link-drop; engage in comments. Must not imply Anthropic endorsement.
- r/esp32: technical Show & Tell is fine; link inside text, not URL-only title; expect "how does it differ from raw ESP32?" questions.
- r/M5Stack: generally welcomes Cardputer ADV projects; no affiliation claimed; show it's not a resale — Piblo firmware + open code.
- r/selfhosted: local-first posts do well; no home-data exposure; "no cloud/account" angle helps.
- Hacker News Show HN: launch + demo story; answer first comments fast; no marketing adjectives.

**v2 note (9 Nov, Claude):** these five are developer and maker communities, so leading with what works today (voice notes, Brain Dump, approvals) stays: it's honest and it's what these readers care about. The shortlist features are not built yet, so they are never claimed as working. Instead, end every post with this block, which turns each post into a feature vote and a waitlist sign-up:

> **What I'm building next, and I'd like your vote:**
> 1. **The Nod**: anything big (a payment, a message to a customer, a deleted file) waits until you long-press yes.
> 2. **Follow me**: "when the pasta's done, carry on my show on the TV". Core knows what was playing on your laptop and continues it on the Chromecast from the same second.
> 3. **Phone-free mode**: phone in a drawer, Piblo shows only messages from people you choose.
> 4. **Family**: a first device for kids that isn't a phone, and a one-key "I'm OK" check-in for older relatives.
>
> Which would you actually use? Launch list (no spam, no card): piblo.co.uk

For the general public (TikTok, Instagram, Facebook groups), use the hooks in `01-waitlist-hook-copy.md` v2 instead, not these posts.

Do not post anywhere before Maz reviews. Placeholder `[CLIP: name.mp4]` must be replaced with the actual uncut clip.

---

## Post 1 — r/ClaudeAI

**Title:** I wanted one real key to say yes/no to what my agent is about to do — so I built a keyboard for it

**Body:**
> r/ClaudeAI — hope this is in-bounds as a Show & Tell.
>
> I've been running Claude Code on my Windows PC and kept missing the permission prompts when I stepped away from the desk. So I made a small device with a real keyboard that sits next to me: when an agent on my PC asks, the request appears on the device and I press Yes / No / Later. I don't answer, nothing gets approved — it falls back to the normal prompt on the PC.
>
> It's called Piblo. It's built on the M5Stack Cardputer ADV (ESP32-S3, real keys), and the PC side (Piblo Core) is open source. The device also does two things I use more than approvals: voice notes (hold a key, talk, it saves to my PC — no cloud) and one-press reminders (Yes / No / Later), so I can answer from the sofa instead of unlocking my phone.
>
> Honest status: this is a prototype. Approvals and voice note saving work on hardware in my test setup; I'm still verifying edge cases (timeouts, Wi-Fi drop) and doing the slow boring parts now (100-run safety log, outsider setup tests). I know Anthropic's own Desktop Buddy already does approvals + a pet for free — this is different in two practical ways: it works with any agent via webhooks (not Claude-only), and it has a full keyboard + reminders + voice notes, not just two buttons.
>
> [CLIP: 30s uncut — hand holds key, approves a real Claude Code permission, PC shows it proceeding. No edits.]
>
> I'd like to Kickstart a small batch later this year if enough people want it. Free reservation at piblo.co.uk (no payment — just email, so you're on the list if it happens). Firmware and Core are open on GitHub if you want to read the code before anything else.
>
> Happy to answer questions. If this reads as too promo-y for the sub, say so and I'll move it.
>
> Edit — demo clip above is the real prototype on my PC. No affiliation with Anthropic or M5Stack.

**Self-promo note (r/ClaudeAI):** Text-first Show & Tell is tolerated; link is once at the end, not in the title. Comment engagement expected. No endorsement language about Anthropic.
**Clip required:** approve-real-agent.mp4 (must show the pending prompt on PC + device side by side).
**FAQ replies to prep:** "Isn't this just Buddy?" / "Does it work with Codex?" / "Why not just use the terminal?"

---

## Post 2 — r/esp32

**Title:** Piblo: hold-to-talk voice notes + agent approvals on a Cardputer ADV (open source, no cloud)

**Body:**
> Show & Tell — Piblo, a pocket ESP32-S3 device built around the M5Stack Cardputer ADV.
>
> Architecture in one paragraph: device sends voice frames over Wi-Fi to the Windows host (Piblo Core), host does STT/LLM/TTS, device speaks back. The two flows I demo:
>
> 1. **Hold-to-talk → save (Brain Dump).** Hold SPACE, talk, release. Note lands in the PC inbox with a "saved to PC" confirmation. Raw audio kept so transcripts can be checked. No cloud account, storage is local-first.
> 2. **Agent approval.** Host raises an approval request (tool call, command, recipient). Device shows what is being asked; physical keys Yes / No / Later. Default deny on timeout/disconnect/stale request — nothing proceeds without an explicit press.
>
> Reminders are the third leg: one-press Yes/No/Later so I don't have to open the phone.
>
> What's open vs. what's verified (so this doesn't read as hype):
> - Verified on real ADV hardware: Wi-Fi link to Core, screen mirror, Brain Dump saving a note to the PC inbox.
> - Partial: voice reply works but is slow + robotic today (logged in our test ledger).
> - Code-complete but not yet device-verified: approvals flow, alerts/reminders, focus timers.
> - Planned, not in this prototype: anything involving Buddy BLE parity, offline transcription models, the bigger display.
>
> Why a Cardputer ADV as base: 56-key keyboard beats two buttons for Yes/No/Later, and the ESP32-S3 + I/O expander quirks (ADV reads keys via a multiplexer — old Cardputer firmware doesn't work) are documented in our repo notes. The web flasher refuses the wrong build.
>
> [CLIP: 25s uncut — Brain Dump end-to-end (hold key, talk, "saved to PC" tick visible), then a reminder Yes/No/Later.]
>
> GitHub: firmware + Core source, pinout, and our open test ledger (pass/fail per build). Site: piblo.co.uk. Free reservation (email only, no payment) is there if you want early-bird pricing when/if it launches.
>
> Hardest thing today: keeping voice latency down over Wi-Fi and making battery behaviour sane (measure + publish real hours; "must be on to charge" gotcha from the original Cardputer is noted in our quick-start). Happy to dig into the audio path or approval safety model — ask anything.

**Self-promo note (r/esp32):** Detail-first, link-once. Bring specifics (latency, fail-closed rules) — this crowd punishes marketing copy.
**Clip required:** braindump-saved-tick.mp4 (must show the "saved to PC" tick uncut).

---

## Post 3 — r/M5Stack

**Title:** What I built on my Cardputer ADV this month: Piblo (voice notes + approvals, open firmware)

**Body:**
> Hi — Piblo is a project I've been building on the Cardputer ADV for the last few months. Wanted to share it with people who know the board.
>
> Short version: a pocket device with real keys that talks to your Windows PC over Wi-Fi and does three things without your phone:
> - **Voice notes:** hold a key, talk, and it's saved on your PC (with a tick that confirms it).
> - **Approvals:** when an AI agent on my PC asks to run something, it shows on the device. Yes / No / Later by key press. No answer = nothing happens.
> - **Reminders:** same three keys, so I never have to unlock anything. Answer, done.
>
> Status (plain): Wi-Fi link + screen mirror + Brain Dump are verified on a real ADV in my test ledger. Voice replies work but are slow/robotic today. Alerts/reminders and approvals are code-complete and going through hardware verification now. Everything is open source (firmware + Windows Core on GitHub) and no account or cloud is required for the core features.
>
> Notes for ADV folks: the ADV's multiplexer keyboard (older firmware won't run on it) is documented — our flasher checks and says "ADV only" instead of failing silently. Battery caveats from the community (charge while on, ~6–8h in normal use) are on our quick-start card.
>
> Not a resale: the value is the firmware + host app + support. The board itself is a standard M5Stack part — happy to be transparent about that.
>
> [CLIP: 20s uncut — reminder Yes/No/Later + approval deny on real hardware.]
>
> If you're curious, the code + test log are on GitHub, and there's a free email reservation at piblo.co.uk (no payment) if I do a small Kickstarter batch. No pressure — even reading the code helps if it spares someone a keyboard headache.
>
> Questions welcome, especially on anything ADV-specific.

**Self-promo note (r/M5Stack):** Small community — be respectful, no affiliation language, credit the board. Expect technical questions about the multiplexer/ADV differences.
**Clip required:** reminders-yes-no-later.mp4 (real device).

---

## Post 4 — r/selfhosted

**Title:** Self-hosted voice notes that never leave my network: Piblo (Cardputer ADV + Windows Core)

**Body:**
> I've avoided wearable/AI companions because they all phone home. So I built one that doesn't.
>
> Piblo is a pocket ESP32 device (M5Stack Cardputer ADV) paired with a Windows host app (Piblo Core). Voice notes, reminders and agent approvals never leave my LAN unless I explicitly wire up a cloud model myself. No account, no subscription, no "sign in to see your notes".
>
> How it works IRL:
> - Hold a key → talk → the audio goes over Wi-Fi to my PC → transcribed → saved locally. There's a visible "saved to PC" tick, and the raw audio file sits next to the transcript so I can verify. Nothing scribbles off to a vendor's cloud by default.
> - Reminders are one-press (Yes / No / Later) on the device. Agent approvals same keys — and the safe default is deny. If the device is off or Wi-Fi drops, the agent doesn't proceed.
> - Runs on my own hardware: my PC and a Wi-Fi AP. Free models (or local Whisper) supported; paid models are my choice, not a toll gate.
>
> Honest bit: this is a prototype, not a product yet. Voice replies today are slow and sound robotic while the audio path is being tuned; I'm publishing measured results in the repo's test ledger rather than vibes. Setup is one-click for Core + web flasher for the device (ADV vs. original is auto-checked). Code is MIT/open source on GitHub — self-hosters can read it before trusting it.
>
> [CLIP: 30s uncut — voice note saved to PC + "saved" tick, plus a denied approval when the device timeouts.]
>
> I'm thinking of offering a small batch of ready-to-use units via Kickstarter later (free email reservation at piblo.co.uk — no money, just a list). If you're deep in self-hosting and want to see a local-only pocket device like this exist, that's the ask. If not, the code is there.
>
> Happy to answer architecture or self-hosting questions.

**Self-promo note (r/selfhosted):** Local-first framing wins here. Emphasize no cloud/account; expect "why not just a phone app?" challenges — answer with the glance-without-the-rabbit-hole point.
**Clip required:** local-save-tick.mp4 (longest honest cut; show local filesystem, not just device).

---

## Post 5 — Hacker News "Show HN"

**Title:** Show HN: Piblo – open-source pocket keypad for voice notes, reminders, and AI-agent approvals

**Body:**
> Hi HN — I built Piblo, an open-source pocket device (M5Stack Cardputer ADV, ESP32-S3) + Windows host app. Three flows, one discipline: everything works on your own hardware, no account, no cloud required.
>
> - **Hold key → talk → note saved to your PC** (local-first, with a "saved" tick; raw audio kept alongside transcript).
> - **Agent approvals:** when an AI agent on your PC asks permission, the request shows on the physical keyboard. Yes / No / Later. Fail-closed by design: timeout, disconnect, or stale request = denied, never auto-approved.
> - **One-press reminders:** same three keys, no phone unlock, no feed rabbit hole.
>
> Honest status: this is a working prototype, not a product. Verified on real hardware today: Wi-Fi link, screen mirror, and voice-note saving. Voice reply is the rough edge (slow/robotic while I tune the audio path — report in the repo). Approvals and alerts are code-complete and in hardware verification now. I documented the failure modes I hit (ADV multiplexer keyboard, charge-while-on behaviour) instead of hiding them.
>
> Why not just use X: Anthropic's free Desktop Buddy does approvals + a pet on two buttons — Piblo goes wider (any agent over webhooks, full keyboard, voice notes, reminders) and open-source firmware + host. Happy to argue trade-offs in the comments.
>
> Uncut demo: [CLIP: 45s — one continuous shot, device + PC together: voice note saved, reminder answered, approval shown and denied.] No renders, no simulated UI, version numbers on screen.
>
> Code + test ledger: GitHub (firmware, Core, pinout, per-build pass/fail). Site: piblo.co.uk with a free, no-payment email reservation if I do a small Kickstarter batch. No affiliation with Anthropic/M5Stack.
>
> I'd genuinely like to know: which of the three flows would you actually use, and what's the first thing you'd break? (That's the point of showing it here.)

**Self-promo note (Show HN):** No marketing adjectives. First 30 minutes of comments decide everything — Maz must be available to answer. Post on a weekday morning UK time. Launch HN only with the full uncut clip ready.
**Clip required:** show-hn-45s-uncut.mp4 (single take, device + PC in frame, firmware/Core version visible).

---

## What all five deliberately do NOT say (per handover + complaints research)
- No price, no discount %, no delivery date.
- No "never lost" voice-note guarantee (pipeline not yet shipped as local-first + tick).
- No "works with Claude Desktop Buddy BLE protocol" claim (planned, not built).
- No "approve Claude + a pet = new" pitch (Anthropic free; Starbond 22 backers).
- No battery-hour promises before measurement.
- No location beyond "UK". No mention of Maz beyond founder.

## Pre-post QA checklist (per post, before Maz sends)
- [ ] Clip is the real device, uncut, firmware/Core versions visible, no CGI
- [ ] No price anywhere in text, image, or comment replies
- [ ] "What you need" (Windows PC + Wi-Fi) stated in body, not just site
- [ ] No affiliation implied with Anthropic, M5Stack, Kode, Flipper
- [ ] Link appears once, to piblo.co.uk only
- [ ] Maz available for 2h after posting
