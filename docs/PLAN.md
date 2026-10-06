# nod — Plan (2026-10-06)

Goal: Cardputer ADV becomes a remote Claude Buddy + gamified action deck, usable anywhere.
Then a custom hardware version.

## Decisions (owner, 2026-10-06)
- Remote first. Emulate Claude Buddy over MAZ Core (Wi-Fi / Tailscale), not BLE. BLE port later for the open-source PR.
- Deck keys v1: Agent control, Call MAZ voice, PC macros. Sales keys later.
- UI: minimal, big glyphs for 240x135, futuristic, gamified (XP, streak, rank).
- Product: hardware version planned.
- Device: same Cardputer ADV.

## Architecture
```
Claude Code (any session) --PermissionRequest hook--> Core /buddy/request (waits for decision)
Cardputer --polls--> Core /buddy/state      (pending prompt, sessions, XP)
Cardputer --Y/N-->   Core /buddy/decide     -> hook returns allow/deny to Claude Code
Timeout (60s) or no device -> hook falls through to the normal terminal prompt. Never auto-approve.
```
Remote: Cardputer reaches Core the same way beam/pull does today (LAN or Tailscale via phone hotspot).

## Slices (each ships working, proof required)
1. Core: `/buddy/request|state|decide` + XP counters (in memory, JSON file persist). Proof: curl round-trip.
2. Hook: `~/.claude/hooks/maz_buddy.py` PermissionRequest hook. Proof: real Claude Code prompt resolved from curl.
3. Firmware: BUDDY DECK home — 4 tiles (BUDDY, CALL, PC, AGENTS), toast + beep on pending prompt from any screen, Y/N, XP bar. Proof: build size < 1.5MB, flashed, photo via camera.
5. Open source: Cardputer port PR to anthropics/claude-desktop-buddy (BLE) — later, after 1-3 are stable.

## Out of scope now
Desk handset phone (next week), character packs, sales keys, BLE.

