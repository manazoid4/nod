#!/usr/bin/env python3
"""Piblo Kickstarter profit model. Pure stdlib. Reads assumptions.csv (single source of truth).

Run:  python3 piblo_model.py            # writes out/scenarios.csv and out/SUMMARY.md
      python3 piblo_model.py --quick    # reference scenario only, prints itemised P&L

The model is a list of (name, expression) lines (MODEL below). The same expressions are
written as live formulas into Piblo-Profit-Model.xlsx by build_xlsx.py, so Python and Excel
cannot drift apart. Expressions use only + - * / ** < > <= >= and the functions in FUNCS.
All money is GBP, pre business-tax (no corporation tax, no personal time costed).
"""
import csv, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TIER_QTY = [0, 100, 250, 500, 1000, 5000]
TIER_PREFIXES = ["elec", "mjf", "cnc", "pack_o", "pack_f"]

# ---------------------------------------------------------------- assumptions
def load_rows(path=None):
    with open(path or os.path.join(HERE, "assumptions.csv"), newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def build_env(rows, mode="value", overrides=None):
    """id -> float (mode value|low|high). overrides: {id: value} or {tier_prefix: factor-dict}."""
    env = {r["id"]: float(r[mode]) for r in rows}
    if overrides:
        env.update(overrides)
    for p in TIER_PREFIXES:
        env[p + "_tier"] = [env[f"{p}_t{q}"] for q in TIER_QTY]
    env["tier_qty"] = TIER_QTY
    return env

# ---------------------------------------------------------------- spreadsheet-compatible functions
def IF(c, a, b): return a if c else b
def AND(*a): return all(a)
def OR(*a): return any(a)
def MIN(*a): return min(a)
def MAX(*a): return max(a)
def ROUND(x, n=0): return math.floor(x * 10 ** n + 0.5) / 10 ** n
def CEILING(x, s): return math.ceil(x / s - 1e-12) * s
def LOOKUP(x, keys, vals):
    out = vals[0]
    for k, v in zip(keys, vals):
        if x >= k: out = v
    return out
FUNCS = dict(IF=IF, AND=AND, OR=OR, MIN=MIN, MAX=MAX, ROUND=ROUND, CEILING=CEILING, LOOKUP=LOOKUP)

# ---------------------------------------------------------------- scenario inputs (defaults)
SCENARIO_DEFAULTS = dict(
    n_ref=500,      # backers at the reference prices, expected demand, before multipliers
    mix_f=0.2,      # Founder's share of backers (0 = Original only, 1 = Founder's only)
    p_o=103, p_f=194,   # headline pledge prices incl UK VAT
    dem_mult=1.0,   # demand multiplier (conservative/expected/optimistic)
    cost_mult=1.0,  # multiplies unit costs + one-off costs (not fees)
    eb_disc=0.0,    # early-bird discount fraction on limited quantities
    ship_mode=2,    # 1 shipping included in price, 2 charged separately at checkout, 3 pledge manager
    vat_mode=1,     # 0 register only when over threshold, 1 register voluntarily, 2 never (illegal over threshold; for comparison)
    d_delay=0,      # shock: months of manufacturing delay
    d_defect=0.0,   # shock: defect rate floor
    d_refund=0.0,   # shock: extra refund rate
    d_lump=0.0,     # shock: unexpected expense (GBP)
    ovr_total=0,    # >0 forces total backers (used for break-even scans)
)

def _fixed_sum(rows, scope, phase):
    ids = [r["id"] for r in rows if r["kind"] == "fixed" and r["scope"] == scope and r["phase"] == phase]
    return " + ".join(ids) if ids else "0"

def build_model(rows):
    """Return the ordered (name, expression, label) lines."""
    M = []
    def m(name, expr, label=""): M.append((name, expr, label))
    # ---- shipping mode, regions, prices, demand
    m("r_row", "1 - r_uk - r_eu - r_us", "Share of backers: RoW")
    m("is_incl", "IF(ship_mode < 1.5, 1, 0)", "Shipping included in price")
    m("is_sep", "IF(AND(ship_mode >= 1.5, ship_mode < 2.5), 1, 0)", "Shipping charged separately")
    m("is_pm", "IF(ship_mode >= 2.5, 1, 0)", "Shipping collected in pledge manager")
    m("chg_avg", "r_uk*chg_uk + r_eu*chg_eu + r_us*chg_us + r_row*chg_row", "Average shipping charge schedule")
    m("sh_chg", "(1 - is_incl)*chg_avg", "Shipping charged per backer (0 if included)")
    m("w_ship", "is_sep*w_sep + is_pm*w_pm", "Weight of shipping in perceived price")
    m("pp_o", "p_o + w_ship*sh_chg", "Perceived price Original")
    m("pp_f", "p_f + w_ship*sh_chg", "Perceived price Founder's")
    m("eb_up", "1 + eb_uplift*eb_disc/0.1", "Early-bird demand uplift")
    m("dm_o", "dem_mult*eb_up*(pp_o/ref_p_o)**(-elast_o)", "Demand factor Original")
    m("dm_f", "dem_mult*eb_up*(pp_f/ref_p_f)**(-elast_f)", "Demand factor Founder's")
    m("raw_o", "IF(ovr_total > 0, ovr_total*(1 - mix_f), n_ref*(1 - mix_f)*dm_o)", "Original backers (raw)")
    m("raw_f", "IF(ovr_total > 0, MIN(founders_cap, ovr_total*mix_f), MIN(founders_cap, n_ref*mix_f*dm_f))", "Founder's backers (raw, capped)")
    m("bk_o", "ROUND(raw_o, 0)", "Original backers pledged")
    m("bk_f", "ROUND(raw_f, 0)", "Founder's backers pledged")
    m("cl_o", "bk_o*(1 - fail_rate)", "Original pledges collected")
    m("cl_f", "bk_f*(1 - fail_rate)", "Founder's pledges collected")
    m("has_o", "IF(mix_f < 1, 1, 0)", "Original offered")
    m("has_f", "IF(mix_f > 0, 1, 0)", "Founder's offered")
    m("eb_o", "IF(eb_disc > 0, MIN(eb_cap_o, eb_share*cl_o), 0)", "Early-bird Original units")
    m("eb_f", "IF(eb_disc > 0, MIN(eb_cap_f, eb_share*cl_f), 0)", "Early-bird Founder's units")
    m("ref_rate", "MIN(0.5, refund_rate + d_refund + refund_delay_month*d_delay)", "Refund rate incl shocks")
    m("ref_keep", "1 - ref_rate", "Share of pledges kept")
    m("dfr", "MAX(defect_rate, d_defect)", "Defect/replacement rate incl shock")
    m("kprod", "1 - ref_rate*refund_cost_recov", "Share of collected units actually produced")
    # ---- revenue
    m("uk_o", "p_o + sh_chg*(1 - is_pm*pm_nonpay)", "Gross cash per collected Original backer")
    m("uk_f", "p_f + sh_chg*(1 - is_pm*pm_nonpay)", "Gross cash per collected Founder's backer")
    m("ksf_o", "p_o + is_sep*sh_chg", "Kickstarter-tracked funds per Original")
    m("ksf_f", "p_f + is_sep*sh_chg", "Kickstarter-tracked funds per Founder's")
    m("pmf", "is_pm*sh_chg*(1 - pm_nonpay)", "Pledge-manager funds per backer")
    m("eb_gross", "eb_disc*(p_o*eb_o + p_f*eb_f)", "Early-bird discount given")
    m("gross_total", "cl_o*uk_o + cl_f*uk_f - eb_gross", "GROSS PLEDGES COLLECTED (incl VAT, shipping)")
    m("ks_funds", "cl_o*ksf_o + cl_f*ksf_f - eb_gross", "Kickstarter-tracked funds collected")
    m("pm_funds", "(cl_o + cl_f)*pmf", "Pledge-manager funds collected")
    m("vat_reg", "IF(vat_mode < 0.5, IF(gross_total > vat_threshold, 1, 0), IF(vat_mode < 1.5, 1, 0))", "VAT registered (1/0)")
    m("vatk", "vat_reg*r_uk*vat_rate/(1 + vat_rate)", "Output VAT as share of gross (UK pledges only; exports zero-rated)")
    m("vat_net", "gross_total*vatk*ref_keep", "Output VAT payable (after refunds)")
    m("refunds", "gross_total*ref_rate", "Refunds paid")
    # ---- fees
    m("fee_intl", "proc_pct + proc_intl_uplift*(1 - r_uk)", "Blended processing % (KS-tracked)")
    m("fees_ks", "ks_fee_pct*ks_funds", "Kickstarter 5% fee")
    m("fees_proc", "fee_intl*ks_funds + proc_fixed*(cl_o + cl_f)", "Payment processing")
    m("fees_pm", "is_pm*(pm_campaign_pct*ks_funds + (pm_txn_pct + fee_intl)*pm_funds + proc_fixed*(cl_o + cl_f))", "Pledge manager + 2nd payment fees")
    m("ads", "ad_pct*ks_funds", "Ads / marketing (variable)")
    # ---- production costs
    m("pr_o", "cl_o*kprod", "Original units produced")
    m("pr_f", "cl_f*kprod", "Founder's units produced")
    m("q_tot", "pr_o + pr_f", "Total units produced (electronics tier)")
    m("elec_u", "cost_mult*LOOKUP(q_tot, tier_qty, elec_tier)*(1 + qa_scrap)", "Cardputer ADV per unit incl QA scrap")
    m("mjf_u", "cost_mult*LOOKUP(pr_o, tier_qty, mjf_tier)/(1 - mjf_scrap)", "Original shell per unit, MJF print")
    m("im_u_c", "cost_mult*im_unit/(1 - mjf_scrap)", "Original shell per unit, injection moulded")
    m("im_tool_c", "cost_mult*im_tool", "Injection tooling cost")
    m("use_im", "IF(AND(pr_o >= im_min_qty, pr_o*mjf_u > im_tool_c + pr_o*im_u_c), 1, 0)", "Injection moulding cheaper (1/0)")
    m("enc_o", "IF(use_im > 0.5, im_u_c, mjf_u)", "Original shell per unit (cheaper route)")
    m("enc_f", "cost_mult*(LOOKUP(pr_f, tier_qty, cnc_tier)/(1 - cnc_scrap) + cnc_window)", "Founder's CNC shell per unit")
    m("lab_o", "cost_mult*labour_rate*(asm_min_o + flash_min + qa_min)/60", "Original labour per unit")
    m("lab_f", "cost_mult*labour_rate*(asm_min_f + flash_min + qa_min)/60", "Founder's labour per unit")
    m("pack_ou", "cost_mult*LOOKUP(pr_o, tier_qty, pack_o_tier)", "Original packaging per unit")
    m("pack_fu", "cost_mult*LOOKUP(pr_f, tier_qty, pack_f_tier)", "Founder's packaging per unit")
    m("frt", "cost_mult*freight_in", "Inbound freight per unit")
    m("duty_o", "duty_elec*elec_u + duty_plastic*enc_o", "Import duty per Original")
    m("duty_f", "duty_elec*elec_u + duty_alu*enc_f", "Import duty per Founder's")
    m("impv_o", "vat_rate*(elec_u + enc_o + pack_ou + frt + duty_o)", "Import VAT per Original")
    m("impv_f", "vat_rate*(elec_u + enc_f + pack_fu + frt + duty_f)", "Import VAT per Founder's")
    m("unrec_o", "(1 - vat_reg)*impv_o", "Irrecoverable import VAT per Original")
    m("unrec_f", "(1 - vat_reg)*impv_f", "Irrecoverable import VAT per Founder's")
    m("goods_o", "elec_u + enc_o + lab_o + pack_ou + frt + duty_o + unrec_o", "Landed cost per Original")
    m("goods_f", "elec_u + enc_f + lab_f + pack_fu + frt + duty_f + unrec_f", "Landed cost per Founder's")
    m("cost_elec", "q_tot*elec_u", "Electronics total")
    m("cost_encl", "pr_o*enc_o + pr_f*enc_f", "Enclosures total")
    m("cost_labour", "pr_o*lab_o + pr_f*lab_f", "Assembly/flash/QA labour total")
    m("cost_pack", "pr_o*pack_ou + pr_f*pack_fu", "Packaging total")
    m("cost_inbound", "pr_o*(frt + duty_o + unrec_o) + pr_f*(frt + duty_f + unrec_f)", "Inbound freight + duty + irrecoverable import VAT")
    # ---- delivery costs
    m("cs_o", "cost_mult*(r_uk*ship_uk + r_eu*(ship_eu + lith_air) + r_us*(ship_us + lith_air) + r_row*(ship_row + lith_air))", "Outbound shipping per Original (blended)")
    m("cs_f", "cs_o + cost_mult*ship_f_extra", "Outbound shipping per Founder's")
    m("fo", "cost_mult*fulfil_order", "Fulfilment per order")
    m("stor_u", "cost_mult*stor_unit_month*(stor_base_months + d_delay)", "Storage per unit")
    m("sup_u", "support_u*(1 + 0.5*d_delay)", "Support per unit (rises with delay)")
    m("cost_ship_out", "ref_keep*(cl_o*cs_o + cl_f*cs_f)", "Outbound shipping total")
    m("cost_fulfil", "ref_keep*(cl_o + cl_f)*fo", "Fulfilment total")
    m("cost_support", "ref_keep*(cl_o + cl_f)*sup_u", "Support total")
    m("cost_storage", "ref_keep*(cl_o + cl_f)*stor_u", "Storage total")
    m("cost_repl", "ref_keep*dfr*(cl_o*(goods_o + cs_o + fo) + cl_f*(goods_f + cs_f + fo))", "Replacements for defects (unit + reship)")
    # ---- fixed costs
    for ph in ("pre", "post"):
        m(f"fx_{ph}_c0", _fixed_sum(rows, "common", ph) + " + has_o*(" + _fixed_sum(rows, "original", ph) + ") + has_f*(" + _fixed_sum(rows, "founder", ph) + ")", f"One-offs paid {ph} at base cost")
    m("fx_pre", "cost_mult*fx_pre_c0", "Pre-launch one-offs (prototypes, samples, video, legal) - lost if campaign fails")
    m("fx_post", "cost_mult*fx_post_c0", "Post-funding one-offs (compliance, test kit, registrations) - paid from payout")
    m("fx_order", "has_f*cost_mult*cnc_nre + use_im*im_tool_c", "One-offs paid at order, before payout (CNC setup, mould tooling)")
    m("fx_vatcost", "(1 - vat_reg)*fx_vat_share*vat_rate*(fx_pre + fx_post + fx_order)", "Irrecoverable VAT on UK-invoiced one-offs")
    m("fx_total", "fx_pre + fx_post + fx_order + fx_vatcost", "TOTAL FIXED COSTS")
    # ---- funding goal (base costs, no shocks)
    m("moq_o", "moq_units*(1 - mix_f)", "MOQ Original")
    m("moq_f", "moq_units*mix_f", "MOQ Founder's")
    m("g_elec", "LOOKUP(moq_units, tier_qty, elec_tier)*(1 + qa_scrap)", "Goal: electronics per unit")
    m("g_o", "g_elec + LOOKUP(moq_o, tier_qty, mjf_tier)/(1 - mjf_scrap) + labour_rate*(asm_min_o + flash_min + qa_min)/60 + LOOKUP(moq_o, tier_qty, pack_o_tier) + freight_in", "Goal: cost per Original")
    m("g_f", "g_elec + LOOKUP(moq_f, tier_qty, cnc_tier)/(1 - cnc_scrap) + cnc_window + labour_rate*(asm_min_f + flash_min + qa_min)/60 + LOOKUP(moq_f, tier_qty, pack_f_tier) + freight_in", "Goal: cost per Founder's")
    m("moq_cash", "moq_o*g_o + moq_f*g_f", "MOQ cash need")
    m("fx_plan", "fx_pre_c0 + fx_post_c0 + has_f*cnc_nre", "Fixed costs for goal (base)")
    m("goal", "CEILING((fx_plan + moq_cash)*(1 + goal_cont)/(1 - ks_fee_pct - proc_pct - ad_pct - fail_rate), 500)", "RECOMMENDED FUNDING GOAL")
    m("pledged_ks", "ks_funds/(1 - fail_rate)", "Kickstarter total as pledged (before failures)")
    m("funded", "IF(pledged_ks >= goal, 1, 0)", "Goal reached (1/0)")
    # ---- profit
    m("prod_total", "cost_elec + cost_encl + cost_labour + cost_pack + cost_inbound", "Production cost total")
    m("deliv_total", "cost_ship_out + cost_fulfil + cost_support + cost_storage + cost_repl", "Delivery cost total")
    m("cost_cont", "cont_pct*(prod_total + deliv_total + fx_total)", "Contingency")
    m("np_funded", "gross_total - refunds - vat_net - fees_ks - fees_proc - fees_pm - ads - prod_total - deliv_total - fx_total - cost_cont - d_lump", "Net profit if funded")
    m("np", "IF(funded > 0.5, np_funded, -(fx_pre + ads))", "NET PROFIT BEFORE BUSINESS TAX (failed campaign loses pre-launch spend + ads)")
    # ---- per-unit contribution (per collected backer, before fixed costs; incl variable ads/fees/contingency on variable)
    for e, ed in (("o", "Original"), ("f", "Founder's")):
        m(f"cu_{e}",
          f"uk_{e}*(1 - vatk)*ref_keep - ks_fee_pct*ksf_{e} - fee_intl*ksf_{e} - proc_fixed - is_pm*(pm_campaign_pct*ksf_{e} + (pm_txn_pct + fee_intl)*pmf + proc_fixed) - ad_pct*ksf_{e}"
          f" - (1 + cont_pct)*(kprod*goods_{e} + ref_keep*(cs_{e} + fo + sup_u + stor_u + dfr*(goods_{e} + cs_{e} + fo)))",
          f"CONTRIBUTION per {ed} backer before fixed costs")
    m("avg_cu", "(cl_o*cu_o + cl_f*cu_f)/MAX(cl_o + cl_f, 0.000000001)", "Average contribution per collected unit")
    m("be_units", "IF(avg_cu > 0, (fx_total*(1 + cont_pct) + d_lump)/avg_cu, 999999)", "Break-even units at this mix/price")
    # ---- cash and risk
    m("sup_cost", "pr_o*(elec_u + enc_o + pack_ou) + pr_f*(elec_u + enc_f + pack_fu)", "Supplier-paid goods")
    m("deposits", "dep_pct*sup_cost + fx_order", "Supplier deposits + tooling paid at order (before payout)")
    m("cash_upfront", "IF(funded > 0.5, fx_pre + ads + deposits, fx_pre + ads)", "CASH NEEDED BEFORE KICKSTARTER PAYOUT")
    m("risk", "MIN(100, IF(np < 0, 30, 0) + IF(np < 0.1*gross_total, 15, 0) + IF(cash_upfront > risk_cash_cap, 20, 0) + IF(funded < 0.5, 25, 0) + IF(pledged_ks < 1.3*goal, 10, 0) + IF(bk_o + bk_f < 50, 5, 0))", "RISK SCORE 0-100")
    return M

NAMES_OUT = ["bk_o", "bk_f", "gross_total", "ks_funds", "pm_funds", "vat_net", "refunds", "fees_ks", "fees_proc", "fees_pm", "ads",
             "cost_elec", "cost_encl", "cost_labour", "cost_pack", "cost_inbound", "cost_ship_out", "cost_fulfil", "cost_support",
             "cost_storage", "cost_repl", "fx_pre", "fx_post", "fx_order", "fx_vatcost", "cost_cont", "np", "cu_o", "cu_f", "funded", "goal",
             "cash_upfront", "be_units", "risk", "use_im", "vat_reg"]

class Model:
    def __init__(self, rows=None, mode="value", overrides=None):
        self.rows = rows or load_rows()
        self.env0 = build_env(self.rows, mode, overrides)
        self.lines = build_model(self.rows)
        dup = set(n for n, _, _ in self.lines) & set(self.env0)
        assert not dup, f"name clash between inputs and model lines: {dup}"
        self.code = [(n, compile(e, n, "eval")) for n, e, _ in self.lines]

    def run(self, **S):
        env = dict(self.env0); env.update(FUNCS); env.update(SCENARIO_DEFAULTS); env.update(S)
        for n, c in self.code:
            env[n] = eval(c, env)
        return env

    def with_overrides(self, overrides=None, mode="value"):
        return Model(self.rows, mode, overrides)

# ---------------------------------------------------------------- cash timeline
def cash_timeline(V, months=16):
    """Monthly cash flows. m0 pre-launch, m1 campaign + supplier deposits, m2 Kickstarter payout (~14 days after close).
    Sum of flows equals net profit when funded (checked in tests)."""
    f = [0.0] * months
    d = int(V["d_delay"])
    f[0] -= V["fx_pre"]
    f[1] -= V["ads"]
    if V["funded"] < 0.5:
        return f
    f[1] -= V["deposits"]
    f[2] += V["ks_funds"] - V["fees_ks"] - V["fees_proc"]
    f[3 + d] += V["pm_funds"] - V["fees_pm"] - V["refunds"] - (1 - V["dep_pct"]) * V["sup_cost"] - V["cost_labour"]
    imp = V["pr_o"] * V["impv_o"] + V["pr_f"] * V["impv_f"]
    f[4 + d] -= V["pr_o"] * (V["frt"] + V["duty_o"]) + V["pr_f"] * (V["frt"] + V["duty_f"]) + imp
    f[3 + d] -= V["fx_post"]
    f[5 + d] -= V["deliv_total"] + V["cost_cont"] + V["d_lump"] + V["fx_vatcost"]
    f[6 + d] -= V["vat_net"]
    if V["vat_reg"] > 0.5:
        f[7 + d] += imp
    return f

def peak_negative_cash(V):
    c = 0.0; low = 0.0
    for x in cash_timeline(V):
        c += x; low = min(low, c)
    return -low

def risk_text(V):
    bits = []
    if V["funded"] < 0.5: bits.append("campaign misses goal: lose pre-launch spend")
    if V["np"] < 0: bits.append("loss-making")
    elif V["np"] < 0.1 * V["gross_total"]: bits.append("thin margin (<10% of pledges)")
    if V["cash_upfront"] > V["risk_cash_cap"]: bits.append(f"needs GBP {V['cash_upfront']:,.0f} before payout")
    if V["pledged_ks"] < 1.3 * V["goal"] and V["funded"] > 0.5: bits.append("only just clears goal")
    return "; ".join(bits) or "comfortable on these inputs"

# ---------------------------------------------------------------- scenario grid
PRICE_SETS = {"103/194": (103, 194), "79/149": (79, 149), "109/199": (109, 199), "119/229": (119, 229), "129/249": (129, 249)}
MIXES = {"Original-only": 0.0, "Founders-only": 1.0, "80/20": 0.2, "60/40": 0.4}
UNITS = [100, 250, 500, 1000, 5000]
COSTS = {"base": 1.0, "+15%": 1.15, "+30%": 1.30}
EB = {"none": 0.0, "-10%": 0.10, "-15%": 0.15}
SHIP = {"included": 1, "separate": 2, "pledge-manager": 3}
SHOCKS = ["delay-3m", "defect-5%", "defect-10%", "refunds+5pp", "lump"]

def demand_levels(A):
    return {"conservative": A["dm_cons"], "expected": A["dm_exp"], "optimistic": A["dm_opt"]}

def shock_kwargs(A, name):
    return {"none": {}, "delay-3m": dict(d_delay=A["shock_delay"]), "defect-5%": dict(d_defect=A["shock_defect_lo"]),
            "defect-10%": dict(d_defect=A["shock_defect_hi"]), "refunds+5pp": dict(d_refund=A["shock_refund"]),
            "lump": dict(d_lump=A["shock_lump"])}[name]

def scenarios(model):
    A = model.env0
    dl = demand_levels(A)
    for u in UNITS:
        for mn, mf in MIXES.items():
            for ps, (po, pf) in PRICE_SETS.items():
                for dn, dm in dl.items():
                    for cn, cm in COSTS.items():
                        for en, ed in EB.items():
                            for sn, sm in SHIP.items():
                                yield dict(units=u, mix=mn, mix_f=mf, price_set=ps, p_o=po, p_f=pf, demand=dn, dem_mult=dm,
                                           cost=cn, cost_mult=cm, eb=en, eb_disc=ed, ship=sn, ship_mode=sm, shock="none")
    for u in UNITS:
        for mn, mf in MIXES.items():
            for ps, (po, pf) in PRICE_SETS.items():
                for sh in SHOCKS:
                    yield dict(units=u, mix=mn, mix_f=mf, price_set=ps, p_o=po, p_f=pf, demand="expected", dem_mult=A["dm_exp"],
                               cost="base", cost_mult=1.0, eb="none", eb_disc=0.0, ship="separate", ship_mode=2, shock=sh)

def run_scenario(model, sc):
    A = model.env0
    S = dict(n_ref=sc["units"], mix_f=sc["mix_f"], p_o=sc["p_o"], p_f=sc["p_f"], dem_mult=sc["dem_mult"], cost_mult=sc["cost_mult"],
             eb_disc=sc["eb_disc"], ship_mode=sc["ship_mode"], vat_mode=sc.get("vat_mode", 1))
    S.update(shock_kwargs(A, sc["shock"]))
    return model.run(**S)

SC_COLS = ["units", "mix", "price_set", "demand", "cost", "eb", "ship", "shock"]

def write_scenarios(model, path):
    n = 0
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["scenario_id"] + SC_COLS + NAMES_OUT[:25] + ["peak_negative_cash"] + NAMES_OUT[25:] + ["risk_text"])
        for sc in scenarios(model):
            V = run_scenario(model, sc); n += 1
            row = [n] + [sc[c] for c in SC_COLS]
            vals = {k: V[k] for k in NAMES_OUT}
            out = [round(vals[k], 2) for k in NAMES_OUT[:25]] + [round(peak_negative_cash(V), 2)] + [round(vals[k], 2) for k in NAMES_OUT[25:]]
            w.writerow(row + out + [risk_text(V)])
    return n

# ---------------------------------------------------------------- analysis helpers
def expected_and_downside(model, units, mix_f, p_o, p_f, eb_disc=0.0, ship_mode=2, vat_mode=1):
    A = model.env0
    probs = dict(conservative=A["p_cons"], expected=A["p_exp"], optimistic=A["p_opt"])
    nps = {}; funded = {}
    for dn, dm in demand_levels(A).items():
        V = model.run(n_ref=units, mix_f=mix_f, p_o=p_o, p_f=p_f, dem_mult=dm, eb_disc=eb_disc, ship_mode=ship_mode, vat_mode=vat_mode)
        nps[dn] = V["np"]; funded[dn] = V["funded"]
    exp = sum(probs[k] * nps[k] for k in nps)
    D = model.run(n_ref=units, mix_f=mix_f, p_o=p_o, p_f=p_f, dem_mult=A["dm_cons"], cost_mult=1.15, eb_disc=eb_disc, ship_mode=ship_mode,
                  vat_mode=vat_mode, d_defect=0.075, d_refund=0.03, d_lump=A["shock_lump"])
    return dict(expected=exp, downside=D["np"], np=nps, funded=funded, cash=D["cash_upfront"], goal=D["goal"])

def break_even_backers(model, mix_f, p_o, p_f, ship_mode=2, vat_mode=1):
    """Smallest total backers (step 5) at which net profit > 0 and goal is met, base costs, no shocks."""
    for n in range(5, 8001, 5):
        V = model.run(ovr_total=n, mix_f=mix_f, p_o=p_o, p_f=p_f, ship_mode=ship_mode, vat_mode=vat_mode)
        if V["np"] > 0:
            return n
    return None

def sensitivity(model, ref):
    """Tornado: net profit at the reference scenario when each driver goes to its low / high value."""
    base = model.run(**ref)["np"]
    rows = model.rows
    groups = {}
    for r in rows:
        if float(r["low"]) == float(r["high"]):
            continue
        key = re.sub(r"_t\d+$", "", r["id"])
        groups.setdefault(key, []).append(r["id"])
    out = []
    for key, ids in groups.items():
        res = []
        for mode in ("low", "high"):
            ov = {i: float(next(r for r in rows if r["id"] == i)[mode]) for i in ids}
            m2 = model.with_overrides(ov)
            res.append(m2.run(**ref)["np"] - base)
        name = next(r["name"] for r in rows if r["id"] == ids[0]).split(" (qty")[0]
        out.append((key, name, res[0], res[1]))
    out.sort(key=lambda x: -max(abs(x[2]), abs(x[3])))
    return base, out

# ---------------------------------------------------------------- main
def money(x): return f"-GBP {abs(x):,.0f}" if x < 0 else f"GBP {x:,.0f}"

def main():
    model = Model()
    if "--quick" in sys.argv:
        V = model.run()
        for n, _, label in model.lines:
            if n in NAMES_OUT or n in ("goal", "fx_total", "cash_upfront"):
                print(f"{label or n:70s} {V[n]:12,.2f}")
        return
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    n = write_scenarios(model, os.path.join(HERE, "out", "scenarios.csv"))
    print(f"wrote {n} scenarios")
    import summary
    summary.write_summary(model, os.path.join(HERE, "out", "SUMMARY.md"))

if __name__ == "__main__":
    main()
