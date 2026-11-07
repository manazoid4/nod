# Nod: unit economics model

File: `ECONOMICS.csv` (open in Excel, Google Sheets or LibreOffice; the formula cells are spreadsheet formulas).

Status: MODEL ONLY. Almost every input is deliberately blank. No supplier quote, fulfilment price or battery cost exists yet, so no result should be quoted publicly.

## Gross pledges are not profit

A Kickstarter total is revenue before almost everything. From each pledge you still pay: VAT (if you are, or must become, VAT-registered), Kickstarter's 5% fee, payment processing, the Cardputer board, print material and machine/labour time, failed prints, assembly and testing, packaging, shipping (UK and international), customs problems, support, replacements and refunds, compliance work and any one-off costs. Funds are only collected if the goal is met, so set the goal from this model, not from a round number.

## Layout

One row per volume (100, 250, 500, 1000 units). Row 2 marks each column INPUT (you type it) or FORMULA (calculated).

Inputs (blank unless stated):
- Cardputer ADV unit cost, print material per unit, print hours per unit, labour rate per hour, print yield, assembly and QA, packaging.
- Reward price and shipping charged to the backer (both including VAT).
- VAT rate. Prefilled 0.2 (UK standard rate). Confirm with an accountant whether VAT applies to the whole pledge and whether you must register.
- UK share of backers, UK shipping cost, international shipping cost.
- Kickstarter fee. Prefilled 0.05 (5%; check current terms).
- Payment fee. Prefilled 0.04 as an EXAMPLE placeholder only. Kickstarter indicates roughly 3 to 5% plus a small fixed amount per pledge; confirm and add the fixed part.
- Support and returns allowance, and contingency (both fractions of product plus shipping cost).
- Fixed one-off costs: compliance assessment, test jigs, samples, video, legal and accounting.

Formulas:
- Print cost per good unit = (material + hours x rate) / yield. A yield of 0.9 adds about 11% to cover failed prints.
- Direct unit cost = Cardputer + print cost + assembly/QA + packaging.
- Average shipping = UK share x UK cost + (1 - UK share) x international cost.
- Gross pledge per unit = reward price + shipping charged.
- VAT = pledge / (1 + rate) x rate.
- Fees = pledge x (Kickstarter fee + payment fee).
- Support/returns and contingency = fraction x (direct cost + shipping).
- Margin per unit = pledge - VAT - fees - total cost.
- Net after fixed costs = margin x units - fixed costs.
- Break-even units = fixed costs / unit margin, or "not viable" if the margin is zero or negative.

A blank input makes the formula return an empty cell rather than a misleading number.

## Not yet covered

- Kickstarter's fixed per-pledge payment fee.
- Customs duty and import VAT on international parcels; exchange rates.
- Cash flow: you pay suppliers before shipping, and Kickstarter releases funds on its own schedule.
- Your own unpaid time.
- Volume discounts. Fill each row with its own quote.
- Software-only reward economics (no hardware, but support time).
- Capacity: check print hours x units against what you can physically print and assemble in time.

## Using it

1. Get at least two written supplier quotes (boards, printed cases or filament and printer time, packaging, UK and international courier rates for parcels containing batteries).
2. Fill the inputs for each volume row.
3. Look for rows with negative or thin margin. Raise price, cut cost or cap the number of kits.
4. Run a bad case: yield 10 points lower, shipping 30% higher, contingency doubled. The goal must survive it.
5. Only then fill in `REWARDS.md`.
