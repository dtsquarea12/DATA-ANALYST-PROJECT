"""Build the analysis tables for middle-east-airport-passengers from data/raw.

Each raw row is one passenger figure as printed in one document. For every
airport, year and measure the script picks the most precise reading, checks
that every other reading agrees with it within its printed rounding, and fails
if two documents disagree.
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

# ACI World preliminary 2025 release (blog and press release): world totals
WORLD_TOTAL_CHANGE_VS_2024 = 3.6
WORLD_TOTAL_CHANGE_VS_2019 = 7.3
WORLD_INTL_CHANGE_VS_2024 = 5.9


def is_lower_bound(text: str) -> bool:
    t = str(text).lower()
    return t.startswith("more than") or t.startswith("over")


def pick_and_check(readings: pd.DataFrame) -> pd.DataFrame:
    rows, problems = [], []
    used = readings[readings["use"] == "yes"]
    for key, g in used.groupby(["airport_code", "year", "measure"], sort=False):
        exact = g[~g["printed_as"].map(is_lower_bound)]
        best = exact.sort_values("rounding_unit", kind="stable").iloc[0]
        value = int(best["passengers"])
        for _, r in g.iterrows():
            if is_lower_bound(r["printed_as"]):
                ok = value >= r["passengers"]
            else:
                ok = abs(value - r["passengers"]) <= r["rounding_unit"] / 2
            if not ok:
                problems.append(f"{key}: {r['source_id']} prints {r['printed_as']}, chosen {value:,}")
        docs = g["source_id"].nunique()
        rows.append({
            "airport_code": key[0], "year": key[1], "measure": key[2],
            "passengers": value, "chosen_source": best["source_id"],
            "documents": docs,
            "check": "two-documents" if docs >= 2 else "one-document",
        })
    if problems:
        raise SystemExit("Documents disagree:\n" + "\n".join(problems))
    return pd.DataFrame(rows)


def main() -> None:
    readings = pd.read_csv(RAW / "passenger_readings.csv")
    sources = pd.read_csv(RAW / "sources.csv")
    missing = set(readings["source_id"]) - set(sources["source_id"])
    assert not missing, f"source ids without a source row: {missing}"
    assert not readings.duplicated(["airport_code", "year", "measure", "source_id"]).any()

    figures = pick_and_check(readings)

    # Muscat: no single total printed for 2025; derive it from international + domestic
    mct = figures[figures["airport_code"] == "MCT"].pivot(index="year", columns="measure", values="passengers")
    derived = mct["international"] + mct["domestic"]
    mct_2024_printed = figures.query("airport_code=='MCT' and year==2024 and measure=='total'")["passengers"].iloc[0]
    assert abs(derived[2024] - mct_2024_printed) <= 50_000, "MCT 2024 parts do not add to the printed total"
    figures = figures[~((figures["airport_code"] == "MCT") & (figures["measure"] == "total"))]
    figures = pd.concat([figures, pd.DataFrame([
        {"airport_code": "MCT", "year": y, "measure": "total", "passengers": int(derived[y]),
         "chosen_source": "AACO_MCT25", "documents": 2, "check": "derived"} for y in (2024, 2025)
    ])], ignore_index=True)
    figures.sort_values(["airport_code", "year", "measure"]).to_csv(OUT / "figures_checked.csv", index=False)

    meta = readings.drop_duplicates("airport_code")[["airport_code", "airport", "city", "country", "subregion"]]
    tot = figures[figures["measure"] == "total"]
    tidy = tot.merge(meta, on="airport_code")[
        ["airport_code", "airport", "city", "country", "subregion", "year", "passengers", "check", "chosen_source"]
    ].sort_values(["airport_code", "year"])
    tidy.to_csv(OUT / "passengers_tidy.csv", index=False)

    wide = tot.pivot(index="airport_code", columns="year", values="passengers")
    chk = tot.pivot(index="airport_code", columns="year", values="check")
    summary = meta.set_index("airport_code").join(wide.rename(columns=lambda y: f"pax_{y}"))
    summary = summary.join(chk.rename(columns=lambda y: f"check_{y}"))
    summary = summary[summary["pax_2025"].notna()].copy()
    summary["pax_2025_m"] = (summary["pax_2025"] / 1e6).round(2)
    summary["change_vs_2024_pct"] = ((summary["pax_2025"] / summary["pax_2024"] - 1) * 100).round(1)
    summary["change_vs_2019_pct"] = ((summary["pax_2025"] / summary["pax_2019"] - 1) * 100).round(1)
    summary["added_vs_2024_m"] = ((summary["pax_2025"] - summary["pax_2024"]) / 1e6).round(2)
    summary["above_world_growth"] = summary["change_vs_2024_pct"] > WORLD_TOTAL_CHANGE_VS_2024
    summary = summary.sort_values("pax_2025", ascending=False)
    summary.insert(0, "rank_2025", range(1, len(summary) + 1))
    for c in ["pax_2019", "pax_2024", "pax_2025"]:
        summary[c] = summary[c].astype("Int64")
    summary.reset_index().to_csv(OUT / "airports_2025.csv", index=False)

    world = pd.read_csv(RAW / "world_top10_2025.csv")
    world.to_csv(OUT / "world_top10_2025.csv", index=False)

    s = summary
    gulf = s[s["subregion"] == "Gulf"]
    both = s[s["pax_2024"].notna()]
    gulf_both = both[both["subregion"] == "Gulf"]
    headline = {
        "airports_covered": len(s),
        "dxb_2025": int(s.loc["DXB", "pax_2025"]),
        "dxb_world_rank_total": 2,
        "dxb_world_rank_international": 1,
        "ist_2025": int(s.loc["IST", "pax_2025"]),
        "doh_2025": int(s.loc["DOH", "pax_2025"]),
        "jed_2025": int(s.loc["JED", "pax_2025"]),
        "doh_change_vs_2019_pct": s.loc["DOH", "change_vs_2019_pct"],
        "shj_change_vs_2019_pct": s.loc["SHJ", "change_vs_2019_pct"],
        "dxb_change_vs_2019_pct": s.loc["DXB", "change_vs_2019_pct"],
        "airports_above_world_growth": int(both["above_world_growth"].sum()),
        "airports_with_2024": len(both),
        "world_change_vs_2024_pct": WORLD_TOTAL_CHANGE_VS_2024,
        "world_change_vs_2019_pct": WORLD_TOTAL_CHANGE_VS_2019,
        "gulf_airports": len(gulf),
        "gulf_total_2025": int(gulf["pax_2025"].sum()),
        "gulf_airports_with_2024": len(gulf_both),
        "gulf_change_vs_2024_pct": round((gulf_both["pax_2025"].sum() / gulf_both["pax_2024"].sum() - 1) * 100, 1),
        "all_covered_total_2025": int(s["pax_2025"].sum()),
        "ist_change_vs_2024_pct_aci_printed": 5.5,
        "all_covered_change_vs_2024_pct": round((both["pax_2025"].sum() / both["pax_2024"].sum() - 1) * 100, 1),
    }
    pd.Series(headline, name="value").rename_axis("measure").to_csv(OUT / "headline_figures.csv")
    print(s[["airport", "pax_2025_m", "change_vs_2024_pct", "change_vs_2019_pct", "check_2025"]].to_string())
    for k, v in headline.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()
