# Piblo editions: Original and Founder's Edition

Status: PLANNING MODEL, 8 Nov 2026. Prices decided by Maz: **Original £79, Founder's Edition £149**. Nothing is supplier-quoted yet, so no cost figure may be shown publicly. Every number is tagged **[S]** source-backed (link given), **[A]** assumption needing a written quote, or **[D]** decision by Maz. GBP; USD converted at about 0.77. Plan assumes Chinese manufacturing (board from M5Stack, enclosures from a CNC/print shop such as JLCCNC, PCBWay or RapidDirect) to protect margin.

`MANUFACTURING-RESEARCH.md` from the free research agent was not present when this was written. Reconcile when it lands.

## The two editions

| | Piblo Original | Piblo Founder's Edition |
|---|---|---|
| Idea | Affordable and approachable. The default backer reward. | Limited, numbered, refined. For first backers who want a keepsake. |
| Hardware | M5Stack Cardputer ADV-class board plus a Piblo enclosure | Same electronics in a CNC-machined aluminium enclosure |
| Enclosure | Printed nylon (MJF/SLS) first; injection tooling only if volume justifies it [A] | 6061 aluminium, 2-part, anodised, laser-engraved serial number [A] |
| Packaging | Simple recycled box, quick-start card, USB-C cable [A] | Rigid gift box, numbered certificate [A] |
| Cap | Open | Numbered 1 to N (suggest 250 to 500 first run) [A] |
| List price (inc VAT if registered) | **£79** [D] | **£149** [D] |

Both ship the same software. Neither promises features not marked working on the device in `FEATURE_INVENTORY.md`.

**Explored, not promised:** a clip-on IPS touchscreen and other accessories. Stretch goal only after the base device is validated, funded and tested. In no reward until then.

## Cost assumptions (per unit)

| Item | Original | Founder's | Basis |
|---|---|---|---|
| Cardputer ADV board | £22 at 100 falling to £17.5 at 1000 | same | **[S]** list $29.90 (about £23) at [M5Stack](https://shop.m5stack.com/products/m5stack-cardputer-adv-version-esp32-s3). Bulk discount is **[A]**, ask M5Stack |
| Enclosure | £7 at 100 to £3 at 1000 (print/soft-tool, China) | £62 at 100, £45 at 250, £32 at 500, £26 at 1000 (CNC, anodise, engrave, China) | **[A]**. Davantech notes CNC has no tooling cost but a higher part cost ([source](https://www.davantech.com/aluminum-enclosures)); no price was published. Quote it |
| Assembly and test | £2.5 to £4 | £4.5 to £6 | **[A]** |
| Packaging and cable | £3.5 | £7 | **[A]** |
| Support and contingency allowance | 6% | 8% | **[A]** |
| Kickstarter fee | 5% of pledge | same | **[S]** [Kickstarter UK fees](https://www.kickstarter.com/help/fees?country=GB) |
| Payment processing | 3% + £0.30 per pledge | same | **[S]** same page |
| VAT | Model uses 20% (registered). Unregistered case shown separately | same | **[A]**. Kickstarter does not withhold VAT ([source](https://www.kickstarter.com/help/fees?country=GB)). Registration depends on turnover and status: accountant must confirm. Import VAT on goods from China is separate |
| Shipping | charged £9.50, cost about £9.60 (UK £4.50, world £13) | charged £11, cost £11 (UK £5, world £15) | **[A]**. Lithium parcels (UN3481) limit carriers; get quotes. Treated as pass-through |

One-off costs:

| Item | Range | Basis |
|---|---|---|
| Radio and EMC testing | EMC £2,000 to £5,000; radio £1,500 to £4,000; Wi-Fi battery product bundle about £8,000 to £8,800 | **[S]** [CASS Industries](https://cassindustries.com/pricing-table), [Market Access Lab](https://marketaccesslab.com/ce-marking-ukca-cost), [euverify](https://euverify.com/resource/ukca-testing-and-certification) |
| Reusing the module's certification | could cut radio scope by about 30% | **[S]** [Blue Asia Labs](https://www.blueasialabs.com/shouyehuandeng/eu-radio-equipment-directive-ce-red-certification-costs). Only if M5Stack's certificates cover our use |
| UN38.3 battery test | €4,000 to €6,000 per cell variant | **[S]** [Ideambox](https://ideambox.com/certification-compliance/). Possibly nil if M5Stack supplies it: ask |
| CE vs UKCA | Great Britain accepts CE for most electronics, one process can cover EU and GB | **[S]** [MarkReady](https://markready.io/learn/ce-marking-cost). Confirm with a UK lab |
| Samples, jigs, prototypes | £2,500 (Original), £5,500 (Founder's) | **[A]** |
| Video, photos, legal, accounting | £3,000 | **[A]** |
| Total used in model | £13,500 (Original), £17,000 (Founder's) | **[A]** |

## Margin at £79 and £149

"Gross margin" here means: pledge price (after VAT if registered), minus Kickstarter 5% and payment 3% + £0.30, minus product cost with allowance, as a share of that price. Shipping is treated as pass-through (backer pays the carrier cost). Target: about 45%.

| Units | Original unit cost | Original GM @ £79 (VAT-registered / not) | Founder's unit cost | Founder's GM @ £149 (registered / not) |
|---|---|---|---|---|
| 100 | £39.08 | 30% / 42% | £108.28 | 3% / 19% |
| 250 | £35.29 | 36% / 47% | £86.80 | 20% / 33% |
| 500 | £31.49 | 42% / 51% | £69.86 | 34% / 45% |
| 1,000 | £28.26 | 47% / 56% | £60.88 | 41% / 51% |

Full-model result (sheet includes shipping gap, support, contingency, VAT 20%), margin per unit before one-off costs and net after one-offs:

| Units | Original per unit | Original net after one-offs | Founder's per unit | Founder's net after one-offs |
|---|---|---|---|---|
| 100 | £17.15 | -£11,785 | -£0.11 | -£17,011 |
| 250 | £20.94 | -£8,265 | £21.38 | -£11,656 |
| 500 | £24.74 | -£1,132 | £38.31 | +£2,157 |
| 1,000 | £27.97 | +£14,471 | £47.30 | +£30,295 |

## Lowest early-bird price that still clears about 45%

| Case | Original | Founder's |
|---|---|---|
| 250 units, not VAT-registered | £77 | £187 (list is too low) |
| 500 units, not VAT-registered | **£69** | £151 (no discount possible) |
| 1,000 units, not VAT-registered | £62 | £132 |
| 500 units, VAT-registered | £85 (list £79 already misses) | £187 |
| 1,000 units, VAT-registered | £77 | £163 |

Reading it honestly:
- **Original £79 hits 45% only at about 500+ units if you are not VAT-registered, or 1,000+ if registered.** At 100 to 250 units it is a loss-leader.
- **Recommended early bird: Original £69, limited to the first 150 to 200 backers, only if the 500-unit cost quotes (board about £19, body about £4) are confirmed in writing and VAT status is unregistered.** Otherwise keep £79 and give the early bird as a free extra, not a price cut.
- **Founder's £149 clears 45% only at 500+ units unregistered. Do not discount it.** At 100 units it makes about nothing, so the Founder's cap should be 250 to 500 and priced only after a real CNC quote at that quantity. If the quote is above about £32 per set at 500, raise it to £179.
- Everything depends on the board price and the CNC quote: they are the two biggest unquoted numbers.
- Bad case (board +25%, shipping +30%, enclosure +30%): margins fall by roughly 10 points. The funding goal must be set from the bad case.

Not yet modelled: import VAT and duty on goods from China, exchange rates, fulfilment-centre handling and storage, cash flow before Kickstarter pays out, tooling for injection moulding. Sheets: `ECONOMICS.csv` (Original) and `ECONOMICS-FOUNDERS.csv`.

## Founder's Edition: what to specify

- Body: 6061-T6 aluminium, 2 parts (shell plus back plate), keyboard and screen cutouts, speaker and mic ports, USB-C access.
- Finish: Type II anodise (thinner, cheaper, per [Davantech](https://www.davantech.com/aluminum-enclosures)). Two colours maximum.
- Marking: laser-engraved serial 001 to N.
- Risk to test first: aluminium blocks Wi-Fi if it covers the antenna, so a plastic window is likely. Heat and the magnetic back also change. Needs a physical prototype before any claim.

## Outstanding supplier questions

Send to 3 to 5. Candidates (not yet contacted): M5Stack (board), JLCCNC, PCBWay and RapidDirect (instant-quote CNC), Davantech (CNC with European engineering management), a UK MJF/SLS print service for the Original, one UK compliance lab, one UK fulfilment partner.

**M5Stack**
1. Price per Cardputer ADV at 100, 250, 500, 1000 units, lead time, and bulk packaging.
2. UN38.3 summary and radio certificates for the module and 1500mAh cell, and may we rely on them in our technical file?
3. OEM variant (custom logo or no stock case) and its MOQ.

**CNC aluminium shops**
4. Price per set (shell plus back plate) at 100, 250, 500, 1000, anodised, laser-engraved serial, from a STEP file; fixture charges separate.
5. Lead time for 10 samples, then production; tolerance and cosmetic rejection rate.
6. Antenna window or plastic insert option and its cost.
7. DDP shipping to the UK, and who pays duty and import VAT?

**Print service (Original)**
8. MJF PA12 price per enclosure at 100 to 1000, dyed, with colour consistency; the volume at which injection tooling wins and tooling cost.

**Fulfilment and shipping**
9. UK, EU and US price for a 300 g boxed device with a lithium cell (UN3481), carriers used, Kickstarter pledge-manager handling, returns, storage fees.

**Compliance lab**
10. Fixed quote for EMC plus RED for a Wi-Fi, battery device reusing a certified module, in aluminium and plastic variants; is CE-only acceptable for GB?

**Top 5 if time is short:** (1) M5Stack volume price and certificates, (2) CNC price per set at 250 and 500, (3) aluminium and Wi-Fi antenna window, (4) battery parcel shipping by region, (5) compliance lab fixed quote.
