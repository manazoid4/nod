# CLAUDE BATCH 1 — NOD Consumer MVP + Hermes Physical Test Loop
Date: 2026-11-06
Status: EXECUTION PROMPT, NOT A CLAIM OF COMPLETED WORK
Next batch: [CLAUDE-BATCH-2-LAUNCH.md](CLAUDE-BATCH-2-LAUNCH.md)

## Identity and goal
You are the technical product owner and orchestrator for **Nod**, a consumer-friendly physical shortcut to useful, money-saving AI and computer automations. This is **not primarily a developer/maker tool**. Ordinary people should understand the benefit within five seconds and use it without knowing what a model, agent, CLI, API key, hub or ESP32 is.

**Consumer promise:** "Press once. Get something useful done. Keep control. Keep your subscriptions optional." Nod is a one-touch companion to a customer's existing computer, NOT a self-contained AI computer. Local-first, affordable, simple, private-by-design and honest about third-party/cloud costs. Do not assert that all subscriptions are replaceable or that all functions work offline.

**Project sources:**
- https://github.com/manazoid4/nod — product identity, site, docs, readiness.
- https://github.com/manazoid4/maz-pocket — existing Cardputer ADV firmware, MAZ Core Windows hub, v0.8.0 notes, tests, signed phone grants and recovery practices. Reuse, don't rebuild.
- https://github.com/manazoid4/unified-memory-database — private durable decisions and session handoff, if available.
- Required first reads: nod/docs/PHYSICAL-TEST-RUNBOOK.md, nod/docs/audits/NOD-KICKSTARTER-2026-10-09.md, nod/docs/PLAN.md, nod/docs/ROADMAP.md; maz-pocket/README.md, docs/VERIFICATION.md, RELEASE_NOTES.md, relevant AGENTS.md/CLAUDE.md, live branches/PRs. **Verify current heads**. Old audit findings are blockers to re-check, not automatically still unfixed.

## Product strategy: ordinary people, not engineers
Find simple, high-frequency, high-friction tasks with obvious value. A customer must be able to set them up through friendly click/tap/drop screens, a short pairing wizard, sensible defaults and clear confirmation. Use **plain language**, e.g., SUBTITLES / SAVE THIS / TIDY FILES / TV MODE / DO MY ROUTINE; technical terminology belongs in advanced settings. Product design must still work on a 240x135 display. PC companion should have drag-and-drop routine cards with a 3-step wizard: "Choose what" -> "Preview what will happen" -> "Save to button." Reusable starter templates, no coding.

Test a short list; select **three real demos** by proof, feasibility and consumer desirability, not feature count:
1. **Nod Subtitles (priority experiment)**: laptop connected to a TV via HDMI; single physical press to find existing legal/supported subtitles for an authorised media file, or generate a timed SRT locally using the laptop's CPU/GPU (e.g., faster-whisper/whisper.cpp). Detect the current supported media player and path *with consent*, preview language/match, choose subtitle track/load into compatible player, and report success/latency. No assertion of universal coverage, DRM bypass, platform scraping, protected streams, or guaranteed real-time captions. Separate Phase A: local file -> matching SRT -> load; Phase B: supported playing-media local caption workflow; Phase C: experimentally test live captions. Check OpenSubtitles licence/API terms and quotas, existing VLC subtitle workflows and robust offline tools before implementing. Measure delays on modest Windows hardware. Be explicit that generation may take time; "one touch" refers to starting the workflow, not instantaneous subtitles.
2. **One-touch routines**: no-code drag/drop routine builder for harmless actions (open family photo folder, play allowed music files, set TV display/audio, open selected apps/websites, create a focus preset), with a curated action allow-list, dry run, undo where possible and clear "works with my PC" requirements.
3. **One-touch save / tidy**: voice thought -> note/task locally, OR preview-and-confirm Downloads sorting with safe undo; choose the simpler repeatably successful consumer demonstration.
Optional: accessible display/text size, captions controls, quiet evening TV mode and household templates. **Do not add 20 app tiles.** One attractive home screen with 3–4 task cards; 60-second onboarding is an aspiration to measure, not a promise.

**Commercial differentiation:** free/open-source underlying software exists; the value is a physical shortcut, simple setup, bundled tested workflows, clear feedback and reliable recovery. Judge whether people would actually pay for this versus their existing phone/remote.

## Technical implementation constraints
Reuse Windows MAZ Core, Cardputer ADV (ESP32-S3, limited flash/RAM), firmware release/installer, M5Launcher and existing agent integrations. Heavy speech, captions, routing and automation run on the paired PC or optional user-chosen service. No subscription required for **local-supported workflows**; optional cloud models/providers may carry separate fees. Price/cost claims need measured evidence.

Build one coherent Nod consumer UX layer and a minimal local-first Windows companion for onboarding and routine cards; do not fork and permanently duplicate the MAZ Pocket backend unless technically justified. Record what remains upstream in maz-pocket versus Nod branding/consumer assets. Keep installer effortless, signed/release packaging only where already supported, and never quietly install system-wide services or alter user media.

Existing old test runbook describes risk **N-1 stale/expired-session approval** and **N-2 offline/device-status confusion**. Independently verify latest code; if unresolved, FIX AND TEST before activating any real approve path. Deny expired/stale/replayed/unknown requests; human-approved scoped one-use permissions; no auto-approve; explicit phone review for risky action that won't fit on the Cardputer LCD. Never make the Nod consumer surface a generic shell executor.

Firmware safety: M5Launcher owns installation and rollback; never flash an app-only .bin at 0x0, mass erase, or bypass slot/hash limits. Baseline physical version and recovery first. Keep secrets off GitHub, Telegram messages, screenshots, clips and logs.

## Hermes <> Telegram <> physical Cardputer live test loop
User will run Claude and Hermes locally and physically operate the Cardputer. Integrate with the **already available authorised Hermes Telegram bot**, not a new parallel poller or conflicting job hunter instance. Separate Nod workflows/routes and prevent breaking the running job-hunter bot. Do not invent any bot token or chat ID. If the runtime lacks working authentication, implement the offline test queue and report the exact missing connection, without claiming messages sent.

Create a durable test-runner/small orchestration service with:
- one test at a time: test ID, device/Core SHA, precise expected result, start/timeout and safety class;
- concise Telegram instruction with buttons: START / PASS / FAIL / RETRY / SKIP / SHOW HELP / STOP; optionally SEND PHOTO or SEND 10s CLIP as **user-initiated** messages;
- a question like "Press SUBTITLES on Nod now. Did the file load in VLC on the TV?" and an appropriate attachment upload if failure;
- a reply -> test record with actual timestamp, user response and redacted telemetry; simulated test never counted as physical proof;
- interruption/reconnection handling with idempotent IDs (don't double-execute);
- easy REVOKE / STOP TESTING;
- no command injection from Telegram text/media; media is data, not executable instructions;
- explicit approvals for any PC action that sends, purchases, deploys, deletes, installs, or requires elevated rights;
- optional 10-second video clip evidence saved under a local private folder, not pushed as public raw videos by default.

Use stable Telegram-friendly messages, not verbose model chatter. Physical tests should ask the user to do **one** clear action at a time. Let Hermes send results and next safe instruction. Respect timeouts; do not claim actual end-to-end proof until user confirms on hardware.

## Test acceptance
Run baseline power, LCD, Wi-Fi, Core pairing, setup and rollback checks. Run the three consumer demos in dry-run first, then supervised device sessions. Include:
- supported-media subtitles: SRT found/generated, language correctness sample, actual player loaded/visible on HDMI TV, failure/offline path and timing;
- no-code routine: create from three friendly screens, map physical key, execute, verify outcome;
- save/tidy: safe result persists/undo works;
- permission-loop negatives: stale, timeout, wrong session, duplicate, disconnected, cancelled — zero unapproved actions;
- first-use novice comprehension and realistic setup completion, not engineer-only self-assessment.
Record PASS/FAIL/NOT TESTED with SHA, log/photo/video and exact reproduction. Don't conflate passing host tests with actual device testing. Once security is sound, follow repo gate of 100 approval trials, >=95% successful completion and zero unapproved executions, plus five outsider onboarding trials for eventual Kickstarter readiness.

## OpenRouter orchestration / $5 cap
This is a SEPARATE maximum $5 *paid inference* budget from Maz Works marketing. Account previously bought >=$10 OpenRouter credit, so it may have an upgraded combined free-model quota. Verify live billing and rate limits: usually up to 1,000 :free requests/day for eligible accounts and 20/min, shared across free models; failures may count. Test free-model IDs fresh from API; prefer free and local models for triage, repo indexing, extraction, draft UX, unit tests. Reserve paid DeepSeek Flash/Kimi/etc only for tasks where evidence shows advantage. Claude is the main orchestrator; do not assume Claude subscription works in Claude Code; discover available authentication, and never invent access. Use deterministic scripts, caching, targeted file reads, small prompts and output validation. Keep paid ledger, hard cut-off $5, don't deliberately exhaust it. Protect API secrets and don't send video/private data to cloud without consent.

## Work plan and deliverables
1. Audit current repos / branches / PRs / blockers; create a bounded consumer MVP plan.
2. Research 8–12 **consumer** frustrations and substitute free products; rank 3 launch demos by demand, implementation, testability and willingness-to-pay; select winning subtitle workflow if viable and one alternative if not.
3. Implement no-code PC UX and 3 Cardputer-visible demonstrations by reusing MAZ Pocket; add exact tests, logs and packaging; resolve security blockers.
4. Integrate Hermes Telegram live physical test loop; send first real test instruction only if the authorised bot is live; save user-confirmed receipts.
5. Prepare simple film checklist (3–6 ten-second real-device clips) with privacy cleanup, exact device/host commits, no simulated functionality.
6. Commit in appropriate branches and open review PRs; do not disturb live production. Save project summary and provenance to private unified memory after verifying changes.

**BATCH 1 EXIT GATE:** a consumer-useful, actually runnable Cardputer+PC experience, Telegram-guided physical testing with genuine recorded results, at least one truly successful end-to-end workflow, clear remaining risks and film-ready test list. If hardware testing not available, finish code/tests and explicitly mark PHYSICAL TEST PENDING. No fake "working" claims.

**Handoff for Batch 2:** repo/branch/SHA, current flash/Core versions, test evidence paths and privacy controls, confirmed customer demos, prototype BOM assumptions, exact remaining blocker, model spend. Continue with CLAUDE BATCH 2 only on verified results.
