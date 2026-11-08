#!/usr/bin/env python3
"""Builds Piblo-Profit-Model.xlsx with LIVE formulas from the same expressions piblo_model.py evaluates.
Needs openpyxl (python3 -m pip install --user openpyxl). Re-run after changing assumptions.csv or the model."""
import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.worksheet.datavalidation import DataValidation
import piblo_model as pm

HERE = os.path.dirname(os.path.abspath(__file__))
YEL = PatternFill("solid", fgColor="FFF2CC")
HDR = PatternFill("solid", fgColor="D9E1F2")
BOLD = Font(bold=True)

def add_name(wb, name, ref):
    dn = DefinedName(name, attr_text=ref)
    try:
        wb.defined_names[name] = dn
    except TypeError:
        wb.defined_names.append(dn)

def xl(expr):
    return "=" + expr.replace("**", "^")

def hdr(ws, row, vals):
    for i, v in enumerate(vals, 1):
        c = ws.cell(row=row, column=i, value=v); c.font = BOLD; c.fill = HDR

def main():
    rows = pm.load_rows()
    model = pm.Model(rows)
    wb = openpyxl.Workbook()
    # ---- README
    ws = wb.active; ws.title = "README"
    for i, t in enumerate([
        "Piblo Kickstarter profit model (editable). All money GBP, net profit BEFORE business tax, Maz's time unpaid.",
        "Nothing here is a supplier quote: see the status/evidence columns on the Inputs sheet (QUOTED / SOURCED-LIST-PRICE / ASSUMPTION).",
        "1. Inputs: yellow cells in column C are the assumptions (source of truth is assumptions.csv; re-run build_xlsx.py after editing the CSV, or just edit here).",
        "2. Scenario: change the yellow cells (nominal backers, mix, prices, demand multiplier, cost multiplier, early bird, shipping strategy, VAT mode, shocks).",
        "   ship_mode: 1 shipping included in price, 2 charged separately, 3 pledge manager.  vat_mode: 0 register only over GBP 90k, 1 register voluntarily, 2 never.",
        "   n_ref = backers at the baseline prices GBP 103/194 under expected demand; actual backers move with price elasticity, shipping and early bird.",
        "3. UnitEconomics: per-backer economics for both editions at the Scenario settings.",
        "4. Scenarios: pasted table of the headline grid (values, from piblo_model.py). Full 8,600-row grid is out/scenarios.csv.",
        "Formulas are identical to piblo_model.py (generated from the same expressions). Open in Excel or Google Sheets; values calculate on open.",
    ], 1):
        ws.cell(row=i, column=1, value=t)
    ws.column_dimensions["A"].width = 150
    # ---- Inputs
    wi = wb.create_sheet("Inputs")
    hdr(wi, 1, ["id", "name", "value (edit)", "unit", "low", "high", "kind", "status", "evidence", "group", "scope", "phase"])
    irow = {}
    for i, r in enumerate(rows, 2):
        irow[r["id"]] = i
        for j, k in enumerate(["id", "name", "value", "unit", "low", "high", "kind", "status", "evidence", "group", "scope", "phase"], 1):
            v = r[k]
            if k in ("value", "low", "high"):
                v = float(v)
            wi.cell(row=i, column=j, value=v)
        wi.cell(row=i, column=3).fill = YEL
        add_name(wb, r["id"], f"Inputs!$C${i}")
    for col, wdt in zip("ABCDEFGHI", (18, 60, 12, 14, 10, 10, 10, 20, 90)):
        wi.column_dimensions[col].width = wdt
    wi.freeze_panes = "C2"
    # ---- Tiers
    wt = wb.create_sheet("Tiers")
    hdr(wt, 1, ["qty >="] + pm.TIER_PREFIXES)
    for i, q in enumerate(pm.TIER_QTY, 2):
        wt.cell(row=i, column=1, value=q)
        for j, p in enumerate(pm.TIER_PREFIXES, 2):
            wt.cell(row=i, column=j, value=f"=Inputs!$C${irow[f'{p}_t{q}']}")
    last = len(pm.TIER_QTY) + 1
    add_name(wb, "tier_qty", f"Tiers!$A$2:$A${last}")
    for j, p in enumerate(pm.TIER_PREFIXES, 2):
        col = openpyxl.utils.get_column_letter(j)
        add_name(wb, p + "_tier", f"Tiers!${col}$2:${col}${last}")
    # ---- Scenario
    sc = wb.create_sheet("Scenario")
    hdr(sc, 1, ["Item", "Value / formula", "Name used in formulas"])
    r = 2
    sc.cell(row=r, column=1, value="SCENARIO INPUTS (edit yellow)").font = BOLD; r += 1
    notes = dict(n_ref="backers at baseline prices, expected demand", mix_f="Founder's share (0 Original-only .. 1 Founder's-only)",
                 p_o="Original pledge price incl UK VAT", p_f="Founder's pledge price incl UK VAT", dem_mult="0.55 cons / 1.0 expected / 1.7 optimistic",
                 cost_mult="1.0 base, 1.15, 1.30", eb_disc="0, 0.10, 0.15", ship_mode="1 included, 2 separate, 3 pledge manager",
                 vat_mode="0 over threshold only, 1 voluntary, 2 never", d_delay="shock: months of delay (3)", d_defect="shock: defect rate (0.05/0.10)",
                 d_refund="shock: extra refund rate (0.05)", d_lump="shock: unexpected expense GBP", ovr_total="force total backers (0 = use demand model)")
    for k, v in pm.SCENARIO_DEFAULTS.items():
        sc.cell(row=r, column=1, value=f"{k}: {notes.get(k, '')}")
        c = sc.cell(row=r, column=2, value=v); c.fill = YEL
        sc.cell(row=r, column=3, value=k)
        add_name(wb, k, f"Scenario!$B${r}")
        r += 1
    dv = DataValidation(type="list", formula1='"1,2,3"'); sc.add_data_validation(dv); dv.add(sc[f"B{3 + list(pm.SCENARIO_DEFAULTS).index('ship_mode')}"])
    dv2 = DataValidation(type="list", formula1='"0,1,2"'); sc.add_data_validation(dv2); dv2.add(sc[f"B{3 + list(pm.SCENARIO_DEFAULTS).index('vat_mode')}"])
    r += 1
    sc.cell(row=r, column=1, value="CALCULATION (formulas; do not edit)").font = BOLD; r += 1
    key = {"np", "gross_total", "fx_total", "goal", "funded", "cash_upfront", "be_units", "risk", "cu_o", "cu_f"}
    for name, expr, label in model.lines:
        sc.cell(row=r, column=1, value=label or name)
        c = sc.cell(row=r, column=2, value=xl(expr))
        sc.cell(row=r, column=3, value=name)
        if name in key:
            sc.cell(row=r, column=1).font = BOLD; c.font = BOLD
        add_name(wb, name, f"Scenario!$B${r}")
        r += 1
    sc.column_dimensions["A"].width = 85; sc.column_dimensions["B"].width = 30; sc.column_dimensions["C"].width = 20
    sc.freeze_panes = "A2"
    # ---- UnitEconomics
    ue = wb.create_sheet("UnitEconomics")
    hdr(ue, 1, ["Per collected backer, at Scenario settings", "Original", "Founder's"])
    lines = [("Headline price incl UK VAT", "p_o", "p_f"), ("Gross cash incl shipping charged", "uk_o", "uk_f"),
             ("Output VAT (UK pledges only)", "uk_o*vatk", "uk_f*vatk"),
             ("Kickstarter 5%", "ks_fee_pct*ksf_o", "ks_fee_pct*ksf_f"), ("Payment processing", "fee_intl*ksf_o + proc_fixed", "fee_intl*ksf_f + proc_fixed"),
             ("Cardputer ADV (incl QA scrap)", "elec_u", "elec_u"), ("Enclosure", "enc_o", "enc_f"), ("Labour (assembly, flash, QA)", "lab_o", "lab_f"),
             ("Packaging", "pack_ou", "pack_fu"), ("Inbound freight + duty + irrecoverable import VAT", "frt + duty_o + unrec_o", "frt + duty_f + unrec_f"),
             ("Landed cost per unit", "goods_o", "goods_f"), ("Outbound shipping (blended)", "cs_o", "cs_f"), ("Fulfilment", "fo", "fo"),
             ("Support + storage", "sup_u + stor_u", "sup_u + stor_u"), ("CONTRIBUTION per backer before fixed costs", "cu_o", "cu_f")]
    for i, (lab, a, b) in enumerate(lines, 2):
        ue.cell(row=i, column=1, value=lab); ue.cell(row=i, column=2, value=xl(a)); ue.cell(row=i, column=3, value=xl(b))
        if lab.startswith("CONTRIBUTION"):
            for c in range(1, 4): ue.cell(row=i, column=c).font = BOLD
    ue.cell(row=len(lines) + 3, column=1, value="Net profit before business tax (Scenario)").font = BOLD
    ue.cell(row=len(lines) + 3, column=2, value="=np").font = BOLD
    ue.cell(row=len(lines) + 4, column=1, value="Total fixed costs"); ue.cell(row=len(lines) + 4, column=2, value="=fx_total")
    ue.cell(row=len(lines) + 5, column=1, value="Funding goal"); ue.cell(row=len(lines) + 5, column=2, value="=goal")
    ue.cell(row=len(lines) + 6, column=1, value="Cash needed before Kickstarter payout"); ue.cell(row=len(lines) + 6, column=2, value="=cash_upfront")
    ue.column_dimensions["A"].width = 60; ue.column_dimensions["B"].width = 16; ue.column_dimensions["C"].width = 16
    # ---- Scenarios (pasted values)
    ss = wb.create_sheet("Scenarios")
    cols = ["units", "mix", "price_set", "demand", "cost"]
    outs = ["bk_o", "bk_f", "gross_total", "fx_total", "np", "funded", "goal", "cash_upfront", "be_units", "risk"]
    hdr(ss, 1, cols + outs)
    n = 2
    for scn in pm.scenarios(model):
        if scn["eb"] != "none" or scn["ship"] != "separate" or scn["shock"] != "none":
            continue
        V = pm.run_scenario(model, scn)
        for j, c in enumerate(cols, 1): ss.cell(row=n, column=j, value=scn[c])
        for j, o in enumerate(outs, len(cols) + 1): ss.cell(row=n, column=j, value=round(V[o], 2))
        n += 1
    ss.freeze_panes = "A2"; ss.auto_filter.ref = f"A1:{openpyxl.utils.get_column_letter(len(cols) + len(outs))}{n - 1}"
    wb.save(os.path.join(HERE, "Piblo-Profit-Model.xlsx"))
    print("saved", n - 2, "pasted scenarios;", sum(1 for _ in model.lines), "formula lines")

if __name__ == "__main__":
    main()
