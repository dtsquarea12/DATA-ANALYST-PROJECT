"""Build the processed tables for the AI use by firm size project.

Reads every printed reading in data/raw/ai_use_readings.csv (one row per figure per document),
checks that documents agree within rounding, keeps the most precise reading, and writes
data/processed/. Fails if two documents disagree.
"""
from decimal import Decimal
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "ai_use_readings.csv"
OUT = ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

SIZE_ORDER = ["Small (10-49)", "Medium (50-249)", "Large (250+)", "All (10+ employees)"]


def interval(printed: str):
    """A figure printed to d decimals stands for anything within half a unit of its last digit."""
    d = Decimal(printed)
    exp = d.as_tuple().exponent
    half = Decimal(5) * Decimal(10) ** (exp - 1)
    return d - half, d + half


def build():
    raw = pd.read_csv(RAW, dtype={"value_printed": str}).fillna({"note": ""})
    assert not raw.duplicated(["economy", "year", "measure", "item", "source_id"]).any(), "duplicate reading"
    used = raw[~raw.note.str.startswith("set_aside")]
    rows = []
    for key, g in used.groupby(["economy", "year", "measure", "item"], sort=False):
        lo = max(interval(v)[0] for v in g.value_printed)
        hi = min(interval(v)[1] for v in g.value_printed)
        if lo > hi:
            raise ValueError(f"documents disagree for {key}: {list(g.value_printed)}")
        best = max(g.value_printed, key=lambda v: -Decimal(v).as_tuple().exponent)
        n = g.source_id.nunique()
        rows.append(dict(zip(["economy", "year", "measure", "item"], key),
                         value=float(best), n_sources=n,
                         verification="two-or-more-documents" if n >= 2 else "one-document",
                         source_ids=";".join(g.source_id)))
    tidy = pd.DataFrame(rows)
    tidy.to_csv(OUT / "ai_use_tidy.csv", index=False)

    use = tidy[tidy.measure == "ai_use"].pivot_table(index=["economy", "year"], columns="item", values="value")
    use = use[SIZE_ORDER].reset_index()
    use.columns.name = None
    use = use.rename(columns={"Small (10-49)": "small_pct", "Medium (50-249)": "medium_pct",
                              "Large (250+)": "large_pct", "All (10+ employees)": "all_pct"})
    use = use.dropna(subset=["small_pct"]).copy()
    use["gap_large_minus_small_pts"] = (use.large_pct - use.small_pct).round(2)
    use["ratio_large_to_small"] = (use.large_pct / use.small_pct).round(2)
    use.to_csv(OUT / "ai_use_by_size.csv", index=False)

    # Identity: Eurostat prints the 2024 to 2025 rise as 6.47 points.
    eu = tidy[(tidy.economy == "EU-27") & (tidy.measure == "ai_use") & (tidy["item"] == "All (10+ employees)")].set_index("year").value
    assert round(eu[2025] - eu[2024], 2) == 6.47, "EU change does not match the printed 6.47 points"

    def v(e, y, m, i):
        return tidy[(tidy.economy == e) & (tidy.year == y) & (tidy.measure == m) & (tidy["item"] == i)].value.iloc[0]

    t25 = use[(use.economy == "Turkey") & (use.year == 2025)].iloc[0]
    t21 = use[(use.economy == "Turkey") & (use.year == 2021)].iloc[0]
    e25 = use[(use.economy == "EU-27") & (use.year == 2025)].iloc[0]
    e24 = use[(use.economy == "EU-27") & (use.year == 2024)].iloc[0]
    head = pd.DataFrame([
        ("turkey_small_2025", t25.small_pct), ("turkey_large_2025", t25.large_pct),
        ("turkey_ratio_2025", t25.ratio_large_to_small), ("turkey_gap_2021", t21.gap_large_minus_small_pts),
        ("turkey_gap_2025", t25.gap_large_minus_small_pts),
        ("eu_small_2025", e25.small_pct), ("eu_large_2025", e25.large_pct),
        ("eu_ratio_2025", e25.ratio_large_to_small), ("eu_gap_2024", e24.gap_large_minus_small_pts),
        ("eu_gap_2025", e25.gap_large_minus_small_pts),
        ("eu_small_rise_pts", round(e25.small_pct - e24.small_pct, 2)),
        ("eu_large_rise_pts", round(e25.large_pct - e24.large_pct, 2)),
        ("turkey_expertise_reason", v("Turkey", 2025, "reason_not_used", "Lack of relevant expertise")),
        ("eu_expertise_reason", v("EU-27", 2025, "reason_not_used", "Lack of relevant expertise")),
        ("turkey_marketing_purpose", v("Turkey", 2025, "purpose", "Marketing or sales")),
        ("eu_marketing_purpose", v("EU-27", 2025, "purpose", "Marketing or sales")),
    ], columns=["figure", "value"])
    head.to_csv(OUT / "headline_figures.csv", index=False)
    return raw, tidy, use, head


if __name__ == "__main__":
    raw, tidy, use, head = build()
    print(f"{len(raw)} readings, {len(tidy)} figures, {(tidy.n_sources >= 2).sum()} in two or more documents")
    print(use.to_string(index=False))
    print(head.to_string(index=False))
