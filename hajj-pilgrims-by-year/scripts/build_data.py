"""Build the processed tables for the Hajj pilgrims project from the raw readings.

Every figure is read from one or more documents (data/raw/pilgrim_readings.csv).
The script stops if two documents print different values for the same figure,
except for readings set aside with a reason in the `note` column, and it checks
the identities that link the published figures.
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

BASE_YEAR = 2019      # last season before COVID-19 limits
PEAK_YEAR = 2012      # highest season on record
LATEST = 2026


def rounding_step(note):
    if "0.01 million" in note:
        return 10_000
    if "nearest hundred" in note:
        return 100
    return None


def consolidate(readings, sources):
    pub = sources.set_index("source_id")["publisher"].to_dict()
    used = readings[~readings["note"].fillna("").str.startswith("set aside")]
    exact = used[used["note"].fillna("").str.contains("rounding check") == False]
    rounded = used[used["note"].fillna("").str.contains("rounding check")]
    rows = []
    for (measure, year), grp in exact.groupby(["measure", "year"]):
        vals = grp["value"].unique()
        assert len(vals) == 1, f"documents disagree on {measure} {year}: {vals}"
        pubs = {pub[s] for s in grp["source_id"]}
        family = {p.split(" (")[0] for p in pubs}
        if len(grp) == 1:
            check = "one-document"
        elif len(family) == 1 and len(pubs) == 1:
            check = "same-publisher"
        else:
            check = "two-publishers"
        rows.append({"measure": measure, "year": int(year), "value": int(vals[0]),
                     "n_documents": len(grp), "n_publishers": len(pubs),
                     "source_check": check, "source_ids": ";".join(grp["source_id"])})
    tidy = pd.DataFrame(rows)
    for _, r in rounded.iterrows():
        step = rounding_step(r["note"])
        idx = tidy.index[(tidy.measure == r.measure) & (tidy.year == r.year)]
        assert len(idx) == 1, f"no exact figure for rounded reading {r.measure} {r.year}"
        v = tidy.loc[idx[0], "value"]
        assert abs(v - r.value) <= step / 2, f"rounded reading disagrees: {r.measure} {r.year}"
        if tidy.loc[idx[0], "source_check"] == "one-document":
            tidy.loc[idx[0], "source_check"] = "one-document-plus-rounded-second"
        tidy.loc[idx[0], "source_ids"] += ";" + r.source_id + "(rounded)"
    return tidy.sort_values(["measure", "year"]).reset_index(drop=True)


def get(tidy, measure, year):
    hit = tidy[(tidy.measure == measure) & (tidy.year == year)]
    return int(hit["value"].iloc[0]) if len(hit) else None


def identities(tidy):
    rows = []
    for year in sorted(tidy.year.unique()):
        t, e, i = (get(tidy, m, year) for m in ("total", "external", "internal"))
        if None not in (t, e, i):
            rows.append({"year": year, "identity": "internal + external = total", "left": e + i, "right": t})
        m, f = get(tidy, "male", year), get(tidy, "female", year)
        if m and f and t:
            rows.append({"year": year, "identity": "male + female = total", "left": m + f, "right": t})
        a, l, s = (get(tidy, k, year) for k in ("arrival_air", "arrival_land", "arrival_sea"))
        if None not in (a, l, s) and e:
            rows.append({"year": year, "identity": "air + land + sea = external", "left": a + l + s, "right": e})
    out = pd.DataFrame(rows)
    out["difference"] = out["left"] - out["right"]
    out["result"] = (out["difference"] == 0).map({True: "pass", False: "FAIL"})
    assert (out["result"] == "pass").all(), out[out.result != "pass"]
    return out


def series(tidy):
    years = sorted(set(tidy[tidy.measure == "internal"].year) & set(tidy[tidy.measure == "external"].year))
    s = pd.DataFrame({"year": years})
    for m in ("total", "external", "internal"):
        s[m] = [get(tidy, m, y) for y in years]
    s["internal_share_pct"] = (s.internal / s.total * 100).round(1)
    for m in ("total", "external", "internal"):
        base = s.loc[s.year == BASE_YEAR, m].iloc[0]
        s[f"{m}_pct_of_{BASE_YEAR}"] = (s[m] / base * 100).round(1)
    s["total_change_pct"] = (s.total.pct_change() * 100).round(1)
    # a gap year (2020, 2021) is not a previous season for the change column
    gap = s.year.diff() != 1
    s.loc[gap, "total_change_pct"] = None
    check = tidy.set_index(["measure", "year"])["source_check"]
    s["split_source_check"] = [check.get(("internal", y)) for y in years]
    return s


def origin(raw_origin):
    o = raw_origin.copy()
    counts = o.dropna(subset=["external_pilgrims"])
    for (year, group), grp in counts.groupby(["year", "origin_group"]):
        assert grp["external_pilgrims"].nunique() == 1, f"origin disagree {year} {group}"
    counts = counts.drop_duplicates(["year", "origin_group"]).copy()
    counts["share_pct"] = counts.groupby("year")["external_pilgrims"].transform(lambda x: x / x.sum() * 100).round(1)
    n_docs = o.groupby(["year", "origin_group"]).size().rename("n_documents").reset_index()
    shares = o[o["external_pilgrims"].isna()].copy()
    shares["share_pct"] = shares["share_pct_printed"]
    out = pd.concat([counts, shares])[["year", "origin_group", "external_pilgrims", "share_pct", "source_id"]]
    out = out.merge(n_docs, on=["year", "origin_group"])
    # combined Arab group (GCC plus other Arab countries) for comparison with the 2024 release
    arab = (counts[counts.origin_group.isin(["GCC countries", "Other Arab countries"])]
            .groupby("year")["share_pct"].sum().round(1).rename("arab_incl_gcc_share_pct"))
    return out.sort_values(["year", "origin_group"]).reset_index(drop=True), arab


def headline(s, tidy):
    r = s.set_index("year")
    L, B, P = r.loc[LATEST], r.loc[BASE_YEAR], r.loc[PEAK_YEAR]
    female_share = get(tidy, "female", LATEST) / get(tidy, "total", LATEST) * 100
    female_share_base = get(tidy, "female", BASE_YEAR) / get(tidy, "total", BASE_YEAR) * 100
    air_share = get(tidy, "arrival_air", LATEST) / L.external * 100
    low_internal = r.drop([y for y in r.index if y in (2020, 2021)]).internal.idxmin()
    items = [
        ("total_pilgrims_2026", L.total, "pilgrims"),
        ("external_pilgrims_2026", L.external, "pilgrims"),
        ("internal_pilgrims_2026", L.internal, "pilgrims"),
        ("total_change_2025_to_2026_pct", round((L.total / r.loc[2025].total - 1) * 100, 1), "percent"),
        ("external_change_2025_to_2026_pct", round((L.external / r.loc[2025].external - 1) * 100, 1), "percent"),
        ("internal_change_2025_to_2026_pct", round((L.internal / r.loc[2025].internal - 1) * 100, 1), "percent"),
        ("total_2026_pct_of_2019", L.total_pct_of_2019, "percent"),
        ("external_2026_pct_of_2019", L.external_pct_of_2019, "percent"),
        ("internal_2026_pct_of_2019", L.internal_pct_of_2019, "percent"),
        ("total_2026_pct_of_2012_peak", round(L.total / P.total * 100, 1), "percent"),
        ("external_2026_pct_of_2012", round(L.external / P.external * 100, 1), "percent"),
        ("internal_share_2026_pct", L.internal_share_pct, "percent"),
        ("internal_share_2019_pct", B.internal_share_pct, "percent"),
        ("internal_share_2012_pct", P.internal_share_pct, "percent"),
        ("lowest_internal_year_excl_2020_2021", low_internal, "year"),
        ("female_share_2026_pct", round(female_share, 1), "percent"),
        ("female_share_2019_pct", round(female_share_base, 1), "percent"),
        ("air_share_of_external_2026_pct", round(air_share, 1), "percent"),
        ("total_gap_2026_vs_2019", L.total - B.total, "pilgrims"),
        ("external_gap_2026_vs_2019", L.external - B.external, "pilgrims"),
        ("internal_gap_2026_vs_2019", L.internal - B.internal, "pilgrims"),
        ("internal_share_of_gap_pct", round((L.internal - B.internal) / (L.total - B.total) * 100, 1), "percent"),
    ]
    return pd.DataFrame(items, columns=["figure", "value", "unit"])


def main():
    readings = pd.read_csv(RAW / "pilgrim_readings.csv")
    sources = pd.read_csv(RAW / "sources.csv")
    raw_origin = pd.read_csv(RAW / "origin_readings.csv")
    assert set(readings.source_id) <= set(sources.source_id), "unknown source id"
    assert not readings.duplicated(["measure", "year", "source_id", "value"]).any(), "duplicate reading"
    assert (readings.value > 0).all()

    tidy = consolidate(readings, sources)
    ids = identities(tidy)
    s = series(tidy)
    org, arab = origin(raw_origin)
    head = headline(s, tidy)

    # tidy long table for Power BI or Tableau: one row per year and pilgrim group
    long = s.melt(id_vars="year", value_vars=["external", "internal"], var_name="pilgrim_group", value_name="pilgrims")
    long["pilgrim_group"] = long["pilgrim_group"].map({"external": "From abroad", "internal": "From inside Saudi Arabia"})
    long = long.sort_values(["year", "pilgrim_group"]).reset_index(drop=True)

    tidy.to_csv(OUT / "figures_checked.csv", index=False)
    s.to_csv(OUT / "pilgrims_by_year.csv", index=False)
    long.to_csv(OUT / "pilgrims_tidy.csv", index=False)
    ids.to_csv(OUT / "identity_checks.csv", index=False)
    org.to_csv(OUT / "external_by_origin.csv", index=False)
    head.to_csv(OUT / "headline_figures.csv", index=False)

    print(f"raw readings: {len(readings)} rows from {readings.source_id.nunique()} documents; "
          f"set aside: {readings.note.fillna('').str.startswith('set aside').sum()}")
    print(f"checked figures: {len(tidy)}; source checks: {tidy.source_check.value_counts().to_dict()}")
    print(f"identities: {ids.result.value_counts().to_dict()}; series years: {s.year.min()}-{s.year.max()} ({len(s)} seasons)")
    print("Arab share incl. GCC:", arab.to_dict())
    print(head.to_string(index=False))


if __name__ == "__main__":
    main()
