"""Build the analysis tables for the mobile internet speed project.

Run from the project folder:  python scripts/build_data.py
Reads  data/raw/speedtest_readings_march_2026.csv
Writes data/processed/speed_tidy.csv, data/processed/speed_by_country.csv
       and data/processed/group_summary.csv
"""
import os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "..", "data", "raw", "speedtest_readings_march_2026.csv")
OUT = os.path.join(HERE, "..", "data", "processed")
os.makedirs(OUT, exist_ok=True)
KEY = ["country", "network"]


def build_tidy():
    raw = pd.read_csv(RAW, dtype={"index_month": str})
    assert raw.notna().drop(columns="published_rank").all().all(), "missing value in raw file"
    assert not raw.duplicated(KEY + ["source"]).any(), "duplicate reading from one source"
    assert set(raw.network) == {"mobile", "fixed"}
    assert raw.median_download_mbps.between(1, 1000).all(), "speed outside plausible range"
    assert raw.index_month.nunique() == 1, "more than one index month in the file"

    # 1. Every source that reports a figure must report the same figure.
    spread = raw.groupby(KEY).median_download_mbps.agg(["min", "max"])
    if (spread["min"] != spread["max"]).any():
        raise SystemExit("Sources disagree:\n" + spread[spread["min"] != spread["max"]].to_string())

    tidy = (raw.groupby(KEY + ["region", "gcc_member", "index_month"])
               .agg(median_download_mbps=("median_download_mbps", "first"),
                    published_rank=("published_rank", "max"),
                    n_sources=("source", "nunique"))
               .reset_index())
    tidy["verification"] = tidy.n_sources.map(lambda n: "two-sources" if n >= 2 else "single-source")
    return tidy.sort_values(["network", "median_download_mbps"], ascending=[True, False]).reset_index(drop=True)


def check_ranks(tidy):
    """Published ranks 1 to 40 must match the order of the speeds, and no unranked country may be faster than rank 40."""
    mob = tidy[tidy.network == "mobile"].sort_values("median_download_mbps", ascending=False).reset_index(drop=True)
    ranked = mob[mob.published_rank.notna()]
    assert list(ranked.published_rank.astype(int)) == list(range(1, len(ranked) + 1)), "rank order does not match speeds"
    floor = ranked.median_download_mbps.min()
    unranked = mob[mob.published_rank.isna()]
    assert (unranked.median_download_mbps < floor).all(), "an unranked country is faster than the last ranked one"
    return len(ranked), floor


def build_country(tidy):
    wide = tidy.pivot(index=["country", "region", "gcc_member", "index_month"], columns="network",
                      values="median_download_mbps").reset_index()
    wide = wide.rename(columns={"mobile": "mobile_mbps", "fixed": "fixed_mbps"})
    rank = tidy[tidy.network == "mobile"].set_index("country").published_rank
    wide["mobile_rank_published"] = wide.country.map(rank).astype("Int64")
    wide["mobile_to_fixed_ratio"] = (wide.mobile_mbps / wide.fixed_mbps).round(2)
    wide["faster_network"] = (wide.mobile_mbps > wide.fixed_mbps).map({True: "mobile", False: "fixed"})
    uae = wide.loc[wide.country == "United Arab Emirates", "mobile_mbps"].iloc[0]
    wide["uae_mobile_multiple"] = (uae / wide.mobile_mbps).round(1)
    ver = tidy.pivot(index="country", columns="network", values="verification")
    wide["mobile_verification"] = wide.country.map(ver["mobile"])
    wide["fixed_verification"] = wide.country.map(ver["fixed"])
    cols = ["country", "region", "gcc_member", "index_month", "mobile_rank_published", "mobile_mbps", "fixed_mbps",
            "mobile_to_fixed_ratio", "faster_network", "uae_mobile_multiple", "mobile_verification", "fixed_verification"]
    return wide[cols].sort_values("mobile_mbps", ascending=False).reset_index(drop=True)


def build_groups(country):
    """Summaries for the countries collected. The sample is not the full index, so these are not regional averages."""
    rows = []
    groups = [("GCC states", country[country.gcc_member == "yes"])]
    groups += [(r + " (countries collected)", g) for r, g in country.groupby("region")]
    groups += [("All countries collected", country)]
    for name, g in groups:
        rows.append({"group": name, "countries": len(g),
                     "median_mobile_mbps": round(g.mobile_mbps.median(), 2),
                     "median_fixed_mbps": round(g.fixed_mbps.median(), 2),
                     "min_mobile_mbps": g.mobile_mbps.min(), "max_mobile_mbps": g.mobile_mbps.max(),
                     "countries_mobile_faster": int((g.faster_network == "mobile").sum())})
    return pd.DataFrame(rows)


def main():
    tidy = build_tidy()
    n_ranked, floor = check_ranks(tidy)
    country = build_country(tidy)
    groups = build_groups(country)
    tidy.to_csv(os.path.join(OUT, "speed_tidy.csv"), index=False)
    country.to_csv(os.path.join(OUT, "speed_by_country.csv"), index=False)
    groups.to_csv(os.path.join(OUT, "group_summary.csv"), index=False)
    print(f"speed_tidy.csv: {len(tidy)} rows | speed_by_country.csv: {len(country)} rows | group_summary.csv: {len(groups)} rows")
    print(tidy.verification.value_counts().to_string())
    print(f"Rank check passed: {n_ranked} ranked countries in speed order, rank {n_ranked} at {floor} Mbps")


if __name__ == "__main__":
    main()
