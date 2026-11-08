# Piblo hardware research: 2026-11-08

Research only. No firmware, no product redesign. Every claim carries a URL.
Tags: **PROVEN** = shipping product or measured by a third party. **SPECULATIVE** = plausible, no evidence for Piblo's use.
Unit costs are **ASSUMPTIONS** (no supplier quotes obtained), marked "(assumption)". Where a price is sourced, it is labelled.

## Key findings (read first)

1. **Cardputer-ADV cannot report its own battery charge state or charging current.** M5 says so directly: https://docs.m5stack.com/en/arduino/m5cardputer/battery . This is the single biggest battery gap.
2. **ESP-NOW is fast and cheap, but its ceiling is low.** Measured one-way latency is 2 to 4 ms. A stop-and-wait round trip carrying commands can reach 40 ms median, with a P95 of 137 ms at 100 Hz (see ESP-NOW section).
3. **The closest comparable (Kode Dot) went from $129 campaign pledge to a $199 store price, with delivery moving to January 2027.** Its modules were added by backer vote and it is 2 chips and a new enclosure later. Lesson: fewer promises, locked dates.
4. **Audio is already good enough on Cardputer-ADV.** It has an ES8311 codec, a 65 dB SNR MEMS mic and a 1 W NS4150B speaker (https://docs.m5stack.com/en/core/Cardputer-Adv). Upgrade the battery and the satellites before the speaker.

---

## Top 10 ideas (ranked)

Scores: usefulness and originality are 1 to 5 (5 = best). Difficulty: 1 = easy, 5 = hard. Kickstarter appeal: 1 to 5.

| # | Idea | Useful (1-5) | Original (1-5) | UK unit cost at 500 (£) | Power impact | Difficulty (1-5) | KS appeal (1-5) | Proven vs speculative | Sources |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Desk approve/reject button satellite (ESP-NOW, coin cell, TX-only) | 5 | 3 | 5 (assumption) | Very low: TX bursts, deep sleep between presses | 2 | 3 | PROVEN parts and protocol; the product is SPECULATIVE | [Espressif coin-cell demo](https://deepwiki.com/espressif/esp-now/8.6-coin-cell-demo), [RichJ233 benchmarks](https://richj233.github.io/ESP32-wireless-link-benchmarks/) |
| 2 | Battery upgrade: charger + fuel gauge + protected pouch cell | 5 | 2 | 6 (assumption) | Adds BMS quiescent current, small | 3 | 3 | PROVEN (Kode Dot ships BQ25896 + CW2217) | [Kode Dot specs](https://kode.diy/), [MAX17048 guide](https://1c3d.com/howtos/battery-fuel-gauge-ics-max17048-bq27441) |
| 3 | Haptic buzzer / vibration satellite (wearable or desk) | 4 | 3 | 7 (assumption) | Receiver must listen: RX about 84 mA on ESP32-C3 | 3 | 4 | PROVEN (haptic motors ship in Kode Dot; ESP-NOW buzzers exist) | [ESP32-C3 datasheet](https://documentation.espressif.com/esp32-c3_datasheet_en.html), [wireless buzzer repo](https://github.com/otakenz/wireless_buzzer_system) |
| 4 | E-ink desk status satellite (today's approvals, next alert) | 4 | 4 | 18 (assumption) | Near zero: image holds without power | 3 | 4 | PROVEN category (M5 lists E-Paper products); Piblo fit SPECULATIVE | [M5 docs search index](https://docs.m5stack.com/en/core/Cardputer-Adv) |
| 5 | Voice pebble: remote MEMS mic satellite | 4 | 3 | 4 (assumption) | Medium while listening | 4 | 3 | PROVEN mic parts; ESP-NOW voice is SPECULATIVE at Piblo quality | [WLED mic hookup](https://mm.kno.wled.ge/WLEDSR/Digital-Microphone-Hookup/), [ESP-NOW walkie-talkie](https://hackaday.io/project/205897-esp32-walkie-talkie) |
| 6 | Magnetic and LEGO-compatible mount / accessory base | 3 | 2 | 2 (assumption) | None | 1 | 3 | PROVEN (Cardputer-ADV ships magnetic back and LEGO holes) | [Cardputer-Adv specs](https://docs.m5stack.com/en/core/Cardputer-Adv) |
| 7 | NFC tap-to-approve tag (sticker tags, not a reader) | 3 | 3 | 0.50 tags (assumption) | Negligible | 2 | 3 | PROVEN (Kode Dot ships NFC; 13.56 MHz tags are cheap) | [Kode Dot](https://kode.diy/), [Kode campaign story](https://kode.diy/news/kode-dot-kickstarter-campaign-story) |
| 8 | Door or presence sensor satellite (reed switch or PIR, coin cell) | 3 | 2 | 5 (assumption) | Very low | 2 | 2 | PROVEN (standard ESP-NOW sensor pattern) | [Espressif ESP-NOW docs](https://docs.espressif.com/projects/esp-now/en/latest/) |
| 9 | External speaker satellite (MAX98357A I2S amp + 3 W speaker) | 3 | 2 | 6 (assumption) | High while playing | 2 | 2 | PROVEN (3.2 W into 4 ohm at 5 V, [Adafruit](https://www.adafruit.com/product/3006)) | Adafruit link above |
| 10 | RGB ambient alert light bar satellite | 3 | 2 | 3 (assumption) | Medium; keep brightness low | 2 | 3 | PROVEN (Kode Dot ships an RGB LED) | [Kode Dot](https://kode.diy/) |

Also noted, not in top 10: a voice walkie-talkie over ESP-NOW (originality 4, usefulness 2, difficulty 5, SPECULATIVE). Source: [Hackaday.io walkie-talkie](https://hackaday.io/project/205897-esp32-walkie-talkie).

---

## Per-idea detail

### 1. Desk approve/reject button satellite
- A coin-cell, TX-only button. Espressif ships a coin-cell demo: a switch on a coin cell controls bulbs, with an estimated 65,000 packets on one CR2032 (figure from DeepWiki search snippet, not verified on the page; the page returned HTTP 429). https://deepwiki.com/espressif/esp-now/8.6-coin-cell-demo
- Use ESP-NOW with an application-level ACK and a sequence number. Espressif's send callback reports MAC-layer receipt only, not app delivery. Source: [xloge summary of Espressif docs](https://www.xloge.site/2026/10/esp-now-latency-range-and-packet-loss.html)
- Recommended parts: ESP32-C3 module (for example ESP32-C3-MINI-1), CR2032 holder, two tactile switches, optional LED. Keep the satellite TX-only so it never runs the RX path.
- Expected latency: about 3 to 4 ms radio RTT for a single press (see ESP-NOW section).
- Reusable repos: https://github.com/espressif/esp-now (examples/coin_cell_demo). Licence not verified in this session; check before reuse.

### 2. Battery upgrade (charger, fuel gauge, protected cell)
- Cardputer-ADV has a 1500 mAh battery and a power switch. Standby at 0.23 µA with the switch OFF; 120 mA operating; 132 mA on Wi-Fi; 155 mA on BLE. Source: https://docs.m5stack.com/en/core/Cardputer-Adv
- Kode Dot uses a BQ25896 PMIC (USB-C charge with power path and OTG) and a CW2217 fuel gauge. Source: https://kode.diy/
- TP4056 is the cheapest charger, but it has no power path and no load management. Buy the DW01A + FS8205A protected variant if you use it at all. Sources: [TP4056 guide](https://mischianti.org/tp4056-lipo-battery-charger-high-resolution-pinout-datasheet-and-specs/), [TP4056 with DW01A and FS8205A](https://github.com/Cyclone-92/TP4056-LiPo-charger-with-DW01A-and-FS8205A-MOSFET-protection)
- MAX17048 is a 4-wire fuel gauge with no sense resistor or calibration cycle. Source: https://1c3d.com/howtos/battery-fuel-gauge-ics-max17048-bq27441
- Recommended: BQ25896 (or BQ25895) + MAX17048 + a protected single-cell pouch with a PCM. Keeps the cell replaceable and the charge state visible.
- UN38.3: a lithium cell needs a UN38.3 test summary before air shipping. Source: https://batteryshipping.com/un38-3-requirements-explained-complete-guide-for-lithium-battery-shipping-compliance/ . A 1500 mAh cell at 3.7 V is about 5.6 Wh, far under the 100 Wh air limit cited at https://volttechinsights.com/post/un38-3-lithium-battery-shipping-regulations . Get the cell vendor's UN38.3 report before the first order.
- Reusable: TP4056 + DW01A board designs (see repo above). Licence not verified.

### 3. Haptic buzzer / vibration satellite
- Kode Dot ships a haptic LRA driver (AW86233) and a vibration motor. Source: https://kode.diy/
- ESP-NOW buzzer systems exist: https://github.com/otakenz/wireless_buzzer_system (ESP32-C3, up to 5 players). A DIY weekend build with a buzzer and vibration motor is documented at https://www.warrenblackwell.com/esp32-intro/
- Power: a receiver must listen. ESP32-C3 RX is about 84 mA (datasheet, 802.11b/g/n HT20). Source: https://documentation.espressif.com/esp32-c3_datasheet_en.html . Keep this node on USB or a larger cell, not a coin cell.
- Recommended: ESP32-C3 + LRA or coin motor + DRV2605L driver (assumption: common Adafruit part, not verified here).

### 4. E-ink desk status satellite
- M5 lists E-Paper products in its hot searches, so the panel class is supported in the ecosystem. Source: https://docs.m5stack.com/en/core/Cardputer-Adv (index page). Piblo-specific use is SPECULATIVE.
- E-ink keeps its image with no power. The satellite can wake on a timer or on an ESP-NOW push, redraw, and sleep. Power is dominated by refresh.
- Cost is the issue: a 2.13 to 2.9 inch panel is roughly £12 to £20 at volume (assumption; no quote obtained).

### 5. Voice pebble (remote mic)
- I2S MEMS mics: INMP441 and ICS-43434 both work with ESP32 and are reported as near-identical in practice. Source: https://mm.kno.wled.ge/WLEDSR/Digital-Microphone-Hookup/ and [AliExpress comparison](https://www.aliexpress.com/s/wiki-ssr/article/ics-43434-vs-inmp441) (low-authority source; treat as a hint). An ICS-43434 is reported to draw less power (same source).
- ESP-NOW payloads cap at 250 bytes in v1.0, 1,470 in v2.0. Source: https://www.xloge.site/2026/10/esp-now-latency-range-and-packet-loss.html . Raw 16 kHz audio is about 256 kbit/s, so the pebble must compress or stream to a Wi-Fi hub instead of ESP-NOW.
- The ESP-NOW walkie-talkie (compressed voice over ESP-NOW) shows it can work: https://hackaday.io/project/205897-esp32-walkie-talkie

### 6. Magnetic and LEGO-compatible mount
- Cardputer-ADV's base has magnets and LEGO-hole compatibility. Source: https://docs.m5stack.com/en/core/Cardputer-Adv
- Kode Dot's magnetic pogo connector gives charge-in and power-out plus two GPIOs. Source: https://kode.diy/
- Lowest-cost accessory path. Zero electronics.

### 7. NFC tap-to-approve tag
- Kode Dot added NFC and 125 kHz RFID to every unit after backer votes. Source: https://kode.diy/news/kode-dot-kickstarter-campaign-story
- A passive NFC sticker costs pennies, but it only works if the Cardputer has a reader. Cardputer-ADV has no NFC reader listed (checked the M5 spec list). A reader is an extra part, so this is a satellite (assumption: PN532 class, not priced).
- Piblo's physical approve/reject buttons already do this job. Treat NFC as a nice-to-have.

### 8. Door or presence sensor satellite
- Standard ESP-NOW sensor pattern. Power is low with deep sleep and an interrupt wake. Source: https://docs.espressif.com/projects/arduino-esp32/en/latest/api/espnow.html
- Reed switch or PIR, coin cell (PIR draws more; check the datasheet first).

### 9. External speaker satellite
- Adafruit MAX98357A breakout: 3.2 W into 4 ohm at 5 V (10% THD), mono I2S class D. Source: https://www.adafruit.com/product/3006 . Stereo version exists: https://www.adafruit.com/product/6513
- Cardputer-ADV already has a 1 W speaker. Upgrade only if an external room speaker is a real use case.
- Note: plugging a 3.5 mm headphone disables the internal speaker amp. Source: https://docs.m5stack.com/en/core/Cardputer-Adv

### 10. RGB ambient alert light bar
- Kode Dot ships a KTD2026 addressable RGB status LED. Source: https://kode.diy/
- Cheapest satellite. Power is driven by brightness; keep it low for battery life.

---

## ESP-NOW section (numbers)

Measured numbers, with the source and test scope. Compare within a study, not across studies.

| Test | Result | Scope | Source |
|---|---|---|---|
| S3 to C3 ESP-NOW one-way | 3.3 to 3.5 ms (S3 to C3), 3.1 to 7 ms (C3 to S3) | Typical; TIMEOUT events occurred | [RichJ233](https://richj233.github.io/ESP32-wireless-link-benchmarks/) |
| Dual S3 ESP-NOW RTT, on-board timing | Median 3.6 ms, P95 8.5 ms, P99 12.4 ms, max 23.8 ms; 2,000 of 2,000 valid | Board timer; excludes USB and PC | [RichJ233](https://richj233.github.io/ESP32-wireless-link-benchmarks/) |
| Dual S3 host-triggered RTT | Median 4.8 ms, P95 13.0 ms, P99 19.2 ms | Includes Python and USB | [RichJ233](https://richj233.github.io/ESP32-wireless-link-benchmarks/) |
| S3 to C3 closed loop, 100 Hz | Complete round trip median 38.8 ms, P95 137 ms, max 201 ms; deadline (10 ms) hit 7.7% | Stop-and-wait, bridged over UART and USB | [RichJ233](https://richj233.github.io/ESP32-wireless-link-benchmarks/) |
| Same, 75 Hz | Deadline hit 2.3%; many ESP_ERR_ESPNOW_NO_MEM | Queue overflow | [RichJ233](https://richj233.github.io/ESP32-wireless-link-benchmarks/) |
| Same, with latest-packet overwrite | Complete round trip median 14.6 ms, P95 43 ms; 24% within 10 ms | Keeps one active and one waiting packet | [RichJ233](https://richj233.github.io/ESP32-wireless-link-benchmarks/) |
| ESP-NOW vs Wi-Fi UDP, 2 m, ESP32 | ESP-NOW 2.35 to 2.57 ms, 0% loss; Wi-Fi UDP 105 to 113 ms, 1.4 to 2.8% loss | 500 samples per rate; preliminary; power-save not stated | [xloge summary of JAIIO 2026 paper](https://www.xloge.site/2026/10/esp-now-latency-range-and-packet-loss.html) |
| Range, ESP32-C6 PCB antenna | About 100% success to 150 m open; 60% at 300 m; under 50% at 125 m in forest | Espressif Developer Portal; one board type | [xloge summary](https://www.xloge.site/2026/10/esp-now-latency-range-and-packet-loss.html) |
| Long-range mode | About 100% to 450 m open; 40% at 900 m; about 10 kbps | Same source | same |
| Multi-node loss | Loss rose to 8.6% going from 1 to 4 senders (exoskeleton study, broadcast) | Abstract only | same |
| Indoor reliability, 8 nodes | About half reliable; walls and open space explain it | Department building | same |

**Read this as:**
- A satellite button to Cardputer: a few ms, in practice. The button press is one-way; that is the fast path.
- Anything with an acknowledged round trip at 10 ms rate fails. Keep command rates under about 20 Hz and use latest-value semantics.
- Multi-node: loss grows with senders. Two or three satellites is the realistic ceiling for v1, not "more ESP32s".
- Power: ESP32-C3 TX peak is 335 mA (802.11b at 21 dBm), RX 84 mA. Source: https://documentation.espressif.com/esp32-c3_datasheet_en.html . Espressif's current-consumption guide is at https://espressif.github.io/esp32-c3-book-en/chapter_12/12.2/12.2.4.html

**Per-module cost (assumption):** ESP32-C3 module £2.50 to £3.50 at 500; tactile switch £0.10; coin-cell holder £0.30; PCB and case £1.50 to £3. A button satellite lands around £5. A receiver with haptic driver lands around £7.

**Verdict:** more ESP32s is only better when each satellite does one job that the hub can't do, and only with a designed ACK and rate limit.

---

## Battery section (recommended parts)

| Need | Part | Notes | Source |
|---|---|---|---|
| Charger with power path | BQ25896 | USB-C, power path, OTG; used by Kode Dot | https://kode.diy/ |
| Fuel gauge | MAX17048 | 4-wire, no sense resistor | https://1c3d.com/howtos/battery-fuel-gauge-ics-max17048-bq27441 |
| Fuel gauge (Kode choice) | CW2217 | Used by Kode Dot | https://kode.diy/ |
| Cheap charger (satellites only) | TP4056 + DW01A + FS8205A | 1 A, protection in the board variant | https://microcontrollerslab.com/best-lipo-battery-charger-modules-buying-guide/ |
| Cell | Single-cell 3.7 V pouch, 1500 mAh, protected | Matches Cardputer-ADV capacity | https://docs.m5stack.com/en/core/Cardputer-Adv |

**Charging current:** Cardputer-ADV charges only with its power switch ON. Source: https://docs.m5stack.com/en/core/Cardputer-Adv

**Safety:** protected cell with PCM; keep to a single known cell; UN38.3 report from the vendor before shipping.

---

## Audio section (recommended parts)

| Need | Part | Cost (assumption unless noted) | Notes | Source |
|---|---|---|---|---|
| Codec (already on Cardputer-ADV) | ES8311 | n/a | Keep it | https://docs.m5stack.com/en/core/Cardputer-Adv |
| Amp (already on Cardputer-ADV) | NS4150B | n/a | 1 W with internal speaker | same |
| Mic (already on Cardputer-ADV) | Built-in MEMS, 65 dB SNR | n/a | Adequate for voice capture | same |
| External amp | MAX98357A | £3 to £4 | 3.2 W into 4 ohm at 5 V; mono I2S | https://www.adafruit.com/product/3006 |
| External mic (satellite) | ICS-43434 | £2 to £3 | Lower power reported; works with ESP32 | https://mm.kno.wled.ge/WLEDSR/Digital-Microphone-Hookup/ |
| External mic (alt) | INMP441 | £1.50 to £2.50 | Widely used | same |
| Speaker | 3 W, 4 ohm, small | £2 to £4 | Enclosure needed for bass | assumption |

Codec-based satellite (ES8311 + NS4150B) reuses the Cardputer-ADV audio path, but no source gives a satellite price. Assumption: £4 to £6.

Reference repo: https://github.com/lichen79/xiaozhi-cardputer-adv (ES8311 + NS4150B support on Cardputer-ADV; licence not verified).

---

## Three realistic prototypes

**P1. Desk approve/reject button satellite (1 day).**
- Parts: 1x ESP32-C3 dev board (about £5 retail, assumption), 2x tactile switches, CR2032 holder, breadboard, 3D-printed case.
- Est. cost: about £15 one-off.
- What it proves: press-to-screen latency, an ACK/sequence scheme, and CR2032 life. Measure with the RichJ233 method (on-board timing).
- Acceptance: 100 presses, zero lost after ACK retry, median press-to-Cardputer under 10 ms.

**P2. Battery board test rig (2 days).**
- Parts: BQ25896 breakout, MAX17048 breakout, protected 1500 mAh pouch cell, load resistor or ESP32-C3, USB-C.
- Est. cost: about £25 to £35.
- What it proves: charge path, state-of-charge accuracy against a coulomb count, and whether the gauge reads correctly at load.
- Acceptance: SoC within 5% after one full discharge, no over-temperature, protection tripped at the cutoff.

**P3. Haptic buzzer satellite (1 day).**
- Parts: ESP32-C3 dev board, coin or LRA vibration motor, motor driver, USB supply.
- Est. cost: about £12.
- What it proves: receiver-side wake on ESP-NOW packet and a real haptic cue for a pocket or desk alert.
- Acceptance: buzz within 50 ms of the send, with receiver RX current measured.

---

## Comparison with other projects (where Piblo can beat them)

- **Kode Dot** (closest): pocket programmable ESP32-P4 device with AMOLED, IR, NFC, RFID, haptics, modules, $199 store price. Strength: capability and community apps. Weakness: 2 chips, first-time team, "next batch January 2027" and modules added by vote. Source: https://backerguardian.com/campaign/kode-dot , https://kode.diy/shop . Backer count conflicts across sources (8,646 on BackerGuardian versus 16,144 on kode.diy's own story). Use the creator's figure only with attribution. Source: https://kode.diy/news/kode-dot-kickstarter-campaign-story
- **Flipper Zero**: a GPIO header and expansion module ecosystem with third-party boards. Lesson: a mechanical standard (pogo or header) lets others build accessories. Source: https://1c3d.com/howtos/flipper-zero-hardware-addons-compared
- **Rabbit R1**: a $199 AI gadget that reviewers called a failure at almost everything, with terrible battery life. Lesson: a device must beat the phone at its one job. Piblo's buttons-plus-alerts job is a clear gap. Source: https://www.engadget.com/rabbit-r1-review-a-199-ai-toy-that-fails-at-almost-everything-161043050.html
- **Cardputer-ADV** (M5): already has ES8311, a 1 W speaker, magnets, LEGO holes and a Grove port. Its weakness is no battery readout. Piblo's opportunity: the battery readout and the satellite ecosystem. Source: https://docs.m5stack.com/en/core/Cardputer-Adv

Opportunity to beat them: a satellite-first approach with one job per satellite, a visible battery state, and a fixed price with a locked date.

---

## Engineering recommendations for the lead

1. Build satellites as ESP-NOW TX-only where possible (button, sensor). Receivers (buzzer) get a USB or larger cell, not a coin cell.
2. Add an application ACK, a sequence number and latest-value overwrite. Do not run stop-and-wait above 20 Hz. The 75 Hz test failed on queue overflow.
3. Cap v1 at 2 or 3 satellites. Loss grows with senders.
4. In the next hardware revision, add BQ25896-class charging and a MAX17048 fuel gauge so the Cardputer can show battery state.
5. Keep the existing ES8311 audio path. Do not redesign audio for v1. Add an external MAX98357A only if a room speaker is a confirmed use case.
6. Use a protected single-cell pouch and get the vendor's UN38.3 report before the first order.
7. Copy the magnetic and LEGO-hole mount approach for accessories: near-zero cost, proven on Cardputer-ADV.
8. Ship with fewer promises and a locked date. Kode Dot's stretch goals and its January 2027 delivery show the cost of open scope.

---

## Source notes

- Repo licences were not checked in this session, except where stated. Check each licence before reuse.
- The Espressif coin-cell figure (65,000 packets) comes from a search snippet; the page itself returned HTTP 429.
- Most unit costs are assumptions. Get supplier quotes before any BOM decision.
