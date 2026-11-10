# Piblo pre-launch viability checklist — DRAFT for Maz's approval

Date: 9 Nov 2026. Sources: `HERMES-HANDOVER-COMPETITORS-2026-11-09.md`, `research/COMPETITORS-2026-11-09.md` (22 competitors), `research/COMPLAINTS-2026-11-09.md` (57 complaints), `EDITIONS.md` (Maz's prices £79/£149), `READINESS-2026-11-08.md`, `GATES.md`, `FEATURE_INVENTORY.md`, `ECONOMICS.md`.

Status of every item below is honest: **NOT READY** means the evidence does not exist yet, not that it is impossible. Nothing here changes prices, makes public claims, spends money, or posts anything.

Owner gate: launch only when the five Gate items in `GATES.md` are MET with evidence in the repo. This checklist explains what to prove and why.

---

## 1. Real feature demonstrations vs. planned features

**Question:** If someone films the campaign video today on real hardware, what actually happens?

**Evidence (from FEATURE_INVENTORY.md — device column):**

| Feature | Reality on real Cardputer ADV | Verified? |
|---|---|---|
| Wi-Fi link to Core | Link works, screen mirror verified | ✅ (ledger #2, #3) |
| Brain Dump / voice note → PC inbox | Note reached inbox | ✅ (ledger #5) |
| Hold-to-talk voice | Answer correct, but voice reply slow + robotic | 🟡 partial (ledger #4) |
| Voice reply (TTS) | Poor quality/latency | ❌ |
| Alerts / reminders / Piblo Buddy | Code-complete | ⬜ not device-verified |
| Agent approvals | Code-complete (security fixes applied) | ⬜ not device-verified |
| Focus timers / Tasks / Shift | Code-complete | ⬜ not device-verified |
| Charging screen | Improved, but charging inferred from voltage trend (may be wrong) | ⬜ not device-verified |
| Desktop app (Electron) | Being built | ⬜ not built |
| Telegram/subtitles/routine builder/larger screen | Planned/not built | ❌ — never claim these |

**Viability test:** Only demo the three rows with ✅/🟡. Before launch, queue:
1. Uncut video per workflow (Gate 1) + 100 approval trials with zero unauthorised executions (Gate 2) — approvals are 🔴 NOT MET, so **approvals must not be the hero demo until Gate 2 passes**.
2. Publish measured voice latency + battery hours; robot-voice TTS is the wrong hero until tuned.

**Risk:** Competitors  failed on demo-vs-product (Rabbit R1: demoed agent-driving-any-app, shipped 4 integrations). Kickstarter hardware retrenchment (Kode spec swaps) is recent. One aspirational render in the campaign page is enough to sink trust.

**Verdict: NOT READY for approval-hero campaign. Ready for Brain Dump + reminders demo once verified.**

---

## 2. Whether buyers understand the Windows PC requirement

**Question:** Do waitlist signups know Piblo does nothing without a Windows PC + Wi-Fi + Piblo Core?

**Evidence:** `CAMPAIGN.md` states it plainly ("What you need" box). Complaints research is explicit: the #1 surprise-subscription pattern (Humane/Plaud, "needs X you didn't know") and K4/P6 extras ("hardware needs separate module", "free minutes then $99.99") all bite when requirements hide at the bottom. Research cards C8/K6 (steep learning curve, not turnkey) echo the same risk.

**Viability test:** None of the five community posts (Task 2) mentions the PC requirement only in the footer — all state it in-body. Waitlist hook copy (Task 1, all versions) carries the "what you need" box *beside* the form, not under the fold. Five outsider setup tests (Gate 3) must prove a non-technical person finishes in <10 min with the written guide alone.

**Risk:** Mac/Linux users. The competitor set (Kode, Flipper) needs no PC. Windows-only is the second-biggest objection after price/value. A stretch-goal Mac/Linux Core vote mitigates this later but does not remove it today.

**Verdict: NOT READY to launch until Gate 3 outsider tests pass and "1 thing that surprises people" is removed from first-run.**

---

## 3. Why buyers would pay for Piblo instead of a Cardputer ADV

**Question:** Piblo's hardware is a US$29.90 M5Stack Cardputer ADV (live M5Stack page SKU K132-ADV, [S] in EDITIONS.md). Why £79?

**Honest answers (which go on the campaign page):**
- Ready-flashed firmware + Piblo Core (one-click installer), vs. raw Linux/board that needs coding (K6/C8 complaints hit both Cardputer and Kode).
- Web flasher that auto-detects ADV vs. original and refuses the wrong build (C1 multiplexer gotcha).
- Voice → PC note pipeline with "saved to PC" tick (P2 lesson), one-press reminders, agent approvals designed fail-closed (Gate 2).
- Printed enclosure, packaging, quick-start card, cable, UK support, replacement promise (vs. AliExpress/M5Stack store, no UK warranty).
- Open source (MIT) — read the code before backing; no account, no cloud required, no subscription (contrasts Humane/Plaud/Limitless deaths).

**Honest weakness to state:** A skilled hobbyist can flash Piblo themselves. The Kickstarter sells the finished experience, safety testing, and support — not exotic hardware. EDITIONS.md route (a) walkthrough confirms £79 is profitable *because* the board is only ~£23, which is a feature (low price), not a scandal.

**Viability test:** "DIY kills it" fails only if Piblo's differentiator is the experience, not the board. Survey the Reddit/ESP32 audience (Task 2, Post 2) with one question: "Would you pay £79 for ready-to-use + everything above?" If the answer is no for hobbyists, the Founder's aluminium tier (keepsake, limited, numbered) is the hobbyist magnet, not a discount.

**Verdict: PLAUSIBLE but unproven. Needs a real answer on the July-settling question — do people pay for polish on a $30 board?**

---

## 4. Realistic unit economics: fees, shipping, taxes, compliance, returns

**Question:** Does £79 survive contact with reality at the volumes Piblo will actually sell?

**Evidence (EDITIONS.md — the Maz-decided model, not yet supplier-quoted):**

- Board: £23 retail [S], £17.5–£19 bulk [A] — route (a) retail works at £79 (35% gross margin registered / 46% unregistered at 500 units).
- Founder's £149: thin at 100 units (3%/19%), viable at 500+ (34%/45% with bulk board).
- Shipping charged ≈ cost (Original £9.50 charged / ~£9.60 cost, world £13; Founder's £11 / £11) — treated as pass-through [A].
- Kickstarter 5% + payment 3% + £0.30 [S]. VAT modelled at 20% registered (accountant must confirm; Kickstarter does not withhold VAT).
- **One-off costs [A/E]:** compliance (EMC + RED bundle £8–8.8k, or ~£3.5–9k if module cert reuses), UN38.3 €4–6k per cell variant (possibly nil if M5Stack supplies), samples/jigs £2.5k Original / £5.5k Founder's, video/legal/accounting £3k. **Total modelled: £13.5k Original / £17k Founder's.**
- **Net after one-offs (EDITIONS.md tables):** −£11,785 at 100 units (Original), −£1,132 at 500, +£14,471 at 1,000. Founder's: −£17,011 at 100, +£2,157 at 500.

**What that means:**
- £79 at 100 units loses money after compliance one-offs regardless of unit margin. Break-even ≈ 500–800 units (registered) or ~500 (unregistered).
- Bad case (board +25%, shipping +30%, enclosure +30%) shaves ~10 points off margin — goal must be set from the bad case (ECONOMICS.md instruction), not the rosy one.
- Not yet modelled: import VAT/duty on China goods, FX, fulfilment-centre handling/storage, cash-flow timing (pay suppliers before Kickstarter pays out), aluminium-antenna plastic window cost. All flagged [A] or missing in EDITIONS.md.
- `ECONOMICS.csv` (both editions) is the living sheet. **Do not quote a margin until M5Stack bulk price + CNC quote are written.**

**Viability test:** Fill `ECONOMICS.csv` from two written supplier quotes (board + enclosure/packaging), accountant VAT confirmation, and one compliance-lab fixed quote. Run the bad case. If 500 units at £79 (unregistered) still clears ≥30% margin, the price is viable. If not, raise or cap units (e.g. capped 250 Founder's batch).

**Verdict: NOT READY for a £79 launch commitment. Model is close; two unquoted numbers (board, CNC) decide it.**

---

## 5. Unique waitlist counts vs. Kickstarter followers

**Question:** Are the numbers real, double-opt-in, and not double-counted?

**Evidence:** `READINESS-2026-11-08.md` says waitlist runs on Resend double-opt-in, but "signup count not recorded in repo; check the Resend segment." Competitor research (competitors §2.8): Kickstarter pre-launch followers are NOT exportable emails; the owned list is the only list Maz controls. Follower→backer ratios are weak-sourced (25% Reddit anecdote, 32% Gizmocrowd claim — both flagged unverified).

**Viability test:** Before any launch date is set:
1. Pull the Resend "Piblo" segment count: `resend audiences list` then segment count. Record it in `handoff`. This is the Task 6 baseline (every Monday thereafter).
2. Create the KS pre-launch page (free) but only after the campaign draft passes internal review; record follower count after 10 (Kickstarter hides it before then).
3. Target: 1,500–3,000 combined (waitlist unique emails + KS followers where overlap is unknown → report as a range, never summed as unique). At 15–30% warm-list day-1 conversion [E], that's 300–600 day-1 backers — the handover's plan.
4. Dedup: same email can't be "2 people". Report two lines: *emails confirmed* and *KS followers*, not a false total.

**Risk:** Unknown overlap + optimistic day-1 % math. Flipper/Kode-scale (10k) needs a creator/press moment, not a list alone (competitors §2.9).

**Verdict: NOT READY — count is not knowable from the repo today. Task 6 measurement is the first fix.**

---

## 6. Evidence of willingness to pledge at the proposed price

**Question:** Will anyone actually pay £79? Has anyone said so in a way that counts?

**Evidence:** None. The waitlist is free reservation (no payment). No pre-order, no £1 reservation, no survey result, no outsider test, no backer quote exists in the repo. Competitor comparables are instructive, not predictive:
- Starbond Vox (same idea): 22 backers. The idea sells 22 people.
- SenseCAP Watcher (Seeed, no maker crowd): 531 backers.
- M5Stack CardputerZero: 13,644 — had 5,000+ KS followers + US$1 reservation on a known brand.
- Kode/Flipper/Tidbyt: scale came from audience + creator moment, not the idea alone.

**Viability test:** Willingness-to-pay must be a *behaviour*, not a survey answer. Cheapest valid test that does not spend money or take payment: a £1 (or £0, refundable) reservation step on piblo.co.uk that locks the early-bird price vs. a control with free reservation only. Count reservations → that's the only number that predicts day-1. Until Maz approves a payment step, the cheapest proxy is the comment-to-signup ratio on Task 2 posts (how many commenters actually sign up).

**Verdict: NO EVIDENCE. This is the gap between 22 backers and 13,644.**

---

## Section 2: The five biggest reasons someone would NOT back Piblo — each with one inexpensive validation test

Ranked by (audience size × deal-breaker strength) from the complaints research.

### 1. "It needs a Windows PC. I'm on Mac/Linux, or I think it's standalone."
**Why:** Windows-only Core shrinks the buyer pool; Kode/Flipper need no PC. Competitors §4 Risk ("Windows-only shrinks the market") and the stretch-goal survey draft ("Mac/Linux Core") both flag it. Highest single objection for non-Windows buyers.
**Inexpensive test:** Add one checkbox to the waitlist form *after* email: "Which PC do you use? Windows / Mac / Linux / Multiple". One week of signups gives the true Windows-only share. If >40% are non-Windows, Mac/Linux Core becomes the #1 stretch goal (and a launch-gate conversation, not an afterthought). Cost: zero (one form field).
**Pass threshold:** ≥60% Windows-only → proceed; <60% → reorder stretch goals before launch.
**Owner:** Maz adds the field. Hermes drafts it; does not deploy.

### 2. "It's just a $30 Cardputer ADV with a 3D-printed shell."
**Why:** The board's retail price is public on M5Stack's store. Hobbyists will flash it themselves and know it. Starbond Vox proved "approval + pet" alone doesn't sell (22 backers).
**Inexpensive test:** In Task 2 Post 2 (r/esp32) and Post 3 (r/M5Stack), end with a single binary question: "Would you pay £79 for ready-to-use firmware + Core + support, or flash it yourself?" Count the ratio in comments. Cost: zero.
**Pass threshold:** ≥30% "would pay" in the hobbyist subs → pitch the experience. <30% → the Founder's aluminium kepsake tier must carry the hobbyist segment (price it as a keepsake, not a tool).
**Owner:** Maz runs the polls; Hermes aggregates replies.

### 3. "AI gadgets are hype. These all die / brick / need subscriptions."
**Why:** The complaints report's #1 theme. Humane (bricked, $24/mo, refunds only 90 days), Limitless (Meta bought it, UK service ended in 2 weeks), Plaud (300 min then $99.99/yr + sync failures + firmware that made it worse). This is the trust objection, and it's rational.
**Inexpensive test:** Publish the "Works without us" pledge (open source, local Core, export/delete, no account) *before* the campaign as a one-page promise, link it from the waitlist page, and ask: "Does this change anything?" in comment replies. The test is whether the pledge alone moves the needle — no, the pledge is free to publish (copy in Task 1).
**Pass threshold:** Commenters cite the pledge unprompted ("that's what sold me") in ≥2 of the 5 posts → trust answer is written and working. Zero mentions → the product story, not the copy, needs more proof (ship the Brain Dump tick; publish the test ledger).
**Owner:** Maz approves and publishes the pledge page.

### 4. "Voice/AI is slow and robotic. It won't feel like the video."
**Why:** Ledger #4 already says voice reply is slow + robotic. Friend's 7–10s lag and Rabbit's misheard requests are the user-facing truth (R3/FR1: "many" frequency). A slick demo that doesn't match day-one reality is the fastest way to a chargeback.
**Inexpensive test:** Publish in the waitlist email an honest 15-second voice clip from the *current* tuning (slow + robotic) and ask: "Would you still back it today at £79?" Measure reply rate + yes share before promising faster voice. Cost: zero (one email to the existing list).
**Pass threshold:** ≥25% reply-yes from a small list → proceed with honest "voice is getting better" framing. <25% → fix voice first; don't launch on the approval hero.
**Owner:** Maz records and sends; Hermes drafts the email.

### 5. "Kickstarter hardware always ships late. I'll get a vague update and silence."
**Why:** G1–G3 + K1: 61% of KS projects ship late, worst damage is silence, Kode slipped July→September after saying "on track". Piblo's READINESS already notes no supplier quote / no compliance — so a late-ship outcome is *likely* unless the plan changes.
**Inexpensive test:** Publish the fixed fortnightly update rhythm now (even pre-launch: a dated milestone list with "done / at risk / late", never "on track" before a gate passes) and run it for one cycle before launch. The test is whether Maz can sustain the rhythm — if the first update misses, fix the process before Kickstarter ever sees him.
**Pass threshold:** Two consecutive on-time fortnightly updates published → launch-ready on trust. One miss → delay the campaign, not the truth.
**Owner:** Maz publishes; Hermes drafts each update.

---

## Section 3: Pre-launch gates summary (what blocks launch)

| # | Blocker | Source | Test to clear |
|---|---|---|---|
| 1 | Approvals not device-verified; 100-trial safety log missing | GATES #2, FEATURE_INVENTORY | Gate 1+2 pass with evidence in repo |
| 2 | No outsider setup tests → Windows requirement friction unknown | GATES #3 | 5 novices, <10 min, from written guide |
| 3 | No supplier quotes → £79 margin is modelled, not real | EDITIONS.md | 2 written quotes + accountant VAT call |
| 4 | No compliance assessment (EMC+RED, UN38.3, WEEE/GPSR) | GATES #5 | Lab quote + scope confirmed |
| 5 | No waitlist count; no willingness-to-pay evidence | READINESS | Task 6 Monday count + £1 reservation behaviour |
| 6 | No uncut demo of any hero workflow | GATES #1, #7 | 3 uncut clips, versions on screen |
| 7 | Voice quality (ledger #4) not launch-ready | FEATURE_INVENTORY | Measured latency/battery published; voice clip test passes |

**Bottom line:** Piblo's story (reminders + voice + any agent + no subscription) is strong and honest. The numbers (500–800 units to break even after one-offs, 1,500–3,000 list for 300–600 day-1 backers) only work if the product gap (approvals verification, voice) and the audience gap (willingness-to-pay at £79) close *before* launch.
