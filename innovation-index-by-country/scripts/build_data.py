"""Build the analysis tables for the innovation index by country project.

Run from the project folder:  python scripts/build_data.py
Reads  data/raw/gii_2026_reading_a.csv, gii_2026_reading_b.csv, gii_2026_web_page_ranks.csv,
       gii_2025_wipo.csv, gii_2025_wikipedia.csv, published_figures.csv, country_reference.csv
Writes data/processed/gii_tidy.csv, data/processed/middle_east.csv,
       data/processed/region_summary.csv, data/processed/source_checks.csv
"""
import os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "..", "data", "raw")
OUT = os.path.join(HERE, "..", "data", "processed")
os.makedirs(OUT, exist_ok=True)

N_ECONOMIES = 139
MIDDLE_EAST = {
    "Gulf": ["BHR", "ARE", "QAT", "KWT", "OMN", "SAU"],
    "Levant and Iraq": ["PSE", "IRQ", "LBN", "JOR", "ISR", "SYR"],
    "North Africa": ["LBY", "TUN", "EGY", "DZA", "MAR"],
    "Iran, Turkey and Yemen": ["YEM", "IRN", "TUR"],
}
SUB_ORDER = ["Gulf", "Levant and Iraq", "Iran, Turkey and Yemen", "North Africa"]
REGION_ORDER = ["Middle East", "Europe", "Rest of Asia", "Rest of Africa", "North America", "South America",
                "Oceania"]
# WIPO's own region "Northern Africa and Western Asia" (18 economies in 2026), used as the alternative grouping.
WIPO_NAWA = ["ISR", "ARE", "CYP", "SAU", "TUR", "QAT", "MAR", "GEO", "ARM", "JOR", "KWT", "BHR", "OMN", "TUN",
             "EGY", "AZE", "LBN", "DZA"]

# WIPO and Wikipedia names -> names in country_reference.csv
ALIAS = {
    "Republic of Korea": "South Korea", "Netherlands (Kingdom of the)": "Netherlands",
    "Kingdom of the Netherlands": "Netherlands", "Hong Kong, China": "Hong Kong", "Hong Kong China": "Hong Kong",
    "Viet Nam": "Vietnam", "Türkiye": "Turkey", "Russian Federation": "Russia", "Republic of Moldova": "Moldova",
    "Iran (Islamic Republic of)": "Iran", "Islamic Republic of Iran": "Iran", "Brunei Darussalam": "Brunei",
    "Cabo Verde": "Cape Verde", "Lao People's Democratic Republic": "Laos", "Côte d'Ivoire": "Ivory Coast",
    "Bolivia (Plurinational State of)": "Bolivia", "United Republic of Tanzania": "Tanzania",
    "Venezuela (Bolivarian Republic of)": "Venezuela", "Democratic Republic of the Congo": "DR Congo",
    "Republic of the Congo": "Congo",
}
# 2025 rows where the WIPO report and Wikipedia print different figures. WIPO, the publisher, is used.
RESOLVED_2025 = {
    "Cyprus": "WIPO prints rank 25, Wikipedia 26; both print 45.5, a tie at one decimal with New Zealand.",
    "New Zealand": "WIPO prints rank 26, Wikipedia 25; both print 45.5, a tie at one decimal with Cyprus.",
    "Kenya": "WIPO prints rank 102, Wikipedia 103; both print 21.4, a tie at one decimal with Paraguay.",
    "Paraguay": "WIPO prints rank 103, Wikipedia 102; both print 21.4, a tie at one decimal with Kenya.",
    "Cambodia": "WIPO prints 22.0, Wikipedia 21.9; rank 100 in both.",
}


def name(s):
    return ALIAS.get(s, s)


def check_order(df, label):
    """Published ranks must follow the scores: a higher rank never has a higher score."""
    d = df.sort_values("gii_rank")
    assert (d.gii_rank.values == range(1, N_ECONOMIES + 1)).all(), f"{label}: ranks are not 1 to {N_ECONOMIES}"
    assert (d.score.diff().dropna() <= 0).all(), f"{label}: a score rises down the ranking (misread digit?)"
    assert d.score.between(0, 100).all() and not d.economy.duplicated().any(), f"{label}: bad score or duplicate"


def load_2026():
    a = pd.read_csv(os.path.join(RAW, "gii_2026_reading_a.csv"))
    b = pd.read_csv(os.path.join(RAW, "gii_2026_reading_b.csv"))
    for df, label in ((a, "2026 reading A"), (b, "2026 reading B")):
        assert len(df) == N_ECONOMIES, f"{label}: expected {N_ECONOMIES} rows"
        check_order(df, label)
    m = a.merge(b, on="economy", suffixes=("_a", "_b"), validate="one_to_one")
    assert len(m) == N_ECONOMIES, "the two 2026 readings list different economies"
    for col in ("score", "gii_rank", "region_rank"):
        bad = m[m[f"{col}_a"] != m[f"{col}_b"]]
        assert bad.empty, f"2026 readings disagree on {col}:\n{bad}"
    web = pd.read_csv(os.path.join(RAW, "gii_2026_web_page_ranks.csv"))
    web["country"] = web.economy.map(name)
    a["country"] = a.economy.map(name)
    w = web.merge(a[["country", "gii_rank"]], on="country", how="left", suffixes=("_web", "_table"))
    assert w.gii_rank_table.notna().all(), "web page names an economy missing from the table"
    assert (w.gii_rank_web == w.gii_rank_table).all(), "web page rank differs from the table:\n" + str(w)
    a["rank_check_2026"] = a.country.isin(web.country).map({True: "two-documents", False: "one-document-read-twice"})
    return a.rename(columns={"score": "score_2026", "gii_rank": "rank_2026", "region_rank": "wipo_region_rank_2026",
                             "income_group_rank": "income_group_rank_2026"})


def load_2025():
    w = pd.read_csv(os.path.join(RAW, "gii_2025_wipo.csv"))
    k = pd.read_csv(os.path.join(RAW, "gii_2025_wikipedia.csv"))
    w = w.assign(country=w.economy.map(name))
    k = k.assign(country=k.economy.map(name))
    assert len(w) == len(k) == N_ECONOMIES, "expected 139 rows in each 2025 reading"
    check_order(w, "2025 WIPO")
    m = w.merge(k[["country", "rank_2025", "score_2025"]], on="country", how="outer", validate="one_to_one")
    assert len(m) == N_ECONOMIES and m.notna()[["gii_rank", "rank_2025"]].all().all(), "2025 country lists differ"
    diff = m[(m.gii_rank != m.rank_2025) | (m.score != m.score_2025)]
    assert set(diff.country) == set(RESOLVED_2025), "unexplained 2025 difference:\n" + diff.to_string()
    m["check_2025"] = ["sources-differ" if c in RESOLVED_2025 else "two-documents" for c in m.country]
    return m[["country", "score", "gii_rank", "check_2025"]].rename(
        columns={"score": "score_2025", "gii_rank": "rank_2025"})


def build():
    ref = pd.read_csv(os.path.join(RAW, "country_reference.csv"))
    me = {iso: sub for sub, codes in MIDDLE_EAST.items() for iso in codes}
    assert set(ref[ref.region == "Middle East"].iso3) == set(me), "reference file and Middle East list differ"
    g26, g25 = load_2026(), load_2025()
    df = g26.merge(g25, on="country", how="left", validate="one_to_one")
    df = df.merge(ref, on="country", how="left", validate="one_to_one")
    assert df.iso3.notna().all(), "economy without a region: " + str(df[df.iso3.isna()].country.tolist())
    df["sub_region"] = [me.get(c, r) for c, r in zip(df.iso3, df.region)]
    df["wipo_nawa"] = df.iso3.isin(WIPO_NAWA)
    assert df.wipo_nawa.sum() == 18, "WIPO region should have 18 economies"
    # WIPO's region rank must match the order of 2026 ranks inside its own region.
    nawa = df[df.wipo_nawa].sort_values("rank_2026")
    assert list(nawa.wipo_region_rank_2026) == list(range(1, 19)), "WIPO region rank does not match"
    df["rank_change"] = df.rank_2025 - df.rank_2026          # positive = moved up
    df["score_change"] = (df.score_2026 - df.score_2025).round(1)
    # Ranks among the 2026 economies of each grouping.
    df["region"] = pd.Categorical(df.region, REGION_ORDER, ordered=True)
    df = df.sort_values(["region", "rank_2026"]).reset_index(drop=True)
    pub = pd.read_csv(os.path.join(RAW, "published_figures.csv"))
    pub["country"] = pub.economy.map(name)
    checks = []
    for r in pub.itertuples():
        row = df[df.country == r.country].iloc[0]
        col = {("2026", "gii_rank"): "rank_2026", ("2025", "gii_rank"): "rank_2025",
               ("2026", "region_rank"): "wipo_region_rank_2026"}[(str(r.edition), r.metric)]
        ok = row[col] == r.value
        assert ok, f"published figure disagrees: {r}"
        checks.append({"source_id": r.source_id, "country": r.country, "edition": r.edition, "metric": r.metric,
                       "published": r.value, "table": row[col], "agrees": ok})
    pd.DataFrame(checks).to_csv(os.path.join(OUT, "source_checks.csv"), index=False)
    gulf_news = set(pub[(pub.source_id == "muscat_daily_2026")].country)
    df.loc[df.country.isin(gulf_news), "rank_check_2026"] = "two-documents"
    cols = ["iso3", "country", "region", "sub_region", "wipo_nawa", "score_2026", "rank_2026",
            "income_group_rank_2026", "wipo_region_rank_2026", "score_2025", "rank_2025", "rank_change",
            "score_change", "rank_check_2026", "check_2025"]
    df[cols].to_csv(os.path.join(OUT, "gii_tidy.csv"), index=False)

    mid = df[df.region == "Middle East"].copy()
    mid["sub_order"] = mid.sub_region.map({s: i for i, s in enumerate(SUB_ORDER)})
    mid = mid.sort_values(["sub_order", "rank_2026"])
    mid["rank_in_middle_east"] = mid.rank_2026.rank(method="min").astype(int)
    mid[["iso3", "country", "sub_region", "score_2026", "rank_2026", "rank_in_middle_east", "rank_2025",
         "rank_change", "score_2025", "score_change"]].to_csv(os.path.join(OUT, "middle_east.csv"), index=False)

    def summary(g, level, label):
        return {"level": level, "group": label, "economies": len(g), "mean_score_2026": round(g.score_2026.mean(), 2),
                "median_rank_2026": g.rank_2026.median(), "best": g.sort_values("rank_2026").country.iloc[0],
                "best_rank": int(g.rank_2026.min()), "moved_up": int((g.rank_change > 0).sum()),
                "moved_down": int((g.rank_change < 0).sum()), "unchanged": int((g.rank_change == 0).sum()),
                "new_in_2026": int(g.rank_change.isna().sum()),
                "in_top_50": int((g.rank_2026 <= 50).sum())}
    rows = [summary(df, "world", "World")]
    rows += [summary(df[df.region == r], "region", r) for r in REGION_ORDER]
    rows += [summary(df[df.sub_region == s], "middle_east_sub_region", s) for s in SUB_ORDER
             if (df.sub_region == s).any()]
    rows.append(summary(df[df.wipo_nawa], "wipo_region", "Northern Africa and Western Asia (WIPO)"))
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "region_summary.csv"), index=False)
    return df


if __name__ == "__main__":
    d = build()
    print(f"{len(d)} economies, {int((d.region == 'Middle East').sum())} in the Middle East")
    print(pd.read_csv(os.path.join(OUT, "middle_east.csv")).to_string(index=False))
    print(pd.read_csv(os.path.join(OUT, "region_summary.csv")).to_string(index=False))
    print(d.rank_check_2026.value_counts().to_string(), d.check_2025.value_counts(dropna=False).to_string())
