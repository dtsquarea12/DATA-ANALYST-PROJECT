"""Build the analysis tables for the import tariffs by country project.

Run from the project folder:  python scripts/build_data.py
Reads  data/raw/wtp2026_all_products_reading_a.txt, wtp2026_all_products_reading_b.txt,
       wto_ttd_profiles.csv, country_reference.csv
Writes data/processed/tariffs_tidy.csv, data/processed/middle_east.csv,
       data/processed/region_summary.csv, data/processed/source_checks.csv

How a printed row is read. The PDF text leaves blank cells out, so the count of numbers on a row tells its type:
  * year first, 15 or more numbers after it: WTO member with an applied tariff.
      order: binding coverage, bound simple average, MFN applied simple average, ...
  * year first, 10 or fewer numbers after it: economy that is not a WTO member (no bound tariffs).
      order: MFN applied simple average, MFN duty-free share, ...
  * no year: WTO member with no MFN applied figure in this edition.
      order: binding coverage, bound simple average, ...
"""
import csv
import os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "..", "data", "raw")
OUT = os.path.join(HERE, "..", "data", "processed")
os.makedirs(OUT, exist_ok=True)

N_TABLE = 152  # economies printed in the summary table
MIDDLE_EAST = {
    "Gulf": ["BHR", "ARE", "QAT", "KWT", "OMN", "SAU"],
    "Levant and Iraq": ["PSE", "IRQ", "LBN", "JOR", "ISR", "SYR"],
    "Iran, Turkey and Yemen": ["YEM", "IRN", "TUR"],
    "North Africa": ["LBY", "TUN", "EGY", "DZA", "MAR"],
}
SUB_ORDER = list(MIDDLE_EAST)
REGION_ORDER = ["Middle East", "Europe", "Rest of Asia", "Rest of Africa", "North America", "South America",
                "Oceania"]
EU_MEMBERS = 27

# WTO names -> names in country_reference.csv
ALIAS = {
    "Bahrain, Kingdom of": "Bahrain", "Kuwait, the State of": "Kuwait", "Saudi Arabia, Kingdom of": "Saudi Arabia",
    "Türkiye": "Turkey", "Hong Kong, China": "Hong Kong", "Macao, China": "Macao", "Chinese Taipei": "Taiwan",
    "Korea, Republic of": "South Korea", "Viet Nam": "Vietnam", "Russian Federation": "Russia",
    "Moldova, Republic of": "Moldova", "Brunei Darussalam": "Brunei", "Cabo Verde": "Cape Verde",
    "Lao People's Democratic Republic": "Laos", "Côte d'Ivoire": "Ivory Coast", "The Gambia": "Gambia",
    "Bolivia, Plurinational State of": "Bolivia", "Venezuela, Bolivarian Republic of": "Venezuela",
    "Democratic Republic of the Congo": "DR Congo", "Micronesia, Federated States of":
    "Federated States of Micronesia", "Kyrgyz Republic": "Kyrgyzstan", "United States of America": "United States",
}


def read_rows(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        lines = [l for l in f if l.strip() and not l.startswith("#")]
    for rec in csv.reader(lines):
        name, vals = rec[0], [v.strip() for v in rec[1:]]
        rows.append((name, vals))
    return rows


def num(v):
    return None if v.startswith(">") else float(v.replace(",", ""))


def parse_a(name, vals):
    """Full row: classify by the count of numbers."""
    has_year = vals[0] in ("2024", "2025")
    if not has_year:
        return dict(economy=name, wto_member=True, mfn_year=None, binding_coverage=num(vals[0]),
                    bound_avg=num(vals[1]), mfn_applied_avg=None, n_values=len(vals))
    rest = vals[1:]
    if len(rest) >= 15:
        return dict(economy=name, wto_member=True, mfn_year=int(vals[0]), binding_coverage=num(rest[0]),
                    bound_avg=num(rest[1]), mfn_applied_avg=num(rest[2]), n_values=len(vals))
    assert len(rest) <= 10, f"{name}: {len(rest)} numbers after the year does not fit a known row type"
    return dict(economy=name, wto_member=False, mfn_year=int(vals[0]), binding_coverage=None, bound_avg=None,
                mfn_applied_avg=num(rest[0]), n_values=len(vals))


def parse_b(name, vals, member):
    """First four numbers only; membership comes from reading A (or is given for rows reading A left out)."""
    if vals[0] not in ("2024", "2025"):
        return dict(economy=name, mfn_year=None, bound_avg=num(vals[1]), mfn_applied_avg=None)
    if member:
        return dict(economy=name, mfn_year=int(vals[0]), bound_avg=num(vals[2]), mfn_applied_avg=num(vals[3]))
    return dict(economy=name, mfn_year=int(vals[0]), bound_avg=None, mfn_applied_avg=num(vals[1]))


a = pd.DataFrame([parse_a(n, v) for n, v in read_rows(os.path.join(RAW, "wtp2026_all_products_reading_a.txt"))])
member = dict(zip(a.economy, a.wto_member))
member["Chinese Taipei"] = True  # WTO member; row missing from reading A
b = pd.DataFrame([parse_b(n, v, member[n]) for n, v in
                  read_rows(os.path.join(RAW, "wtp2026_all_products_reading_b.txt"))])

# ---- data checks ----
assert len(b) == N_TABLE, f"reading B has {len(b)} rows, expected {N_TABLE}"
assert not a.economy.duplicated().any() and not b.economy.duplicated().any(), "duplicate economy"
missing_a = sorted(set(b.economy) - set(a.economy))
assert missing_a == ["Chinese Taipei"], f"rows missing from reading A: {missing_a}"
m = b.merge(a, on="economy", how="left", suffixes=("_b", "_a"))
both = m[m.economy != "Chinese Taipei"]
for col in ["mfn_year", "bound_avg", "mfn_applied_avg"]:
    x, y = both[f"{col}_a"], both[f"{col}_b"]
    bad = both[~((x == y) | (x.isna() & y.isna()))]
    assert bad.empty, f"readings A and B disagree on {col}: {bad.economy.tolist()}"
vals = a.mfn_applied_avg.dropna()
assert vals.between(0, 100).all(), "applied average out of range"
assert a.bound_avg.dropna().between(0, 200).all(), "bound average out of range"
# A member's applied average above its bound average would mean a misread column.
mem = a[a.wto_member & a.mfn_applied_avg.notna()]
over = mem[mem.mfn_applied_avg > mem.bound_avg]

# ---- tidy table ----
ref = pd.read_csv(os.path.join(RAW, "country_reference.csv"))
tidy = b[["economy"]].copy()
tidy = tidy.merge(a[["economy", "wto_member", "mfn_year", "binding_coverage", "bound_avg", "mfn_applied_avg"]],
                  on="economy", how="left")
tw = b.set_index("economy").loc["Chinese Taipei"]
idx = tidy.economy == "Chinese Taipei"
tidy.loc[idx, ["wto_member", "mfn_year", "bound_avg", "mfn_applied_avg"]] = [True, tw.mfn_year, tw.bound_avg,
                                                                            tw.mfn_applied_avg]
tidy["readings"] = "two"
tidy.loc[idx, "readings"] = "one (B)"
tidy["country"] = tidy.economy.map(lambda s: ALIAS.get(s, s))
tidy = tidy.merge(ref, on="country", how="left")
assert tidy.region.notna().all(), f"no region for {tidy[tidy.region.isna()].economy.tolist()}"
sub = {iso: s for s, isos in MIDDLE_EAST.items() for iso in isos}
tidy["sub_region"] = tidy.iso3.map(sub)
tidy["mfn_year"] = tidy.mfn_year.astype("Int64")
tidy["has_applied"] = tidy.mfn_applied_avg.notna()
ranked = tidy[tidy.has_applied].copy()
N = len(ranked)
tidy["rank_low_to_high"] = tidy.mfn_applied_avg.rank(method="min").astype("Int64")
tidy["economies_higher"] = tidy.mfn_applied_avg.map(
    lambda v: int((ranked.mfn_applied_avg > v).sum()) if pd.notna(v) else None).astype("Int64")
tidy["share_economies_lower_pct"] = tidy.mfn_applied_avg.map(
    lambda v: round(100 * (ranked.mfn_applied_avg < v).sum() / N, 1) if pd.notna(v) else None)

# ---- second WTO document ----
ttd = pd.read_csv(os.path.join(RAW, "wto_ttd_profiles.csv")).rename(
    columns={"mfn_applied_simple_avg": "mfn_applied_avg", "bound_simple_avg": "bound_avg"})
chk = ttd.merge(tidy[["economy", "mfn_year", "mfn_applied_avg", "bound_avg"]], on="economy",
                suffixes=("_ttd", "_wtp"))
assert len(chk) == len(ttd), "a WTO profile did not match an economy in the table"


def status(r):
    same_val = abs(r.mfn_applied_avg_ttd - r.mfn_applied_avg_wtp) < 1e-9
    if same_val and r.mfn_year_ttd == r.mfn_year_wtp:
        return "confirmed: same value and year"
    if same_val:
        return "confirmed value: profile labels another year"
    if r.mfn_year_ttd == r.mfn_year_wtp:
        return "differs: same year"
    return "differs: profile shows another year"


chk["check"] = chk.apply(status, axis=1)
chk = chk[["economy", "mfn_applied_avg_wtp", "mfn_year_wtp", "mfn_applied_avg_ttd", "mfn_year_ttd", "check"]]
tidy = tidy.merge(chk[["economy", "check"]].rename(columns={"check": "wto_profile_check"}), on="economy",
                  how="left")
tidy["wto_profile_check"] = tidy.wto_profile_check.fillna("not checked")

cols = ["economy", "country", "iso3", "region", "sub_region", "wto_member", "mfn_year", "mfn_applied_avg",
        "bound_avg", "binding_coverage", "rank_low_to_high", "economies_higher", "share_economies_lower_pct", "readings",
        "wto_profile_check"]
tidy = tidy[cols]
tidy["region"] = pd.Categorical(tidy.region, REGION_ORDER, ordered=True)
tidy = tidy.sort_values(["region", "mfn_applied_avg", "economy"]).reset_index(drop=True)
tidy.to_csv(os.path.join(OUT, "tariffs_tidy.csv"), index=False)

# ---- Middle East (20 economies, all listed, missing ones marked) ----
names = ref.set_index("iso3").country
me_rows = []
for s in SUB_ORDER:
    for iso in MIDDLE_EAST[s]:
        r = tidy[tidy.iso3 == iso]
        if r.empty:
            me_rows.append(dict(country=names[iso], iso3=iso, sub_region=s, in_table=False))
        else:
            d = r.iloc[0].to_dict()
            d["in_table"] = True
            me_rows.append(d)
me = pd.DataFrame(me_rows)
me["sub_region"] = pd.Categorical(me.sub_region, SUB_ORDER, ordered=True)
me = me.sort_values(["sub_region", "mfn_applied_avg"], na_position="last")
me = me[["country", "iso3", "sub_region", "in_table", "wto_member", "mfn_year", "mfn_applied_avg", "bound_avg",
         "rank_low_to_high", "economies_higher", "share_economies_lower_pct", "readings", "wto_profile_check"]]
me.to_csv(os.path.join(OUT, "middle_east.csv"), index=False)

# ---- region summary: equal weight per economy; EU counted once (main) and as 27 members (alternative) ----
rk = tidy[tidy.mfn_applied_avg.notna()].copy()
rows = []
for reg in REGION_ORDER + ["World"]:
    d = rk if reg == "World" else rk[rk.region == reg]
    v = d.mfn_applied_avg
    rows.append(dict(region=reg, economies=len(d), mean=round(v.mean(), 2), median=round(v.median(), 2),
                     min=v.min(), max=v.max(), basis="EU counted once"))
eu_val = rk.loc[rk.economy == "European Union", "mfn_applied_avg"].iloc[0]
expanded = pd.concat([rk[rk.economy != "European Union"].mfn_applied_avg, pd.Series([eu_val] * EU_MEMBERS)])
eu_reg = pd.concat([rk[(rk.region == "Europe") & (rk.economy != "European Union")].mfn_applied_avg,
                    pd.Series([eu_val] * EU_MEMBERS)])
rows.append(dict(region="Europe", economies=len(eu_reg), mean=round(eu_reg.mean(), 2),
                 median=round(eu_reg.median(), 2), min=eu_reg.min(), max=eu_reg.max(),
                 basis="EU as 27 members"))
rows.append(dict(region="World", economies=len(expanded), mean=round(expanded.mean(), 2),
                 median=round(expanded.median(), 2), min=expanded.min(), max=expanded.max(),
                 basis="EU as 27 members"))
gulf = rk[rk.sub_region == "Gulf"].mfn_applied_avg
rows.insert(0, dict(region="Gulf (6)", economies=len(gulf), mean=round(gulf.mean(), 2),
                    median=round(gulf.median(), 2), min=gulf.min(), max=gulf.max(), basis="EU counted once"))
summ = pd.DataFrame(rows)
summ.to_csv(os.path.join(OUT, "region_summary.csv"), index=False)

# ---- source checks ----
chk.to_csv(os.path.join(OUT, "source_checks.csv"), index=False)

# ---- headline figures (asserted again in the notebook) ----
world = summ[(summ.region == "World") & (summ.basis == "EU counted once")].iloc[0]
print(f"economies in table: {len(tidy)}; with an applied average: {N}; member rows applied > bound: "
      f"{over.economy.tolist()}")
print(f"world median {world['median']}, mean {world['mean']}")
print(summ.to_string(index=False))
print(me[["country", "mfn_year", "mfn_applied_avg", "rank_low_to_high", "economies_higher", "share_economies_lower_pct",
          "wto_profile_check"]].to_string(index=False))
print(chk.to_string(index=False))
