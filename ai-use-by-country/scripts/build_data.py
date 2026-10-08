"""Build the analysis tables for the AI use by country project.

Run from the project folder:  python scripts/build_data.py
Reads  data/raw/ai_diffusion_readings.csv
Writes data/processed/ai_use_tidy.csv, data/processed/ai_use_by_economy.csv,
       data/processed/region_summary.csv, data/processed/source_checks.csv
       and data/processed/world_aggregates.csv (from data/raw/aggregate_readings.csv)
"""
import os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "..", "data", "raw", "ai_diffusion_readings.csv")
AGG = os.path.join(HERE, "..", "data", "raw", "aggregate_readings.csv")
OUT = os.path.join(HERE, "..", "data", "processed")
os.makedirs(OUT, exist_ok=True)

PERIODS = ["2025-H1", "2025-H2", "2026-Q1", "2026-Q2"]
Q2_REPORT = "Microsoft AI Economy Institute, Global AI Diffusion Q2 2026 (September 2026)"
Q1_REPORT = "Microsoft AI Economy Institute, Global AI Diffusion Report 2026 Q1 (May 2026)"
H2_REPORT = "Microsoft AI Economy Institute, Global AI Adoption in 2025 (H2 2025 report, January 2026)"
# Each value comes from the newest report that prints it. The Q2 2026 report prints Q1 2026 and Q2 2026;
# the Q1 2026 report prints H1 2025 to Q1 2026; the H2 2025 report prints H1 2025 and H2 2025.
VINTAGE = {Q2_REPORT: 2, Q1_REPORT: 1, H2_REPORT: 0}

# Middle East is split into four sub-regions. Bahrain, Yemen and Palestine are not in the report.
MIDDLE_EAST = {
    "Gulf": ["United Arab Emirates", "Qatar", "Saudi Arabia", "Oman", "Kuwait"],
    "Levant and Iraq": ["Israel", "Jordan", "Lebanon", "Syria", "Iraq"],
    "North Africa": ["Egypt", "Libya", "Tunisia", "Algeria", "Morocco"],
    "Iran and Turkey": ["Iran", "Turkey"],
}
REGIONS = {
    "Europe": ["Ireland", "France", "Norway", "Spain", "United Kingdom", "Netherlands", "Belgium", "Switzerland",
               "Sweden", "Austria", "Hungary", "Denmark", "Germany", "Poland", "Italy", "Czech Republic", "Bulgaria",
               "Finland", "Slovenia", "Portugal", "Croatia", "Slovak Republic", "Serbia", "Lithuania",
               "Bosnia and Herzegovina", "Greece", "Albania", "Moldova", "Romania", "Belarus", "Russia", "Ukraine"],
    "Asia": ["Singapore", "South Korea", "Taiwan", "Vietnam", "Japan", "Malaysia", "Georgia", "Philippines",
             "Azerbaijan", "India", "Mongolia", "China", "Kazakhstan", "Indonesia", "Nepal", "Thailand", "Pakistan",
             "Myanmar", "Kyrgyzstan", "Laos", "Bangladesh", "Armenia", "Sri Lanka", "Uzbekistan", "Tajikistan",
             "Afghanistan", "Turkmenistan", "Cambodia"],
    "Oceania": ["New Zealand", "Australia", "Papua New Guinea"],
    "Americas": ["Canada", "United States", "Costa Rica", "Colombia", "Dominican Republic", "Uruguay", "Jamaica",
                 "Panama", "Chile", "Argentina", "Mexico", "Ecuador", "Brazil", "El Salvador", "Peru", "Guatemala",
                 "Honduras", "Bolivia", "Paraguay", "Nicaragua", "Guyana", "Suriname", "Venezuela", "French Guiana",
                 "Haiti", "Cuba"],
    "Sub-Saharan Africa": ["South Africa", "Gabon", "Namibia", "Botswana", "Senegal", "Cote d'Ivoire", "Zambia",
                           "Gambia", "Mozambique", "Angola", "Madagascar", "Malawi", "Togo", "Guinea", "Niger",
                           "Liberia", "Nigeria", "Benin", "Mali", "Ghana", "Guinea-Bissau", "Sierra Leone",
                           "Mauritania", "Burkina Faso", "Lesotho", "Chad", "Central African Republic", "Cameroon",
                           "Democratic Republic of the Congo", "Congo", "Kenya", "Zimbabwe", "Uganda", "Ethiopia",
                           "Somalia", "Eritrea", "South Sudan", "Sudan", "Burundi", "Tanzania", "Rwanda"],
}
REGION_ORDER = ["Middle East", "Europe", "Asia", "Oceania", "Americas", "Sub-Saharan Africa"]


def region_table():
    rows = [(e, "Middle East", sub) for sub, es in MIDDLE_EAST.items() for e in es]
    rows += [(e, r, r) for r, es in REGIONS.items() for e in es]
    reg = pd.DataFrame(rows, columns=["economy", "region", "sub_region"])
    assert not reg.economy.duplicated().any(), "economy assigned to two regions"
    return reg


def load_raw():
    raw = pd.read_csv(RAW)
    assert raw[["economy", "period", "ai_diffusion_pct", "document", "url"]].notna().all().all(), "missing value"
    assert not raw.duplicated(["economy", "period", "document"]).any(), "duplicate reading from one document"
    assert set(raw.period) == set(PERIODS), "unexpected period label"
    assert raw.ai_diffusion_pct.between(0, 100).all(), "share outside 0 to 100"
    return raw


def reconcile(raw):
    """One value per economy and period. Rules:
    - Readings from different publishers must agree exactly, or the build stops.
    - Two Microsoft reports may differ by at most 0.1 point (a revision in the later report).
      The later report's value is used and the row is labelled 'revised'.
    """
    ms = raw[raw.document.isin(VINTAGE)].copy()
    ms["vintage"] = ms.document.map(VINTAGE)
    latest = ms.sort_values("vintage").groupby(["economy", "period"]).tail(1)
    latest = latest.set_index(["economy", "period"]).ai_diffusion_pct

    checks = []
    for (e, p), g in raw.groupby(["economy", "period"]):
        value = latest.loc[(e, p)]
        msg = g[g.document.isin(VINTAGE)]
        others = g[~g.document.isin(VINTAGE)]
        spread = msg.ai_diffusion_pct.max() - msg.ai_diffusion_pct.min()
        if round(spread, 2) > 0.1:
            raise SystemExit(f"Microsoft reports disagree by more than 0.1 point: {e} {p}\n{msg}")
        bad = others[others.ai_diffusion_pct != value]
        if len(bad):
            raise SystemExit(f"Publication disagrees with report: {e} {p}\n{bad}")
        n_docs = g.document.nunique()
        n_pub = g.publisher.nunique()
        if spread > 0:
            status = "revised"
        elif n_pub >= 2:
            status = "two-publishers"
        elif n_docs >= 2:
            status = "two-reports"
        else:
            status = "single-document"
        checks.append({"economy": e, "period": p, "ai_diffusion_pct": value, "documents": n_docs,
                       "publishers": n_pub, "verification": status,
                       "earlier_report_value": msg.ai_diffusion_pct.iloc[0] if spread > 0 else None})
    return pd.DataFrame(checks)


def published_ranks(raw):
    """Ranks printed in each report must follow the order of the values (ties may be printed either way)."""
    out = {}
    for doc, period in [(Q2_REPORT, "2026-Q2"), (Q1_REPORT, "2026-Q1"), (H2_REPORT, "2025-H2")]:
        t = raw[(raw.document == doc) & (raw.period == period)].copy()
        t = t.sort_values("published_rank")
        assert list(t.published_rank.astype(int)) == list(range(1, 148)), f"ranks not 1 to 147 in {doc}"
        assert t.ai_diffusion_pct.is_monotonic_decreasing, f"rank order does not follow values in {doc}"
        out[period] = t.set_index("economy").published_rank.astype(int)
    return out


def imputed_groups(tidy):
    """Economies that share the same value in all four periods carry a regional estimate, not their own figure."""
    wide = tidy.pivot(index="economy", columns="period", values="ai_diffusion_pct")[PERIODS]
    key = wide.apply(lambda r: "|".join(f"{v:.1f}" for v in r), axis=1)
    sizes = key.map(key.value_counts())
    groups = {}
    for i, k in enumerate(sorted(key[sizes > 1].unique(), key=lambda k: -float(k.split("|")[-1]))):
        groups.update({e: f"group {i + 1}" for e in key[key == k].index})
    return groups


def build_aggregates():
    """World, Global North and Global South as published. Every document must give the same figure."""
    agg = pd.read_csv(AGG)
    spread = agg.groupby(["group", "period"]).ai_diffusion_pct.agg(["min", "max", "count"])
    if (spread["min"] != spread["max"]).any():
        raise SystemExit("Documents disagree on an aggregate:\n" + spread[spread["min"] != spread["max"]].to_string())
    out = spread["min"].unstack("group")[["World", "Global North", "Global South"]].reindex(PERIODS)
    out.columns = ["world_pct", "global_north_pct", "global_south_pct"]
    out["north_south_gap_pp"] = (out.global_north_pct - out.global_south_pct).round(1)
    out["documents_world"] = spread["count"].unstack("group")["World"].reindex(PERIODS)
    out.index.name = "period"
    out.reset_index().to_csv(os.path.join(OUT, "world_aggregates.csv"), index=False)
    return out


def main():
    agg = build_aggregates()
    print(agg.to_string())
    raw = load_raw()
    checks = reconcile(raw)
    ranks = published_ranks(raw)
    reg = region_table()
    assert set(reg.economy) == set(checks.economy), set(reg.economy) ^ set(checks.economy)
    assert checks.groupby("economy").period.nunique().eq(4).all(), "an economy is missing a period"

    tidy = checks.merge(reg, on="economy")
    groups = imputed_groups(tidy)
    tidy["shared_value_group"] = tidy.economy.map(groups)
    tidy["own_estimate"] = tidy.shared_value_group.isna().map({True: "yes", False: "no"})
    tidy["period_order"] = tidy.period.map({p: i for i, p in enumerate(PERIODS)})
    tidy = tidy.sort_values(["region", "sub_region", "economy", "period_order"]).drop(columns="period_order")
    tidy.to_csv(os.path.join(OUT, "ai_use_tidy.csv"), index=False)

    wide = tidy.pivot(index="economy", columns="period", values="ai_diffusion_pct")[PERIODS]
    wide.columns = ["h1_2025_pct", "h2_2025_pct", "q1_2026_pct", "q2_2026_pct"]
    eco = reg.set_index("economy").join(wide)
    eco["rank_q2_2026"] = ranks["2026-Q2"]
    eco["rank_q1_2026_report"] = ranks["2026-Q1"]
    eco["change_q1_to_q2_pp"] = (eco.q2_2026_pct - eco.q1_2026_pct).round(1)
    eco["change_h1_2025_to_q2_2026_pp"] = (eco.q2_2026_pct - eco.h1_2025_pct).round(1)
    eco["shared_value_group"] = eco.index.map(groups)
    eco["own_estimate"] = eco.shared_value_group.isna().map({True: "yes", False: "no"})
    ver = tidy[tidy.period == "2026-Q2"].set_index("economy").verification
    eco["q2_2026_verification"] = ver
    eco = eco.reset_index().sort_values("rank_q2_2026")
    eco.to_csv(os.path.join(OUT, "ai_use_by_economy.csv"), index=False)

    world = agg.loc["2026-Q2", "world_pct"]
    rows = []
    for region in REGION_ORDER:
        g = eco[eco.region == region]
        subs = [(region, g)] + ([(f"Middle East: {s}", g[g.sub_region == s]) for s in MIDDLE_EAST] if region == "Middle East" else [])
        for name, s in subs:
            own = s[s.own_estimate == "yes"]
            top = s.loc[s.q2_2026_pct.idxmax()]
            low = s.loc[s.q2_2026_pct.idxmin()]
            rows.append({"group": name, "economies": len(s), "economies_own_estimate": len(own),
                         "median_q2_2026_pct": round(s.q2_2026_pct.median(), 2),
                         "median_change_q1_to_q2_pp": round(s.change_q1_to_q2_pp.median(), 2),
                         "highest": top.economy, "highest_q2_2026_pct": top.q2_2026_pct,
                         "lowest": low.economy, "lowest_q2_2026_pct": low.q2_2026_pct,
                         "economies_above_world_pct": int((s.q2_2026_pct > world).sum())})
    rows.append({"group": "All 147 economies", "economies": len(eco),
                 "economies_own_estimate": int((eco.own_estimate == "yes").sum()),
                 "median_q2_2026_pct": round(eco.q2_2026_pct.median(), 2),
                 "median_change_q1_to_q2_pp": round(eco.change_q1_to_q2_pp.median(), 2),
                 "highest": eco.iloc[0].economy, "highest_q2_2026_pct": eco.iloc[0].q2_2026_pct,
                 "lowest": eco.iloc[-1].economy, "lowest_q2_2026_pct": eco.iloc[-1].q2_2026_pct,
                 "economies_above_world_pct": int((eco.q2_2026_pct > world).sum())})
    summary = pd.DataFrame(rows)
    summary.to_csv(os.path.join(OUT, "region_summary.csv"), index=False)

    src = (tidy.groupby(["period", "verification"]).size().unstack(fill_value=0).reindex(PERIODS))
    src.to_csv(os.path.join(OUT, "source_checks.csv"))

    print(f"{len(raw)} raw readings -> {len(tidy)} tidy rows, {len(eco)} economies")
    print(f"economies sharing a value with others in all four periods: {len(groups)} in {len(set(groups.values()))} groups")
    print(src.to_string())
    print(summary[["group", "economies", "economies_own_estimate", "median_q2_2026_pct", "highest",
                   "highest_q2_2026_pct", "lowest", "lowest_q2_2026_pct", "economies_above_world_pct"]].to_string(index=False))
    return tidy, eco, summary


if __name__ == "__main__":
    main()
