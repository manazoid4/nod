# CLAUDE BATCH 2 — NOD Physical Design, Brag Video, Consumer Validation + Kickstarter
Date: 2026-11-06
Status: EXECUTION PROMPT, NOT A CLAIM OF COMPLETED WORK
Prerequisite: [CLAUDE-BATCH-1-CONSUMER-MVP.md](CLAUDE-BATCH-1-CONSUMER-MVP.md)

## Mission
You are Claude, orchestrator and creative/commercial lead. Turn **verified** Nod consumer MVPs into a convincing, honest product demonstration and a funding-ready hardware business. Target **ordinary people**, not engineers. Aim for maximum economically sustainable revenue and mainstream appeal, **not a headline crowdfunding number without viable fulfilment**. Nod is the simple physical button that makes useful computer tasks easier and can reduce dependence on optional paid services through genuinely local/free workflows.

This is BATCH 2. **Read and verify the exact Batch 1 handoff** before any marketing claim. Do not assume untested features shipped. Maintain the public Nod repo, companion MAZ Pocket repo, and appropriate private unified-memory record; verify current heads and owner permissions. Retain security, approval and device-test gates.

## Competitive inspiration — not a template to clone
Study Kode Dot's Kickstarter (https://www.kickstarter.com/projects/kode/kode-dot-the-all-in-one-pocket-size-maker-device), product, price/reward tiers, campaign narrative, launches, community comments, execution risk and lessons. It had 16,193 backers and $3,366,566 pledged (public project figures). Its maker audience/hardware feature breadth is NOT our target and its result is not a forecast. Study other normal-user consumer Kickstarter successes/failures, especially simple home technology and no-subscription hardware. Document customer demand and why "why not phone?" has an answer. Do not copy creative assets, trademark, rewards or marketing claims.

## Product hook and consumer validation
Create a five-second explanation, e.g., "Press Nod. Your laptop does the useful thing — with no fiddly apps and no mandatory Nod subscription." Test understanding with ordinary users, not developers. A physical SUBTITLES button (supported video on laptop connected to TV; existing file captions or locally generated SRT) is the lead demo **if Batch 1 proves it**. Other verified demo choices: one-touch TV routine; "save this thought"; safe file tidy. Demonstrate supported media only; no DRM bypass or suggestion that it works on all streaming apps. Product must be usable with friendly click/drop onboarding and 1–3 big physical choices.

Validate genuine willingness-to-pay with an opt-in waitlist and buyer interviews. Measure conversion, actual comments/interest and 5 first-time setup experiences; never fabricate audience or imply pledges/reservations that do not exist. Tests should include: "Would you buy at £X? Why? What would stop you? What can your phone already do?" Avoid too many features.

## Physical prototype: use the owner's 3D printer first
Evaluate three specific configurations with honest trade-offs:
A) **Cardputer ADV + purpose-designed 3D-printed Nod enclosure/clip shell**, reversible, easy access to keys, microphone, speaker, power, USB, battery, LEDs, SD and thermal vents. Use real measurements or manufacturer CAD; **never invent fit dimensions**. Prefer printed case/skin as cheapest functional founder prototype. Produce parametric OpenSCAD/FreeCAD or other editable model + STL + print profile + photo/assembly guide + print/fit revisions. Observe print material heat and battery/charging safety. Never compromise vents, buttons or battery for aesthetics.
B) **Cardputer-based founder's kit**, transparent third-party core, Nod designed casing/software/experience; check existing manufacturer marks, reselling rights, Kickstarter new-unique reward requirements, and UK product rules.
C) **fully custom Nod hardware** after validation, not before: design-for-manufacture estimates, screen/button/haptics/battery choices, BOM, tooling, certification, manufacturing/QA, returns and MOQ.
Prototype, photograph and validate Option A first unless evidence makes it infeasible. Evaluate options B and C as later reward/scale paths. Do not publicly promise exact custom formfactor or shipment dates without costing and supplier proof. Clear separations: prototype, envisioned industrial design, manufactured final product.

## Record real clips -> Brag launch video
Ask the user via Hermes Telegram for **3–6 genuine 10-second recordings** (plus any necessary uncut full demo), shot on Pixel/phone of actual Cardputer display, actual TV/laptop action and responsive physical interaction. Provide tailored shot list: (1) pain/hook (laptop+TV missing captions), (2) physical SUBTITLES tap, (3) real result visible on TV with device in frame, (4) one-touch routine, (5) voice capture or other verified benefit, (6) 3D-printed Nod enclosure. Ensure privacy: hide desktops, API tokens, IP addresses, emails, personal files and copyrighted film shots not licensed for public use; use owned/test video content.

Inspect https://github.com/latent-spaces/brag and install current skill in appropriate available agent environment if dependencies/rights permit. Its recent workflows include /brag and /brag-slim; classic /brag uses Hyperframes; /brag-slim may be preferable with Opus 5.5. Check current README and runtime prerequisites (Node 22+, ffmpeg, Hyperframes if used). **Do not imply the tool natively ingests hardware footage without verifying**: adapt via consented, local clip-preprocessing and explicit media inclusion, or compose directly with FFmpeg if easier. Do not spend on video/cloud providers without approval. Real footage is the factual layer; graphics only augment tested functions, not invent capabilities.

Deliver:
- honest uncut 30–60s functionality proof plus 15–25s polished Brag teaser;
- landscape, vertical 9:16, square versions if feasible;
- storyboards, source clips, title/captions, thumbnail, music licensing and share copy;
- accessible subtitle track/captions for promotional video;
- render checks, links to files, and source provenance. Every feature in footage must have Batch 1 physical test receipt. Synthetic UI/renders must be clearly labelled concepts and cannot show nonexistent functionality.

## Consumer-first prelaunch marketing
Develop Nod's landing page and campaign story (not a catalogue of specs):
Pain: modern screens, subscriptions and repetitive clicks -> Solution: a simple physical shortcut -> Three actual examples -> Safety/limits -> No mandatory Nod subscription for supported local flows -> Setup requirements (PC/laptop, HDMI-TV example, local CPU capability) -> Who it's for -> Honest roadmap -> waitlist CTA.
Use the existing nod/site source and update it, never fabricate social proof. Test opt-in signup end-to-end, privacy, unsubscribe, mobile usability and analytics. Prepare 5 organic LinkedIn posts in established Maz Works style, 2 concise carousels, one maker/process post showing 3D printing, one before/after demo, plus short-form video descriptions. Include TikTok/Reels/YouTube Shorts draft material but do **not post, DM, buy ads or create a public campaign without express approval**. Avoid unnatural hype, invented performance/savings, or misleading claims of subscription replacement.

## Revenue economics, Kickstarter readiness and sourcing
Make truthful funding projections at multiple **hypothetical** units/price/return/conversion scenarios without pretending they are evidence. Research actual competing prices and survey willingness-to-pay. Require two written supplier quotes, reliable sourcing, MOQ, assembly/burn-in/QA, returns, customs/tax/VAT, payment platform fees, shipping zones and reserves. Model 100/250/500/1,000 unit cases, show profitable and loss-making cases. Owner already has a 3D printer; account for filament, failed prints, postprocessing, operator time, mechanical stress and production throughput. Don't assume a home printer can produce thousands of retail units.

Check current Kickstarter Rules (https://www.kickstarter.com/rules), UK fees (https://www.kickstarter.com/help/fees?country=GB), UK radio/electrical/EMC/battery/consumer-product/WEEE responsibilities (https://www.gov.uk/guidance/placing-ukca-or-ce-marked-products-on-the-market-in-great-britain). Assess the legal distinction between kits, assembled third-party Cardputer hardware, own-branded device and a fully custom product; existing CE/UKCA on a component may not automatically cover the final modified marketed product. Consider DFM, safety, support/refunds, supplier failure, shipping delay, supply-chain dependence and FX. Avoid unsupported legal certification promises; identify when specialist assessment is needed.

**Launch gate (non-negotiable, inherited from nod audit):**
1. 3 hardware workflows demonstrated on actual Cardputer with records.
2. 100 approval-loop attempts, >=95% end-to-end success and **zero unapproved executions** (after security fixes).
3. 5 fresh ordinary-user setup sessions.
4. product form selected and 2 written supplier quotes.
5. applicable compliance risks and costs assessed.
6. credible unit economics, shipping, taxes, support and funding goal.
7. uncut real working-prototype footage, meaningful opt-in audience and honest Kickstarter content.
If not complete, build a **prelaunch audience and draft**, NOT a live funding campaign.

## Deliverables
- Consumer positioning and validated 3-feature pitch.
- 3D-printable measured case/enclosure model and fit/assembly test with genuine photos once printed by the user.
- Private clip intake and footage ledger; Brag rendered teaser and full uncut demo when clips exist.
- Tested opt-in prelaunch website plus marketing assets and an approval-only publication queue.
- Source-linked Kickstarter draft, FAQ, risks, reward structure and factory/founder-kit comparison.
- Full manufacturing economics worksheet and 7-gate readiness score.
- Private source-of-truth memory note and public updates only backed by proof.
- Exact commit SHA(s), versioned demo files, failed tests, remaining budget and next request to owner.

## Orchestration & spend
Claude orchestrates. Dispatch bounded tasks to verified free OpenRouter models first; account may qualify for up to 1,000 combined free :free requests/day (20/min), verify authenticated limits. Use existing local hardware/PC/GitHub capabilities. **Paid OpenRouter inference shared with Batch 1 is capped at $5 total** (not $5 each). Avoid paid video/cloud render tools unless explicitly approved. Keep ledger and don't silently spend. Use strong model only for hard quality reviews and storytelling refinement. Don't assume Claude Code subscription entitles API access.

Communicate with user through existing authorised Hermes Telegram bot, one actionable question/request at a time. Ask for physically printing/checking shell, performing tests or sending short clips only when needed. Never fake tests, clips, costs, waitlist metrics or grant approval.

**Finish with an honest handover:** what was built and filmed, the best consumer hook, manufacturing path, calculated costs/risk, verified waitlist interest, state of all seven launch gates and a concrete next user action. The objective is a credible consumer hardware venture that can scale if backers actually want it; raising substantial funds is a possibility, not a promise.
