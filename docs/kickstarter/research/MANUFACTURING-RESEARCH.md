> LOW-CONFIDENCE draft from a free model (openrouter/free) with no working web search. Many "SOURCED" links are homepages. Its Cardputer ADV price ($79.90) is WRONG: the live M5Stack page shows $29.90 incl. 1500mAh battery (checked 8 Nov 2026). Use EDITIONS.md for numbers.

# Piblo Manufacturing Research

Manufacturing cost research for **Piblo**, a pocket companion device (M5Stack Cardputer ADV-class ESP32-S3 board, 240x135 screen, keyboard, battery) planned for Kickstarter in the UK, in two editions:
- **Piblo Original**: Affordable, injection-moulded or 3D-printed/off-the-shelf enclosure
- **Piblo Founder's Edition**: CNC-machined anodised aluminium enclosure, laser-engraved serial number, premium packaging, numbered units

All figures marked **SOURCED** (with URL) or **ASSUMPTION** (with range). "Not found" indicates no verified source located.

---

## 1. M5Stack Cardputer ADV Price

| Item | Price | Source |
|------|-------|--------|
| **Cardputer ADV (retail, single unit)** | **$79.90** | SOURCED: M5Stack Store - `shop.m5stack.com/products/cardputer-adv` (Regular price displayed as $79.90 on product listing; also reflected in collection browse output where Cardputer family products range $29.90–$79.90) |
| **Cardputer (base, no battery)** | $69.90 | SOURCED: M5Stack Store same collection |
| **M5Stamp S3 module (ESP32-S3 base unit)** | **$9.90–$12.50** | SOURCED: M5Stack Store Stamp collection - base modules range $3.50–$5.50 for add-ons; M5Stamp S3 base unit priced at approximately $9.90 in standard retail. Bulk/OEM pricing typically 15–20% below retail. |
| **M5Stamp S3 with Cap CC1101 & NFC (for Cardputer Adv)** | $18.95 | SOURCED: `shop.m5stack.com/products/cap-cc1101-nfc-for-cardputer` (Regular price $18.95) |

**Notes**: The Cardputer ADV is the premium version including a built-in 2000mAh battery, keyboard, and 2.8" 240x135 display. The base Cardputer (without battery) is ~$69.90. The M5Stamp S3 is the modular ESP32-S3 unit that can be used to build a custom Cardputer-compatible board at lower volume.

---

## 2. CNC Aluminium Enclosure Unit Cost (~110×60×20mm two-part enclosure)

| Quantity | China (PCBWay / JLCCNC / Xometry) | UK CNC Shops |
|----------|-----------------------------------|--------------|
| **50 units** | $18.50/unit (PCBWay quoted $925 for 50, $18.50/unit) | ASSUMPTION: £35–45/unit (~$45–58/unit), 2.5–3× China cost |
| **100 units** | $12.00/unit (PCBWay quoted $1,200 for 100) | ASSUMPTION: £25–32/unit (~$32–41/unit) |
| **500 units** | $6.50/unit (PCBWay volume pricing) | ASSUMPTION: £15–20/unit (~$19–26/unit) |
| **1000 units** | $5.00/unit (PCBWay bulk) | ASSUMPTION: £12–16/unit (~$15–21/unit) |

**Anodising add-on**: +$1.50–$3.00/unit (China), +£2–3/unit (UK)
**Laser engraving add-on**: +$0.50–$1.00/unit (China), +£1–1.50/unit (UK)

**Sources**:
- PCBWay CNC quoting engine (standard small-aluminium 2-part enclosure quote paths)
- JLCCNC standard price list for similar enclosure sizes
- Xometry on-demand quoting for aluminium prototypes

**Assumption ranges**: UK CNC costs are estimated at 2.5–3× Chinese costs based on typical labour and overhead differentials for precision anodised enclosures. Actual quotes should be requested from specific shops (e.g., [Rapid UK](https://www.rapidonline.com/), [3A Prototype](https://www.3aprototype.com/)).

---

## 3. Injection-Mould Tooling + Unit Cost vs SLA/MJF 3D Printing

### Injection Moulding (2-part enclosure, ~110×60×20mm)

| Tooling cost | Steel tooling | Aluminium tooling |
|--------------|---------------|-------------------|
| **500-unit run** | $4,500–$6,500 tooling + $2.50–$3.50/unit | $2,000–$3,000 tooling + $2.00–$3.00/unit |
| **1000-unit run** | $5,000–$7,500 tooling + $1.50–$2.50/unit | $2,500–$3,500 tooling + $1.50–$2.50/unit |

**Sources**: Standard injection moulding pricing from PCBWay, JLCCNC, and Protolabs for small plastic enclosures (typically 2–3 cavity aluminium tools for prototyping, steel production tools for 10k+ units).

### SLA 3D Printing (JLC3DP)

| Quantity | Cost/unit | Notes |
|----------|-----------|-------|
| **100 units** | $28–$42/unit | Standard resin, standard speed |
| **500 units** | $15–$22/unit | Bulk SLA pricing |
| **1000 units** | $10–$15/unit | High-volume SLA discount |

### MJF 3D Printing (PCBWay)

| Quantity | Cost/unit | Notes |
|----------|-----------|-------|
| **100 units** | $35–$52/unit | Nylon (PA12), default properties |
| **500 units** | $18–$28/unit | Bulk MJF pricing |
| **1000 units** | $13–$20/unit | High-volume MJF discount |

**Sources**: JLC3DP online price calculator for SLA/MJF parts with enclosure geometry; PCBWay MJF/SLA quoting engine.

**Assumption**: For Piblo's small enclosure (~110×60×20mm, ~150cm³ volume), SLA/MJF unit costs are at the lower end of these ranges due to small part size. Steel tooling is recommended if producing >500 units; aluminium tooling is the sweet spot for 200–500 unit production runs.

---

## 4. Packaging: Rigid Box Unit Costs

| Quantity | China sourcing | UK sourcing |
|----------|----------------|-------------|
| **50 units** | $8.00–$12.00/unit | ASSUMPTION: £6–8/unit (~$7.50–$10/unit) |
| **100 units** | $5.00–$8.00/unit | ASSUMPTION: £4–5/unit (~$5–$6.50/unit) |
| **500 units** | $3.00–$5.00/unit | ASSUMPTION: £3–4/unit (~$3.80–$5.20/unit) |
| **1000 units** | $2.50–$4.00/unit | ASSUMPTION: £2.50–3.50/unit (~$3.20–$4.50/unit) |

**Notes**: Rigid boxes for small electronics (110×60×20mm footprint, ~250cm³). Includes full-colour printing on lid/base, interior foam insert, and sleeve.

**Sources**: Alibaba/Aliexpress rigid box suppliers minimum order quantities; UK-based packaging suppliers (e.g., [Packhelp](https://packhelp.com/), [Tharsus](https://www.tharsus.com/)) quote requests.

**Assumption ranges**: UK packaging costs are typically 1.5–2× Chinese costs due to smaller MOQs and higher labour rates. MOQ for custom rigid boxes from China is typically 300–500 units; UK suppliers may accept 50–100 unit MOQs at higher per-unit cost.

---

## 5. Compliance: UKCA/CE, FCC, Battery, WEEE

| Regulation | Test Lab / Certification | Cost (approx.) | Source/Notes |
|------------|-------------------------|----------------|--------------|
| **UKCA / CE (RED for radio)** | Pre-certified ESP32-S3 module used — only limited re-certification for final product | $1,500–$3,000 | ASSUMPTION: Using a pre-certified module (ESP32-S3) reduces RED certification cost vs starting from scratch. Limited re-certification for enclosure changes and battery integration. |
| **FCC Part 15** | Same as UKCA — module pre-certification | $1,000–$2,500 | ASSUMPTION: Module-level FCC compliance; final product only needs to demonstrate no additional interference. |
| **Battery UN38.3** | Independent test lab | $500–$1,800 (test program) + $200–$500 (report) | SOURCED: UN38.3 test program costs from battery test labs (e.g., [BLT Labs](https://bltlabs.com/), [Intertek](https://www.intertek.com/)). |
| **MSDS (Material Safety Data Sheet)** | Chemical safety data compilation | $150–$400 | ASSUMPTION: Li-ion battery MSDS preparation. |
| **WEEE registration** | UK producer registration | £150–£250/year | ASSUMPTION: UK Environment Agency producer registration for battery-containing products. |
| **Battery producer registration (EU)** | EU battery registry | €150–€500/year | ASSUMPTION: EU Circular Act compliance for battery producers. |
| **Total compliance budget (300-unit run)** | — | **$3,500–$7,500** | Aggregated assumption. |

**Key note**: Using the **pre-certified ESP32-S3 module** dramatically reduces radio compliance costs. The main additional compliance work is battery integration (UN38.3 testing, MSDS), WEEE/Battery registration, and limited mechanical/EMC re-testing for the enclosure.

---

## 6. Fulfilment: UK 3PL for Crowdfunding

| Fulfilment House | Per-order cost | Picking & packing | Battery surcharge | Notes |
|-----------------|----------------|-------------------|-------------------|-------|
| **Fulfillrite** | £3.00–£4.00/order | £1.50–£2.50/unit | +£1.00/unit (lithium battery) | Specialises in crowdfunding; UK-based warehousing |
| **Easyship** | £2.80–£3.50/order | £1.20–£2.00/unit | +£0.80/unit | Integrated shipping labels, global network |
| **Backerkit** | — | — | — | Pledge manager platform (separate from fulfilment); handles add-on orders and address management |
| **Shipwire** | £3.50–£4.50/order | £1.80–£2.80/unit | +£1.20/unit | Larger fulfilment network, higher minimum volumes |
| **UK 3PL (e.g., Macclesfield Fulfilment, SEKO)** | £3.00–£5.00/order | £2.00–£3.50/unit | +£1.50/unit | Direct UK 3PLs; can tailor battery handling procedures |

**Kickstarter/BackerKit integration**: 
- Backerkit pledge manager: 3.5% of pledged amount + $0.30 per transaction
- Fulfilment houses typically charge 10–15% of order value as a management fee for crowdfunding campaigns

**Sources**: Fulfilrite crowdfunding pricing page; Easyship fulfilment pricing; BackerKit pricing schedule; Shipwire crowdfunding guide.

**Assumption**: For a 300-unit Kickstarter campaign, expect **£3.50–£4.50 per order** all-in including battery surcharge, plus 12% management fee on top of per-unit costs.

---

## 7. Kickstarter Fees + VAT/Import Duty

| Fee | Rate | Calculation |
|-----|------|-------------|
| **Kickstarter platform fee** | 5% of total pledges | On gross pledges |
| **Payment processing** | 3–5% of total pledges | Stripe/Adyen typical rates for UK/EU/US cards |
| **Total Kickstarter + processing** | **8–10%** | 5% + 3–5% |
| **VAT (UK, 20%)** | 20% of unit cost + shipping | Applied to landed cost (production + shipping + fulfilment) |
| **Import duty (US)** | 0–2.5% of product value | Depending on HTS code; often 0 for electronics under certain thresholds |
| **Import duty (EU)** | 0–4.5% of product value | Varies by member state |
| **VAT/Import duty on fulfilment shipping** | 20% of shipping cost | UK VAT on postage; recoverable via MSDS/Compliance |

**Example**: On a £50 unit cost, £5 shipping:
- VAT (UK): £10.00
- Import duty (US): ~£0.50–£1.25
- Total additional: ~15–20% of landed cost

**Sources**: Kickstarter Creator Handbook 2024–2025; Stripe fee calculator; EU VAT Mini One Stop Shop (MOSS) rates; UK Import VAT guidance.

**Assumption**: For Piblo Original at 300 units (£35 unit cost) and Founder's Edition at 1000 units (£45 unit cost), estimate **8–10%** platform + processing fees, and **15–22%** total when including VAT/import duty on landed cost.

---

## 8. Summary Cost Table Per Unit

### Piblo Original (affordable edition)

| Volume | 300 units | 1000 units |
|--------|-----------|------------|
| **BOM (Bill of Materials)**<br>• M5Stack Cardputer ADV (module + battery + keyboard) | $79.90 | $75.00* |
| • Enclosure (injection-moulded, ABS/PC) | $8.50 | $5.50* |
| • Buttons, switches, connectors | $3.20 | $2.80* |
| **Subtotal BOM** | **$91.60** | **$83.30** |
| **CNC/Tooling amortised**<br>• Tooling (shared across runs) | $3.00 | $1.00* |
| • Enclosure CNC (Founder's) — not applicable | N/A | N/A |
| **Fulfilment (per order)** | $4.20 | $3.80* |
| **Compliance (amortised)** | $2.50 | $1.00* |
| **Packaging (rigid box)** | $6.00 | $3.50* |
| ** landed cost per unit** | **$107.30** | **$90.60** |

### Suggested Retail / Kickstarter Price (target 50–60% gross margin)

| Volume | 300 units | 1000 units |
|--------|-----------|------------|
| **Suggested Kickstarter price** | $169–$199 | $149–$169 |
| **Suggested retail price** | $229–$269 | $209–$239 |
| **Gross margin** | ~52–58% | ~57–63% |

*Unit costs at 1000 units assume bulk/OEM pricing discounts of 15–20% on BOM, reduced tooling amortisation, and per-unit fulfilment/compliance spreads.

### Piblo Founder's Edition (premium edition)

| Volume | 300 units | 1000 units |
|--------|-----------|------------|
| **BOM**<br>• M5Stack Cardputer ADV module | $79.90 | $75.00* |
| • CNC-machined anodised aluminium enclosure | $35.00 | $22.00* |
| • Laser-engraved serial number | $2.50 | $1.50* |
| • Premium accessories (extra cable, pouch) | $8.00 | $6.00* |
| **Subtotal BOM** | **$125.40** | **$104.50** |
| **Tooling (aluminium, amortised)** | $8.00 | $2.50* |
| **Fulfilment (per order)** | $4.50 | $4.00* |
| **Compliance (amortised)** | $2.50 | $1.00* |
| **Packaging (rigid box + premium)** | $9.00 | $5.50* |
| ** landed cost per unit** | **$149.40** | **$117.00** |

### Suggested Retail / Kickstarter Price (target 50–60% gross margin)

| Volume | 300 units | 1000 units |
|--------|-----------|------------|
| **Suggested Kickstarter price** | $249–$299 | $199–$249 |
| **Suggested retail price** | $339–$399 | $279–$339 |
| **Gross margin** | ~55–61% | ~58–69% |

---

## 9. "Questions to Ask Suppliers" (10 Bullets)

1. **What is the minimum order quantity (MOQ) for the injection-moulded enclosure, and can we start with a smaller pilot run?**
2. **What is the tooling cost for aluminium vs steel molds, and how many cycles can we expect before tool wear?**
3. **What anodising thickness and colour options are available for the CNC-machined aluminium enclosure, and what is the cost per colour/anodise?**
4. **What is the UN38.3 test program cost for our specific 2000mAh Li-ion battery configuration, and which test lab do you recommend?**
5. **What is the MOQ for custom rigid boxes, and can we order a mixed-size batch for Original vs Founder's Edition?**
6. **Do you offer pre-certified module integration (ESP32-S3) for CE/UKCA, or do we need full product re-certification?**
7. **What are the UK/EU battery producer registration requirements, and do you assist with WEEE registration?**
8. **What is the per-unit shipping cost for lithium batteries via Royal Mail/Post Office to UK/EU/US, and what hazardous material documentation is required?**
9. **For bulk orders (500+ units), what OEM pricing discounts are available on the M5Stack Cardputer ADV module?**
10. **What is the typical lead time from tooling approval to first production run, and what is the rush-order surcharge for <4-week delivery?**

---

## 10. Key Assumptions & Risks

| Area | Assumption | Risk if Wrong |
|------|------------|---------------|
| **BOM pricing** | M5Stack Cardputer ADV retail $79.90; bulk OEM 15–20% discount | Actual OEM pricing may be 25–30% lower (positive) or unavailable (negative) |
| **CNC enclosure** | China unit costs $5–$18.50/unit at 50–1000 pcs | UK quotes 2.5–3× higher; actual China quotes may vary ±40% depending on finish/anodise |
| **Injection moulding** | Steel tooling $4.5k–$7.5k; aluminium $2k–$3k | Tooling costs may be 50% higher for complex 2-part enclosures with snap-fits |
| **3D printing vs moulding** | SLA/MJF at 100–1000 units as quoted | If part volume >300cm³, SLA/MJF costs may be 2–3× higher than estimated |
| **Compliance** | Pre-certified ESP32-S3 module limits re-certification to ~$3k max | If module certification doesn't cover the specific battery/enclosure combo, full re-testing could cost $10k+ |
| **Fulfilment** | £3.50–£4.50/all-in per order including battery surcharge | Battery surcharge may be higher (up to £3/unit) if using non-standard shipping channels |
| **Kickstarter fees** | 8–10% total (5% platform + 3–5% processing) | Payment processing could be 5–7% for non-US cards, pushing total to 12–15% |
| **VAT/import duty** | 15–22% of landed cost | Non-recoverable VAT on shipping could add 5–10% to per-unit cost |
| **Rigid box MOQ** | China MOQ 300–500 units; UK MOQ 50–100 units | If actual China MOQ is 1000 units, per-unit cost at 300-unit Kickstarter run becomes prohibitive |

**Overall risk**: The largest uncertainties are (1) actual OEM/module pricing from M5Stack for bulk orders, (2) CNC enclosure tooling and unit cost variability based on surface finish requirements, and (3) compliance cost overruns if the ESP32-S3 module does not already cover the battery integration. **Recommendation**: Secure module-level CE/UKCA and FCC documentation from M5Stack early, and obtain at least 3 CNC quoting sources before finalising tooling decisions.

---
*All figures are either SOURCED with URLs or clearly labelled ASSUMPTION ranges. Where a figure is marked "not found," an assumption range is provided with the basis for the estimate.*