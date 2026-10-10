"""Build the analysis tables for the passport strength by country project.

Run from the project folder:  python scripts/build_data.py
Reads  data/raw/henley_2026_april_reading_wikipedia.csv, henley_2026_april_reading_packzup.txt,
       henley_2026_edition_readings.csv, published_figures.csv, country_reference.csv
Writes data/processed/passport_tidy.csv, data/processed/middle_east_editions.csv,
       data/processed/region_summary.csv, data/processed/source_checks.csv
"""
import os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "..", "data", "raw")
OUT = os.path.join(HERE, "..", "data", "processed")
os.makedirs(OUT, exist_ok=True)

MIDDLE_EAST = {
    "Gulf": ["BHR", "ARE", "QAT", "KWT", "OMN", "SAU"],
    "Levant and Iraq": ["PSE", "IRQ", "LBN", "JOR", "ISR", "SYR"],
    "North Africa": ["LBY", "TUN", "EGY", "DZA", "MAR"],
    "Iran, Turkey and Yemen": ["YEM", "IRN", "TUR"],
}
REGION_ORDER = ["Middle East", "Europe", "Rest of Asia", "Rest of Africa", "North America", "South America",
                "Oceania"]
SUB_ORDER = ["Gulf", "Levant and Iraq", "Iran, Turkey and Yemen", "North Africa"]
DESTINATIONS = 227
# Names that differ between the two readings of the April table.
ALIAS = {"Sao Tome and Principe": "São Tomé and Príncipe", "Cote d'Ivoire": "Ivory Coast"}
# Rows where the two publishers print different figures. The value used and the reason are written out here.
RESOLVED = {"Bangladesh": (36, "Wikipedia prints 34 at rank 97, out of order in its own table. Packzup prints 36 "
                               "at rank 95, which fills the gap between ranks 94 and 96, and What's On "
                               "(12 May 2026) prints 36.")}


def load_april():
    """The full April 2026 table as printed by two publishers. The build stops on any unexplained difference."""
    w = pd.read_csv(os.path.join(RAW, "henley_2026_april_reading_wikipedia.csv"))
    rows = []
    with open(os.path.join(RAW, "henley_2026_april_reading_packzup.txt"), encoding="utf-8") as f:
        for line in f:
            score, rank, names = line.strip().split("|")
            rows += [(ALIAS.get(n, n), int(rank), int(score)) for n in names.split(";")]
    p = pd.DataFrame(rows, columns=["country", "rank_packzup", "score_packzup"])
    assert len(w) == 199 and len(p) == 199, "expected 199 passports in each reading"
    assert not w.country.duplicated().any() and not p.country.duplicated().any(), "duplicate passport"
    m = w.rename(columns={"rank": "rank_wikipedia", "visa_free_score": "score_wikipedia"}).merge(
        p, on="country", how="outer", validate="one_to_one")
    assert len(m) == 199 and m.notna().all().all(), "the two readings list different passports"
    diff = m[(m.score_wikipedia != m.score_packzup) | (m.rank_wikipedia != m.rank_packzup)]
    assert set(diff.country) == set(RESOLVED), "unexplained difference between publishers:\n" + diff.to_string()
    m["score_apr_2026"] = [RESOLVED[c][0] if c in RESOLVED else s for c, s in zip(m.country, m.score_packzup)]
    m["apr_check"] = ["publishers-differ" if c in RESOLVED else "two-publishers" for c in m.country]
    assert m.score_apr_2026.between(0, DESTINATIONS).all(), "score outside 0 to 227"
    # The published rank is a dense rank of the score. A misread score or rank breaks this.
    m["rank_apr_2026"] = m.score_apr_2026.rank(method="dense", ascending=False).astype(int)
    assert (m.rank_apr_2026 == m.rank_packzup).all(), "printed rank is not the dense rank of the score"
    return m[["country", "score_apr_2026", "rank_apr_2026", "apr_check", "score_wikipedia", "score_packzup"]]


def load_readings():
    r = pd.read_csv(os.path.join(RAW, "henley_2026_edition_readings.csv"), dtype={"edition": str})
    r["country"] = r.country.replace(ALIAS)
    return r


def check_april_against_articles(apr, readings):
    """Every April figure printed in a news article must equal the full table."""
    a = readings[readings.edition == "2026-04"].merge(apr, on="country", how="left", validate="many_to_one")
    assert a.score_apr_2026.notna().all(), "article names a passport that is not in the table"
    bad_s = a[a.visa_free_score.notna() & (a.visa_free_score != a.score_apr_2026)]
    bad_r = a[a["rank"].notna() & (a["rank"] != a.rank_apr_2026)]
    assert bad_s.empty and bad_r.empty, "April article disagrees with the table:\n" + pd.concat([bad_s, bad_r]).to_string()
    return a.groupby("country").source_id.nunique()


def july_table(readings):
    """One July 2026 figure per passport. Scores must agree across documents. A rank is kept only if they agree."""
    j = readings[readings.edition == "2026-07"]
    rows = []
    for c, g in j.groupby("country"):
        scores = g.visa_free_score.dropna().unique()
        assert len(scores) <= 1, f"July documents print different scores for {c}: {scores}"
        ranks = g["rank"].dropna().unique()
        rows.append({"country": c,
                     "score_jul_2026": int(scores[0]) if len(scores) else pd.NA,
                     "rank_jul_2026": int(ranks[0]) if len(ranks) == 1 else pd.NA,
                     "jul_rank_note": "" if len(ranks) <= 1 else "documents print ranks " + " and ".join(
                         str(int(x)) for x in sorted(ranks)),
                     "jul_documents": int(g[g.visa_free_score.notna()].source_id.nunique()),
                     "jul_sources": ";".join(sorted(g[g.visa_free_score.notna()].source_id.unique()))})
    return pd.DataFrame(rows)


def jul_check(n):
    if pd.isna(n) or n == 0:
        return "no-july-figure"
    return "one-publisher" if n == 1 else f"{int(n)}-publishers"


def build():
    apr = load_april()
    ref = pd.read_csv(os.path.join(RAW, "country_reference.csv"))
    df = apr.merge(ref, on="country", how="left", validate="one_to_one")
    assert df.iso3.notna().all() and not df.iso3.duplicated().any(), "country code missing or repeated"
    me = {c: sub for sub, cs in MIDDLE_EAST.items() for c in cs}
    assert set(me) <= set(df.iso3), "Middle East code not in table"
    assert set(df[df.region == "Middle East"].iso3) == set(me), "reference file and Middle East list differ"
    df["sub_region"] = [me.get(c, r) for c, r in zip(df.iso3, df.region)]

    readings = load_readings()
    n_art = check_april_against_articles(apr, readings)
    df["apr_article_checks"] = df.country.map(n_art).fillna(0).astype(int)
    jul = july_table(readings)
    df = df.merge(jul, on="country", how="left")
    df["jul_documents"] = df.jul_documents.fillna(0).astype(int)
    df["jul_check"] = [jul_check(n) if pd.notna(s) else "no-july-figure"
                       for n, s in zip(df.jul_documents, df.score_jul_2026)]
    df["change_apr_to_jul"] = df.score_jul_2026 - df.score_apr_2026
    # A passport's score moves by a few destinations between editions. A large jump points to a misread figure.
    assert df.change_apr_to_jul.dropna().abs().max() <= 5, "April to July change larger than 5 destinations"

    world_mean = round(df.score_apr_2026.mean(), 2)
    df["share_of_destinations_pct"] = (df.score_apr_2026 / DESTINATIONS * 100).round(1)
    df["vs_world_mean_apr"] = (df.score_apr_2026 - world_mean).round(2)
    df["latest_score"] = df.score_jul_2026.fillna(df.score_apr_2026).astype(int)
    df["latest_edition"] = ["2026-07" if pd.notna(s) else "2026-04" for s in df.score_jul_2026]
    df["region"] = pd.Categorical(df.region, REGION_ORDER, ordered=True)
    df = df.sort_values(["region", "score_apr_2026", "country"], ascending=[True, False, True]).reset_index(drop=True)
    cols = ["iso3", "country", "region", "sub_region", "score_apr_2026", "rank_apr_2026",
            "share_of_destinations_pct", "vs_world_mean_apr", "apr_check", "apr_article_checks",
            "score_jul_2026", "rank_jul_2026", "change_apr_to_jul", "jul_check", "jul_documents", "jul_sources",
            "jul_rank_note", "latest_score", "latest_edition", "score_wikipedia", "score_packzup"]
    tidy = df[cols].copy()
    for c in ["score_jul_2026", "rank_jul_2026", "change_apr_to_jul"]:
        tidy[c] = tidy[c].astype("Int64")
    tidy.to_csv(os.path.join(OUT, "passport_tidy.csv"), index=False)

    # Long table of the Middle East by edition, for charts and BI tools.
    mid = tidy[tidy.region == "Middle East"]
    long = pd.concat([
        mid.assign(edition="2026-04", score=mid.score_apr_2026, rank=mid.rank_apr_2026, check=mid.apr_check),
        mid.assign(edition="2026-07", score=mid.score_jul_2026, rank=mid.rank_jul_2026, check=mid.jul_check),
    ])[["iso3", "country", "sub_region", "edition", "score", "rank", "check"]]
    long = long.sort_values(["sub_region", "country", "edition"]).reset_index(drop=True)
    long.to_csv(os.path.join(OUT, "middle_east_editions.csv"), index=False)

    def summary(g, level, name):
        return {"level": level, "group": name, "passports": len(g),
                "mean_score": round(g.score_apr_2026.mean(), 2), "median_score": float(g.score_apr_2026.median()),
                "min_score": int(g.score_apr_2026.min()), "max_score": int(g.score_apr_2026.max()),
                "above_world_mean": int((g.score_apr_2026 > world_mean).sum()),
                "score_150_or_more": int((g.score_apr_2026 >= 150).sum()),
                "score_below_60": int((g.score_apr_2026 < 60).sum())}
    rows = [summary(tidy[tidy.region == r], "region", r) for r in REGION_ORDER]
    rows += [summary(tidy[tidy.sub_region == s], "middle_east_sub_region", s) for s in SUB_ORDER]
    rows.append(summary(tidy, "world", "World"))
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "region_summary.csv"), index=False)

    # Published figures against the table.
    pub = pd.read_csv(os.path.join(RAW, "published_figures.csv"))
    get = lambda f, e: float(pub[(pub.figure == f) & (pub.edition == e)].value.iloc[0])
    lookup = tidy.set_index("country")
    checks = [
        ("passports_ranked", get("passports_ranked", "2026-07"), len(tidy), "exact"),
        ("gap_top_to_bottom_apr", get("gap_top_to_bottom", "2026-04"),
         int(tidy.score_apr_2026.max() - tidy.score_apr_2026.min()), "exact"),
        ("gap_top_to_bottom_jul", get("gap_top_to_bottom", "2026-07"),
         int(lookup.loc["Singapore", "score_jul_2026"] - lookup.loc["Afghanistan", "score_jul_2026"]), "exact"),
        # The published average is for July and is rounded. The April table should sit within one destination of it.
        ("world_average_score", get("world_average_score", "2026-07"), world_mean, "within 1"),
    ]
    out = []
    for name, published, computed, rule in checks:
        ok = published == computed if rule == "exact" else abs(published - computed) <= 1
        assert ok, f"published figure {name} = {published} but the table gives {computed}"
        out.append({"check": name, "published_value": published, "computed_value": computed, "rule": rule,
                    "result": "match"})
    pd.DataFrame(out).to_csv(os.path.join(OUT, "source_checks.csv"), index=False)

    m = tidy[tidy.region == "Middle East"]
    print(f"passports: {len(tidy)} | world mean (April): {world_mean} | median: {tidy.score_apr_2026.median()}")
    print(f"Middle East mean (April): {m.score_apr_2026.mean():.2f} | above world mean: "
          f"{(m.score_apr_2026 > world_mean).sum()} of {len(m)}")
    print("April check status:", tidy.apr_check.value_counts().to_dict())
    print("July figures in the Middle East:", m.jul_check.value_counts().to_dict())
    return tidy


if __name__ == "__main__":
    build()
