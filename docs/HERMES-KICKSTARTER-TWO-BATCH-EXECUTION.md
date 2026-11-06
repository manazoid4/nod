> **SUPERSEDED — DO NOT EXECUTE.** This is a historical $5/Hermes strategy. The latest owner instructions (6 November 2026) use a $10 total paid OpenRouter budget, Claude as thin orchestrator with free Groq/NVIDIA/OpenRouter/local workers, **no Hermes/Telegram test loop**, existing MAZ Pocket features preserved, a Cardputer ADV + 3D-printed shell (no custom PCB), and consumer-focused Kickstarter prelaunch. **Use [the canonical updated master prompt](CLAUDE-NOD-10USD-MASTER-EXECUTION.md), plus [Batch 1](CLAUDE-BATCH-1-CONSUMER-MVP.md) and [Batch 2](CLAUDE-BATCH-2-LAUNCH.md), instead.**

---

# NOD — Hermes interactive prototype and Kickstarter launch programme
**Owner direction: 6 November 2026.** Two separately copyable Claude execution batches. This is an execution mandate, not proof of completed work.

## Sources of truth and confirmed boundaries
- Product/story and truthful prelaunch site: https://github.com/manazoid4/nod — read README, docs/PLAN.md, docs/ROADMAP.md, docs/PHYSICAL-TEST-RUNBOOK.md, docs/audits/NOD-KICKSTARTER-2026-10-09.md and site/README.md.
- Existing firmware and Windows Core: https://github.com/manazoid4/maz-pocket — inspect main, deploy/local, current commits, branches, PRs, tests, releases, and local installation before reusing anything. Public nod currently has a draft firmware only, not an independently proven flashable product.
- Agent control and cross-agent state: existing Hermes runtime and private https://github.com/manazoid4/unified-memory-database; read only relevant status and operating policies, preserve unrelated agents.
- Inspiration, not material to copy: https://www.kickstarter.com/projects/kode/kode-dot-the-all-in-one-pocket-size-maker-device — Kode Dot raised $3,366,566 from 16,193 backers (historical campaign result). Study messaging, price architecture and risks, never imply NOD will replicate this.
- Short project video tool: https://github.com/latent-spaces/brag . Read current README and skill. It is an agent skill for shareable launch video composition (Hyperframes; brag-slim path can compose directly), **not** proof it can automatically turn raw phone footage into a photorealistic hardware demo. Incorporate user-recorded real clips explicitly or use an FFmpeg/Remotion fallback; check runtime and costs.
- Official Kickstarter rules: https://www.kickstarter.com/rules ; UK fees: https://www.kickstarter.com/help/fees?country=GB . Existing hardware audit contains regulatory references.

## BATCH 1 — Claude: build Hermes ↔ Cardputer interactive field-test loop

You are the lead NOD engineering orchestrator. **Execute code and tests, not another planning document.** Allocate isolated bounded analysis to inexpensive OpenRouter agents; use your strongest available coding/review model only when complexity warrants. Do not burn paid inference on tools or trivial edits.

### Objective
Make Hermes communicate with me through my existing **Telegram** on my phone, and guide interactive tests using my **real M5Stack Cardputer ADV**. End with at least one photographed/recorded, repeatable, end-to-end NOD capability and a durable session handoff suitable for a second Claude session. Do not present simulated results as physical tests.

### Invariant rules
1. Read repo rules and unified memory first. Audit the actual latest NOD/MAZ Pocket code, runtime, branches, open PRs and test artifacts. Reuse MAZ Pocket/MAZ Core, do not start a second competing firmware stack. NOD is the customer-facing product; MAZ Pocket is implementation heritage. Document any code-sharing, vendoring or migration decision before acting.
2. Do not disrupt the already-running Hermes Job Hunter, Telegram polling, schedules, existing bot identity or other production agents. Avoid a second Telegram poller against the same token; integrate by the existing dispatcher or a safely isolated queue/command namespace.
3. Telegram must be **two-way and reliable**. At minimum: /nod status, /nod start, /nod next, /nod result, /nod stop; compact inline **READY**, **PASS**, **FAIL**, **RETRY**, **SKIP**, **SEND VIDEO**, **STOP** controls where supported. Verify Telegram user/chat allowlist, signed or unguessable session IDs, idempotent callbacks, persistent queue/checkpoint, restart recovery and timeout notifications. Private media uploads go into a local redacted evidence directory, not a public Git repo; preserve capture timestamps, linked test IDs, hashes, firmware and host commits. No secret tokens or user location in reports.
4. A Telegram PASS means **user-reported** until backed by the promised evidence; a passing unit test means **SIMULATED** until hardware tested. Mark PASS/FAIL/NOT TESTED/BLOCKED and provenance separately.
5. No automatic real privileged execution. Any agent approval must show exact source, command/scope/target, expiry and session binding through trusted UI; device and Telegram may notify, but never constitute blanket consent. Deny on stale/replayed/expired/offline/mismatched requests; single-use acknowledgement and terminal/phone fallback are required. Fix and independently test outstanding N-1 expiry and N-2 offline-current status defects before authorising live commands. Until then, test approvals DENY-ONLY using harmless synthetic fixtures.
6. Avoid over-the-air or direct flashes until the existing physical version, correct device variant, partition map, recovery and SHA-256 are checked. An **app-only M5Launcher .bin must NEVER be flashed to address 0x0**, mass-erased, or treated like a factory image. Verify app slot bounds and use the existing VERIFY+STAGE→M5Launcher flow, with user's explicit physical confirmation. Stop on uncertain partition or device identity.
7. Device stays behind a local private network or Tailscale. No public unauthenticated hub, command interpreter or raw local credentials. Use separate consent for audio/video capture, avoid exposing account names or private messages in clips.
8. User has a physical 3D printer, but CAD/printing is Batch 2; do not stall firmware testing for enclosure design.

### Build tasks
A. Create a small evidence-driven baseline report: actual Cardputer ADV firmware/version/slot unknown until observed; Core/firmware latest installed vs latest repo commit, host connectivity, microphone/speaker, keyboard, screen, Tailscale/LAN, M5Launcher recovery, dependency compatibility, open PRs and security blockers. Review the physical test runbook first.
B. Implement a safe NOD testing flow in Hermes, with durable test state and human-facing Telegram prompts. Notify me when a step needs a physical action. Example: “NOD TEST 02 — Open CALL, hold SPACE, say ‘what time is it?’, release. Did text appear and did sound play? [PASS] [FAIL] [VIDEO]”. When FAIL, request one short observation/log/photo and diagnose; repair, rebuild, then repeat the failed step. Each action should be simple enough to perform from a phone.
C. Select **three core product journeys:** (1) ASK: push-to-talk request, visible and spoken response using the paired PC/cloud; (2) CAPTURE: voice note becomes a persistent item, including honest offline/failure handling; (3) APPROVE: a safe synthetic request appears on the actual device, deny/time-out/terminal fallback verified, then guarded live approvals only after all security fixes and authorisation checks. All PC/cloud dependencies must be stated.
D. Build deterministic host and firmware tests (including failure cases) and preserve logs; test reconnects, device offline, repeated callbacks, expiry and replay. Use physical tests to verify real mic, speaker, display, buttons, latency and battery behaviour. For the approval journey, eventually run 100 recorded loop trials with target ≥95% completed and zero unapproved execution; until proven label it a launch gate.
E. Build a simple /nod progress command and short digest: tested features, next user action, bugs, costs, build hashes and current blocker. Allow /nod stop and state resumption without losing prior evidence. Notify only actionable milestones; avoid constant chat spam.
F. Capture my **10-second physical phone clips** via Telegram uploads or clearly specified local import folder. Link each clip to an actual test, store original untouched privately, optionally create redacted/public-safe cutouts separately. Never pass raw sensitive footage to cloud providers without my explicit approval.
G. Update NOD's truthful docs/status and unified-memory project state. Do not mark readme marketing promises as shipped without physical evidence. Commit source/test changes safely, report actual tests and an exact next-session handoff.

### Model budget
A separate **maximum $5 paid OpenRouter inference pool** applies to this NOD project and both batches combined, not $5 each. Check the authenticated rate limits/balance and current model IDs; as the account has bought at least $10 historically, the free-model daily allowance may be up to 1,000 requests/day, subject to actual account checks, provider caps and 20 RPM. Free/local models first for structured extraction, small code, tests, competitors and drafts. Strong paid models only for security-critical reviews or demonstrable improvements. Track actual model, task, input/output tokens and billed cost. Fail closed near the budget ceiling. No Claude subscription/API assumption if CLI credentials aren't working. Do not automatically install costly dependencies.

### Batch 1 completion criteria
- A working and verified Telegram ↔ Hermes guided test session, with start/stop/resume and a first real device check.
- At least one useful real Cardputer flow evidenced, or an exact reproducible blocker and the work completed toward it.
- N-1/N-2 resolved with evidence before any positive approval of real commands.
- Persistent private test evidence, build/commit references, cost ledger and concise machine-readable handoff.
- A short Telegram report: “NOD READY / TESTING / BLOCKED; what worked; please do [one physical action]”.

**STOP after Batch 1 deliverables. Do not start Kickstarter publication or claim production readiness.**

---

## BATCH 2 — Claude: distinctive 3D-printed NOD, authentic launch films and Kickstarter prelaunch
**Input:** Load Batch 1's saved handoff, tests and evidence; do not re-research or reimplement its completed work. If Batch 1 isn't complete, build only independent CAD, content and economic artefacts and explicitly gate any demo/claims.

You are the lead NOD hardware-product and launch orchestrator. **Build working prototypes and publish only approved, truthful prelaunch material.** The ambition is a high-upside crowdfunding business, but size the goal by validated demand and fulfilment costs, not the Kode Dot funding headline.

### Product promise and positioning
NOD is a distraction-free pocket interface to the user's own AI/PC agents — *ask, capture, approve*. It is NOT a standalone massive AI model or a universal replacement for phones. Distinguish it from Cardputer/MAZ Pocket and competing mini AI devices through proven workflows, onboarding, craftsmanship and trustworthy human approvals. Research real developer/maker pain points, competitors, pricing and IP/trademark issues; don't copy Kode Dot's assets or make implied affiliation claims.

### Physical product fork: compare three paths honestly
**Option A:** Commercial NOD software/firmware for user-owned M5Stack Cardputer ADV, plus open-source builds/support.
**Option B:** A genuinely designed 3D-printed NOD enclosure/add-on kit around an off-the-shelf Cardputer ADV, possibly with assembled hardware after supply/legal feasibility. This is the preferred **prototype experiment**, not a guaranteed commercial tier.
**Option C:** Fully custom PCB, industrial design and housing after validation, with hardware engineering, assembly, test, certification, rework, MOQ, shipping and warranty budgeting.

Compare ergonomics, dimensions, M5Stack attribution, brand/licence, batteries/charging, button and port access, antenna/radio performance, mic/speaker openings, thermal clearance, ventilation, safety and manufacturability. Do not imply a cosmetic shell turns an existing board into original hardware IP. Kickstarter requires unique, creator-designed rewards — verify which options qualify before setting tiers.

### 3D printer and CAD work
Find my printer model, build volume, nozzle/materials and CAD tool in available local project context, or ask through a single Telegram choice only when genuinely required. **Design and deliver a printable physical NOD enclosure** fitted to measured, verified ADV geometry, not a guessed scale. Research manufacturer CAD structure files where permitted. Provide at least:
- Version 1: low-part-count snap-on sleeve for fastest real test.
- Version 2: distinctive ergonomic NOD shell with readable display, usable keyboard, device charging, speaker/mic and safe heat/antenna clearance.
- Version 3: optional concept for custom hardware (clearly future/not functional).
Deliver parametric source (FreeCAD/OpenSCAD or practical alternative), STEP if available, STL/3MF, assembly drawings, tolerances, screw details, print orientation/material and exact bill of materials. Check licence/fit. Generate slicer previews; the user prints one physical iteration and sends Telegram photos/short clips; refine after measurements. Do not state printed/tested without photos and owner confirmation. Do not modify built-in lithium batteries or charge wiring casually.

### Turn real 10-second clips into authentic films
As physical capabilities pass, ask for **three to six ~10-second clips** via Telegram:
1. NOD hero shot in hand; show authentic size and physical enclosure.
2. PRESS → SPEAK → response on real screen/speaker.
3. Save a real voice note; show timestamped item on PC.
4. Safe agent request appears on NOD; user explicitly DENIES; then show approved action only if security gates passed.
5. Real CAD→3D printer→fitted shell physical process.
6. Optional realistic unboxing/battery/hotspot field test.

Read and integrate https://github.com/latent-spaces/brag via the documented /brag or /brag-slim skill. Assess if it can incorporate externally imported phone footage; if not, use FFmpeg/Remotion/manual composition to edit authentic clips and use Brag for typography, motion, music and share copy. Video export targets: 9:16 15–25s LinkedIn/Shorts, 16:9 ~30–60s campaign teaser, longer uncut Kickstarter prototype proof. Preserve originals. Add captions, accessible titles, licensed music, consistent NOD aesthetic. **Never use AI video generation, CGI or altered frames to simulate device functions not really shown**; marketing motion graphics must be visually distinct from real product demonstration. Disclose relevant AI use as Kickstarter requires.

### Kickstarter benchmark and launch engineering
Research the Kode Dot campaign as a **comparative case study** (actual $3,366,566 / 16,193 backers): study hook, problem framing, real prototype, features, reward tiers, stretch goal risks, manufacturing status, build quality, community, advertising and fulfilment. Also contrast smaller unsuccessful comparable campaigns to avoid survivor bias. Use current Kickstarter policy and accurate fee references.

Create a complete launch-ready *draft*, not a live fundraising campaign: one-line hook, honest prototype state, features demonstrated vs planned, founder story, short video storyboard, technical specs, comparison chart, risk disclosure, timeline bands, honest AI/tool dependencies, privacy/local-host story, FAQ, captions and press kit. If claiming “open source,” specify licences and what will actually be published. Don't advertise unrestricted free inference or lifetime cloud costs unless independently financed.

### Manufacturing economics and launch gates
Get two independent written sourcing/assembly quotes where feasible. Create GBP scenario spreadsheet/CSV for 100/250/500 units: hardware purchases or components, printer materials, labour, power, tools, QA/rejects, packaging, shipping, duties, VAT/taxes, Kickstarter platform fee **5%**, UK payment processing (currently **3% + £0.30** for standard pledges; verify again), support, returns, spares, contingency and currency volatility. Include production lead times and cash needed before payout. Check whether using M5Stack boards inside a rebranded finished unit is permitted commercially, and UK radio/EMC/safety/battery/WEEE/CE/UKCA obligations; these cannot be waived by putting an existing device in a custom shell. Have explicit manufacturer/responsible-person and fulfilment assumptions.

Campaign cannot proceed without **seven proven gates** from docs/audits/NOD-KICKSTARTER-2026-10-09.md: three real-device workflows; 100 approval trials ≥95% completion and zero unapproved action; five external onboarding trials; decided product form + two quotes; regulation review; positive unit economics and realistic funding target; authentic uncut demo and measurable opt-in audience. If any fail, remain in prelaunch and fix them.

### Marketing and demand validation
Use existing NOD /site as starting point, and verify current deployment before editing. Make a high-quality **truthful prelaunch landing page** with real footage and a proper opt-in waitlist (consent, privacy and verified delivery) when available. Never fake registrations or substitute a mailto CTA for an actual subscriber form.

Review previous Maz Works LinkedIn materials before producing posts; follow existing restrained developer-led aesthetic and **value-first, non-pushy marketing**. Deliver founder build logs, useful “what physical AI control gets right/wrong” comparisons, behind-the-scenes test clips, 3D-print iterations, demo breakdowns, and simple community interest/poll posts. Don't publicise my exact location. No mass unsolicited marketing. Only publish public content with my approval.

Set a transparent conversion funnel: witnessed product demos → interested viewers → verified opt-in waitlist → interested beta testers → permission-based feedback → launch-go/no-go. The amount raised is not known; use sensitivity analysis and don't invent community conversion metrics.

### Batch 2 end state
1. Printed-and-tested prototype if user performed physical prints, otherwise clean ready-to-print CAD with proof status.
2. Edited authentic short film(s), source files and signed-off claims, or ready-to-edit briefs awaiting real clips.
3. Honest NOD site / public demo and content drafts (publish only with owner approval).
4. Kickstarter campaign draft, commercial feasibility spreadsheet/CSV, regulatory/supplier checklist and clear **GO / NO-GO** decision.
5. Unified-memory updates, linked repo commits, private evidence archive index, OpenRouter ledger and daily Telegram summary.

### Operating style, both batches
- Claude acts as orchestrator; Hermes is the durable Telegram field-test coordinator. Cheap/local OpenRouter workers handle bounded tasks, strong agents resolve difficult decisions. Keep one writer per shared repo branch, isolated worktrees for parallel tasks and evidence-based reviews before merges.
- Use A→B→C: Analyse, execute, verify. Avoid circular planning or creating more scaffolds than working outcomes.
- Ask my physical involvement as one step at a time by Telegram, including photo/video upload when needed; don't ask to repeat context already provided.
- Use existing private paths, repo rules and unified memory. Never commit tokens, private video, address, unredacted logs or personally identifying details to public NOD repo.
- No external purchases, paid API use beyond the $5 cap, live Kickstarter pledge/reward activation or public posting without explicit approval. A plan is not a test; a render is not a prototype; a video edit is not proof of a feature.
- Report actual successes and failures, not aspirational status.

**Final objective:** NOD becomes an unmistakably differentiated, working physical AI approval/capture device, demonstrated with my Cardputer and 3D printer, with a trusted Telegram iteration loop and a commercially feasible, evidence-backed Kickstarter path.
