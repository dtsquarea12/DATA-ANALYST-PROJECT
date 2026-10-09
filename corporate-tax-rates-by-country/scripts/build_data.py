"""Build the analysis tables for the corporate tax rates by country project.

Run from the project folder:  python scripts/build_data.py
Reads  data/raw/tax_foundation_2025_reading_a.csv, tax_foundation_2025_reading_b.csv,
       tax_foundation_2025_published_checks.csv, pwc_quick_chart_2026.csv, trading_economics_2026.csv
Writes data/processed/corporate_tax_tidy.csv, data/processed/region_summary.csv,
       data/processed/published_checks.csv
"""
import os
import re
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "..", "data", "raw")
OUT = os.path.join(HERE, "..", "data", "processed")
os.makedirs(OUT, exist_ok=True)

# The Middle East is split into four sub-regions (20 economies). Every other jurisdiction keeps the
# continent given in the Tax Foundation table.
MIDDLE_EAST = {
    "Gulf": ["BHR", "ARE", "QAT", "KWT", "OMN", "SAU"],
    "Levant and Iraq": ["PSE", "IRQ", "LBN", "JOR", "ISR", "SYR"],
    "North Africa": ["LBY", "TUN", "EGY", "DZA", "MAR"],
    "Iran, Turkey and Yemen": ["YEM", "IRN", "TUR"],
}
CONTINENT = {"AF": "Rest of Africa", "AS": "Rest of Asia", "EU": "Europe", "NO": "North America",
             "SA": "South America", "OC": "Oceania"}
REGION_ORDER = ["Middle East", "Europe", "Rest of Asia", "Rest of Africa", "North America", "South America",
                "Oceania"]

# Short names used in tables and charts.
SHORT = {"IRN": "Iran", "SYR": "Syria", "PSE": "Palestine", "USA": "United States", "KOR": "South Korea",
         "VNM": "Vietnam", "RUS": "Russia", "HKG": "Hong Kong", "MAC": "Macao", "BOL": "Bolivia",
         "VEN": "Venezuela", "TZA": "Tanzania", "MDA": "Moldova", "LAO": "Laos", "XKX": "Kosovo",
         "BRN": "Brunei", "SWZ": "Eswatini", "FSM": "Micronesia", "CIV": "Cote d'Ivoire",
         "COD": "DR Congo", "COG": "Congo (Republic)"}

# Names used by PwC and Trading Economics that differ from the short names above.
ALIAS = {"Bahamas, The": "BHS", "Brunei Darussalam": "BRN", "Cameroon, Republic of": "CMR",
         "China, People's Republic of": "CHN", "Congo, Democratic Republic of the": "COD",
         "Congo, Republic of": "COG", "Republic of the Congo": "COG", "Czech Republic": "CZE",
         "Guernsey, Channel Islands": "GGY", "Jersey, Channel Islands": "JEY", "Hong Kong SAR": "HKG",
         "Ivory Coast (Cote d'Ivoire)": "CIV", "Ivory Coast": "CIV", "Korea, Republic of": "KOR",
         "Lao PDR": "LAO", "Liberia, Republic of": "LBR", "Macau SAR": "MAC", "Macau": "MAC",
         "Namibia, Republic of": "NAM", "Palestinian territories": "PSE", "Slovak Republic": "SVK",
         "Uzbekistan, Republic of": "UZB", "Macedonia": "MKD", "Swaziland": "SWZ",
         "Trinidad And Tobago": "TTO", "Turkey": "TUR",
         # Trading Economics lists "Congo" at 30% next to "Republic of the Congo" at 28%: the first is DR Congo.
         "Congo": "COD"}

# PwC headline text that does not start with the general rate. Read from the text in the raw file.
PWC_GENERAL = {"BHR": 0.0,   # "46 for oil corps; 0 for other corps; 15% DMTT may apply"
               "JOR": 20.0,  # "Banks 35; ... other 20"
               "KWT": 15.0,  # "15 flat"
               "GGY": 0.0, "JEY": 0.0, "IMN": 0.0,  # "0; 10 for ..." / "Corporate 0; ..."
               "KEN": 30.0, "PNG": 30.0,  # "Resident 30; foreign 30"
               "NGA": 30.0,  # "30 for large companies; 0 for small companies"
               "UKR": 18.0,  # "General 18; ..."
               "IRL": 12.5,  # "Trading 12.5; non-trading 25"
               "BRN": 18.5, "HKG": 16.5, "GTM": 25.0, "HND": 25.0}


def load_tax_foundation():
    a = pd.read_csv(os.path.join(RAW, "tax_foundation_2025_reading_a.csv"))
    b = pd.read_csv(os.path.join(RAW, "tax_foundation_2025_reading_b.csv"))
    assert len(a) == 226 and len(b) == 226, "expected 226 jurisdictions"
    assert not a.iso3.duplicated().any() and not b.iso3.duplicated().any(), "duplicate code"
    m = a.merge(b, on="iso3", suffixes=("_a", "_b"), validate="one_to_one")
    assert len(m) == 226, "the two readings list different jurisdictions"
    bad = m[(m.rate_pct_a - m.rate_pct_b).abs() > 1e-9]
    assert bad.empty, "the two readings of the table disagree:\n" + bad.to_string()
    assert m.rate_pct_a.between(0, 60).all(), "rate outside 0 to 60"
    gmt = m.rate_with_gmt_pct.dropna()
    assert (m.loc[gmt.index, "rate_with_gmt_pct"] >= m.loc[gmt.index, "rate_pct_a"]).all(), "GMT rate below rate"
    m = m.rename(columns={"rate_pct_a": "rate_2025_pct", "rate_with_gmt_pct": "rate_with_min_tax_2025_pct",
                          "country": "name_in_source"})
    return m[["iso3", "name_in_source", "continent_code", "rate_2025_pct", "rate_with_min_tax_2025_pct"]]


def add_regions(df):
    me = {c: sub for sub, cs in MIDDLE_EAST.items() for c in cs}
    assert set(me) <= set(df.iso3), "Middle East code not in table"
    df["region"] = [("Middle East" if c in me else CONTINENT[k]) for c, k in zip(df.iso3, df.continent_code)]
    df["sub_region"] = [me.get(c, r) for c, r in zip(df.iso3, df.region)]
    df["country"] = [SHORT.get(c, n) for c, n in zip(df.iso3, df.name_in_source)]
    return df


def name_to_iso(df):
    lut = {n: c for c, n in zip(df.iso3, df.country)}
    lut.update({n: c for c, n in zip(df.iso3, df.name_in_source)})
    lut.update(ALIAS)
    return lut


def parse_pwc(text, iso):
    """General headline rate from the PwC text, or None when the text gives no single general rate."""
    if iso in PWC_GENERAL:
        return PWC_GENERAL[iso]
    t = str(text).strip()
    if re.fullmatch(r"\d+(\.\d+)?", t):
        return float(t)
    m = re.match(r"(\d+(?:\.\d+)?) \(", t)  # a rate followed by a note in brackets
    if m:
        return float(m.group(1))
    m = re.match(r"(\d+(?:\.\d+)?) (?:from|for tax periods from|combined) ", t)
    if m:
        return float(m.group(1))
    return None


def load_second_sources(df):
    lut = name_to_iso(df)
    pwc = pd.read_csv(os.path.join(RAW, "pwc_quick_chart_2026.csv"))
    pwc["iso3"] = pwc.territory.map(lut)
    assert pwc.iso3.notna().all(), "PwC name not matched: " + str(pwc[pwc.iso3.isna()].territory.tolist())
    assert not pwc.iso3.duplicated().any()
    pwc["pwc_rate_2026_pct"] = [parse_pwc(t, c) for t, c in zip(pwc.headline_cit_rate_text, pwc.iso3)]
    te = pd.read_csv(os.path.join(RAW, "trading_economics_2026.csv"))
    te = te[~te.country.isin(["Euro area", "European Union"])].copy()
    te["iso3"] = te.country.map(lut)
    assert te.iso3.notna().all(), "Trading Economics name not matched: " + str(te[te.iso3.isna()].country.tolist())
    assert not te.iso3.duplicated().any()
    te = te.rename(columns={"last_pct": "te_rate_2026_pct"})
    return pwc[["iso3", "pwc_rate_2026_pct", "headline_cit_rate_text"]].rename(
        columns={"headline_cit_rate_text": "pwc_text"}), te[["iso3", "te_rate_2026_pct"]]


def check_status(r):
    """How the 2025 rate compares with the two 2026 listings."""
    others = [v for v in (r.pwc_rate_2026_pct, r.te_rate_2026_pct) if pd.notna(v)]
    if not others:
        return "single-source"
    if any(abs(v - r.rate_2025_pct) < 0.005 for v in others):
        return "confirmed"
    return "differs"


def build():
    df = add_regions(load_tax_foundation())
    pwc, te = load_second_sources(df)
    df = df.merge(pwc, on="iso3", how="left").merge(te, on="iso3", how="left")
    df["check_status"] = df.apply(check_status, axis=1)
    df["rank_lowest"] = df.rate_2025_pct.rank(method="min").astype(int)
    df["rank_highest"] = df.rate_2025_pct.rank(method="min", ascending=False).astype(int)
    df["min_tax_uplift_pts"] = df.rate_with_min_tax_2025_pct - df.rate_2025_pct
    df["region"] = pd.Categorical(df.region, REGION_ORDER, ordered=True)
    df = df.sort_values(["region", "sub_region", "rate_2025_pct", "country"]).reset_index(drop=True)
    cols = ["iso3", "country", "region", "sub_region", "rate_2025_pct", "rate_with_min_tax_2025_pct",
            "min_tax_uplift_pts", "rank_lowest", "rank_highest", "pwc_rate_2026_pct", "te_rate_2026_pct",
            "check_status", "pwc_text", "name_in_source"]
    df = df[cols]

    def summary(g):
        return pd.Series({"jurisdictions": len(g), "mean_rate_pct": round(g.rate_2025_pct.mean(), 2),
                          "median_rate_pct": round(g.rate_2025_pct.median(), 2),
                          "min_rate_pct": g.rate_2025_pct.min(), "max_rate_pct": g.rate_2025_pct.max(),
                          "at_or_below_15_pct": int((g.rate_2025_pct <= 15).sum()),
                          "confirmed": int((g.check_status == "confirmed").sum())})
    parts = [df.groupby("region", observed=True).apply(summary, include_groups=False).reset_index()
             .assign(level="region").rename(columns={"region": "group"})]
    me = df[df.region == "Middle East"]
    parts.append(me.groupby("sub_region").apply(summary, include_groups=False).reset_index()
                 .assign(level="middle_east_sub_region").rename(columns={"sub_region": "group"}))
    parts.append(pd.DataFrame([summary(df)]).assign(group="All 226 jurisdictions", level="world"))
    reg = pd.concat(parts, ignore_index=True)
    reg["group"] = reg["group"].astype(str)
    for c in ["jurisdictions", "at_or_below_15_pct", "confirmed"]:
        reg[c] = reg[c].astype(int)
    reg = reg[["level", "group", "jurisdictions", "mean_rate_pct", "median_rate_pct", "min_rate_pct",
               "max_rate_pct", "at_or_below_15_pct", "confirmed"]]

    # Totals printed in the Tax Foundation text, recomputed from the table. A misread row would break these.
    pub = pd.read_csv(os.path.join(RAW, "tax_foundation_2025_published_checks.csv"))
    r = df.rate_2025_pct
    nonzero = df[r > 0].sort_values("rate_2025_pct")
    computed = {
        "jurisdictions_in_table": len(df),
        "mean_rate_all_jurisdictions_pct": round(r.mean(), 2),
        "jurisdictions_no_corporate_income_tax": int((r == 0).sum()),
        "jurisdictions_at_or_below_20_pct": int((r <= 20).sum()),
        "jurisdictions_above_20_to_30_pct": int(((r > 20) & (r <= 30)).sum()),
        "jurisdictions_at_or_below_30_pct": int((r <= 30).sum()),
        "jurisdictions_above_30_to_35_pct": int(((r > 30) & (r <= 35)).sum()),
        "jurisdictions_above_35_pct": int((r > 35).sum()),
        "uae_rank_lowest_nonzero": int((nonzero.rate_2025_pct < 9).sum()) + 3,  # three share 9%; printed fourth
    }
    pub["computed_value"] = pub.check.map(computed)
    pub["result"] = ["not recomputed (needs GDP data)" if pd.isna(c) else
                     ("match" if abs(c - p) < 0.005 else "MISMATCH")
                     for c, p in zip(pub.computed_value, pub.published_value)]
    return df, reg, pub


if __name__ == "__main__":
    df, reg, pub = build()
    print(pub.to_string())
    assert not (pub.result == "MISMATCH").any(), "a published total does not match the table"
    df.to_csv(os.path.join(OUT, "corporate_tax_tidy.csv"), index=False)
    reg.to_csv(os.path.join(OUT, "region_summary.csv"), index=False)
    pub.to_csv(os.path.join(OUT, "published_checks.csv"), index=False)
    print(reg.to_string())
    print(df.check_status.value_counts().to_string())
    print(df[df.region == "Middle East"].drop(columns=["pwc_text", "name_in_source"]).to_string())
    print(df[df.check_status == "differs"][["country", "rate_2025_pct", "pwc_rate_2026_pct", "te_rate_2026_pct", "pwc_text"]].to_string())
