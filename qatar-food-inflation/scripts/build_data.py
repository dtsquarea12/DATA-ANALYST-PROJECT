"""Build the analysis tables for the Qatar food inflation project.

Run from the project folder:  python scripts/build_data.py
Reads  data/raw/qatar_cpi_readings_by_source.csv and data/raw/qatar_cpi_quarterly_check.csv
Writes data/processed/qatar_cpi_tidy.csv and data/processed/cumulative_change_by_group.csv
"""
import os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "..", "data", "raw")
OUT = os.path.join(HERE, "..", "data", "processed")
os.makedirs(OUT, exist_ok=True)

KEY = ["month", "cpi_group", "measure"]
LABELS = {
    "all_items": "All items",
    "all_items_ex_housing": "All items excluding housing and utilities",
    "food_beverages": "Food and beverages",
    "tobacco": "Tobacco",
    "clothing_footwear": "Clothing and footwear",
    "housing_utilities": "Housing, water, electricity and fuel",
    "furniture_household": "Furniture and household equipment",
    "health": "Health",
    "transport": "Transport",
    "communication": "Communication",
    "recreation_culture": "Recreation and culture",
    "education": "Education",
    "restaurants_hotels": "Restaurants and hotels",
    "miscellaneous": "Miscellaneous goods and services",
}
WINDOWS = {"since_feb_2026": ("2026-02", "2026-06"), "since_dec_2025": ("2025-12", "2026-06")}


def build_tidy():
    raw = pd.read_csv(os.path.join(RAW, "qatar_cpi_readings_by_source.csv"), dtype={"month": str})
    assert not raw.duplicated(KEY + ["publisher"]).any(), "duplicate reading from one publisher"
    assert set(raw.cpi_group) == set(LABELS), "unknown CPI group"

    # 1. Every publisher that reports a figure must report the same figure.
    #    Some publishers round to one decimal, so compare at the coarsest precision reported.
    def agree(g):
        dp = int(g.decimals_reported.min())
        return g.value.round(dp).nunique() == 1
    ok = raw.groupby(KEY)[["value", "decimals_reported"]].apply(agree)
    if not ok.all():
        raise SystemExit("Publishers disagree:\n" + ok[~ok].to_string())

    def best(g):
        top = g[g.decimals_reported == g.decimals_reported.max()]
        return pd.Series({"value": top.value.iloc[0],
                          "decimals_reported": int(top.decimals_reported.iloc[0]),
                          "n_publishers": g.publisher.nunique(),
                          "publishers": "; ".join(sorted(g.publisher.unique()))})
    tidy = raw.groupby(KEY)[["value", "decimals_reported", "publisher"]].apply(best).reset_index()
    tidy["verification"] = tidy.n_publishers.map(lambda n: "two-publishers" if n >= 2 else "single-publisher")
    tidy["group_label"] = tidy.cpi_group.map(LABELS)
    tidy["month_start"] = tidy.month + "-01"
    tidy["base_year"] = "2018=100"
    cols = ["month", "month_start", "cpi_group", "group_label", "measure", "value", "decimals_reported",
            "n_publishers", "publishers", "verification", "base_year"]
    return tidy[cols].sort_values(KEY).reset_index(drop=True)


def check_identities(tidy):
    """Published index levels must follow from the published monthly changes."""
    worst = 0.0
    for grp in ("all_items", "all_items_ex_housing"):
        s = tidy[tidy.cpi_group == grp].pivot(index="month", columns="measure", values="value").sort_index()
        implied = s["index"].shift(1) * (1 + s["mom_pct"] / 100)
        gap = (implied - s["index"]).abs().max()
        worst = max(worst, gap)
        if gap > 0.02:
            raise SystemExit(f"Index chain check failed for {grp}: gap {gap:.3f} points")
    q = pd.read_csv(os.path.join(RAW, "qatar_cpi_quarterly_check.csv"))
    q1_published = q[(q.period == "2026-Q1") & (q.measure == "index")].value.iloc[0]
    idx = tidy[(tidy.cpi_group == "all_items") & (tidy.measure == "index")].set_index("month").value
    q1_mean = idx.loc[["2026-01", "2026-02", "2026-03"]].mean()
    if abs(q1_mean - q1_published) > 0.01:
        raise SystemExit(f"Q1 average check failed: {q1_mean:.3f} vs {q1_published}")
    return worst, q1_mean, q1_published


def build_cumulative(tidy):
    """Chain the published monthly changes into a cumulative change per group and window."""
    mom = tidy[tidy.measure == "mom_pct"].pivot(index="month", columns="cpi_group", values="value").sort_index()
    ver = tidy[tidy.measure == "mom_pct"].pivot(index="month", columns="cpi_group", values="verification")
    idx = tidy[(tidy.cpi_group == "all_items") & (tidy.measure == "index")].set_index("month").value
    rows = []
    for window, (start, end) in WINDOWS.items():
        months = [m for m in mom.index if start < m <= end]
        for grp in mom.columns:
            factor = (1 + mom.loc[months, grp] / 100).prod()
            rows.append({"window": window, "start_month": start, "end_month": end,
                         "cpi_group": grp, "group_label": LABELS[grp],
                         "months_chained": len(months),
                         "cumulative_change_pct": round((factor - 1) * 100, 2),
                         "index_start_100": round(factor * 100, 2),
                         "single_publisher_months": int((ver.loc[months, grp] == "single-publisher").sum()),
                         "method": "chained monthly changes"})
        # Alternative for all items: ratio of the published index levels.
        ratio = idx[end] / idx[start]
        rows.append({"window": window, "start_month": start, "end_month": end,
                     "cpi_group": "all_items", "group_label": LABELS["all_items"],
                     "months_chained": len(months),
                     "cumulative_change_pct": round((ratio - 1) * 100, 2),
                     "index_start_100": round(ratio * 100, 2),
                     "single_publisher_months": 0,
                     "method": "ratio of published index levels"})
    return pd.DataFrame(rows)


def main():
    tidy = build_tidy()
    worst, q1_mean, q1_pub = check_identities(tidy)
    cum = build_cumulative(tidy)
    # The two methods for all items must agree within rounding.
    a = cum[cum.cpi_group == "all_items"].pivot(index="window", columns="method", values="cumulative_change_pct")
    assert (a.iloc[:, 0] - a.iloc[:, 1]).abs().max() < 0.05, "chained and index-ratio results differ"
    tidy.to_csv(os.path.join(OUT, "qatar_cpi_tidy.csv"), index=False)
    cum.to_csv(os.path.join(OUT, "cumulative_change_by_group.csv"), index=False)
    print(f"qatar_cpi_tidy.csv: {len(tidy)} rows, {tidy.month.nunique()} months, {tidy.cpi_group.nunique()} groups")
    print(tidy.verification.value_counts().to_string())
    print(f"cumulative_change_by_group.csv: {len(cum)} rows")
    print(f"Index chain check: largest gap {worst:.3f} index points")
    print(f"Q1 2026 average of monthly index {q1_mean:.2f} vs published {q1_pub}")


if __name__ == "__main__":
    main()
