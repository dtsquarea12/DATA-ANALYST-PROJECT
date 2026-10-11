"""Build the analysis tables for the renewable power capacity by country project.

Run from the project folder:  python scripts/build_data.py
Reads  data/raw/irena_2026_total_renewable_reading_a.csv, irena_2026_total_renewable_reading_b.csv,
       data/raw/secondary_reports.csv
Writes data/processed/renewable_capacity_tidy.csv, data/processed/country_summary_2025.csv,
       data/processed/group_summary.csv, data/processed/secondary_checks.csv
"""
import os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "..", "data", "raw")
OUT = os.path.join(HERE, "..", "data", "processed")
os.makedirs(OUT, exist_ok=True)

YEARS = [str(y) for y in range(2016, 2026)]

# Label printed in the IRENA table -> (code, name used here, name used in the first reading).
COUNTRIES = {
    "Bahrain": ("BHR", "Bahrain", "Bahrain"), "Kuwait": ("KWT", "Kuwait", "Kuwait"),
    "Oman": ("OMN", "Oman", "Oman"), "Qatar": ("QAT", "Qatar", "Qatar"),
    "Saudi Arabia": ("SAU", "Saudi Arabia", "Saudi Arabia"),
    "United Arab Em": ("ARE", "United Arab Emirates", "United Arab Emirates"),
    "Iraq": ("IRQ", "Iraq", "Iraq"), "Israel": ("ISR", "Israel", "Israel"),
    "Jordan": ("JOR", "Jordan", "Jordan"), "Lebanon": ("LBN", "Lebanon", "Lebanon"),
    "Palestine": ("PSE", "Palestine", "Palestine"), "Syrian AR": ("SYR", "Syria", "Syria"),
    "Iran IR": ("IRN", "Iran", "Iran"), "Türkiye": ("TUR", "Turkey", "Turkey"),
    "Yemen": ("YEM", "Yemen", "Yemen"),
    "Algeria": ("DZA", "Algeria", "Algeria"), "Egypt": ("EGY", "Egypt", "Egypt"),
    "Libya": ("LBY", "Libya", "Libya"), "Morocco": ("MAR", "Morocco", "Morocco"),
    "Tunisia": ("TUN", "Tunisia", "Tunisia"),
}
# The same four sub-regions (20 economies) used in the other projects of this portfolio.
SUB_REGION = {
    "Gulf": ["BHR", "KWT", "OMN", "QAT", "SAU", "ARE"],
    "Levant and Iraq": ["IRQ", "ISR", "JOR", "LBN", "PSE", "SYR"],
    "Iran, Turkey and Yemen": ["IRN", "TUR", "YEM"],
    "North Africa": ["DZA", "EGY", "LBY", "MAR", "TUN"],
}
SUB_ORDER = list(SUB_REGION)
# The 14 countries printed under the "Middle East" heading of the IRENA table.
IRENA_MIDDLE_EAST = ["BHR", "IRN", "IRQ", "ISR", "JOR", "KWT", "LBN", "OMN", "PSE", "QAT", "SAU", "SYR", "ARE",
                     "YEM"]
REGION_NAME = {"Middle East": "Middle East", "Asia": "Asia", "Africa": "Africa", "Europe": "Europe",
               "Eurasia": "Eurasia", "N America": "North America", "S America": "South America",
               "C America + Carib": "Central America and the Caribbean", "Oceania": "Oceania"}
REGION_ORDER = list(REGION_NAME.values())


def load_readings():
    b = pd.read_csv(os.path.join(RAW, "irena_2026_total_renewable_reading_b.csv"))
    a = pd.read_csv(os.path.join(RAW, "irena_2026_total_renewable_reading_a.csv"))
    assert len(b) == 31 and not b.label_in_source.duplicated().any(), "expected 31 distinct rows in reading B"
    assert len(a) == 22 and not a.label_requested.duplicated().any(), "expected 22 distinct rows in reading A"
    assert b[YEARS].notna().all().all() and a[YEARS].notna().all().all(), "missing value in a reading"
    assert (b[YEARS] >= 0).all().all(), "negative capacity"
    # Compare the two readings on every row they share.
    a_key = {v[2]: k for k, v in COUNTRIES.items()}
    a_key.update({"World": "World", "Middle East": "Middle East"})
    a["label_in_source"] = a.label_requested.map(a_key)
    assert a.label_in_source.notna().all(), "reading A label not matched"
    m = a.merge(b, on="label_in_source", suffixes=("_a", "_b"), validate="one_to_one")
    assert len(m) == 22
    for y in YEARS:
        bad = m[m[y + "_a"] != m[y + "_b"]]
        assert bad.empty, f"the two readings disagree in {y}:\n{bad[['label_in_source', y + '_a', y + '_b']]}"
    b["read_twice"] = b.label_in_source.isin(a.label_in_source)
    return b


def identity_checks(b):
    """Totals printed by IRENA must equal the sum of their parts in every year."""
    idx = b.set_index("label_in_source")[YEARS]
    code_to_label = {v[0]: k for k, v in COUNTRIES.items()}
    me_sum = idx.loc[[code_to_label[c] for c in IRENA_MIDDLE_EAST]].sum()
    diff_me = (me_sum - idx.loc["Middle East"]).abs()
    # Every figure is rounded to a whole megawatt, so a total can differ from its parts by a few MW.
    assert (diff_me <= 3).all(), "Middle East total is not the sum of its 14 countries:\n" + str(diff_me)
    world_sum = idx.loc[list(REGION_NAME)].sum()
    diff_w = (world_sum - idx.loc["World"]).abs()
    assert (diff_w <= 5).all(), "World total is not the sum of the nine regions:\n" + str(diff_w)
    assert (idx.loc["European Union"] < idx.loc["Europe"]).all()
    return int(diff_me.max()), int(diff_w.max())


def tidy(b):
    rows = []
    sub = {c: s for s, cs in SUB_REGION.items() for c in cs}
    for _, r in b.iterrows():
        lab = r.label_in_source
        if r.row_type == "country":
            code, name, _ = COUNTRIES[lab]
            base = dict(entity=name, entity_type="country", iso3=code, sub_region=sub[code],
                        in_irena_middle_east=code in IRENA_MIDDLE_EAST)
        elif r.row_type == "region":
            base = dict(entity=REGION_NAME[lab], entity_type="irena_region", iso3="", sub_region="",
                        in_irena_middle_east=False)
        elif r.row_type == "world":
            base = dict(entity="World", entity_type="world", iso3="", sub_region="", in_irena_middle_east=False)
        else:
            continue  # the European Union is a subset of Europe and is kept in the raw file only
        for y in YEARS:
            rows.append(dict(base, year=int(y), capacity_mw=int(r[y]), label_in_source=lab,
                             read_twice=bool(r.read_twice)))
    t = pd.DataFrame(rows)
    # Sub-region and Middle East (20) aggregates, computed here.
    c = t[t.entity_type == "country"]
    aggs = []
    for s in SUB_ORDER:
        g = c[c.sub_region == s].groupby("year").capacity_mw.sum()
        aggs += [dict(entity=s, entity_type="sub_region", iso3="", sub_region=s, in_irena_middle_east=False,
                      year=int(y), capacity_mw=int(v), label_in_source="", read_twice=True) for y, v in g.items()]
    g = c.groupby("year").capacity_mw.sum()
    aggs += [dict(entity="Middle East and North Africa (20 economies)", entity_type="aggregate_20", iso3="",
                  sub_region="", in_irena_middle_east=False, year=int(y), capacity_mw=int(v), label_in_source="",
                  read_twice=True) for y, v in g.items()]
    t = pd.concat([t, pd.DataFrame(aggs)], ignore_index=True)
    t = t.sort_values(["entity", "year"]).reset_index(drop=True)
    prev = t.groupby("entity").capacity_mw.shift(1)
    t["change_mw"] = (t.capacity_mw - prev).astype("Int64")
    t["change_pct"] = ((t.capacity_mw / prev - 1) * 100).where(prev > 0).round(1)
    order = {"country": 0, "sub_region": 1, "aggregate_20": 2, "irena_region": 3, "world": 4}
    t["_o"] = t.entity_type.map(order)
    t["_s"] = t.sub_region.map({s: i for i, s in enumerate(SUB_ORDER)}).fillna(9)
    t["_r"] = t.entity.map({r: i for i, r in enumerate(REGION_ORDER)}).fillna(0)
    t = t.sort_values(["_o", "_s", "_r", "entity", "year"]).drop(columns=["_o", "_s", "_r"]).reset_index(drop=True)
    return t[["entity", "entity_type", "iso3", "sub_region", "in_irena_middle_east", "year", "capacity_mw",
              "change_mw", "change_pct", "label_in_source", "read_twice"]]


def summarise(t):
    w = t.pivot(index="entity", columns="year", values="capacity_mw")
    meta = t.drop_duplicates("entity").set_index("entity")[["entity_type", "iso3", "sub_region",
                                                             "in_irena_middle_east"]]
    s = meta.copy()
    s["capacity_2016_mw"] = w[2016]
    s["capacity_2024_mw"] = w[2024]
    s["capacity_2025_mw"] = w[2025]
    s["added_2025_mw"] = w[2025] - w[2024]
    s["growth_2025_pct"] = ((w[2025] / w[2024] - 1) * 100).round(1)
    s["added_2016_2025_mw"] = w[2025] - w[2016]
    s["multiple_of_2016"] = (w[2025] / w[2016]).round(1)
    return s.reset_index()


def secondary(s):
    """Compare each figure printed in a press release or news report with the IRENA table."""
    sec = pd.read_csv(os.path.join(RAW, "secondary_reports.csv"))
    name = {"C America + Carib": "Central America and the Caribbean"}
    idx = s.set_index("entity")
    col = {"capacity_2025": "capacity_2025_mw", "capacity_2024": "capacity_2024_mw", "added_2025": "added_2025_mw",
           "growth_2025_pct": "growth_2025_pct"}
    out = []
    for _, r in sec.iterrows():
        ent = name.get(r.entity, r.entity)
        assert ent in idx.index, "entity not in table: " + ent
        if r.measure == "growth_2025_pct":
            raw = (idx.loc[ent, "capacity_2025_mw"] / idx.loc[ent, "capacity_2024_mw"] - 1) * 100
        else:
            raw = idx.loc[ent, col[r.measure]] / (1000 if r.unit == "GW" else 1)
        step = 10 ** (-int(r.decimals))
        # A report agrees when it is within one unit of its last printed digit (rounded or cut off).
        status = "agrees" if abs(raw - r.published_value) < step else "differs"
        out.append(dict(source=r.source, entity=ent, measure=r.measure, published_value=r.published_value,
                        unit=r.unit, irena_table_value=round(float(raw), 3), status=status,
                        note=r.note if isinstance(r.note, str) else ""))
    out = pd.DataFrame(out)
    differs = out[out.status == "differs"]
    assert len(differs) == 1 and differs.iloc[0].entity == "United Arab Emirates", (
        "unexpected disagreement with a secondary report:\n" + differs.to_string())
    return out


def build():
    b = load_readings()
    diff_me, diff_w = identity_checks(b)
    t = tidy(b)
    s = summarise(t)
    checks = secondary(s)
    ok = checks[(checks.status == "agrees") & checks.measure.isin(["capacity_2025", "added_2025"])]
    confirmed = set(ok.entity)
    s["check_status"] = ["two-publishers" if e in confirmed else
                         ("computed" if ty in ("sub_region", "aggregate_20") else "irena-only")
                         for e, ty in zip(s.entity, s.entity_type)]
    countries = s[s.entity_type == "country"].copy()
    countries["_s"] = countries.sub_region.map({x: i for i, x in enumerate(SUB_ORDER)})
    countries = countries.sort_values(["_s", "capacity_2025_mw"], ascending=[True, False]).drop(columns="_s")
    countries["rank_capacity_2025"] = countries.capacity_2025_mw.rank(ascending=False, method="min").astype(int)
    countries["rank_added_2025"] = countries.added_2025_mw.rank(ascending=False, method="min").astype(int)
    groups = s[s.entity_type != "country"].copy()
    order = SUB_ORDER + ["Middle East and North Africa (20 economies)"] + REGION_ORDER + ["World"]
    groups["_o"] = groups.entity.map({e: i for i, e in enumerate(order)})
    groups = groups.sort_values("_o").drop(columns=["_o", "iso3", "sub_region", "in_irena_middle_east"])
    world25 = float(groups.loc[groups.entity == "World", "capacity_2025_mw"].iloc[0])
    groups["share_of_world_2025_pct"] = (groups.capacity_2025_mw / world25 * 100).round(2)
    t.to_csv(os.path.join(OUT, "renewable_capacity_tidy.csv"), index=False)
    countries.drop(columns=["entity_type"]).rename(columns={"entity": "country"}).to_csv(
        os.path.join(OUT, "country_summary_2025.csv"), index=False)
    groups.to_csv(os.path.join(OUT, "group_summary.csv"), index=False)
    checks.to_csv(os.path.join(OUT, "secondary_checks.csv"), index=False)
    print(f"tidy rows: {len(t)} | countries: {len(countries)} | groups: {len(groups)} | checks: {len(checks)}")
    print(f"largest gap, Middle East total against its 14 countries: {diff_me} MW")
    print(f"largest gap, World against the nine regions: {diff_w} MW")
    print("secondary reports:", checks.status.value_counts().to_dict())
    print("2025 figure also printed by a second publisher:", int((countries.check_status == 'two-publishers').sum()),
          "of", len(countries))
    return t, countries, groups, checks


if __name__ == "__main__":
    build()
