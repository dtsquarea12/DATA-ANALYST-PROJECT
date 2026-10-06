"""Build the analysis tables for the Saudi women in work project.

Run from the project folder:  python scripts/build_data.py
Reads  data/raw/saudi_labour_readings_by_source.csv
Writes data/processed/saudi_labour_tidy.csv and data/processed/window_comparisons.csv
"""
import os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "..", "data", "raw", "saudi_labour_readings_by_source.csv")
OUT = os.path.join(HERE, "..", "data", "processed")
os.makedirs(OUT, exist_ok=True)

KEY = ["quarter", "nationality", "sex", "indicator"]
REDESIGN = "2025-Q1"  # first quarter of the redesigned questionnaire and new sample


def publisher(source):
    for name in ("GASTAT", "GLMM", "Argaam", "Saudi Press Agency", "vision2030.ai", "Jadwa"):
        if name in source:
            return name
    raise ValueError("Unknown publisher: " + source)


def build_tidy():
    raw = pd.read_csv(RAW)
    raw["publisher"] = raw.source.map(publisher)

    # 1. Every source that reports a figure must report the same figure.
    spread = raw.groupby(KEY).value_pct.agg(["min", "max"])
    conflicts = spread[spread["min"] != spread["max"]]
    if len(conflicts):
        raise SystemExit("Sources disagree:\n" + conflicts.to_string())

    tidy = (raw.groupby(KEY)
               .agg(value_pct=("value_pct", "first"),
                    n_documents=("source", "nunique"),
                    n_publishers=("publisher", "nunique"))
               .reset_index())
    tidy["verification"] = "single-document"
    tidy.loc[tidy.n_documents >= 2, "verification"] = "two-gastat-releases"
    tidy.loc[tidy.n_publishers >= 2, "verification"] = "two-publishers"

    tidy["year"] = tidy.quarter.str[:4].astype(int)
    tidy["quarter_number"] = tidy.quarter.str[-1].astype(int)
    tidy["quarter_start"] = pd.PeriodIndex(tidy.quarter.str.replace("-", ""), freq="Q").start_time.strftime("%Y-%m-%d")
    tidy["survey_design"] = tidy.quarter.map(lambda q: "2025 questionnaire" if q >= REDESIGN else "earlier questionnaire")

    cols = ["quarter", "quarter_start", "year", "quarter_number", "nationality", "sex", "indicator",
            "value_pct", "n_documents", "n_publishers", "verification", "survey_design"]
    tidy = tidy[cols].sort_values(KEY).reset_index(drop=True)

    # 2. Identity check: employment ratio = participation x (1 - unemployment rate), within rounding.
    wide = tidy[tidy.nationality == "Saudi"].pivot_table(index=["quarter", "sex"], columns="indicator", values="value_pct").dropna()
    implied = wide.participation_rate * (1 - wide.unemployment_rate / 100)
    worst = (implied - wide.employment_to_population).abs().max()
    if worst > 0.15:
        raise SystemExit(f"Identity check failed, largest gap {worst:.2f} points")
    return tidy, worst


def window(tidy, sex, start, end):
    """Compare two quarters for Saudi nationals of one sex."""
    s = tidy[(tidy.nationality == "Saudi") & (tidy.sex == sex)].pivot(index="quarter", columns="indicator", values="value_pct")
    a, b = s.loc[start], s.loc[end]
    return {
        "sex": sex, "start_quarter": start, "end_quarter": end,
        "participation_start": a.participation_rate, "participation_end": b.participation_rate,
        "participation_change_pts": round(b.participation_rate - a.participation_rate, 1),
        "employment_ratio_start": a.employment_to_population, "employment_ratio_end": b.employment_to_population,
        "employment_ratio_change_pts": round(b.employment_to_population - a.employment_to_population, 1),
        "unemployment_rate_start": a.unemployment_rate, "unemployment_rate_end": b.unemployment_rate,
        "unemployment_rate_change_pts": round(b.unemployment_rate - a.unemployment_rate, 1),
        # share of the whole group that is unemployed = participation - employment ratio
        "unemployed_share_start": round(a.participation_rate - a.employment_to_population, 1),
        "unemployed_share_end": round(b.participation_rate - b.employment_to_population, 1),
        # unemployment rate at the end if participation had stayed at its starting level
        "unemployment_rate_end_if_participation_unchanged":
            round(100 * (1 - b.employment_to_population / a.participation_rate), 1),
    }


WINDOWS = [
    ("two years", "2024-Q2", "2026-Q2"),            # headline: same quarter, two years apart
    ("one year", "2025-Q2", "2026-Q2"),             # same quarter, both on the 2025 questionnaire
    ("since 2025 redesign", "2025-Q1", "2026-Q2"),  # from the first redesigned quarter
]


def main():
    tidy, worst = build_tidy()
    tidy.to_csv(os.path.join(OUT, "saudi_labour_tidy.csv"), index=False)
    rows = []
    for label, start, end in WINDOWS:
        for sex in ("Female", "Male"):
            rows.append({"window": label, **window(tidy, sex, start, end)})
    comp = pd.DataFrame(rows)
    comp.to_csv(os.path.join(OUT, "window_comparisons.csv"), index=False)
    print(f"saudi_labour_tidy.csv: {len(tidy)} rows")
    print(tidy.verification.value_counts().to_string())
    print(f"Identity check passed, largest gap {worst:.2f} points")
    print(f"window_comparisons.csv: {len(comp)} rows")
    print(comp.T.to_string())


if __name__ == "__main__":
    main()
