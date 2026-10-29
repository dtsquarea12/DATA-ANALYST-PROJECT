"""Build the processed tables for the AI skills in job ads project.

Reads every printed figure in data/raw/readings.csv (one row per figure per document),
checks that documents agree within rounding, keeps the most precise reading, tests the
links between published figures, and writes data/processed/. Fails if two documents disagree.
"""
from decimal import Decimal
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)
KEY = ["dataset", "geography", "segment", "period", "measure"]

REGION = {
    "United Arab Emirates": "Middle East",
    "Singapore": "Asia", "Hong Kong": "Asia",
    "Canada": "Americas", "United States": "Americas", "Chile": "Americas", "Mexico": "Americas",
    "Australia": "Oceania", "New Zealand": "Oceania",
}
REGION_ORDER = ["Middle East", "Asia", "Europe", "Americas", "Oceania"]


def interval(printed: str):
    """A figure printed to d decimals stands for anything within half a unit of its last digit."""
    d = Decimal(printed)
    half = Decimal(5) * Decimal(10) ** (d.as_tuple().exponent - 1)
    return d - half, d + half


def ratio_value(text: str) -> float:
    """'1 in 30' -> 3.33 (percent). 'fewer than 1 in 10' and '1 in 100 or fewer' are upper bounds."""
    n = int(text.replace("fewer than", "").replace("or fewer", "").split("in")[1])
    return round(100 / n, 2)


def build():
    raw = pd.read_csv(RAW / "readings.csv", dtype=str).fillna("")
    sources = pd.read_csv(RAW / "sources.csv")
    assert set(raw.source_id) <= set(sources.source_id), "reading cites an unknown source"
    assert not raw.duplicated(KEY + ["source_id", "value_printed", "ratio_printed"]).any(), "duplicate reading"

    used = raw[~raw.note.str.startswith("set_aside")]
    rows = []
    for key, g in used.groupby(KEY, sort=False):
        if g.value_printed.iloc[0]:
            lo = max(interval(v)[0] for v in g.value_printed)
            hi = min(interval(v)[1] for v in g.value_printed)
            if lo > hi:
                raise ValueError(f"documents disagree for {key}: {list(g.value_printed)}")
            best = max(g.value_printed, key=lambda v: -Decimal(v).as_tuple().exponent)
            value, ratio = float(best), ""
        else:
            assert g.ratio_printed.nunique() == 1, f"ratio wording differs for {key}"
            ratio = g.ratio_printed.iloc[0]
            value = ratio_value(ratio)
        n = g.source_id.nunique()
        rows.append(dict(zip(KEY, key), value=value, ratio_printed=ratio, n_sources=n,
                         verification="two-or-more-documents" if n >= 2 else "one-document",
                         source_ids=";".join(sorted(set(g.source_id))),
                         note=next((x for x in g.note if x), "")))
    tidy = pd.DataFrame(rows)
    tidy.to_csv(OUT / "readings_tidy.csv", index=False)

    def v(ds, geo, seg, per, meas):
        t = tidy[(tidy.dataset == ds) & (tidy.geography == geo) & (tidy.segment == seg)
                 & (tidy.period == per) & (tidy.measure == meas)]
        assert len(t) == 1, (ds, geo, seg, per, meas)
        return t.value.iloc[0]

    GT, GEO = "gulftalent", "UAE, Saudi Arabia, Qatar"
    PW, AI = "pwc_lightcast", "ai_index_lightcast"

    # Check 1: GulfTalent's 3.4% is printed as "about 1 in 30" (3.33%).
    assert abs(v(GT, GEO, "all professional vacancies", "2026H1", "share_pct") - 100 / 30) < 0.15
    # Check 2: "nearly tripled": 3.4 / 1.2 sits between 2.5 and 3.
    growth = v(GT, GEO, "all professional vacancies", "2026H1", "share_pct") / v(GT, GEO, "all professional vacancies", "2022", "share_pct")
    assert 2.5 < growth < 3.0, growth
    # Check 3: the four role shares add to 100, and each sits close to the ratio the other articles print.
    roles = tidy[(tidy.dataset == GT) & (tidy.measure == "role_share_pct")].copy()
    assert roles.value.sum() == 100, roles.value.sum()
    for _, r in roles.iterrows():
        ratio = v(GT, GEO, r.segment, "2026H1", "role_share_ratio")
        if r.segment.endswith("models"):
            assert r.value < ratio, r.segment          # "fewer than 1 in 10"
        else:
            assert abs(r.value - ratio) <= 3, (r.segment, r.value, ratio)
    # Check 4: exact sector shares printed by one outlet sit within a quarter of the ratio printed by the others.
    for s in ["Technology", "Banking", "Audit", "Oil and gas", "Real estate"]:
        exact, ratio = v(GT, GEO, s, "2026H1", "share_pct"), v(GT, GEO, s, "2026H1", "share_ratio")
        assert abs(exact - ratio) / ratio <= 0.25, (s, exact, ratio)
    # Check 5: PwC UAE AI-skill postings rise by the printed ~2.7k from 2024 to 2025.
    d = v(PW, "United Arab Emirates", "AI-skill postings", "2025", "postings_thousand") - v(PW, "United Arab Emirates", "AI-skill postings", "2024", "postings_thousand")
    assert abs(d - v(PW, "United Arab Emirates", "AI-skill postings", "2024 to 2025", "postings_change_thousand")) < 0.05, d
    # Check 6: PwC prints +2.2 points for the UAE, 2021 to 2025.
    assert round(v(PW, "United Arab Emirates", "all postings", "2025", "share_pct") - v(PW, "United Arab Emirates", "all postings", "2021", "share_pct"), 1) == 2.2
    # Check 7: AI Index country ranking: 22 areas, values printed in descending order.
    ctry = tidy[(tidy.dataset == AI) & (tidy.segment == "all postings") & (tidy.period == "2025")].copy()
    assert len(ctry) == 22, len(ctry)
    # Check 8: US sectors, every 2025 share above 2024 (the chart shows all rising).
    us = tidy[(tidy.dataset == AI) & (tidy.geography == "United States") & (tidy.segment != "all postings")]
    us_w = us.pivot(index="segment", columns="period", values="value")
    assert len(us_w) == 15 and (us_w["2025"] > us_w["2024"]).all()

    # Processed tables
    trend = pd.DataFrame([
        dict(series="GulfTalent: professional vacancies, UAE + Saudi Arabia + Qatar", source="GulfTalent", period=p,
             share_pct=v(GT, GEO, "all professional vacancies", p, "share_pct")) for p in ["2022", "2026H1"]] + [
        dict(series=f"PwC/Lightcast: all postings, {g}", source="PwC AI Jobs Barometer 2026", period=p,
             share_pct=v(PW, g, "all postings", p, "share_pct"))
        for g in ["United Arab Emirates", "World (27-country average)", "India", "China (Mainland)"] for p in ["2021", "2025"]])
    def ver(ds, geo, seg, per):
        t = tidy[(tidy.dataset == ds) & (tidy.geography == geo) & (tidy.segment == seg) & (tidy.period == per) & (tidy.measure == "share_pct")]
        return t.verification.iloc[0]
    trend["verification"] = [ver(GT, GEO, "all professional vacancies", p) for p in ["2022", "2026H1"]] + [
        ver(PW, g, "all postings", p) for g in ["United Arab Emirates", "World (27-country average)", "India", "China (Mainland)"] for p in ["2021", "2025"]]
    trend.to_csv(OUT / "ai_share_trend.csv", index=False)

    sectors = []
    for s in ["Technology", "Banking", "Audit", "Oil and gas", "Real estate", "Construction", "Retail", "Healthcare", "Manufacturing", "Education", "Hospitality"]:
        t = tidy[(tidy.dataset == GT) & (tidy.segment == s)]
        r = t[t.measure == "share_ratio"].iloc[0]
        e = t[t.measure.isin(["share_pct", "share_pct_max"])].iloc[0]
        sectors.append(dict(sector=s, published_ratio=r.ratio_printed, ratio_pct=r.value,
                            exact_pct=e.value if e.measure == "share_pct" else None,
                            exact_is_upper_bound=e.measure == "share_pct_max",
                            ratio_sources=r.n_sources, exact_sources=e.n_sources))
    sectors = pd.DataFrame(sectors)
    sectors.to_csv(OUT / "gulf_ai_share_by_sector.csv", index=False)

    roles = roles.assign(role=roles.segment.str.replace("AI-connected vacancies: ", "", regex=False))[["role", "value", "n_sources"]]
    roles = roles.rename(columns={"value": "share_of_ai_vacancies_pct"})
    roles.to_csv(OUT / "gulf_ai_vacancies_by_role.csv", index=False)

    ctry = ctry.assign(region=ctry.geography.map(REGION).fillna("Europe"))
    ctry["rank"] = ctry.value.rank(ascending=False, method="min").astype(int)
    ctry["region_order"] = ctry.region.map(REGION_ORDER.index)
    ctry = ctry.sort_values(["region_order", "rank"])[["region", "geography", "value", "rank", "n_sources", "verification"]]
    ctry = ctry.rename(columns={"geography": "country", "value": "ai_share_pct_2025"})
    ctry.to_csv(OUT / "ai_share_by_country_2025.csv", index=False)

    us_w = us_w.rename(columns={"2024": "share_2024_pct", "2025": "share_2025_pct"}).reset_index().rename(columns={"segment": "sector"})
    us_w["change_pts"] = (us_w.share_2025_pct - us_w.share_2024_pct).round(2)
    us_w = us_w.sort_values("share_2025_pct", ascending=False)
    us_w.to_csv(OUT / "us_ai_share_by_sector.csv", index=False)

    c = ctry.set_index("country").ai_share_pct_2025
    head = pd.DataFrame([
        ("gulf_share_2022_pct", v(GT, GEO, "all professional vacancies", "2022", "share_pct")),
        ("gulf_share_2026h1_pct", v(GT, GEO, "all professional vacancies", "2026H1", "share_pct")),
        ("gulf_growth_multiple", round(growth, 2)),
        ("role_build_pct", float(roles.set_index("role").loc["Building and training AI models"].iloc[0])),
        ("role_use_or_implement_pct", float(roles.set_index("role").loc[["Implementing AI", "Using AI in the job"]].iloc[:, 0].sum())),
        ("uae_ai_index_2025_pct", c["United Arab Emirates"]),
        ("uae_ai_index_rank_of_22", int(ctry.set_index("country").loc["United Arab Emirates", "rank"])),
        ("median_22_areas_2025_pct", round(float(c.median()), 3)),
        ("uae_pwc_2021_pct", v(PW, "United Arab Emirates", "all postings", "2021", "share_pct")),
        ("uae_pwc_2025_pct", v(PW, "United Arab Emirates", "all postings", "2025", "share_pct")),
        ("uae_ai_postings_2021_thousand", v(PW, "United Arab Emirates", "AI-skill postings", "2021", "postings_thousand")),
        ("uae_ai_postings_2025_thousand", v(PW, "United Arab Emirates", "AI-skill postings", "2025", "postings_thousand")),
    ], columns=["figure", "value"])
    head.to_csv(OUT / "headline_figures.csv", index=False)
    print(head.to_string(index=False))
    print(f"\n{len(tidy)} figures, {(tidy.n_sources >= 2).sum()} in two or more documents")
    return tidy


if __name__ == "__main__":
    build()
