"""Build the processed tables for the Saudi business AI adoption project.

Every figure is read from one or more documents (data/raw/ai_use_readings.csv),
one row per figure per document per reading. The script stops if two readings
disagree on the same figure, except readings set aside with a reason in the
`note` column. It then checks the published growth rate against the two
national rates, using rounding intervals: a value printed to one decimal
stands for anything within 0.05 of it.
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)



def consolidate(readings, sources):
    publisher = sources.set_index("source_id")["publisher"].to_dict()
    kind = sources.set_index("source_id")["kind"].to_dict()
    used = readings[~readings["note"].fillna("").str.startswith("set aside")].copy()
    rows = []
    for (year, code), g in used.groupby(["year", "isic_section"]):
        vals = g["value"].round(2).unique()
        assert len(vals) == 1, f"documents disagree on {year} {code}: {g.raw.tolist()}"
        docs = sorted(g["source_id"].unique())
        pubs = sorted({publisher[s] for s in docs})
        official = [s for s in docs if kind[s] == "official"]
        if len(pubs) >= 2:
            status = "official-and-press" if official else "two-publishers"
        else:
            status = "one-document"
        rows.append(dict(year=int(year), isic_section=code, sector=g["sector"].iloc[0],
                         pct_using_ai=float(vals[0]), n_documents=len(docs),
                         n_publishers=len(pubs), verification=status,
                         sources=";".join(docs)))
    return pd.DataFrame(rows)


def main():
    readings = pd.read_csv(RAW / "ai_use_readings.csv")
    sources = pd.read_csv(RAW / "sources.csv")
    assert set(readings.source_id) <= set(sources.source_id)

    tidy = consolidate(readings, sources).sort_values(["year", "isic_section"])
    # coverage checks
    sectors = tidy[tidy.isic_section != "ALL"]
    assert sectors.groupby("year").size().to_dict() == {2024: 18, 2025: 18}
    assert tidy.pct_using_ai.between(0, 100).all()
    assert not tidy.duplicated(["year", "isic_section"]).any()
    tidy.to_csv(OUT / "ai_use_tidy.csv", index=False)

    wide = tidy.pivot(index=["isic_section", "sector"], columns="year", values="pct_using_ai").reset_index()
    wide.columns = ["isic_section", "sector", "pct_2024", "pct_2025"]
    ver = tidy.pivot(index="isic_section", columns="year", values="verification")
    wide["verification_2024"] = wide.isic_section.map(ver[2024])
    wide["verification_2025"] = wide.isic_section.map(ver[2025])
    wide["change_pts"] = (wide.pct_2025 - wide.pct_2024).round(1)
    wide["change_rel_pct"] = ((wide.pct_2025 / wide.pct_2024 - 1) * 100).round(1)
    nat = wide[wide.isic_section == "ALL"].iloc[0]
    sec = wide[wide.isic_section != "ALL"].copy()
    sec["rank_2025"] = sec.pct_2025.rank(ascending=False, method="min").astype(int)
    sec["rank_2024"] = sec.pct_2024.rank(ascending=False, method="min").astype(int)
    sec["gap_to_national_2025_pts"] = (sec.pct_2025 - nat.pct_2025).round(1)
    sec = sec.sort_values("pct_2025", ascending=False)
    out = pd.concat([wide[wide.isic_section == "ALL"], sec], ignore_index=True)
    out.to_csv(OUT / "ai_use_by_sector.csv", index=False)

    # published growth check: GASTAT prints growth of 20.0% from 2024 to 2025
    lo = (nat.pct_2025 - 0.05) / (nat.pct_2024 + 0.05) - 1
    hi = (nat.pct_2025 + 0.05) / (nat.pct_2024 - 0.05) - 1
    assert lo <= 0.2005 and 0.1995 <= hi, "national rates do not give the published 20.0% growth"

    top, bottom = sec.iloc[0], sec.iloc[-1]
    rise = sec.sort_values("change_pts", ascending=False)
    head = [
        ("national_2025_pct", nat.pct_2025),
        ("national_2024_pct", nat.pct_2024),
        ("national_change_pts", round(nat.pct_2025 - nat.pct_2024, 1)),
        ("national_change_rel_pct", round((nat.pct_2025 / nat.pct_2024 - 1) * 100, 1)),
        ("sectors_rising", int((sec.change_pts > 0).sum())),
        ("sectors_above_national_2025", int((sec.pct_2025 > nat.pct_2025).sum())),
        ("highest_sector_2025", f"{top.sector} {top.pct_2025}"),
        ("lowest_sector_2025", f"{bottom.sector} {bottom.pct_2025}"),
        ("gap_high_low_2025_pts", round(top.pct_2025 - bottom.pct_2025, 1)),
        ("gap_high_low_2024_pts", round(sec.pct_2024.max() - sec.pct_2024.min(), 1)),
        ("largest_rise", f"{rise.iloc[0].sector} {rise.iloc[0].change_pts}"),
        ("smallest_rise", f"{rise.iloc[-1].sector} {rise.iloc[-1].change_pts}"),
        ("median_sector_change_pts", round(sec.change_pts.median(), 2)),
    ]
    pd.DataFrame(head, columns=["measure", "value"]).to_csv(OUT / "headline_figures.csv", index=False)
    print(out[["sector", "pct_2024", "pct_2025", "change_pts", "verification_2024", "verification_2025"]].to_string(index=False))
    for k, v in head:
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()
