# Easy Mode handover (Codex, 9 Nov 2026)

Built on `feat/easy-mode-keyboard` (from `origin/main`). No hardware was
used; everything below is *build-verified* (MAZPC PlatformIO) or
*simulated* (native logic tests, Core pytest). Never flash-tested.

## What works

- **Easy Home (Settings → Easy Mode, default on).** Home becomes a plain
  list: Notes, Reminders, Messages (results inbox), Tasks, Shortcuts
  (snippets), Settings, Help. UP/DOWN (or `;`/`.`) + ENTER, no Fn.
  Classic home is one toggle away and otherwise untouched.
- **One reusable text field.** Cursor (LEFT/RIGHT), Backspace/Delete,
  double-Shift CAPS, Ctrl+P quick shortcuts, Ctrl+H recent phrases,
  Ctrl+SPACE dictation, all in `apps/common.h`. Word suggestions are
  skipped (flash; see below) — that is the only item Maz asked for that
  this PR does not ship, and the code says so.
- **Phone Keyboard Mode.** `POST /buddy/text` (dedupe by uuid, 400/401/429,
  2-minute TTL) → `text_input` ring event → literal insert into the drawn
  field via the host worker, ack `inserted`/`no_field`/`too_long`,
  `GET /buddy/text/{id}`. `send` inserts only, never presses ENTER.
  Protocol: `docs/protocol/PHONE-KEYBOARD.md`. Full key map: `docs/KEYS.md`.
- **Safety held.** Approvals untouched (Y/ENTER approve, N/ESC reject,
  timeout = rejected); no Easy Mode, phone-text or "any key" path can
  approve, pinned by native tests. Untrusted text stays text.

## What's simulated / where to look

- Native logic tests: `firmware/nod/include/phone_text.h`,
  `firmware/nod/include/easy_keys.h`, `firmware/nod/tests/test_nod.cpp`
  (1528 checks; they caught one overflow bug, `SeenIds::add` wrap).
- Core protocol tests: `host/tests/test_phone_text.py` (9 tests).
- No keyboard/UI simulator step was added: navigation and field editing
  follow the existing `TextField`/`ListCursor` patterns and are covered by
  the native contract tests + the new Core tests. A visual pass still
  needs the device (checklist below).

## Size

MAZPC `pio run -e cardputer-adv` (same machine, before/after):
`origin/main` firmware.bin **1,487,088** → this branch **1,499,856**
(**+12,768**), headroom **7,472** of the 1,507,328 slot — **below the
16,384 CI gate**. No features were cut to chase the gate: please sequence
this after `fw/optimise-adv` (which frees headroom). CI will report its
own numbers.

## Needs device (not claimable without hardware)

- [ ] Key feel: arrows on Fn keys, double-Shift CAPS, Ctrl+P/H.
- [ ] Readability at arm's length (Easy list, field chip, 240×135 body).
- [ ] Easy Mode toggle survives a reboot (NVS "easy").
- [ ] Phone typing end-to-end once `android/companion` sends to
      `POST /buddy/text` (its lane; follow-up listed in the PR).
- [ ] Ack round-trips, disconnect-during-typing keeps the buffer.
- [ ] Hold-Y approvals still need an explicit press (no auto-approve).

## Lanes / conflicts

- Did not touch: `docs/protocol/PROTOCOL.md` (MCP), `platformio.ini` +
  `src/audio/sfx.*` (optimisation), `android/`, `site/`, kickstarter.
- `buddy.py` and `shell.cpp` overlap other lanes by design (additive).
  The Nod branch (`feature/the-nod`) also touches both — rebase needed,
  hold-Y-800 ms behaviour not present on this branch and untouched here.

## Logging

Run `git log --oneline origin/main..HEAD` for the three commits; this file
is uncommitted handover narrative, not code.
