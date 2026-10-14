"""Build the processed tables for the Egypt remittances project.

Reads every figure collected from every document in data/raw, checks that
documents agree, tests the published growth rates and the accounting
identities that link the figures, and writes data/processed.

Run from the project folder:  python scripts/build_data.py
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

# Readings set aside on purpose, with the reason recorded in the raw file.
EXCLUDED = {
    ("fiscal_year", "FY2023/24", "enterprise_2025_08"),  # 22.1 against 21.9 in two documents
    ("fiscal_year", "FY2017/18", "enterprise_2019_10"),  # rounded, and the year is outside the series
    ("cumulative_fy", "FY2025/26 Jul-Feb", "ahram_2026_06"),  # one document; implies an unconfirmed March of 5.5
}
ROUNDED_ONLY = {("fiscal_year", "FY2018/19", "enterprise_2019_10")}  # printed to whole billions

# Values are printed to one decimal place, so each one stands for a range of +/- 0.05.
HALF = 0.05


def load():
    readings = pd.read_csv(RAW / "remittance_readings.csv")
    growth = pd.read_csv(RAW / "published_growth_rates.csv")
    sources = pd.read_csv(RAW / "sources.csv")
    assert readings["source_id"].isin(sources["source_id"]).all(), "unknown source id"
    assert growth["source_id"].isin(sources["source_id"]).all(), "unknown source id"
    return readings, growth, sources


def consolidate(readings, sources):
    key = list(zip(readings["measure"], readings["period"], readings["source_id"]))
    readings = readings.assign(_key=key)
    used = readings[~readings["_key"].isin(EXCLUDED)]
    exact = used[~used["_key"].isin(ROUNDED_ONLY)]
    rounded = used[used["_key"].isin(ROUNDED_ONLY)]

    rows = []
    for (measure, period), grp in exact.groupby(["measure", "period"], sort=False):
        values = grp["value_usd_bn"].unique()
        if len(values) != 1:
            raise ValueError(f"documents disagree on {measure} {period}: {values}")
        publishers = sources.set_index("source_id").loc[grp["source_id"], "publisher"].unique()
        n_docs = grp["source_id"].nunique()
        if len(publishers) >= 2:
            check = "two-publishers"
        elif n_docs >= 2:
            check = "two-documents-same-publisher"
        else:
            check = "one-document"
        rows.append({
            "measure": measure,
            "period": period,
            "period_start": grp["period_start"].iloc[0],
            "period_end": grp["period_end"].iloc[0],
            "value_usd_bn": float(values[0]),
            "n_documents": n_docs,
            "n_publishers": len(publishers),
            "source_check": check,
            "source_ids": ";".join(grp["source_id"]),
        })
    tidy = pd.DataFrame(rows)

    # A reading printed to whole billions must round to the same value.
    for _, r in rounded.iterrows():
        v = tidy.loc[(tidy.measure == r.measure) & (tidy.period == r.period), "value_usd_bn"].iloc[0]
        assert round(v) == r.value_usd_bn, f"rounded reading disagrees for {r.period}"
        idx = tidy.index[(tidy.measure == r.measure) & (tidy.period == r.period)][0]
        tidy.loc[idx, "source_check"] = "one-document-plus-rounded-second"
        tidy.loc[idx, "source_ids"] += ";" + r.source_id + "(rounded)"
    return tidy


def value(tidy, measure, period):
    hit = tidy[(tidy.measure == measure) & (tidy.period == period)]
    assert len(hit) == 1, f"missing {measure} {period}"
    return float(hit["value_usd_bn"].iloc[0])


def growth_range(new, old):
    """Range of growth rates (%) consistent with two values rounded to 0.1."""
    lo = ((new - HALF) / (old + HALF) - 1) * 100
    hi = ((new + HALF) / (old - HALF) - 1) * 100
    return lo, hi


def check_growth(tidy, growth):
    rows = []
    for _, g in growth.iterrows():
        new = value(tidy, g.measure, g.period)
        old_measure = g.measure
        old = value(tidy, old_measure, g.compared_with) if (
            (tidy.measure == old_measure) & (tidy.period == g.compared_with)).any() else None
        if old is None:
            # cumulative comparison periods and some months exist only as a base in the text
            rows.append({**g.to_dict(), "computed_lo": None, "computed_hi": None, "result": "base not in table"})
            continue
        lo, hi = growth_range(new, old)
        # published rates are themselves rounded (to 0.1 or to a whole number)
        tol = 0.5 if float(g.growth_pct).is_integer() else 0.05
        ok = lo - tol <= g.growth_pct <= hi + tol
        rows.append({**g.to_dict(), "computed_lo": round(lo, 2), "computed_hi": round(hi, 2),
                     "result": "pass" if ok else "FAIL"})
    out = pd.DataFrame(rows)
    return out


def identities(tidy):
    checks = []

    def add(name, left, right, tol):
        checks.append({"identity": name, "left": round(left, 2), "right": round(right, 2),
                       "difference": round(left - right, 2), "tolerance": tol,
                       "result": "pass" if abs(left - right) <= tol + 1e-9 else "FAIL"})

    # Calendar 2025 = second half of FY2024/25 + first half of FY2025/26
    h2_fy25 = value(tidy, "fiscal_year", "FY2024/25") - value(tidy, "cumulative_fy", "FY2024/25 Jul-Dec")
    add("calendar 2025 = (FY2024/25 - Jul-Dec 2024) + Jul-Dec 2025",
        h2_fy25 + value(tidy, "cumulative_fy", "FY2025/26 Jul-Dec"),
        value(tidy, "calendar_year", "2025"), 0.15)
    # Apr-Jun 2025 quarter = FY2024/25 - Jul-Mar of FY2024/25
    add("Apr-Jun 2025 = FY2024/25 - Jul-Mar FY2024/25",
        value(tidy, "fiscal_year", "FY2024/25") - value(tidy, "cumulative_fy", "FY2024/25 Jul-Mar"),
        value(tidy, "quarter", "Apr-Jun 2025"), 0.15)
    # January 2026 = Jul-Jan total - Jul-Dec total
    add("Jan 2026 = Jul-Jan FY2025/26 - Jul-Dec FY2025/26",
        value(tidy, "cumulative_fy", "FY2025/26 Jul-Jan") - value(tidy, "cumulative_fy", "FY2025/26 Jul-Dec"),
        value(tidy, "month", "2026-01"), 0.15)
    # cumulative sums must rise month by month
    seq = [value(tidy, "cumulative_fy", p) for p in
           ["FY2025/26 Jul-Dec", "FY2025/26 Jul-Jan", "FY2025/26 Jul-Mar"]]
    seq.append(value(tidy, "fiscal_year", "FY2025/26"))
    assert all(b > a for a, b in zip(seq, seq[1:])), "cumulative FY2025/26 figures do not rise"
    checks = pd.DataFrame(checks)
    return checks


def derived(tidy):
    """Figures computed from published ones (labelled as derived)."""
    rows = []
    fy26 = value(tidy, "fiscal_year", "FY2025/26")
    pairs = [
        ("Apr-Jun 2026", fy26 - value(tidy, "cumulative_fy", "FY2025/26 Jul-Mar"), "FY2025/26 minus Jul-Mar"),
        ("Feb-Mar 2026", value(tidy, "cumulative_fy", "FY2025/26 Jul-Mar") - value(tidy, "cumulative_fy", "FY2025/26 Jul-Jan"), "Jul-Mar minus Jul-Jan"),
        ("Jan-Jun 2025", value(tidy, "fiscal_year", "FY2024/25") - value(tidy, "cumulative_fy", "FY2024/25 Jul-Dec"), "FY2024/25 minus Jul-Dec 2024"),
        ("Jan-Jun 2026", fy26 - value(tidy, "cumulative_fy", "FY2025/26 Jul-Dec"), "FY2025/26 minus Jul-Dec 2025"),
    ]
    for period, v, how in pairs:
        rows.append({"period": period, "value_usd_bn": round(v, 1), "method": how})
    return pd.DataFrame(rows)


def fiscal_series(tidy):
    fy = tidy[tidy.measure == "fiscal_year"].copy().sort_values("period_start").reset_index(drop=True)
    fy["change_usd_bn"] = fy["value_usd_bn"].diff().round(1)
    fy["change_pct"] = (fy["value_usd_bn"].pct_change() * 100).round(1)
    fy["index_fy2018_19_100"] = (fy["value_usd_bn"] / fy["value_usd_bn"].iloc[0] * 100).round(1)
    fy["is_record_so_far"] = fy["value_usd_bn"] >= fy["value_usd_bn"].cummax()
    return fy[["period", "period_start", "period_end", "value_usd_bn", "change_usd_bn", "change_pct",
               "index_fy2018_19_100", "is_record_so_far", "source_check", "source_ids"]]


def headline(tidy, fy):
    v = lambda m, p: value(tidy, m, p)
    h = {
        "fy2025_26_usd_bn": v("fiscal_year", "FY2025/26"),
        "fy2025_26_growth_pct": round((v("fiscal_year", "FY2025/26") / v("fiscal_year", "FY2024/25") - 1) * 100, 1),
        "fy2023_24_usd_bn": v("fiscal_year", "FY2023/24"),
        "two_year_multiple": round(v("fiscal_year", "FY2025/26") / v("fiscal_year", "FY2023/24"), 2),
        "two_year_gain_usd_bn": round(v("fiscal_year", "FY2025/26") - v("fiscal_year", "FY2023/24"), 1),
        "pct_above_previous_peak_fy2021_22": round((v("fiscal_year", "FY2025/26") / v("fiscal_year", "FY2021/22") - 1) * 100, 1),
        "fy2022_23_fall_pct": round((v("fiscal_year", "FY2022/23") / v("fiscal_year", "FY2021/22") - 1) * 100, 1),
        "calendar_2025_usd_bn": v("calendar_year", "2025"),
        "calendar_2025_growth_pct": round((v("calendar_year", "2025") / v("calendar_year", "2024") - 1) * 100, 1),
        "apr_jun_2026_derived_usd_bn": round(v("fiscal_year", "FY2025/26") - v("cumulative_fy", "FY2025/26 Jul-Mar"), 1),
        "jun_2026_usd_bn": v("month", "2026-06"),
        "jul_2026_usd_bn": v("month", "2026-07"),
    }
    return pd.DataFrame([{"measure": k, "value": val} for k, val in h.items()])


def main():
    readings, growth, sources = load()
    print(f"raw readings: {len(readings)} rows from {readings.source_id.nunique()} documents")
    assert readings.isna().sum()[["measure", "period", "value_usd_bn", "source_id"]].sum() == 0
    assert not readings.duplicated(["measure", "period", "source_id"]).any(), "duplicate reading"
    assert readings["value_usd_bn"].between(0.5, 60).all(), "value out of range"

    tidy = consolidate(readings, sources)
    g = check_growth(tidy, growth)
    ids = identities(tidy)
    assert (g["result"] != "FAIL").all(), g[g.result == "FAIL"]
    assert (ids["result"] == "pass").all(), ids
    fy = fiscal_series(tidy)
    d = derived(tidy)
    h = headline(tidy, fy)

    tidy.sort_values(["measure", "period_start"]).to_csv(OUT / "remittances_tidy.csv", index=False)
    fy.to_csv(OUT / "fiscal_year_series.csv", index=False)
    d.to_csv(OUT / "derived_figures.csv", index=False)
    g.to_csv(OUT / "growth_rate_checks.csv", index=False)
    ids.to_csv(OUT / "identity_checks.csv", index=False)
    h.to_csv(OUT / "headline_figures.csv", index=False)

    print(f"tidy figures: {len(tidy)}; source checks: {tidy.source_check.value_counts().to_dict()}")
    print(f"growth checks: {g.result.value_counts().to_dict()}; identities: {ids.result.value_counts().to_dict()}")
    print(fy[["period", "value_usd_bn", "change_pct", "source_check"]].to_string(index=False))
    print(h.to_string(index=False))


if __name__ == "__main__":
    main()
