# Site feature rows — 13 November 2026

Scope: reuse the existing homepage feature list, chips and responsive disclosure behaviour. No prices, new dependencies or hardware claims. No feature is described as Shipped: the product is pre-launch. Existing prototype labels stay; Beta means a separate test build, absent from the released app.

## Evidence per new row

All three rows refer to the inspected local feature head `d8434a94f7618f07a695f294ce0d2aa39e9befe0`, not this site branch. Its build report is `docs/FLAGSHIP-BUILD-2026-11-13.md` at that head. This evidence note is linked beside the public rows. The feature head was local-only at the original handover; the orchestrator must publish/reconcile the feature source before promoting its claims beyond this preview candidate.

| Row | Status | Inspected implementation and recorded evidence | Exact limit |
|---|---|---|---|
| Fetch from Home | Beta | `host/mazhost/file_vault.py`, `host/tests/test_file_vault.py`, `app/src/components/FileVault.tsx`; recorded Electron original-byte download/text preview and isolated Core/UI smoke | Explicitly chosen folder; supported originals up to 10 MiB. Remote API fixture passes, real second-PC/Tailscale transfer untested. No real private files tested. |
| Shortcuts you approve | Beta | `host/mazhost/shortcuts.py`, `host/tests/test_shortcuts.py`, `docs/voice-shortcuts.md`; recorded signed approval/grant and real PowerShell output test | Fixed owner-configured actions only. Each run requires device approval; commands also require a signed authority grant. Real microphone-to-device end-to-end trial remains open; direct local speech-to-speech does not route these intents. |
| Hey Piblo | Beta | `host/mazhost/wakeword.py`, `host/tests/test_wakeword_gate.py`, `docs/WAKEWORD-SETUP.md`; recorded 2/2 synthetic positives and 0/20 tested synthetic negatives at the documented settings | Optional detector/model setup; only an already-open Live session. No always-on Home wake, real-mic accuracy measurement or wake chime. Model redistribution rights unresolved. |

Evidence above was read from the existing feature branch and the supplied handover. Those feature tests were not rerun for a static-copy edit. No new desktop features were implemented here, so the isolated `scripts/feature-preview.py` run is not claimed as new evidence.

## Competitor check, without unsupported holes

The open-websearch tools are unavailable in this session; the available web search was used as fallback. Official rabbit documentation was checked on 13 November 2026:

- [OS3](https://www.rabbit.tech/support/article/rabbitos-3) describes memory, skills, local computer execution and multiple connected computers.
- [rabbit agent](https://www.rabbit.tech/support/article/rabbit-agent) describes access to a connected computer's files, tools and local models.

Therefore, “competitors cannot use your PC/files/local AI” is **not** a verified hole and is not used. The rows address practical gaps to test — deliberately bounded folder access, explicit per-run approval, and optional local wake detection — without claiming exclusivity or superiority. The official pages do not establish that competitors lack those safeguards. Competitor absence remains unverified, not a marketing claim.

## Acceptance

1. Three new rows with evidence and visible Beta/release limits; no prices or unsupported competitor claims.
2. Existing HTML/CSS/JS look and interactions reused; mobile and desktop browser check.
3. Bundled site gate and existing site tests pass. Preview only; orchestrator owns merge.

## Slice 1 verification

- Bundled `site-gate.js site`: exit 0, zero findings, before and after.
- Existing `node --test site/tests/site.test.mjs site/tests/waitlist.test.mjs`: 36/36 pass.
- Visible Chromium: 360, 390, 768, 1280 and 1440 px; all three Beta descriptions open/readable, no horizontal overflow. Reduced-motion preference enabled. Screenshots retained in the local temporary directory.
- Independent read-only agent review: new rows match source limits, no CSS/JS changes or price/exclusivity claims. Existing Show me once overstatement identified for Slice 2.
- Scope trimmed for this PR: copy-only change to the key legend, three Beta rows and the evidence link. Unrelated WIP (token comment rename, Buddy forms/moods, editions wording, subscription copy, Show me once relabel) was dropped here and belongs to Slice 2.
