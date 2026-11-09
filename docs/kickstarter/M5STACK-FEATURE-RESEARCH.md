# Piblo — M5Stack Feature Research

*Research date: 9 Nov 2026. Sources: https://docs.m5stack.com/en/products , https://shop.m5stack.com , https://docs.m5stack.com/en/core/Cardputer-Adv . Prices USD, shop list Nov 2026 — verify before any Kickstarter promise. No components purchased, no firmware changed.*

## 0. Baseline: what Cardputer ADV already has (no accessory)

Cardputer-Adv (SKU K132-Adv, $29.90 shop): ESP32-S3FN8 @240MHz, 1.14" ST7789V2 240×135, 56-key keyboard, ES8311 codec + NS4150B + 8Ω@1W speaker + MEMS mic (SNR 65dB) + 3.5mm headphone jack, BMI270 6-axis IMU, 1× IR emitter, microSD slot, 1500mAh battery, HY2.0-4P Grove + EXT 2.54-14P (2×7). Docs: https://docs.m5stack.com/en/core/Cardputer-Adv

Key physical constraints for everything below:
- **One EXT socket.** Only ONE Cap (LoRa-1262 or CC1101) can be fitted at a time. Screwed with M2×4mm, power-off to swap (not hot-swap).
- **One Grove socket** (HY2.0-4P). Only ONE Unit at a time without a hub.
- Caps expose a pass-through HY2.0-4P so Grove + Cap can coexist.
- Battery: 1500mAh, Wi-Fi ~132mA / BLE ~155mA (official). Every add-on draws from the same pack.
- Firmware budget: 1,507,328 B per OTA slot (partitions.csv). Library size matters.

## 1. The official "For Cardputer-Adv" category is exactly 2 products

Docs browse `For Cardputer-Adv → Wireless` and shop collection `for-cardputer-adv` both list **only**:
1. Cap LoRa-1262 (U214) — https://docs.m5stack.com/en/cap/Cap_LoRa-1262
2. Cap CC1101 (U219) — https://docs.m5stack.com/en/cap/Cap_CC1101

There is **no official "Cap RFID"**. No other Cap exists as of Nov 2026. The old U201 LoRa+GPS Cap is **EOL**, replaced by U214 (adds HY2.0-4P, shielding, RP-SMA, +22dBm, RF-switch via IO expander).

| Product | SKU | Price | Chips | Connection | Meshtastic |
|---|---|---|---|---|---|
| Cap LoRa-1262 | U214 | $14.50 | SX1262 + ATGM336H/AT6668 GNSS | EXT 14P + HY2.0-4P + RP-SMA | Yes (via Mesh Kit / flash) |
| Cap CC1101 & NFC | U219 | $18.95 | TI CC1101 + ST25R3916 NFC | EXT 14P + HY2.0-4P + RP-SMA | No (not LoRa) |
| Cardputer Mesh Kit | K152 | $48.00 | ADV + U214 bundle | pre-assembled | Yes (licensed, pre-flashed) |
| Cardputer Accessory Kit v1.1 | A145-V033 | $9.95 | Stamp-S3A + screen (repair) | FPC/headers | N/A |
| LoRa+GPS Cap (old) | U201 | $14.50 EOL | SX1262 + AT6668 | EXT 14P, SMA | Yes* (EOL — do not buy new) |

Mesh Kit: https://docs.m5stack.com/en/core/Cardputer_Mesh_Kit — includes green ADV + U214 + duck antenna + M2 screws + hex key. Officially licensed Meshtastic registration (`meshtastic-reg.m5stack.com`). Standalone ADV+U214 flashed manually also works but is not the licensed bundle.

Accessory Kit v1.1: https://docs.m5stack.com/en/accessory/Cardputer_Accessory_Kit_v1.1 — repair kit only (Stamp-S3A + 1.14" screen), not a feature expansion. Useful as a Piblo spare-parts / repair story, not a selling feature.

## 2. Feature-by-feature (all 10 requested areas)

For each: component, customer value, Piblo integration, hardware/libs/deps, cost, power/size/battery, Cardputer ADV compatibility, offline vs PC/internet.

### 2.1 Personal productivity — reminders, alarms, timers, voice notes, offline tasks

**Existing hardware is sufficient. No accessory needed.**
- Timers/alarms/reminders already exist in firmware (`flowtools` under WORK in FEATURE_INVENTORY.md: Focus timer, Sprint, Tasks, Reminders). microSD already gives offline persistence.
- What Piblo adds: schedule them from voice ("remind me at 3pm"), surface via Alerts/Buddy, sync to Core inbox. Pure software.
- Cost: $0. Power: negligible (ESP32-S3 + existing 1500mAh). Offline: yes, tasks persist on-device.
- Libraries: none new. Existing M5Unified + ArduinoJson + WebSockets.

**Gap to close:** today these are buried one level deep (`flowtools` under WORK, Moved per inventory). Promotion to Home-level is software, already planned (New Home: big talk circle).

### 2.2 AI interaction — approval, multi-agent, voice, local AI, persistent assistant

**Physical agent approval/rejection — already core, no new hardware.**
Piblo's differentiator is `approvals.cpp` + host `authority.py` (fail-closed, 60s timeout, Fn+H Halt/Pause). Y/N on keyboard is the approval hardware. No encoder/button accessory needed for the MVP story — the 56-key keyboard IS the physical control.

**Voice commands — already present, quality is the gap.**
ES8311 mic + speaker + 3.5mm jack built in. The blocker is TTS latency/quality (ledger #4: 4.4s robotic), not hardware. Local-first Kokoro + streaming (agents/nod-voice branch #95) is the fix, not new hardware.

**Local AI integrations — M5Stack Module LLM (AX630C) is real but INCOMPATIBLE as a plug-in.**
- Module LLM: AX630C, 3.2 TOPS, 4GB, KWS/ASR/LLM/TTS, $49.90 (Kit $79.90, OOS Nov 2026). Docs: https://docs.m5stack.com/en/module/Module_LLM
- Interface: M5-Bus (2×10-pin stacking for Core/Stack), **NOT** HY2.0-4P/EXT14P. There is no official Cardputer ADV adapter. Power ~5V/2A class, size 54×54mm — larger than the Cardputer itself.
- Verdict: **D — experimental / incompatible plug-in.** Would need a custom bridge board + UART/SPI hack. Do not promise for Kickstarter. Piblo's local-AI story is "hub on your PC does the LLM" (existing architecture), not on-device LLM.

**Multi-agent control — software (host `executor.py`/`jobs.py` + device agents hub). No hardware.**

**Persistent assistant — microSD + Core memory already. No hardware.**

### 2.3 Communications — LoRa, Meshtastic, GPS sharing, offline/emergency

**Cap LoRa-1262 (U214) — $14.50 — ★ THE headline expansion.**
- Component: SX1262 LoRa (868–923MHz, +22dBm, -147dBm RX, 3dBi RP-SMA) + ATGM336H-6N@AT6668 GNSS (50ch, <1.5m CEP50, 10Hz, TTFF 23s cold / 1s hot, built-in ceramic antenna). Size 84×24×15.2mm, 22.1g ex-antenna (+108mm duck antenna). Power: LoRa TX DC5V@163.4mA, GPS 33.1mA.
- Customer can do: send/receive Meshtastic mesh messages from the keyboard, see GPS position on map in Meshtastic app, share location, emergency offline comms where phone signal is absent. With Piblo firmware: approval prompts relayed over LoRa, voice-note metadata + location breadcrumbs, SOS broadcast.
- Integration: Cap uses EXT14P SPI (LoRa_NSS G5, MISO G39, MOSI G14, SCK G40, BUSY G6, IRQ G4, RST G3) + GPS UART (TX G15, RX G13). RadioLib driver (`jgromes/RadioLib`, already the official example lib). Meshtastic firmware exists officially for Cardputer Mesh Kit.
- Offline: **fully offline** (LoRa + GPS need no internet/PC). This is the killer feature.
- Compatibility: **direct plug, official.** But occupies the EXT socket — cannot also run Cap CC1101 at once.
- Libraries: RadioLib (SX1262), TinyGPSPlus (GNSS), Meshtastic mesh stack (for full Meshtastic).
- Cost/power impact: +$14.50, +22g + antenna, TX bursts 163mA — significant vs 1500mAh (budget ~30–60 min TX-equivalent if continuous, far more in practice duty-cycled). GPS ~33mA continuous.

**LoRa Unit (U170, E220) — $33.00 — NO, not needed.**
Grove LoRa Unit (433MHz) duplicates the Cap at worse price/range. The Cap is strictly better for Cardputer ADV. Do not recommend.

**GPS via Unit ($~5–12 class) — NO, Cap GNSS wins.**
Unit GPS (AT6668) duplicates what U214 already integrates. Redundant.

**Module LTE/NB-IoT (COM.LTE SIM7600G $79, COMX NBIoT SIM7020G) — Stack Modules, incompatible.**
M5-Bus stacking, 54×54mm, 5V rail, needs SIM + subscription. No official Cardputer ADV fit. D — incompatible. If cellular is wanted, do it via the PC hub/phone, not on-device cellular.

### 2.4 Smart home — IR remote, environmental, motion, smart control

**Built-in IR emitter — already there, $0.**
Cardputer ADV has 1× IR emitter. TV/AC/speaker control via IR blast is firmware-only (IRremoteESP8266 or projectIR). Offline: yes. This is an A-tier feature (existing hardware) for the roadmap.

**Unit ENV-IV (U001-D) — $~6 — temp/humidity/pressure.**
SHT40 (0x44) + BMP280 (0x76), I2C via HY2.0-4P, 32×24×8mm, 3.9g, low-power. Customer: "what's the temp/humidity here", log to notes, trigger automations ("if >26°C remind me to open window"). Offline: yes. Lib: `m5stack/M5Unit-ENV` (official).
- ENV-III (SHT30+QMP6988) $5.95–$6.95 is the cheaper equivalent; ENV-IV is the current-gen. Either works — same footprint.
- ENV-Pro (BME688) adds gas/IAQ (10.8s scan) — better air story, pricier, slower. Optional upgrade.

**Unit PIR (U004) — ~$3–5 — motion detection.**
Pyroelectric IR, 500cm, <100°, <60µA idle, 32×24×12.5mm, 5.1g. Customer: occupancy detection, "anyone home?" checks, security alerts, motion-triggered voice note. Offline: yes. Lib: none (digital in).

**UV/CO2/eCO2 Units — CO2 Unit (SCD40-based class) ~$25–35 — air quality.**
CO2 + temp + humidity in one. Customer story: "is this room stuffy?", meeting-room CO2 checks. Worth including as a premium sensor but pricey vs ENV. Lib: Sensirion SCD4x.

**Unit Relay / PLC — smart-device control.**
Unit Relay (1-ch, ~250V/10A class) and Unit PLC (6-ch) let Piblo switch mains/relay outputs. Offline: yes (local switching). Customer: lights, kettle, doorbell chime. Cost ~$5–15. Note: mains = safety/regulatory story for Kickstarter — keep to low-voltage/USB relay demos for consumer safety, or skip mains in the campaign.

**Thermal Camera Unit (U016, MLX90640) — $65.00 — premium wow-factor.**
32×24, 110°×75°, -40–300°C, ±1.5°C, 23mA, I2C 0x33, 32×24×8.6mm, 5.1g. Customer: spot overheating, night vision-lite, "is the pipe hot", fun thermal photos. Offline: yes. Lib: `m5stack/M5Stack` thermal example. At $65 it is 2× the Cardputer price — bundle as a Premium tier, not base.

**BLE/Zigbee/Ethernet Modules — not Cardputer-direct.**
M5-Bus stacking modules (DIO, Ethernet W5500, etc.) need Core/Stack bases. Cardputer ADV already has BLE + Wi-Fi built in, so BLE smart-home is firmware-only. Zigbee would need a separate bridge — D/experimental, out of scope.

### 2.5 Audio — better recording, playback, notifications, external mic, headphones

**Already equipped — this is Piblo's home turf.**
ES8311 + MEMS mic (65dB SNR) + NS4150B + 1W speaker + 3.5mm jack built in. Nothing to buy.

**PDM Microphone Unit (U089, SPM1423) — $3.50 — stereo/directional mic option.**
Digital PDM mic via HY2.0-4P. Customer: far-field recording, interview mode, better voice notes. Cheap, tiny, low-power. **This is the best $3.50 in the entire ecosystem for Piblo.**
Docs: https://shop.m5stack.com/products/pdm-microphone-unit-spm1423

**Audio Module (ES8388, Stack Module) — $~15 — NOT Cardputer-direct.** M5-Bus, for Core. Duplicates built-in ES8311. Skip.

**SPK HAT / DAC — no.** Built-in amplification already.

**Voice quality fix is software** (Kokoro local TTS, streaming — branch #95), not hardware. Headphones = existing 3.5mm jack, $0.

### 2.6 Vision — cameras, QR/barcode, image capture, object detection

**QR/barcode scanning — existing hardware + software. A-tier.**
Cardputer already has QRCode lib (`ricmoo/QRCode@0.0.1` in platformio.ini) for generation. Scanning is camera-dependent (see below), but URL/vCard/Wi-Fi QR display + camera-less workflows (type in URL) work today. QR generation = $0, already in lib_deps.

**USB UVC camera (generic, via EXT/USB) — the pragmatic vision path.**
ESP32-S3 USB-OTG UVC (4-bit/8-bit parallel DCMI) + a $15–25 USB webcam = QR scan, shelf/document photos, visual AI notes. Offline: capture offline, visual AI via PC hub. This is cheaper and more useful than M5Stack's own cameras for a pocket device.

**ESP32 Camera Module (OV2640, U007) — $11.95 EOL — do not buy.**
End-of-life in official store. No official Cardputer ADV mount.

**TimerCam / TimerCam-M (OV3660 fisheye) — $19.95 — standalone, not Grove-paired.**
TimerCam is its own ESP32-S3 camera + battery + display unit, not a Grove unit. It can be a **companion Piblo Snap device** (paired over Wi-Fi) but not a plug-in for the Cardputer. Customer: timelapse, motion-triggered captures, "snap a photo of this" → sent to Piblo core for captioning. Cost ~$20. Verdict: B/C — companion device, not expansion. Cool story, adds a second device.

**AtomS3R-CAM / -M12 (GC0308/OV3660, 3MP) — $15–25 class — companion, not plug-in.**
Atom-form-factor, USB-C, own ESP32-S3. Same verdict as TimerCam: a Piblo Camera companion over Wi-Fi, not a Cardputer Cap/Unit.

**Unit-V / AI camera (OV2640, face/object) — ~$30–50 — D.**
Unit-V is a standalone K210 AI camera. Interesting for on-device object detection but another whole computer, another stack to maintain. D/experimental.

**Object detection — do it on the PC hub, not on the ESP32-S3.**
Cardputer captures (USB cam), hub runs the vision model (existing `llm.py`/`executor` architecture). On-device inference on S3FN8 (8MB flash, no PSRAM beyond internal) is too constrained for anything beyond QR.

### 2.7 Physical controls — encoder, buttons, haptics, RGB, programmable

**Unit Encoder — $7.95 — the best physical UX upgrade.**
30-position rotary encoder + button + 2× SK6812 RGB LEDs, STM32F030 + HY2.0-4P, 32×24mm class. Customer: scroll with a real knob, push-to-approve (tactile YES), RGB status ("listening=blue, thinking=amber, approval needed=pulsing red"). Offline: yes. Lib: M5Unit-Encoder (official). This makes Piblo feel like a product, not a dev board. ★
Docs: https://shop.m5stack.com/products/encoder-unit

**Built-in keyboard + buttons — already the primary control.**
56-key keyboard with Fn/Ctrl/Opt/Alt is the approval + typing surface. No additional buttons needed.

**Unit (RGB LED / LED) — $~2–3 — status light.**
SK6812 RGB via HY2.0-4P. But Encoder already includes 2× RGB LEDs — buy Encoder, not standalone RGB.

**Haptics — no M5Stack haptic/vibration Unit identified.**
No official vibration motor unit in the catalogue. D — would need a custom breakout (GPIO-driven motor via EXT/Grove). The built-in speaker chime (Alerts/Buddy priority sound table) covers alerting today.

**8Encoder / EXT.IO2 — overkill.**
8-channel IO expansion (STM32F030, I2C) — useful for DIY GPIO, not customer-facing. D for the product, fine for makers.

### 2.8 Developer tools — serial, GPIO, diagnostics, automation triggers, remote agent

**Serial monitoring — already via USB-C + `monitor_speed=115200` in platformio.ini.** $0.

**GPIO control — EXT 2.54-14P header is exposed.** UART/I2C/SPI/GPIO available. Unit EXT.IO2 ($~8) extends to 8-ch IO if a customer needs more pins than the 14P exposes.

**Hardware diagnostics — BMI270 IMU already built in.**
Shake-to-wake, motion-triggered alerts, "dropped it" detection, orientation-based UI (rotate = different view). All $0, firmware-only. E.g. shake the device to trigger an approval ping.

**Automation triggers — existing hub (`executor.py`, `jobs.py`, webhook alerts).** Sensor Units (PIR/ENV) feed these. Software.

**Remote agent management — already the core use case (Core over Wi-Fi/Tailscale).** No new hardware.

### 2.9 Location and outdoor — GPS, navigation, geofencing, tracking, environmental

**Covered by Cap LoRa-1262's built-in GNSS** (see 2.3). Multi-GNSS, 50ch, 1.5m, 10Hz. Customer: trail breadcrumbs, geofenced reminders ("when I get to work, show my day"), lost-device ping, Meshtastic map sharing. Offline: GPS is satellite (no internet), LoRa sharing is offline mesh. ALL of 2.9 collapses into the $14.50 Cap.
- Standalone GPS Unit is redundant (Cap includes it).
- Environmental outdoor: same ENV/PIR Units as 2.4.

### 2.10 Modular expansion — other interesting accessories

**Unit Hub (HY2.0-4P → 3×) — ~$4 — the enabler that unlocks everything.**
Expands ONE Grove port into three parallel (same I2C bus, same addresses). Customer: run ENV + PIR + mic simultaneously, or ENV + Encoder + Relay. This is what turns "one accessory at a time" into a real pocket sensor kit. Must be in the ecosystem.
Docs: https://docs.m5stack.com/en/unit/Unit_Hub

**Unit RFID (MFRC522) / Unit RFID2 (WS1850S, $4.95) — access control.**
13.56MHz NFC via Grove. Customer: tap to unlock/check in, tag luggage, smart-lock trigger. Offline: yes. BUT Cap CC1101 already includes a far better NFC front-end (ST25R3916) — choose Cap CC1101 for NFC, Unit RFID2 for cheap Grove NFC.

**Unit UHF-RFID (JRD-4035, UART) — long-range tag reading.**
12m-class inventory (warehouse, asset tracking). ~$40–60 class. B/C — niche, but a genuine differentiator for a "field computer" story.

**Servo / StepMotor Units — makers, not consumers.**
Servo ($~8) + StepMotor (5V, TMC2209-class) for robotics. D for the Piblo consumer story; keep as maker-tier.

**Atom / AtomS3R / StickS3 — companion devices, not expansions.**
AtomS3R ($12.50), AtomS3U ($12.50, USB-A), StickS3 — each an ESP32-S3 mini-computer. As Piblo companions: Atom = IR blaster desk remote, Stick = wearable approval fob, AtomS3U = USB gadget. C — interesting but scope-creep for Kickstarter v1.

**RoverC Pro ($65, w/o StickC) — robot base.** D — fun but a different product.

**Cardputer Accessory Kit v1.1 ($9.95) — repair kit, include as a £10 add-on** for the "repairable product" story (replace screen/Stamp).

## 3. Compatibility rules (memorise before ordering anything)

| Type | Interface | Cardputer ADV fit |
|---|---|---|
| **Cap** | EXT 2.54-14P (2×7) | **Direct plug (1 at a time)** |
| **Unit** | HY2.0-4P Grove (I2C/UART/GPIO) | **Direct plug (1 at a time, 3 via Hub)** |
| **Module** (Stack) | M5-Bus 2-connector stacking | **No — needs Core/Stack base** |
| **Atom/Stick/Core** | Own computer + own Grove | Companion over Wi-Fi, not plug-in |
| **TimerCam/Unit-V** | Own computer | Companion over Wi-Fi/cable, not plug-in |

Module LLM, COM.LTE, COMX NBIoT, LAN W5500, DIO, Audio ES8388 — all Stack Modules. **None plug into Cardputer ADV.** Any doc that implies they do is wrong. Workarounds (custom Grove breakout + level shifting) are D-tier engineering, not product features.

## 4. Power & size budget (1500mAh reference)

| Add-on | Current | Size | Weight | Daily-driver impact |
|---|---|---|---|---|
| Cap LoRa-1262 (idle/RX) | Low (duty-cycled) | +15.2mm thick | +22g | None |
| Cap LoRa-1262 (TX) | 163mA bursts | +108mm antenna | +~5g | Budget TX duty cycle |
| Cap LoRa-1262 (GPS) | 33mA | — | — | ~45h continuous* |
| Unit ENV-IV | ~2mA | 32×24×8 | 3.9g | None |
| Unit PIR | <60µA idle | 32×24×12.5 | 5.1g | None |
| Unit Encoder | ~5–15mA (LEDs) | 32×24mm | ~4g | Minimal |
| PDM Mic Unit | ~2mA | 20×12mm | ~1g | None |
| Thermal U016 | 23mA | 32×24×8.6 | 5.1g | Noticeable if streaming |
| CC1101 (TX max) | 96mA | +19.7mm | 14.9g | Budget duty cycle |
| CC1101 (sleep) | 141µA | — | — | None |

*GPS continuous on 1500mAh alone; in practice GPS is intermittent.

## 5. What to buy first (evidence-based, not hype)

1. **Cap LoRa-1262 ($14.50)** — GPS + Meshtastic = the offline pocket computer story. Owns the EXT socket; buy before anything else that needs it.
2. **Unit Hub ($4) + Unit Encoder ($7.95) + PDM Mic Unit ($3.50)** — $15.45 turns the keyboard into a knob + better mic + 3 simultaneous sensors.
3. **Unit ENV-IV ($6) + Unit PIR ($4)** — the smart-home/environment kit.
4. **Cap CC1101 ($18.95)** only if NFC + sub-GHz RF (garage door, access) is the chosen lane — it is mutually exclusive with Cap LoRa-1262. Pick ONE Cap as the Kickstarter default (recommend LoRa).
5. Thermal ($65) as a stretch/premium add-on. TimerCam (~$20) as a companion-device stretch goal.

**Do not buy:** Module LLM, COM.LTE, NBIoT, LoRa Unit E220, standalone GPS Unit, Audio Module ES8388, EOL U201, EOL OV2640 camera.

---

*Evidence: official docs/shop URLs in-line per product. Prices were shop list prices Nov 2026. Power/size from official Specs tables. "Incompatible" = no official fit, not "might work with a hack".*
