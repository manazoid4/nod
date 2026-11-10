# Piblo Pro: processor shortlist and measurement plan (10 Nov 2026)

**Status: Research only.** No processor, price, dimensions, battery life, standalone features or production software stack is committed. Do not copy these exploratory claims as shipped features to piblo.co.uk or Kickstarter.

## Product separation
- **Piblo Standard:** current Cardputer ADV / ESP32-S3 prototype, small screen + real keys, Piblo Core on Windows. Preserve existing firmware and Android companion progress.
- **Piblo Pro:** a cleaner, larger-screen, richer-audio device. Goals: reduce dependence on a PC, stronger local privacy, responsive interactions. Need to establish whether local Linux genuinely improves the user's tasks enough to justify cost and power.

## Candidate hardware
| Route | Silicon | Development module price reference, 10 Nov 2026 | Best reason to choose | Main limitation |
| --- | --- | --- | --- | --- |
| **A – Value Pro** | ESP32-P4 + ESP32-C6 | Waveshare P4+C6 core board $9.99–$10.99, dev/test touchscreen boards cost more | Touch UX, mic, peripherals and radio at low board cost; offload advanced actions to PC/phone | Not a Linux-class machine; cannot promise strong on-device conversational models |
| **B – Budget Linux Pro** | Rockchip RK3566 + ESP32-C6 | Luckfox Core3566 Lite (2GB, no eMMC/wireless) $77.99 | Linux with 4×A55 and low-power MCU for alerts/wake | Lower NPU power; more memory, storage, display, PMIC and thermal engineering |
| **C – Independent Pro** | Rockchip RK3576 + ESP32-C6 | Seeed RK3576 4GB/32GB SOM $130 | Linux 8-core and 6 TOPS NPU; on-device ML experiments feasible | High SOM cost, heat, idle power, boot/suspend complexity, larger battery |
**Component-only public retail references** are NOT final BOM or volume quotes; duties, VAT, power, screen, microphones, speaker, keyboard, battery, PCB, case, assembly, warranty, compliance and packaging are additional.

Sources (check again before ordering):
- https://www.waveshare.com/product/esp32-p4-module.htm
- https://www.luckfox.com/luckfox/EN-Core3566
- https://www.seeedstudio.com/reComputer-RK3576-Module-0432-p-6949.html
- https://www.rock-chips.com/uploads/pdf/2024.3.18/191/RK3576%20Brief%20Datasheet.pdf
- https://github.com/airockchip/rknn-llm (supported conversion/runtime; no inference speed assumed)

## Proposed hardware split for Linux variants
- **ESP32-C6:** key scanning, wake/alerts, basic connectivity, retained settings, battery monitoring and safe handshake with host.
- **Rockchip:** display compositor, richer app state, audio processing, local services and optional converted NPU models.
- **Bridge:** versioned framed UART or SPI, checksummed messages, replay-safe intents, bounded queues, secure signed updates.
- **Power:** isolated or switchable Rockchip power rails only after an orderly filesystem shutdown; validate resume time and C6 power budgets before claiming always-on.
- **Privacy:** physical mic mute and visible indicator; local-first storage, no compulsory cloud or mandatory subscription.
- **Common software:** transport/protocol layer shared with Standard; do not fork every feature or break Piblo Core compatibility.

## Required hardware bake-off before selecting Pro
1. Buy/borrow **one P4+C6** reference board with 3.5–4.3in capacitive IPS display and **one RK3576** kit only if the higher-cost Linux route remains desirable. Do not buy volume stock.
2. Build exactly the same UI flows on both: reminder, Buddy mood, speech capture/replay, a PC action, a phone action, and Wi-Fi reconnect. State which are real versus mocked.
3. Measure: boot-to-useful-screen, wake-to-alert, cold/warm speech latency, touch responsiveness, idle/active/sleep power in W, measured surface temperature, crash recovery, audio clarity and memory headroom.
4. Assemble a real per-unit BOM at **100 / 250 / 500 units**, with battery, display, enclosure, antenna testing, VAT treatment, fees, shipping, defect/yield and warranty allowance. Get supplier quotes.
5. Test whether the RK3576 NPU runs the **specific** proposed speech/assistant workload on the actual module at useful latency. "6 TOPS" is not a token-speed guarantee.
6. Check UK product compliance before any sale: battery safety and shipping, EMC/radio, RoHS, WEEE, applicable UKCA/CE requirements, safety documentation and software licences. Engage an appropriate compliance specialist.

### Decision rule
Prefer **P4+C6** if the user-visible tasks remain fast with phone/PC offload and the Linux alternative cannot show measurable advantage at an acceptable sale price/battery life. Choose **RK3576+C6** only if measured standalone capability justifies its total delivered cost. RK3566 is an intermediate option, not a presumed upgrade.

### Design constraint
No final product photographs, Kickstarter pricing, dates, sales claims or standalone guarantees until physical prototypes and quotes exist. All current Pro art must say **concept**.
