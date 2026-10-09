# NOD independent-lens audit — 9 October 2026
## Scope and source discipline
Primary GitHub: https://github.com/manazoid4/nod (main at 0723c3e3b4ace47ab76b84167be69f1678d78a20)
Prototype software: https://github.com/manazoid4/maz-pocket (main, reviewed 9 October 2026)
External: Kickstarter rules https://www.kickstarter.com/rules ; M5Stack https://docs.m5stack.com/en/core/Cardputer-Adv ; UK product regulations https://www.gov.uk/guidance/placing-ukca-or-ce-marked-products-on-the-market-in-great-britain ; WEEE https://www.gov.uk/guidance/electrical-and-electronic-equipment-eee-producer-responsibility .

Audit method: six distinct review lenses (product, engineering, security, UX, industrialisation/economics, campaign); these are structured perspectives, NOT independent sub-agent executions. No physical device was flashed, tested or observed. No supplier quote, business conversion data, or battery measurements were obtained. Do not convert self-reported verified status in docs into independent proof.

## Executive finding
NOD is a credible concept with related functioning software on MAZ Pocket, but not yet ready to accept Kickstarter hardware pledges. The narrow defensible product is a pocket companion control for a paired PC: press-to-talk, voice note capture, deliberate on-device approvals. Avoid competing with the smartphone as a general assistant. Its strongest unique benefit is a physical approval boundary, not chatbot answers.
Kickstarter target: November 2026 is a planning review target, not a declared campaign launch.

## Repository audit
- nod main contains README, docs/PLAN.md, docs/ROADMAP.md, docs/UPSTREAM-NOTE.md, MIT/NOTICE and firmware/draft/. It does NOT currently include a standalone nod buildable platformio.ini, dedicated tests, shipping pipeline, hub service, or Kickstarter page.
- firmware/draft/README.md explicitly says not compiled; buddy.cpp includes MAZ Pocket headers. BLE draft is not a Wi-Fi remote approval implementation.
- NOD plan proposes /buddy/request, /buddy/state, /buddy/decide and Claude Code hook with fallback to the terminal on 60s timeout. These are NOT established as shipped in nod.
- MAZ Pocket README describes v0.8.0, six home tiles, Windows MAZ Core, model routing, phone-approved scopes and voice functions; ROADMAP describes Wi-Fi sync/hub Q&A/firmware updates as verified, but voice, PC action and approvals still in progress.
- MAZ Pocket open PRs reviewed include #41 agent approvals via nod (unmerged), #43 nod Flow dictation (unmerged), #42 focus sprint, #69 docked mode, and #35 reliability recovery. Being on a PR does not prove merged or flashed.
- Security groundwork in MAZ Pocket host includes constant-time bearer comparison and signed short-lived grants, but these are a different surface than the proposed NOD Claude Code permission flow. No independent penetration/security tests were executed.

## Lens 1 — Product and positioning
Problem: AI tools are powerful but fragmented and demand screen attention. NOD offers deliberately physical one-step access and approvals.
Current README overextends into XP, ranks, reminders, media/PC macros, unlimited assistant, action packs and bespoke metal hardware. Narrow Kickstarter MVP to 3 core journeys: ASK, CAPTURE and APPROVE (with at least 1 verified end-to-end prototype). For strongest differentiation, demonstrate an agent proposing an operation and a user affirmatively accepting/denying from a device, with safe terminal fallback.
Audience: developer/maker/founder who ALREADY runs an AI workflow on a PC; avoid promising universal consumer plug-and-play until validated.
Success measures: first-task time, end-to-end task success, response latency, setup completion, retained daily usage, support incidents.

## Lens 2 — Technical feasibility
Available Cardputer ADV: ESP32-S3, 8 MB flash, 240×135 display, 56-key keyboard, mic, speaker, 1750mAh battery, Wi-Fi, BLE. AI inference and complex work happen on paired PC/cloud; avoid implying offline full inference on device.
Integration path: device ⇄ private authenticated network ⇄ Windows PC hub ⇄ configured AI and agent tools. Questions to settle: polling backoff, disconnection and heartbeat, per-device tokens/rotation, event signing, time drift, duplicate event handling, prompt queue, timeout races, ambiguous partial results, resume after OTA.
Evidence gaps: compile independent NOD firmware; record deterministic integration test harness; physical latency/mic/voice tests, power/heat measurements, mobility path via phone hotspot or VPN, fallback while hub is offline.
Definition of done for demos: uncut device+PC screen video, logs and hashes bound to the demonstrated firmware and hub versions, 100 repeat trials with failures categorised.

## Lens 3 — Security, safety and privacy
Never use ambiguous YES for a high-impact action: display exact tool, target, scope, expiration and source agent; on 240x135 screen use short summary and details accessible from trusted companion UI; if details cannot fit, require phone/PC review. Explicitly deny on stale prompt, timeout, disconnect, replay, duplicate ID, wrong session, unpaired client or user abort. Binding approval to the exact original request and single-use token is mandatory. Never auto-approve on reconnect.
MAZ Pocket phone grant code is promising separate evidence, not proof NOD approval is secure. Have threat model for pairing, local LAN adversary, rogue device, token exfiltration, forged hook, external Internet. Protect API route (do not expose raw hub publicly), encrypted transport where feasible, diagnostics that omit sensitive prompts by default, revocation and emergency stop.
Privacy: clear local-vs-cloud distinction, consent for optional external models, audio retention defaults, collection/data use transparency and delete workflow.

## Lens 4 — UX, accessibility, user onboarding
On-screen states: waiting, listening, thinking, reply, approval, timeout, offline, reconnection. Distinguish color with shape/text; button labels consistent; no impossible miniature walls of text; strong battery/offline indicator. Unambiguous physical affordance over gamification. Build 5-person outsider usability benchmark on Windows and Android hotspot. Provide visual step-by-step onboarding plus repair path, firmware rollback and working documentation. Browser site accessible at 320px+, reduced-motion support and no unverified device renders.

## Lens 5 — Hardware, supply and business
Decision needed: Cardputer-based Founders Kit (fastest possible, transparently third-party board) vs genuinely custom consumer device (higher design, enclosure, PCB, assembly, certification, QA, tooling/returns expense). Do not imply a CNC shell already exists. Request 2 independent written supplier quotes, MOQ, tooling and production sample lead time, batch yield, battery safety, label and test obligations, WEEE producer duties.
Per unit budget: BOM + sourcing + PCB/assembly + casing + QA/burn-in + packing + domestic/international fulfilment + duties/VAT + Kickstarter/platform/payment fees + failures/replacements + support + contingency. Compute prices only after quotes. Test breakeven vs 100/250/500 units and overrun scenarios. Do not promise free lifetime external model inference.
Campaign rewards should be something genuinely distinct/new designed by project, not simply resale of an off-the-shelf board. Seek counsel/check Kickstarter hardware/design criteria.

## Lens 6 — Crowdfunding and communication
Kickstarter rules require real honest demonstration of prototype state and software/hardware integration and no CGI to simulate as-yet-nonexistent functions. Record real prototype and disclose PC dependency. Avoid promises of feature breadth/ship date or fabricated endorsements. Do not use imagery of a fictional final enclosure as if already manufactured. The site mock device is labelled 'interface illustration — not product photo'.
Earn waitlist interest via honest progress, uncut demos, maker developer forums and opt-in updates; track real verified signups (no invented count). Prototype project story: frustration → physical control → real task demonstration → limitations → roadmap → backer reward → fulfilment → risks. Never add a Kickstarter countdown unless date confirmed. Update Kickstarter prelaunch link only once it exists.

## Seven go/no-go launch gates
1. Three workflows shown on actual Cardputer ADV, reproducible and documented.
2. At least 100 approval-loop trials, ≥95% full completion target and ZERO unapproved executions; timeout/fallback/security verified.
3. At least five external first-time user setup tests, with recorded friction and repair.
4. Selected product form and two written supplier quotes with realistic MOQ, QA/lead times.
5. Shipping scope and product compliance risk reviewed (radio/EMC/battery, UKCA/CE as applicable, WEEE) with costs.
6. Unit economics built from supplier/fulfilment figures including taxes/fees/reserves; funding goal sufficient for realistic delivery.
7. Honest uncut hardware video and meaningful opt-in early audience. Verify Kickstarter rules before publishing rewards.

## Priority programme (not guaranteed calendar)
P0 this week: protect narrow narrative; merge/retest only relevant code from MAZ Pocket PRs after review; verify hook and session-ID binding; log tests on real hardware; capture video.
P1 next: external setup and voice tests; build exact-cost prototype BOM; two supplier calls; UK product regulation checklist; decide Founders Kit vs custom.
P2 then: opt-in launch audience, Kickstarter story/assets, reliable fulfilment model, backer support/cancellation/refund communications, campaign review.
Do not launch funding before gates pass. Kickstarter November target may have to move; prefer an honest pre-launch page meanwhile.

## Site delivery
Site source is in /site, deploy rootDirectory site to separate Vercel project. Plain HTML/CSS/JS means zero JavaScript build dependencies and portable text/sections to Kickstarter editor. /readiness is a noindex, publicly accessible founder audit (not an authenticated dashboard). Main CTA mailto is honest and usable but not a true email-subscribed waitlist; replace with double-opt-in system once chosen and tested. Site intentionally does not mention price, live orders, production date, fictional testimonials, or fabricated device photo.
