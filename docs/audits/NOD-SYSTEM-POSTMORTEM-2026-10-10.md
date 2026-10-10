# NOD multipass audit and post-mortem — 10 October 2026

**Scope:** NOD landing page, roadmap, Kickstarter readiness, the connected Vercel project `nod-kickstarter`, and the trust-critical MAZ Pocket host/device approval surface on `deploy/local`. This is a source, deployment-metadata and CI review. **No direct physical Cardputer operation or unauthenticated end-to-end browser fetch was possible during this run.** Do not present this as a user test or penetration test.

## Executive finding

The most consequential failure mode was **mistaking successful Git/Vercel publishing for proof that the product works**. The site already carried the saved-video and Reel-to-Print story, but the actual importer, model finder, slicer handoff and hardware acceptance are unimplemented or not physically verified. The homepage did not offer a working subscriber funnel. Meanwhile, the host approval interface permitted persistent broad authority and did not enforce request expiry at the point of approval. The operational risk is greater than the cosmetics.

## Multiperspective review rounds

**Round A — buyer/conversion:** Hero led to a concept explorer rather than a clear audience action; the second CTA implied “Get updates” but was really just an anchor to a mailto link. There is no real waitlist, consent double-opt-in, UTM attribution, marketing measurement or conversion baseline. **Patched:** primary CTA now clearly opens a pre-addressed email; secondary explores concepts; explanatory disclosure and privacy link; no false signup claims. **Still open:** a real consent-backed email capture solution, analytics baseline, actual product demo and observed buyer interviews.

**Round B — UX/accessibility:** Mobile top navigation was hidden, leaving features and roadmap hard to reach; newly generated roadmap uses low-contrast body labels (~3:1), tiny metadata, and 21 items that dilute “what next?”. A simulated handheld screen showed a green READY indicator despite being only a drawing. **Patched:** native no-JavaScript mobile menu across four pages; colour tokens strengthened (key checked combinations around 5.1–7:1); concept renamed; shortcut links to the two differentiators; roadmap now leads with the first priority gate. **Still open:** real-device photography, screen-reader and five-user task tests, 320px / 360px / 390px live browser measurements and actual task-completion times.

**Round C — engineering/release:** A static site used Vercel Git integration but lacked a dedicated regression suite, code-level link verification, meaningful security headers, and discoverability metadata for the roadmap. Earlier publishing relied on “READY” deployment status as sufficient QA. **Patched:** dependency-free Node site tests, GitHub Actions quality gate, CSP/security/permissions headers, verified-route checks, sitemap and canonical metadata. **Still open:** production synthetic browser checks across target screen sizes and an automatically run actual axe/Lighthouse audit; independent external URL loading was blocked in this workspace.

**Round D — threat model:** `maz-pocket/host/mazhost/buddy.py` granted `allow_all` persistently per session; other requests could inherit authority; expired requests stayed in some pending lists and late decisions were accepted. The 240×135 approval UI contained a one-press `A always` shortcut, and action summary truncation limited informed approval. `agent_runner.py` may launch Claude with `--dangerously-skip-permissions`, while a working directory does not sandbox OS file/network access. **Patched and merged in separate PR #81 (not a site change):** default to one-request approvals, refuse session-wide authority, use monotonic deadline checks, reject approvals after expiry, remove the `A` shortcut and add tests. **Still open:** sandboxed agent execution, detailed hardware approval UX, full security review of authority tokens, build flashing and repeated on-device deny/allow tests. Do not treat #81 as an end-to-end approval security certification.

**Round E — content/platform compliance:** Instagram Saved JSON can contain pointers rather than source video bytes. Video analysis requires actual legitimately accessible audio/frames and original-source evidence. Creators' original 3D models may be absent, paid or separately licensed. **Site correctly says proposals**, but a buyer can still overestimate scope. **Patched:** prominent future-only and research links, explicit concept labelling. **Still open:** real permitted-video acquisition, accurate frame/transcript analysis, source-grounded match ranking and confirmation of rights; never guarantee arbitrary saved Reel access.

**Round F — physical printing/product economics:** A Reel-to-Print pipeline must verify creator model licensing, untrusted STL/3MF contents, geometry, slicer profile, filament and G-code before handing anything to a printer. Per OctoPrint's official API docs, uploading, selecting and starting a print are distinct operations; `print=true` can start jobs on upload or select. **Required design:** default to `select=false`, `print=false`; physically present human explicitly starts after final preview. The current website has no printer runtime action. **Still open:** implementation, calibration, on-site Ender 5 proof, hardware BOM, supplier quotes, legal/compliance and fulfilment evidence.

**Independent adversarial reviewer pass:** Caught that a new privacy page initially used inline style attributes incompatible with the proposed strict CSP; replaced inline attributes with a stylesheet before merging. Also caught that an approved action polled *after* its deadline could still be consumed if approval had occurred earlier; PR #81 now returns a non-authorising expired response in that case and tests it. These are source-based reviewer findings, not evidence from separate spawned AI process identities.

## Findings register (severity, outcome)

| ID | Severity | Problem | State |
|---|---|---|---|
| F01 | Critical | Session-wide and late approvals | PR #81 MERGED into `deploy/local`, nod CI green; installed PC and Cardputer not physically updated/verified |
| F02 | Critical | Unconfined agent execution with permissions bypass | PR #82 MERGED to `deploy/local` with green CI; PROJECT FULL unattended work blocked, genuine OS sandbox still OPEN |
| F03 | High | Approval summary clips detail on 240×135 display | OPEN — design review + firmware hardware acceptance |
| F04 | High | Mock READY display suggests a connected product | FIXED on site branch |
| F05 | High | Mobile page navigation disappears | FIXED on site branch |
| F06 | High | Prelaunch funnel actually mailto, not opt-in signups | PARTIAL — accurately labelled only |
| F07 | High | Reel video import/access and visual understanding absent | OPEN, no shipping claims |
| F08 | High | Reel-to-Print discovery and slice integration absent | OPEN, print must require explicit physical start |
| F09 | Medium | No automated site regression tests | FIXED in new Node tests/CI |
| F10 | Medium | No site-level Content Security Policy | FIXED with Vercel header config |
| F11 | Medium | Small low-contrast text in roadmap and concept art | PARTIAL — improved key tokens, manual audit open |
| F12 | Medium | No clear public privacy notice | FIXED new /privacy/ |
| F13 | Medium | Roadmap overwhelms new visitors and buries first priorities | PARTIAL — stage filter retained, primary CTA reprioritised |
| F14 | Medium | Missing public SEO discovery/canonical on roadmap | FIXED sitemap, canonical, robots |
| F15 | High | No real hardware footage / supplier costing / product reward definition | OPEN — crowdfunding gate |
| F16 | Medium | Duplicate product truth across NOD site/MAZ Pocket/unified memory | OPEN — proof ledger and ownership needed |
| F17 | Medium | No end-to-end external visitor/browser verification | OPEN — Vercel READY does not prove browser accessibility |
| F18 | Medium | Unmeasured voice speed, value and new-user setup success | OPEN — 5-user trial / real timing benchmark |
| F19 | High | Competes with established Cardputer product; no independently demonstrated new hardware value proposition | OPEN — buyer studies, real task differentiation and distinct reward required |

## Root cause and 5-whys

1. **Why did the user ask for another audit after “all pushed”?** The release was announced as done although the product itself had never been physically demonstrated.
2. **Why did that happen?** GitHub merged PR and Vercel READY were the release acceptance gate instead of buyer and hardware acceptance.
3. **Why no stronger gate?** No repeatable test suite or single proof-led feature/status ledger covered site and firmware/host end to end.
4. **Why was the roadmap not enough?** Twenty-one commitments represented planning breadth, not tested outcomes or active ownership.
5. **Why is this commercially risky?** A beautifully presented concept can attract interest while setting promises the prototype and manufacturing plan cannot yet fulfil.

## Market and competitive review (external-source pass, 10 October)

**Comparison baseline:** M5Stack's CardputerZero maker-computer campaign concluded 3 July 2026 with 13,644 backers and approximately HK$ 14.96m pledged (https://www.kickstarter.com/projects/m5stack/cardputerzero). This proves that maker-sized computing can attract backers, **not** that an NOD-branded Cardputer or thin AI wrapper is a new/viable product. Their product comes from the original hardware maker; NOD's current real device is a third-party M5Stack Cardputer ADV with connected-PC dependency. Claiming original NOD-designed hardware would be misleading without a distinct real prototype and design/production rights.

**Failure precedent:** A 2024 independent Rabbit R1 review criticized limited useful integrations at launch, unreliable basic responses, privacy concerns and having to return to a phone to finish tasks (https://www.wired.com/review/rabbit-r1/). NOD must avoid an impressive concept funnel around non-working workflows, and demonstrate one useful, repeatable loop before fundraising.

**Applicable campaign constraints:** Kickstarter requires original/new reward output, rights to used materials, honest non-simulated hardware/software integration, and disclosure of AI content/data sources/consent and credit. See https://www.kickstarter.com/rules and https://updates.kickstarter.com/kickstarter-project-guidelines-for-ai-generated-content-and-ai-technology/ . Do not treat licences for *viewing* Instagram content as licences to redistribute its video or creator-linked 3D designs.

**Commercial action:** Test whether prospective backers prefer (A) original NOD companion software and hardware integration kit, (B) genuinely original NOD hardware, or (C) simply a phone/PC app. Ask 10 potential customers to complete a real task and compare against phone usage; request actual waitlist opt-in and target price willingness only after a live prototype. Differentiate with `saved video → source-backed answer → approved tangible result`, not generic AI voice. No invented conversion figures, revenue projections or presale date.

## Guardrails and next execution batch

- **Release gate A (site):** Node static suite green in GitHub Actions; Vercel linked production SHA READY; external browser/mobile/keyboard smoke tests; no false signup/working feature/connected-device claims.
- **Release gate B (device):** fix all broad or expired authorisations, stop unrestricted execution, then physically reproduce ASK/CAPTURE/one-time DENY+ALLOW and a safe, legible permission prompt. Never auto-accept sensitive actions or shifts.
- **Release gate C (video):** 10 real authorised videos processed with audio and visual evidence; unavailable media marked LINK ONLY/NOT WATCHED.
- **Release gate D (print):** real creator-linked model → licence/geometry validated → actual profile slice → reviewed OctoPrint upload with no auto-print → supervised owner start.
- **Release gate E (Kickstarter):** hardware prototype documentation, verified demonstration footage, materials rights, supplier/BOM/compliance/shipping, fees and return contingencies, tested opt-in funnel.

## Accountability and limitations

- No separate external AI subagents were spawned by this chat environment; six independent **audit perspectives** and an adversarial **reviewer pass** were performed, with a parallel GitHub CI test gate. Do not misrepresent that as six autonomous agents or live penetration tests.
- Site and MAZ Pocket are separate repositories. The website deploy does not ship or install changes on the connected Windows computer or handheld.
- Vercel production deployment status, source metadata and routing do not by themselves prove the end user can load the site anonymously.
- This document is the release post-mortem and a handoff to the next agent; every stated FIXED item is subject to PR merge/CI/production confirmation and should be updated as results arrive.

**Evidence:** GitHub `manazoid4/nod` PR #8 (prior production update); this site-hardening PR; `manazoid4/maz-pocket` PR #81; OctoPrint API file and job operations documentation; Unified Memory 21-deliverable NOD audit.

## Verified release addendum (10 October)
- `manazoid4/nod` site hardening PR #9 merged at `9df6028133f510765afc2957fb6cd6fc65dfd844`. New `NOD Site Quality` GitHub Actions run 38050035925: **8/8 static tests passed**. Vercel production deployment `dpl_4Ye8xMmbPQSMzVTm9HbiRr6xSVxf` READY for the exact merge commit; project SSO is set to preview-only. Public anonymous browser fetch was unavailable to this audit.
- `manazoid4/maz-pocket` approval fix PR #81 merged at `f6957a887a6334afaadf18d0c3b460c5be44fd31`. nod CI run 38049932894 passed host tests and firmware build. No actual Windows Core restart or Cardputer flash is implied.
- Agent-runner isolation mitigation PR #82 undergoing CI after a test harness API-name correction (not yet installed). Distinguish this mitigation from a future properly sandboxed project runner.
- Release verdict: **web content and infrastructure improved; product feature and crowdfunding readiness NOT CLEARED**. Outstanding physical tests, true opt-in signup, video-content acquisition and 3D print proof remain blocking.

### Second security mitigation verified
- `maz-pocket` PR #82 merged at `9eb4e1dc22ccf4b3a293aac016aa3c7ff36615cf` after its initial CI failure (test called nonexistent `start_job` API) was caught, corrected to `start`, and the full nod CI run 38050348566 passed. For now PROJECT FULL coding-agent jobs fail closed rather than run unconfined. This intentionally removes part of unattended agent functionality until a real sandbox can be built. Avoid promising otherwise. Explicit PC FULL is separately authorised, and the provider permission bypass is no longer added to Claude's argv.
- Market/evidence follow-up site PR #11 merged at `ef2f0ea7f3f202b25493a323055923e3ed7acd08`, site quality tests passed, Vercel production `dpl_9vHbZbGxohGoFx9yhEyVDsY54meF` READY for that exact SHA. Readiness page now links this postmortem. Anonymous end-to-end browser smoke remains open.
