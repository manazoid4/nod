# Piblo — Feature Roadmap

*Derived from docs/kickstarter/M5STACK-FEATURE-RESEARCH.md (official M5Stack evidence, Nov 2026). No Kickstarter promises. Every item names a real component.*

## The product thesis in one paragraph

Piblo today is "a Cardputer ADV with good firmware and a PC hub". That is a £30 dev board with nice software — Kickstarter backers ask "why not just flash my own Cardputer?". The answer must be hardware+software they cannot get by flashing: **an offline pocket computer** — physical AI approvals, a real rotary knob, LoRa mesh + GPS that works with no phone signal, and a £10 sensor kit — all speaking to one hub. Everything below serves that thesis. Anything that does not is in Tier D (deferred).

## Tier A — Existing Cardputer ADV hardware, firmware only ($0)

These ship in the base device. Ranked by value.

| # | Feature | Component | Value | Difficulty | KS potential |
|---|---|---|---|---|---|
| A1 | Ask / Call push-to-talk + voice reply, fixed quality/latency | ES8311 + NS4150B + 1W speaker (built-in) | ★★★★★ — the core loop | M (software: Kokoro streaming) | High — "talk, don't type" |
| A2 | Agent approvals Y/N + Halt (Fn+H) + Quiet (Fn+Q) | 56-key keyboard (built-in) | ★★★★★ — the differentiator | S (exists) | High — "stay in charge of AI" |
| A3 | Reminders / alarms / timers / tasks, promoted to Home | microSD persistence (built-in) | ★★★★ | S (move screens) | Medium |
| A4 | IR remote: TV/AC/speaker blast + learn | Built-in IR emitter | ★★★★ — "phone-free remote" | S–M (IRremote lib) | Medium — visible demo |
| A5 | Shake-to-act + orientation UI | BMI270 IMU (built-in) | ★★★ | S | Low — delight |
| A6 | Voice-note recording + offline capture queue | MEMS mic + microSD (built-in) | ★★★★ | S (exists: Recorder) | Medium |
| A7 | QR generate + typed-URL workflows | QRCode lib (already in platformio.ini) | ★★ | S | Low |
| A8 | Headphone output for voice replies | 3.5mm jack (built-in) | ★★★ | S (exists) | Low–Medium |
| A9 | Serial/GPIO diagnostics + remote agent management | USB-C UART + EXT header (built-in) | ★★★ | S | Makers only |

**A-tier rule:** if a competitor Cardputer flashed with stock firmware can do it, say so honestly. A4 (IR) and A5 (IMU) are where the stock firmware does not compete — a "Configure Piblo" flow that learns the IR codes is a reason to keep Piblo firmware rather than blank-flashing.

## Tier B — Inexpensive plug-in accessories (the Kickstarter value stack)

All connect via HY2.0-4P Grove and/or the Cap HP port. Costs are USD shop list.

| # | Feature | Exact component | Price | Offline | Value / diff / KS |
|---|---|---|---|---|---|
| B1 | **Rotary knob + push button + RGB status** | **Unit Encoder** | $7.95 | Yes | ★★★★★ / S / ★★★★★ — the hero accessory |
| B2 | **Meshtastic mesh + GPS location sharing + emergency SOS** | **Cap LoRa-1262 (U214)** | $14.50 | Yes — fully offline | ★★★★★ / M / ★★★★★ — the headline |
| B3 | **Far-field / interview mic** | **PDM Microphone Unit (U089)** | $3.50 | Yes | ★★★★ / S / ★★★ — cheap, "voice notes that actually sound good" |
| B4 | **Room climate: temp + humidity + pressure** | **Unit ENV-IV (U001-D)** | ~$6 | Yes | ★★★★ / S / ★★★ — "is this room comfortable" + automations |
| B5 | **Motion / occupancy detection** | **Unit PIR (U004)** | ~$4 | Yes | ★★★★ / S / ★★★ — security + "anyone home" |
| B6 | **NFC tap + sub-GHz RF (garage, access, remote control)** | **Cap CC1101 & NFC (U219)** | $18.95 | Yes | ★★★★ / S / ★★★★ — **mutually exclusive with B2 (one EXT socket)** |
| B7 | **RFID/NFC tag reader (Grove, cheap)** | **Unit RFID2 (WS1850S)** | $4.95 | Yes | ★★★ / S / ★★ — overlaps B6, cheaper |
| B8 | **Multi-sensor purse** | **Unit Hub (HY2.0-4P → 3×)** | ~$4 | Yes | ★★★★ / S / ★★★ — the enabler: ENV+PIR+mic at once |
| B9 | **CO2 / air quality** | **Unit CO2 (SCD40)** | ~$25–35 | Yes | ★★★ / S / ★★ — premium sensor, pricey |
| B10 | **UHF RFID inventory (12m tags)** | **Unit UHF-RFID** | ~$40–60 | Yes | ★★★ / M / ★★ — field-worker story |

**Kickstarter value stack (recommendation):** B1 + B3 + B8 in the box (or +$10 add-on), B2 (LoRa) as THE headline upgrade, B4+B5 as the £10 "Home sensor pack". B6 vs B2 is a fork — ship ONE Cap as default and sell the other as a swap. Never promise both at once.

## Tier C — Premium expansion ($40+ add-ons, bundles, companion devices)

| # | Feature | Component | Price | Verdict |
|---|---|---|---|---|
| C1 | **Thermal imaging / non-contact temp** | Unit Thermal (U016, MLX90640) | $65 | Stretch goal + Premium bundle. 2× device price — do not put in base tier. |
| C2 | **Snap photos → caption → note** | TimerCam (OV3660) / AtomS3R-CAM | ~$20–25 | Companion device over Wi-Fi, not a plug-in. Coherent "Piblo family" story. |
| C3 | **Wearable approval fob** | StickS3 / AtomS3R | ~$15–25 | Same companion story. Scope-creep risk — v2, not v1. |
| C4 | **Cellular when no Wi-Fi** | Stack Modules COM.LTE/NBIoT | $79+ | **No official Cardputer fit.** D. Do via phone/PC hub instead. |
| C5 | **Robot / servo control** | RoverC Pro ($65), Servo/StepMotor | $8–65 | Maker tier. Fun video demo, tiny market. |

## Tier D — Experimental / incompatible (do not promise)

| Idea | Why it's D |
|---|---|
| On-device LLM (Module LLM AX630C) | M5-Bus Stack Module. No Cardputer ADV outlet. 4GB/5V. Custom bridge needed. |
| Zigbee hub-on-device | No Zigbee Unit that fits Grove cleanly; would need bridge. Use hub/Wi-Fi instead. |
| Haptic vibration | No official haptic Unit. Custom motor breakout only. |
| Unit-V on-device object detection | Whole second computer (K210). PC-hub vision instead. |
| Native M5-Bus Modules (DIO, Ethernet, Audio ES8388) | Core/Stack only. Built-in Wi-Fi/BLE/audio already cover these. |
| EOL parts (U201 Cap, OV2640 cam) | Do not design around dead SKUs. |

## Ranked top 10 (customer usefulness × difficulty × cost × KS potential)

1. **B2 — LoRa + GPS Meshtastic (Cap LoRa-1262, $14.50)** — the only feature a phone cannot do offline. Headline.
2. **B1 — Rotary encoder + RGB approval knob (Unit Encoder, $7.95)** — the tactile hero visible in every video.
3. **A2 — Physical AI approvals (existing)** — the reason Piblo exists. Keep the story tight.
4. **A1 — Push-to-talk voice with fixed quality (existing)** — the daily loop. Voice quality is the #1 software risk.
5. **B3 — PDM external mic ($3.50)** — cheapest audio upgrade, makes voice notes credible.
6. **A4 — IR remote (existing IR emitter)** — free, demoable, "replaces the TV remote battery drawer".
7. **B4+B5 — ENV + PIR sensor pack (~$10)** — smart-home credibility, "Piblo senses my room".
8. **A6 — Offline voice notes + tasks (existing)** — "no signal, still useful" pairs with LoRa.
9. **B6/B7 — NFC/RFID ($5–19)** — access/check-in, maker + field story.
10. **C1 — Thermal ($65)** — the wow stretch, not the core promise.

## The coherent product experience (v1)

Not 30 features. One morning, one device:

> You wake up. Piblo (with Cap LoRa) shows today's approvals waiting. You twist the encoder knob to approve an agent action. You ask "what's the room like" — ENV-IV answers 21°C, 48%. You hold the talk key, dictate a note offline. Out the front door with no signal, your location shares over Meshtastic to your walking group; a pothole-free route breadcrumb logs. Home again, PIR + IR: the TV wakes, the AC responds. All one pocket computer. All £45 of hardware. Zero subscriptions.

Everything in that paragraph maps to a real component above. That is the campaign page.

## Sequencing

- **Now (no purchase):** Tier A firmware promotion (A3 to Home, A4 IR, A5 IMU), voice quality (A1 fix from branch #95).
- **Next (buy 1× Cap LoRa-1262 + Hub + Encoder + Mic):** prototype B1/B2/B3/B8 — proves the ecosystem story on camera.
- **Kickstarter tiers:** Base (ADV+Piblo firmware) / Knock (Knob+Mic+Hub pack) / Mesh (Cap LoRa + Sensor pack) / Premium (Thermal + TimerCam companion). One Cap default; offer the other as a swap, never both.
- **Later:** C2/C3 companion devices as a v2 family.

## Risks / honest constraints

- **One EXT socket:** LoRa and NFC Caps cannot coexist. The campaign must pick a default (recommend LoRa) and present NFC as the swap, transparently.
- **Firmware size:** RadioLib + Meshtastic + encoder/mic drivers must fit 1,507,328 B/slot. Budget libraries; Meshtastic full stack is the fattest — prototype first, before promising.
- **Battery:** LoRa TX (163mA bursts) + GPS (33mA) + Wi-Fi (132mA) on a 1500mAh pack. Duty-cycle everything; publish honest battery numbers.
- **Antenna:** Cap LoRa needs the 108mm RP-SMA duck fitted — a chunky lump on a "pocket" device. The kit must include it and the case/render must show it.
- **EOL risk:** M5Stack EOLs fast (U201, A145, OV2640 already dead). Do not hard-dependency a campaign promise on a single SKU without a pinned alternative.
- **Stack Modules are a trap:** Module LLM / LTE / NBIoT look tempting in the catalogue but do not fit. The docs above document the incompatibility — reuse that table so nobody re-proposes them.
