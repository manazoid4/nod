# Piblo — Expansion Components Catalogue

*Every component below is a real M5Stack SKU with an official docs/shop URL. "Cardputer ADV fit" = direct plug unless stated companion/incompatible. Prices USD, shop list Nov 2026 — re-verify before campaign.*

## How to read this

- **Cap** — EXT 2.54-14P (2×7) screw-on. ONE at a time. M2×4mm screws, power-off to swap.
- **Unit** — HY2.0-4P Grove. ONE at a time; three parallel via Unit Hub.
- **Module (Stack)** — M5-Bus 2-connector stacking for Core/Stack. **Does NOT fit Cardputer ADV.**
- **Companion** — own ESP32-S3 computer. Talks to Piblo over Wi-Fi, not plugged in.

---

## 1. Cardputer ADV Caps (the only two that exist)

### Cap LoRa-1262 — U214 — $14.50 ★ buy first
- Docs: https://docs.m5stack.com/en/cap/Cap_LoRa-1262
- Shop: https://shop.m5stack.com/products/cap-lora-1262-for-cardputer-adv-sx1262-atgm336h
- Chips: SX1262 LoRa (868–923MHz, +22dBm, -147dBm, 3dBi RP-SMA) + ATGM336H-6N@AT6668 GNSS (50ch, <1.5m, 10Hz, 23s cold TTFF, ceramic antenna)
- Conn: EXT14P SPI + GPS UART + HY2.0-4P pass-through. 84×24×15.2mm, 22.1g ex-antenna. Must fit 108mm duck antenna (never power on without it).
- Power: TX burst DC5V@163.4mA; GPS 33.1mA.
- Libs: RadioLib (SX1262), TinyGPSPlus (GNSS), Meshtastic stack (official Cardputer Mesh Kit guide: https://docs.m5stack.com/en/guide/lora/meshtastic/cardputer_mesh_kit)
- Offline: Yes — fully (LoRa mesh + satellite GPS, no internet/PC).
- Notes: EOL predecessor U201 — do not buy. Occupies EXT socket.

### Cap CC1101 & NFC — U219 — $18.95
- Docs: https://docs.m5stack.com/en/cap/Cap_CC1101
- Shop: https://shop.m5stack.com/products/cap-cc1101-nfc-for-cardputer
- Chips: TI CC1101 (315/433/868/915MHz, +10dBm, 441m@58kbps, 3 antennas incl.) + ST25R3916 NFC (ISO14443A/B, FeliCa, ISO15693, reader/writer + card emulation)
- Conn: EXT14P SPI + HY2.0-4P. 84×24×19.7mm, 14.9g. Sleep 141µA, TX-max 96mA.
- Libs: RadioLib (CC1101), M5Unit-NFC (ST25R3916).
- Offline: Yes.
- Notes: **Cannot run Meshtastic** (not LoRa). Mutually exclusive with U214.

### Cardputer Mesh Kit — K152 — $48.00 (bundle)
- Docs: https://docs.m5stack.com/en/core/Cardputer_Mesh_Kit
- Shop: https://shop.m5stack.com/products/cardputer-mesh-kit-for-meshtastic-esp32-s3
- Includes: Cardputer ADV + U214 + duck antenna + M2 screws. Pre-flashed, Meshtastic-licensed.
- Use: buy the bundle for the campaign; sell ADV+U214 + Piblo firmware as the "Piblo Mesh" tier.

### Cardputer Accessory Kit v1.1 — A145-V033 — $9.95 (repair, not a feature)
- Docs: https://docs.m5stack.com/en/accessory/Cardputer_Accessory_Kit_v1.1
- Stamp-S3A + 1.14" screen. Sell as a £10 spare-parts add-on for the repairability story.

---

## 2. Grove Units — sensors & actuators (HY2.0-4P, direct fit)

| Component | SKU | Price | Chip / function | Size | Power | Use |
|---|---|---|---|---|---|---|
| **Unit Hub** | — | ~$4 | HY2.0-4P → 3× parallel I2C | ~30×24mm | passive | Run 3 Units at once |
| **Unit Encoder** | — | $7.95 | STM32F030, rotary + button + 2× SK6812 RGB | 32×24mm | ~5–15mA | Knob approval + visual status |
| **PDM Microphone Unit** | U089 | $3.50 | SPM1423 PDM MEMS | ~20×12mm | ~2mA | Far-field mic |
| Unit ENV-IV | U001-D | ~$6 | SHT40 + BMP280 (temp/hum/press) | 32×24×8mm | ~2mA | Climate + automation triggers |
| Unit ENV-III | U001 | $5.95–6.95 | SHT30 + QMP6988 | 32×24×8mm | ~2mA | Cheaper ENV equivalent |
| Unit ENV-Pro | — | ~$25 | BME688 (T/H/P/gas IAQ) | 32×24mm | ~10mA | Air-quality IAQ (slow 10.8s scan) |
| **Unit PIR** | U004 | ~$4 | Pyroelectric IR, 500cm, <60µA | 32×24×12.5mm | <60µA idle | Motion/occupancy |
| Unit CO2 | — | ~$25–35 | SCD40 (CO2 + T/H) | 32×24mm | ~15mA | Room air quality |
| Unit RFID2 | — | $4.95 | WS1850S 13.56MHz | 32×24mm | ~20mA | Tag/proximity (cheap NFC alt) |
| Unit RFID | U031 EOL | $12.50 | MFRC522 13.56MHz | 32×24mm | ~20mA | EOL — prefer RFID2 |
| Unit UHF-RFID | — | ~$40–60 | JRD-4035 UHF UART | 32×24mm | ~100mA | 12m inventory tags |
| Unit Relay | — | ~$5–8 | 1-ch relay | 32×24mm | coil ~30mA | Lamp/door switch (low-V demos) |
| Unit PLC | — | ~$15 | 6-ch IO | 32×24mm | ~30mA | Multi-relay / GPIO |
| Unit EXT.IO2 | — | ~$8 | STM32F030 8-ch IO I2C | 32×24mm | ~5mA | Extra GPIO for makers |
| Unit Servo | — | ~$8 | Servo PWM | 32×24mm | 100mA+ | Robot demos |
| Unit Thermal | U016 | $65.00 | MLX90640 32×24, 110°×75° | 32×24×8.6mm | 23mA | Thermal imaging (Premium) |

All Units: docs `https://docs.m5stack.com/en/unit/Unit_*`, shop search `shop.m5stack.com/collections/unit`. Libs: `m5stack/M5Unit-ENV`, `m5stack/M5Stack` examples, Adafruit/Sensirion libs. All offline-capable (I2C/UART/digital).

---

## 3. Cameras — honest split: plug-in vs companion

| Component | Price | Fit | Verdict |
|---|---|---|---|
| **Generic USB UVC webcam** (via USB-OTG) | $15–25 | USB-C OTG on ADV | **Recommended vision path.** QR scan, document/shelf photos. No M5Stack SKU needed. |
| ESP32 Camera Module (OV2640) U007 | $11.95 **EOL** | No official ADV mount | **Do not buy.** Dead SKU. |
| TimerCam / TimerCam-M (OV3660) | $19.95 | Own ESP32-S3 + battery | Companion (Wi-Fi). Timelapse, snap-to-note. |
| AtomS3R-CAM / -M12 (GC0308/OV3660 3MP) | ~$15–25 | Own ESP32-S3 | Companion (Wi-Fi). Better stills than TimerCam. |
| Unit-V (OV2640 + K210) | ~$30–50 | Own computer | D — on-device AI camera, second stack to maintain. PC-hub vision instead. |
| Module Camera B2M / Flash | — | M5-Bus / Stack | **No ADV fit.** Skip. |
| Camera Module 8MP for LLM630 (SC850SL) | $32.90 | Module LLM kit only | **No ADV fit.** Skip. |

Object detection: run on the PC hub (existing `llm.py`/`executor.py`), not on the S3FN8. QR scan = USB UVC path above.

---

## 4. Audio

| Component | Price | Fit | Verdict |
|---|---|---|---|
| Built-in ES8311 + NS4150B + 1W + 3.5mm | — | Built-in | **Already Piblo's audio.** Nothing to buy. |
| **PDM Microphone Unit (U089)** | $3.50 | Grove | **Best $3.50 in the ecosystem.** Far-field upgrade. |
| Audio Module (ES8388) | ~$15 | M5-Bus Stack | **No ADV fit.** Duplicates built-in ES8311. Skip. |
| SPK HAT / DAC | — | Stack/Core | **No ADV fit.** Skip. |

---

## 5. Stack Modules — DO NOT buy for Cardputer ADV (documented for the record)

All M5-Bus stacking, need a Core/Stack base. No official Cardputer ADV adapter exists.

| Module | Price | Why it tempts | Why not |
|---|---|---|---|
| Module LLM (AX630C) | $49.90 (Kit $79.90 OOS) | Offline LLM/KWS/ASR/TTS | M5-Bus only, 54×54mm, 4GB — bigger than the Cardputer |
| COM.LTE (SIM7600G) | $79.00 | Cellular data | M5-Bus + SIM + subscription; use phone/PC instead |
| COMX NBIoT (SIM7020G) | ~$50 | NB-IoT | M5-Bus + SIM; same objection |
| LAN W5500 / PoE | ~$25 | Wired Ethernet | ADV already has Wi-Fi; M5-Bus |
| DIO / Relay Module | ~$10 | GPIO | Use Unit Relay/PLC (Grove) instead |
| CC1101 Module (855–925MHz) | $10.95 | Sub-GHz | M5-Bus; Cap CC1101 (U219) covers it properly |
| Module LoRa E220 / GPS v2.1 | $12–25 | LoRa/GPS | Cap LoRa-1262 (U214) covers both, official fit |

Anyone proposing these for Piblo v1 must first produce an official adapter or a custom bridge design — neither exists.

---

## 6. Companion devices (own computer, Wi-Fi paired)

| Device | Price | Role in Piblo family |
|---|---|---|
| AtomS3R | ~$15–25 | Desk IR blaster / presence node |
| AtomS3U | $12.50 | USB-A gadget / UVC source |
| AtomS3R-CAM | ~$25 | Camera node (see §3) |
| StickS3 | ~$20 | Wearable approval fob |
| TimerCam | $19.95 | Snap/timelapse node |
| RoverC Pro | $65.00 | Robot base (demo, niche) |

Family story is v2, not v1. Do not let it cannibalise the core campaign.

---

## 7. Shopping list (build these SKUs, in this order)

**Prototype kit (~$84):**
- Cardputer ADV (already owned) — $0
- Cap LoRa-1262 (U214) — $14.50
- Cap CC1101 & NFC (U219) — $18.95 *(buy for evaluation, choose ONE as campaign default)*
- Unit Hub — ~$4
- Unit Encoder — $7.95
- PDM Microphone Unit (U089) — $3.50
- Unit ENV-IV (U001-D) — ~$6
- Unit PIR (U004) — ~$4
- Unit RFID2 — $4.95
- Thermal U016 — $65 *(stretch; buy last)*
- USB UVC webcam — $15–25
- M2×4mm screws (pack) — $1
- Cardputer Accessory Kit v1.1 — $9.95 *(spares)*

**Campaign default recommendation:** ADV + U214 (LoRa) + Hub + Encoder + PDM Mic in the "Mesh" tier; U219 (NFC) as a free-swap add-on; ENV+PIR as the "Home Pack"; Thermal + TimerCam as Premium stretch.

**Never order:** U201 EOL Cap, U007 EOL camera, any M5-Bus Stack Module without a bridge design, LoRa Unit E220 (redundant), standalone GPS Unit (redundant with U214).

---

*Every SKU above was checked against docs.m5stack.com / shop.m5stack.com on 9 Nov 2026. "—" = price not captured in the official scrapes — treat as approximate and re-verify before quoting to backers.*
