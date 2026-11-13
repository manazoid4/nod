# Everyday polish — 13 November 2026

Exactly two goals: finish expired Windows focus sprints, and read full saved thoughts.

## Focus finish

Core intentionally stays muted in `awaiting_done` until `/focus/end`. The Windows
card previously hid Finish in that state and offered a replacement sprint instead.
It now retains Finish (`done:true`) and Stop (`done:false`) for running and expired
sprints. Existing 15/25/50-minute presets and firmware remain unchanged.

Evidence: three renderer regression tests; Electron/IPC fixture check in
`app/scripts/verify-focus-finish.mjs` clicks both decisions and verifies their
request bodies and return to idle. Owner test: pending. No hardware claim.

## Full thoughts

Core retains the transcript, but Memory previously rendered only the summary.
Read now fetches the existing authenticated `/dumps/{id}` endpoint and displays
the original text inline, preserving line breaks and treating markup as text.
Close/Read retries a failed fetch. Nothing is rewritten or deleted.

Evidence: `app/scripts/verify-saved-thought.mjs` exercises save, a >280-character
transcript, literal script text, close, and reopen through Electron and Core IPC.
The installed Core returned the complete 621-character live test note, including
the final `blue notebook` phrase. **Owner's first test failed** (Read failed or
text missing). Owner then confirmed Read changed to Close but quoted truncated
text. A fresh Electron check against installed Core displayed the entire note;
the screen showed the shortened summary above the full transcript. The UI now
replaces that summary with a labelled Full thought on expansion. Retest pending.
Local HTTP connections also reset and Core restarted during diagnosis; causation
is unconfirmed. Do not treat this as a passing owner test.

## Verification and compatibility

- `npm run typecheck`: passed.
- `npm test`: 176 passed, 13 files. Existing preferred-contrast warnings remain.
- Main and renderer builds: passed.
- Runtime feature catalogue tests: 5 passed (`PYTHONPATH=host python -m pytest host/tests/test_features.py -q`).
- Independent review of Read: no blocking findings; lead reviewed Focus diff.
- Existing HTTP contracts reused. No firmware, Android, keyboard, recovery,
  Kokoro or website changes. Device connected at initial status check; this is
  connection evidence only.
- No release published. Owner tests and PR CI must be complete before release.

Audit inputs: fetched main `4e71480`; recent merged PR/commit history, open PRs
#75 and #107–#113, no open issues, feature inventory/runtime catalogue,
Windows and Android integration notes, voice research/legacy resume board,
and the unified 13 November handover including its 04:30 update. Existing work
is present in separate worktrees; those files were left untouched.
