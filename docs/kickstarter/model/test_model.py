"""Run: python3 test_model.py   (or pytest). Pure stdlib except the optional xlsx check."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import piblo_model as pm

ROWS = pm.load_rows()
STATUSES = {"QUOTED", "SOURCED-LIST-PRICE", "ASSUMPTION"}

def test_every_assumption_has_evidence_and_status():
    ids = set()
    for r in ROWS:
        assert r["id"] not in ids, f"duplicate id {r['id']}"
        ids.add(r["id"])
        assert r["status"] in STATUSES, r
        assert r["kind"] in {"fixed", "variable", "percent"}, r
        assert r["evidence"].strip(), f"no evidence for {r['id']}"
        if r["status"] == "ASSUMPTION":
            assert "ASSUMPTION" in r["evidence"] or r["evidence"].startswith("Maz"), f"assumption must say why: {r['id']}"
        if r["status"] in ("QUOTED", "SOURCED-LIST-PRICE"):
            assert "http" in r["evidence"], f"sourced row needs a URL: {r['id']}"
        assert float(r["low"]) <= float(r["value"]) <= float(r["high"]) + 1e-9, f"value outside low/high: {r['id']}"

def test_hand_computed_profit():
    """1000 Original backers at GBP 100, shipping included, everything else stripped to round numbers.
    Per unit: 100 - fees(5 + 3 + 0.30) - elec 20 - shell 5 - labour (60 min at 10/h = 10) - pack 3 - ship 5 - fulfil 1 = 47.70."""
    ov = {"fail_rate": 0, "refund_rate": 0, "defect_rate": 0, "cont_pct": 0, "ad_pct": 0, "qa_scrap": 0, "mjf_scrap": 0, "vat_rate": 0,
          "freight_in": 0, "duty_elec": 0, "duty_plastic": 0, "support_u": 0, "stor_unit_month": 0, "proc_intl_uplift": 0,
          "labour_rate": 10, "asm_min_o": 60, "flash_min": 0, "qa_min": 0, "r_uk": 1, "r_eu": 0, "r_us": 0, "ship_uk": 5, "fulfil_order": 1,
          "im_min_qty": 10 ** 9, "refund_delay_month": 0}
    for r in ROWS:
        if r["kind"] == "fixed" and r["group"] not in ("fee", "tax", "demand", "goal", "shock", "risk"):
            ov[r["id"]] = 0
    for q in pm.TIER_QTY:
        ov[f"elec_t{q}"] = 20; ov[f"mjf_t{q}"] = 5; ov[f"pack_o_t{q}"] = 3
    m = pm.Model(ROWS, overrides=ov)
    V = m.run(ovr_total=1000, mix_f=0.0, p_o=100, ship_mode=1, vat_mode=2)
    assert V["bk_o"] == 1000 and V["bk_f"] == 0
    assert abs(V["gross_total"] - 100000) < 1e-6
    assert abs(V["cu_o"] - 47.70) < 1e-6, V["cu_o"]
    assert abs(V["np"] - 47700) < 1e-6, V["np"]

def test_itemised_costs_reconcile_to_unit_contribution():
    m = pm.Model(ROWS)
    for kw in (dict(n_ref=1000, mix_f=0.2), dict(n_ref=2000, mix_f=0.4, ship_mode=3, d_delay=3), dict(n_ref=800, mix_f=0.0, d_lump=1234, vat_mode=0)):
        V = m.run(**kw)
        assert V["funded"] > 0.5
        via_units = V["cl_o"] * V["cu_o"] + V["cl_f"] * V["cu_f"] - V["fx_total"] * (1 + V["cont_pct"]) - V["d_lump"]
        assert abs(via_units - V["np_funded"]) < 1e-6, (kw, via_units, V["np_funded"])

def test_cash_timeline_sums_to_profit_and_failed_campaign_loses_only_prelaunch():
    m = pm.Model(ROWS)
    for kw in (dict(n_ref=1000, mix_f=0.2), dict(n_ref=3000, mix_f=0.4, d_delay=3), dict(n_ref=1500, mix_f=0.2, ship_mode=3, vat_mode=0)):
        V = m.run(**kw)
        assert abs(sum(pm.cash_timeline(V)) - V["np"]) < 1e-6, kw
    V = m.run(n_ref=100)
    assert V["funded"] < 0.5
    assert abs(V["np"] + V["fx_pre"] + V["ads"]) < 1e-9
    assert abs(sum(pm.cash_timeline(V)) - V["np"]) < 1e-9

def test_goal_covers_fixed_costs_and_vat_threshold_logic():
    m = pm.Model(ROWS)
    V = m.run(n_ref=500)
    assert V["goal"] >= V["fx_plan"] + V["moq_cash"]
    small = m.run(ovr_total=100, vat_mode=0); big = m.run(ovr_total=2000, vat_mode=0)
    assert small["vat_reg"] == 0 and big["vat_reg"] == 1   # 100 backers < GBP 90k, 2000 backers > GBP 90k

def test_higher_costs_never_raise_profit():
    m = pm.Model(ROWS)
    a = m.run(n_ref=1000)["np"]; b = m.run(n_ref=1000, cost_mult=1.3)["np"]
    assert b < a

def test_xlsx_has_live_formulas():
    try:
        import openpyxl
    except ImportError:
        return
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Piblo-Profit-Model.xlsx")
    if not os.path.exists(p):
        return
    wb = openpyxl.load_workbook(p)
    ws = wb["Scenario"]
    formulas = [c.value for row in ws.iter_rows() for c in row if isinstance(c.value, str) and c.value.startswith("=")]
    assert len(formulas) > 100
    assert any("LOOKUP" in f for f in formulas)

if __name__ == "__main__":
    n = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn(); n += 1; print("ok", name)
    print(n, "tests passed")
