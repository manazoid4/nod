# Firmware optimisation

Before/after from `pio run -e cardputer-adv` (PlatformIO 6.x, espressif32@6.9.0, M5Unified 0.2.20). Baseline: [FIRMWARE-BASELINE.md](FIRMWARE-BASELINE.md) / `fw-baseline.json`; optimised numbers: `fw-optimised.json`. Build-verified only; **needs device test** (no hardware connected, nothing flashed).

| metric | before | after | delta |
|---|---:|---:|---:|
| `firmware.bin` | 1,490,896 | 1,346,016 | **−144,880** (−9.7%) |
| OTA headroom (slot 1,507,328) | 16,432 | 161,312 | +144,880 |
| `.flash.text` | 1,098,779 | 1,046,879 | −51,900 |
| `.flash.rodata` | 302,744 | 209,752 | −92,992 |
| IRAM | 69,358 | 69,358 | 0 |
| static RAM (data+bss+iram) | 141,142 | 141,214 | +72 |
| `.dram0.bss` | 52,128 | 52,200 | +72 |
| PIO RAM usage | 71,784 (21.9%) | 71,856 (21.9%) | +72 |

Headroom now 161 KB — 9.8× the previous 16 KB. CI floor (32 KB) passes.

## What changed

### `-fno-exceptions` (platformio.ini) — 145 KB saved
Nothing in `src/` or `firmware/` uses try/catch/throw (verified by grep; the only matches are JS strings inside embedded portal pages and the word "try again"). ArduinoJson, std::string/vector and WebSockets are used in ways that don't throw: no `.at()`, no `std::stod/stoi/...` (those throw `invalid_argument`/`out_of_range` on bad input). Under `-fno-exceptions` a throw becomes an abort, but with nothing throwing, there's no new crash path — and an uncaught throw aborted anyway before. The arduino-esp32 default `-fexceptions` only added `.eh_frame` and landing pads.

Reproduce: `python scripts/fw-size-report.py --baseline docs/perf/fw-baseline.json` after `pio run -e cardputer-adv`.

### Non-blocking tone sequencer (`firmware/nod/include/tone_seq.h`, `src/audio/sfx.cpp`)
Alert, approval, agent-done and Focus chirps used to `delay()` between notes, freezing the UI loop for up to ~0.5 s. Notes are now queued and stepped from `loop()` by `sfx::update()`; single UI clicks stay quiet while a chirp is sounding. Only `recStart`/`recStop` stay synchronous (their order against the mic is the point).

### Poll back-off (`firmware/nod/include/poll_backoff.h`, `src/core/approvals.cpp`, `src/core/field.cpp`)
While Core is unreachable (laptop asleep), each failed poll used to burn a connect timeout at a fixed cadence (5 s / 15 s). `backoffMs()` doubles the wait per consecutive failure, capped at 15 s for approvals (still inside the 60 s approval window) and 30 s for the Field beam pull. One success resets the counter.

### Size tooling (`scripts/fw-size-report.py`, `host/tests/test_fw_size_report.py`)
Map-file parser that prints flash/RAM per build, top contributors, and diff vs a baseline JSON. CI now runs it with a 32 KB headroom floor (was 16 KB).

## Tests

- `uvx --from ziglang python -m ziglang c++ -std=c++11 -Wall -Wextra -Werror -O1 firmware/nod/tests/test_nod.cpp -o nod_test && ./nod_test` → `1546 checks, 0 failed` (tone sequencer timing/overflow/wrap, back-off cap/monotonicity, plus all pre-existing checks). `make -C firmware/nod test` is the CI form (needs g++/make on the runner).
- `uv run pytest host/tests -q` → all green (includes 4 new tests in `host/tests/test_fw_size_report.py`).
- `pio run -e cardputer-adv` (MAZPC) → SUCCESS, 1,346,016 B.

## What needs the device

- Boot + Wi-Fi on real hardware with `-fno-exceptions` (aborts would be fatal — this is the main risk, though the audit found no throw paths).
- Tone timing by ear (chirps now queued; recStart/recStop synchronous so recording order is unchanged).
- Battery impact of back-off (should improve; measure with portal `/api/status` free_heap + current).
- No code removes any user-visible feature and the wire protocol (piblo-proto v1) is unchanged.
