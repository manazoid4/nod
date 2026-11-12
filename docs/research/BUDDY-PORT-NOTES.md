# Buddy port notes — upstream (StickC Plus) → Cardputer ADV → your Wi-Fi firmware

Read from source: both `src/` trees, `platformio.ini`, `REFERENCE.md`, READMEs. Line numbers are for the files as vendored in
this folder. Upstream = `claude-desktop-buddy/`, port = `claude-desktop-buddy-cardputer/`.

Byte-identical: `ble_bridge.cpp/.h`, `buddy_common.h`, `buddy.h`, `stats.h`, `REFERENCE.md`. Changed: `main.cpp` (1265→1768
lines), `character.cpp` (401→409), `buddy.cpp` (196→207), `data.h` (2 lines), `xfer.h` (4 lines), `platformio.ini` (15→34). New:
`hal.h`, `hal.cpp`, `buddies/doge.cpp`, `buddies/llama.cpp`. `platformio.ini:17-34` adds env `cardputer-adv` (StampS3,
`-DCARDPUTER_ADV`, `-DBOARD_HAS_PSRAM`, M5Unified + M5Cardputer, same library pins).

## 1. Physical Y/N approval + keyboard map

**Upstream** `src/main.cpp`: `sendCmd()` 115-120; prompt arrival 1023-1039; BtnA/BtnB wake-swallow 1046-1052; long-press menu
1065-1076; BtnA release=approve 1077-1106; BtnB=deny 1109-1139; `drawApproval()` 725-768. Two buttons only, A approves, B denies.

**Port** `src/hal.cpp`: `KeyBtn` 209-250 (debounce, `_rose`/`_fell`, `suppressPending`), `EnterBtn` 252-257
(`keysState().enter`), `EscBtn` 258-267 (Del or backtick), `_pollKeyEvents()` 302-332 (rising-edge diff of `.word`),
`halPollKey()` 335-340. `src/hal.h` `HalKey` 130-139. `src/main.cpp` key loop 1511-1626: pending prompt wins, then picker
1556-1572, reset 1574-1580, settings 1581-1587, menu 1588-1594, home 1597-1625. Enter also drives `HalBtnA`, so modal
handlers call `suppressPending()` (1550-1551); without it one Enter confirms *and* cycles the display mode. Approve/deny
JSON at 1524-1539.

Map (`hal.h:124-128`): `;` `.` `,` `/` = up/down/left/right; `y`/`Y` and Enter = approve; `n`/`N` = deny; backtick, Del or
Backspace = back; `m` = menu; `g` = demo. Fn-held keys ignored.

```cpp
// hal.cpp:307-322 — diff the held-key set into edge events
for (char c : st.word) {
  if (_wordContains(_prevWord, c)) continue;
  HalKey k = HalKey::None;
  switch (c) {
    case ';': k = HalKey::Up; break;      case '.': k = HalKey::Down; break;
    case ',': k = HalKey::Left; break;    case '/': k = HalKey::Right; break;
    case 'y': case 'Y': k = HalKey::Approve; break;
    case 'n': case 'N': k = HalKey::Deny; break;
    case 'm': case 'M': k = HalKey::Menu; break;
    case '`': k = HalKey::Back; break;
  }
  if (k != HalKey::None) _pushKey(k);
}
```

Deps: `M5Cardputer.h` only. **Portable: yes** — the most reusable piece. Keep `HalKey` + queue, decode from your key
driver, send over HTTP instead of `bleWrite`, and keep both fixes: modal release suppression and re-evaluating `promptLive`
inside the loop (main.cpp:1519) so one Enter cannot approve twice.

## 2. Notification sounds (tone sequences, volume)

**Upstream** `src/main.cpp:111-113` `beep(freq,dur)` → `M5.Beep.tone()`, gated on `settings().sound`; single tones at 1030
(1200/80), 1086 (2400/60), 1118 (600/60), etc.

**Port** `src/main.cpp:152-198`: ten const frequency/duration pairs (nav, confirm, back, approve C-E-G-C, deny A-F-C, save,
Mario-1UP alert E5-G5-E6-C6-D6-G6, menu, warn, warn2), wrappers `sfxNav()…sfxWarn2()`, one gate in `sfxPlay()` (184-186).
`src/hal.cpp:14-39` is the sequencer: `halBeepSeq()` stores pointers and resets the index, `_pumpSeq()` (from
`halBeepUpdate()`) fires the next note at `millis() >= _seqNextAt` and schedules `+dur+8ms`; new calls pre-empt old ones.
Volume is fixed at `M5.Speaker.setVolume(160)` in `halInit()` (hal.cpp:112, 0-255); the UI only toggles sound
(`settings().sound`, stats.h:180/192).

```cpp
// main.cpp:175-176 + 184-186 — one table pair, shared player
static const uint16_t SFX_ALERT_F[] = { 659, 784, 1319, 1047, 1175, 1568 };
static const uint16_t SFX_ALERT_D[] = {  35,  35,   35,   35,   35,   90 };
static void sfxPlay(const uint16_t* f, const uint16_t* d, uint8_t n) {
  if (settings().sound) halBeepSeq(f, d, n);
}
```

Deps: StickC `M5.Beep`; ADV `M5.Speaker` (M5Unified I²S). **Portable: yes**, verbatim. Tables must stay `static const`
(the player keeps raw pointers); the player assumes `tone(freq,dur)` is non-blocking. Volume has no UI — add one.

## 3. LED alerts — does the ADV have an RGB LED?

**Code says yes, via the StampS3 module:** `src/hal.cpp:135-140` drives a WS2812B/SK6812 on GPIO 21 with the core's
`neopixelWrite()` (no library); `README.md:41` lists it as ADV hardware. Not verifiable without a unit: the module LED may
be hidden inside the case, so treat visibility as "check your unit"; keep `halLedSet()` as the seam.

**Upstream** is a single active-low red LED on GPIO 10: `main.cpp:944-945` (init), 1004-1009 (pulse while attention and
`settings().led`). **Port** `main.cpp:1356-1363` pulses red-orange `(180,40,0)` at 2 Hz while attention, else `(0,0,0)`;
toggle at 261; both boards in `hal.h:111-117`.

```cpp
// hal.cpp:137-140
constexpr int CARDPUTER_RGB_PIN = 21;
void halLedSet(uint8_t r, uint8_t g, uint8_t b) {
  neopixelWrite(CARDPUTER_RGB_PIN, r, g, b);
}
```

Deps: Arduino-ESP32 core `neopixelWrite` (RMT). **Portable: yes, 8 lines**, if the pixel is real. Fix the port's waste: it
calls `halLedSet(0,0,0)` every loop frame (~60 Hz) — gate on state change.

## 4. Animated character mood/state machine

Seven states, same order everywhere: sleep, idle, busy, attention, celebrate, dizzy, heart (`main.cpp:50-51`; mirrored
`character.cpp:9-11`, `buddy.cpp:9`, `buddy.h:25-29`).

- `derive()` 646-652: disconnected→idle; `waiting>0`→attention; `recentlyCompleted`→celebrate; `running>=3`→busy; else idle.
- One-shots `triggerOneShot()` 654-657: level-up→celebrate 3 s (1347); shake→dizzy 2 s (1366-1373; `checkShake()` 659-666,
  EMA baseline, 0.8 g); fast approval (<5 s)→heart 2 s (1448/1531); picker save→heart 1.5 s (1565).
- 12 s post-wake sleep hold overrides idle only (124, 1350-1352); expired one-shot restores `baseState` (1354).
- Charging clock overrides mood by wall clock (1655-1671): 01-07 sleep, weekend mostly sleep+heart, <09 drowsy, 12:xx heart,
  Fri≥15:00 celebrate, ≥22:00 dizzy, else idle; skipped during one-shots.
- Nap 1735-1756: face-down debounce 15 up/−8 frames, dim 8 %, pause render, count nap seconds; energy refills on wake
  (`stats.h:160-171`). `statsMoodTier()` (`stats.h:141-158`) rates approval speed 0-4 but only feeds the stats page.

ASCII species are `StateFn states[7]` (`buddy.h:23-29`), ticked 5 fps by `buddyTick()` (`buddy.cpp:184-207`, `TICK_MS=200`,
redraw gated on tick/state/species change); GIF characters switch files per state in `characterSetState()`
(`character.cpp:303-339`).

```cpp
// main.cpp:646-657
PersonaState derive(const TamaState& s) {
  if (!s.connected)            return P_IDLE;
  if (s.sessionsWaiting > 0)   return P_ATTENTION;
  if (s.recentlyCompleted)     return P_CELEBRATE;
  if (s.sessionsRunning >= 3)  return P_BUSY;
  return P_IDLE;
}
void triggerOneShot(PersonaState s, uint32_t durMs) {
  activeState = s; oneShotUntil = millis() + durMs;
}
```

Deps: none (plain C++ + `millis`). **Portable: yes** — copy enum, `derive`, one-shot timer, wake hold; drop clock/IMU
branches if absent. ~60 lines for most of the personality.

## 5. GIF support

All `src/character.cpp` (logic identical both repos; only `PEEK_TOP`/home-zone constants differ, 45-51). Libs
**bitbank2/AnimatedGIF ^2.1.1**, **ArduinoJson ^7**; LittleFS callbacks `gifOpenCb/gifCloseCb/gifReadCb/gifSeekCb` (80-104).
`characterInit()` 148-253 scans `/characters/<name>/manifest.json`, reads `colors` + `states` (up to `MAX_GIFS=32`, 29-34),
calls `gif.begin(LITTLE_ENDIAN_PIXELS)`; text manifests (`"mode":"text"`, 209-229) animate short strings.
`characterSetState()` 303-339 opens the state's GIF, records W/H, places it; `characterTick()` 341-408 calls
`gif.playFrame(false,&delayMs)` when due and schedules `now + (delayMs>0?delayMs:100)`.

`gifDrawCb()` 110-144 decodes one scanline at a time and writes **pixel by pixel** into the shared sprite (`put()` →
`drawPixel`), substituting `pal.bg` for transparent pixels (no ghosting); peek mode halves it by skipping odd rows/columns.
Full-frame unoptimized GIFs are required on purpose — the disposal/delta path was tried and reverted (comment 116-120).

**Memory:** no PSRAM is used; `-DBOARD_HAS_PSRAM` (`platformio.ini:27`) is never referenced. The only framebuffer is
`TFT_eSprite spr` (`main.cpp:8`, `createSprite(240,135)` at 1306) = 240×135×2 = 64,800 B internal RAM; AnimatedGIF adds a
small line/decoder buffer per `gif.open()`. Storage ≈1.8 MB LittleFS; installs stream a folder over BLE (`xfer.h:77-235`,
base64, ack per chunk).

```cpp
// character.cpp:267-272 — one frame per GIF delay, 100 ms fallback
uint32_t now = millis();
if (now >= nextFrameAt) {
  int delayMs = 0;
  if (!gif.playFrame(false, &delayMs)) { gif.reset(); gif.playFrame(false, &delayMs); }
  nextFrameAt = now + (delayMs > 0 ? delayMs : 100);
}
```

Variants 390-406: single-GIF states freeze on the last frame (avoids repeated LittleFS opens); multi-variant states loop
5 s (`VARIANT_DWELL_MS`), rotate, pause 800 ms. **Portable: yes** (this is that build). Two caveats: comment 106 claims
"line buffer → pushImage" but the code calls `drawPixel` per pixel — batching a 240-px line cuts SPI calls ~240×; and your
HTTP build needs a replacement for `xfer.h` (multipart/base64 POST) if folder installs stay.

## 6. Battery saving (dim/off/sleep/CPU)

Implemented both: brightness ladder 0-4 → 20-100 % (`main.cpp:64`, `applyBrightness()` 138); idle screen-off timer **30 s
upstream** (84) vs **120 s port** (125), skipped during a prompt or on USB (upstream 1258-1262, port 1761-1765);
`halScreenPower()` = LDO2 off (StickC) or `setBrightness(0)+sleep()` (port, `hal.cpp:121-124`); `wake()` restores brightness
and arms a 12 s sleepy window (140-149); face-down nap dims to 8 % and pauses rendering; loop throttles to 100 ms when off
vs 16 ms awake (1767).

Not implemented anywhere: no `setCpuFrequencyMhz`, `esp_pm_configure`, light/deep sleep or partial refresh. CPU is fixed at
build time — upstream `board_build.f_cpu = 160 MHz` (platformio.ini:8), Cardputer env leaves the S3 at 240 MHz. BLE stays
always-on by design (comment 254-259, 1305); `bluetooth`/`wifi` settings are stored booleans, nothing is torn down
(`applySetting` case 3: wifi is a pure placeholder in both repos).

```cpp
// main.cpp:140-149 — one wake path for keys, timer expiry and nap end
static void wake() {
  lastInteractMs = millis();
  if (screenOff) {
    halScreenPower(true);
    applyBrightness();
    screenOff = false;
    wakeTransitionUntil = millis() + 12000;
  }
  if (dimmed) { applyBrightness(); dimmed = false; }
}
```

Deps: AXP192 (StickC) vs M5Unified `M5.Display`/`M5.Power`. **Portable: yes**, and the cheapest way to beat upstream on
battery: `setCpuFrequencyMhz(80)` while screen-off, light sleep with GPIO key wake, blank the panel rather than dimming.
Keep the "no auto-off during prompt / on USB" rules.

## 7. Bluetooth BLE bridge protocol

**Transport** (`src/ble_bridge.cpp`, identical both repos): Nordic UART Service, UUIDs 13-15; RX ring 2048 B (20-40);
notify TX + write/write-NR RX (102-116); MTU request 517 (92); notifies chunked to `mtu-3`, capped 180, `delay(4)` between
chunks (162-180); re-advertises on disconnect (60-62). **Pairing/security** 69-134: LE Secure Connections, MITM, bonding
(`SC_MITM_BOND`), DisplayOnly (`ESP_IO_CAP_OUT`), 16-byte keys, characteristics and the TX CCCD `*_ENCRYPTED`; the 6-digit
passkey arrives in `onPassKeyNotify`, is rendered by `drawPasskey()` (main.cpp:685-697), cleared on auth;
`bleClearBonds()` 140-149 backs `{"cmd":"unpair"}`.

**Messages** (`src/data.h`): newline-delimited JSON, 1024-byte line buffers (129-145), ASCII fast check `buf[0]=='{'`.
Fields parsed 70-127: `total`, `running`, `waiting`, `completed`, `tokens`, `tokens_today`, `msg`, `entries[≤8]`,
`prompt{id,tool,hint}`; `{"time":[epoch,tz]}` sets the RTC. Liveness: 30 s silence = disconnected (51), BLE traffic 15 s
(54-57). Outbound (`main.cpp:200-205`) writes one JSON line to Serial *and* BLE:
`{"cmd":"permission","id":...,"decision":"once"|"deny"}`. Commands/acks, status shape and folder push are in
`REFERENCE.md` (96-192), implemented in `xfer.h:77-235` (`name`, `owner`, `species`, `unpair`, `status`,
`char_begin/file/chunk/file_end/char_end`).

```cpp
// ble_bridge.cpp:121-124 — the security posture in four lines
BLESecurity* sec = new BLESecurity();
sec->setAuthenticationMode(ESP_LE_AUTH_REQ_SC_MITM_BOND);
sec->setCapability(ESP_IO_CAP_OUT);
sec->setKeySize(16);
```

Deps: ESP32 Arduino BLE. **Portable: protocol yes, transport no.** The stack compiles on S3, but for Wi-Fi HTTP keep
`TamaState`, `_applyJson()` and the permission JSON verbatim; replace the BLE drain in `dataPoll()` with HTTP GET/POST
(poll 1-2 s, POST decisions). Replace MITM pairing with an explicit shared token — the JSON layer has **no
authentication**; link security did that job.

## 8. What the Cardputer port changed vs the original

1. **HAL shim** (new `hal.h`/`hal.cpp`): wraps `M5.Axp`, `M5.Beep`, `M5.BtnA/B`, `M5.Imu`, `M5.Rtc`; aliases `TFT_eSPI` to
   `lgfx::LovyanGFX` and `TFT_eSprite` to `M5Canvas` (hal.h:34-35), and re-declares the StickC RTC structs (27-28) because
   `character.cpp`/`buddy.cpp` take `TFT_eSPI*`. `data.h` and `xfer.h` swap includes and battery/RTC calls (2 and 4 lines).
2. **Landscape UI**: `W,H = 240,135`, `HOME_ROTATION 1`, panel tops 4 (`main.cpp:23-44`); every panel relaid out, settings
   at 10 px pitch (349-357), info/pet full-screen with pet suppressed (1684-1689), approval full-screen (939-982),
   transcript centred at x=57 (1236-1240).
3. **Keyboard** replaces two buttons: `HalKey` queue + virtual Enter/Esc; modal branches removed from `BtnA`/`BtnB`
   (`#ifndef CARDPUTER_ADV` 1449-1460, 1482-1492) to avoid double-fire.
4. **Sound**: single `beep()` → 10-sequence SFX library + `halBeepSeq()` sequencer. **LED**: GPIO 21 RGB instead of GPIO 10.
5. **Content/UX**: +2 species (doge, llama → 20), live pet picker (394-420, 1556-1572), menu gains `pet` (225-226), compact
   10 px clock strip (574-584), tilt clock disabled (512-517), idle timeout 30 s → 120 s, battery current/temp stubbed
   (README 113-118).
6. **RTC**: no battery-backed chip → `settimeofday()` via `halRtcSetTime/Date` (`hal.cpp:184-202`). Unchanged: BLE bridge,
   stats/NVS schema, GIF decoder, xfer protocol, art.

## Top 6 things worth porting (ranked)

1. **`data.h` model + `_applyJson()` + permission JSON** (data.h:7-127, main.cpp:200-205) — product contract; swap BLE for HTTP in one function.
2. **Keyboard approval flow** (`hal.cpp` 209-340, `main.cpp` 1522-1541) — Y/N edges, prompt priority, no double-fire. The reason to own it.
3. **Mood machine** (`derive`/`triggerOneShot`/wake hold/nap) — ~60 lines, no deps, all the charm; clock-hour table free with RTC/NTP.
4. **SFX sequencer** (`hal.cpp:14-39` + tables) — 25 lines, no library, instantly recognisable; add a volume setting.
5. **LED pulse** (`halLedSet` + 4 calls) — trivial and glanceable; verify visibility on your ADV, else drive a Grove LED.
6. **Power policy** (`wake()`, 120 s off, prompt/USB exceptions, nap) — right rules, board calls isolated; add CPU/light sleep.

## Do NOT port

- **`characters/bufo/*.gif`** — third-party **non-MIT** art (`LICENSE`, `characters/bufo/README.md:8-10`); do not copy or bundle.
- **20 ASCII species** (`src/buddies/*.cpp`) — MIT code but artwork; port the `Species`/`StateFn` interface, draw your own.
- **BLE stack, UUIDs, passkey, bonds** — you are Wi-Fi/HTTP now; keep the JSON, add a token since BLE's MITM is gone.
- **StickC HAL passthrough / AXP192 / GPIO 10 LED / M5.Beep** — dead weight on an S3.
- **Tilt-to-landscape clock** (`clockUpdateOrient`, main.cpp:511-554) — disabled for landscape, pointless with a fixed UI.
- **`xfer.h` base64 chunk-ack push** — built for BLE backpressure; over HTTP use one multipart upload (validate `path`).
