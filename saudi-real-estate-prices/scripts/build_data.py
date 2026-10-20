"""Build the processed tables for the Saudi real estate prices project.

Every figure is read from one or more documents (data/raw/price_index_readings.csv).
The script stops if two documents print different values for the same figure,
except for readings set aside with a reason in the `note` column. It then checks
the identities that link the published figures:

  * an annual change must match the index levels four quarters apart,
  * a quarterly change must match the index levels one quarter apart,
  * four quarterly changes must chain to the annual change.

All checks use interval arithmetic: a value printed to d decimals stands for
any number within half a unit of its last digit.
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

LATEST = "Q2 2026"
SECTOR = {
    "all": "All", "residential": "Residential", "residential_land": "Residential",
    "villa": "Residential", "apartment": "Residential", "floor": "Residential",
    "commercial": "Commercial", "commercial_land": "Commercial",
    "commercial_building": "Commercial", "showroom_shop": "Commercial",
    "agricultural": "Agricultural", "agricultural_land": "Agricultural",
}
LABEL = {
    "all": "All property", "residential": "Residential (sector)",
    "residential_land": "Residential land", "villa": "Villas",
    "apartment": "Apartments", "floor": "Residential floors",
    "commercial": "Commercial (sector)", "commercial_land": "Commercial land",
    "commercial_building": "Commercial buildings", "showroom_shop": "Showrooms and shops",
    "agricultural": "Agricultural (sector)", "agricultural_land": "Agricultural land",
}


def pkey(p):
    q, y = p.split()
    return int(y) * 4 + int(q[1]) - 1


def pname(k):
    return f"Q{k % 4 + 1} {k // 4}"


def decimals(s):
    s = str(s)
    return len(s.split(".")[1]) if "." in s else 0


def interval(value, dec):
    h = 0.5 * 10.0 ** (-int(dec))
    return value - h, value + h


def overlaps(a, b):
    return a[0] <= b[1] + 1e-9 and b[0] <= a[1] + 1e-9


def consolidate(readings, sources):
    pub = sources.set_index("source_id")["publisher"].to_dict()
    kind = sources.set_index("source_id")["kind"].to_dict()
    used = readings[~readings["note"].fillna("").str.startswith("set aside")].copy()
    used["dec"] = used["raw"].map(decimals)
    rows = []
    for (period, geo, seg, measure), g in used.groupby(["period", "geography", "segment", "measure"]):
        if measure == "level":
            # levels are printed to 0, 1 or 2 decimals; they must agree within rounding
            best = g.sort_values("dec", ascending=False).iloc[0]
            for _, r in g.iterrows():
                assert overlaps(interval(r.value, r.dec), interval(best.value, best.dec)), \
                    f"documents disagree on {measure} {geo} {seg} {period}: {g.raw.tolist()}"
            value, dec = best.value, best.dec
        else:
            vals = g["value"].round(4).unique()
            assert len(vals) == 1, f"documents disagree on {measure} {geo} {seg} {period}: {g.raw.tolist()}"
            value, dec = vals[0], g["dec"].max()
        pubs = sorted({pub[s] for s in g.source_id})
        check = "two-publishers" if len(pubs) >= 2 else "one-document" if len(g) == 1 else "same-publisher"
        rows.append(dict(period=period, geography=geo, segment=seg, measure=measure,
                         value=value, decimals=int(dec), value_basis="printed",
                         n_documents=len(g), n_publishers=len(pubs),
                         official_report="yes" if any(kind[s] == "official" for s in g.source_id) else "no",
                         source_check=check, source_ids=";".join(g.source_id)))
    t = pd.DataFrame(rows)
    t["pk"] = t.period.map(pkey)
    return t


def lookup(t, geo, seg, measure, k):
    r = t[(t.geography == geo) & (t.segment == seg) & (t.measure == measure) & (t.pk == k)]
    return None if r.empty else r.iloc[0]


def ratio_interval(a, b):
    """Percent change from b to a, as an interval."""
    lo_a, hi_a = interval(a.value, a.decimals)
    lo_b, hi_b = interval(b.value, b.decimals)
    return (lo_a / hi_b - 1) * 100, (hi_a / lo_b - 1) * 100


def identity_checks(t):
    out = []
    lev = t[t.measure == "level"]
    for _, a in lev.iterrows():
        for lag, measure in ((4, "yoy"), (1, "qoq")):
            b = lookup(t, a.geography, a.segment, "level", a.pk - lag)
            c = lookup(t, a.geography, a.segment, measure, a.pk)
            if b is None or c is None:
                continue
            implied = ratio_interval(a, b)
            ok = overlaps(implied, interval(c.value, c.decimals))
            out.append(dict(check=f"{measure} from levels", geography=a.geography, segment=a.segment,
                            period=a.period, printed=c.value,
                            implied_low=round(implied[0], 3), implied_high=round(implied[1], 3), passed=ok))
    q = t[t.measure == "qoq"]
    for _, y in t[(t.measure == "yoy") & (t.geography == "Saudi Arabia")].iterrows():
        parts = [lookup(t, y.geography, y.segment, "qoq", y.pk - i) for i in range(4)]
        if any(p is None for p in parts):
            continue
        lo = hi = 1.0
        for p in parts:
            a, b = interval(p.value, p.decimals)
            lo *= 1 + a / 100
            hi *= 1 + b / 100
        implied = ((lo - 1) * 100, (hi - 1) * 100)
        ok = overlaps(implied, interval(y.value, y.decimals))
        out.append(dict(check="yoy from four qoq", geography=y.geography, segment=y.segment,
                        period=y.period, printed=y.value,
                        implied_low=round(implied[0], 3), implied_high=round(implied[1], 3), passed=ok))
    return pd.DataFrame(out)


def derive_levels(t):
    """Index levels that are not printed but follow from a printed level and a printed change."""
    new = []
    def add(geo, seg, k, value, how):
        new.append(dict(period=pname(k), geography=geo, segment=seg, measure="level",
                        value=round(value, 2), decimals=2, value_basis="derived",
                        n_documents=0, n_publishers=0, official_report="no",
                        source_check="derived", source_ids=how, pk=k))
    # National Q3 2025: from Q4 2025 level and the Q4 2025 quarterly change
    k = pkey("Q3 2025")
    a = lookup(t, "Saudi Arabia", "all", "level", k + 1)
    c = lookup(t, "Saudi Arabia", "all", "qoq", k + 1)
    add("Saudi Arabia", "all", k, a.value / (1 + c.value / 100), "Q4 2025 level / (1 + Q4 2025 qoq)")
    # National Q2 2026: from Q1 2026 level and the Q2 2026 quarterly change
    k = pkey(LATEST)
    a = lookup(t, "Saudi Arabia", "all", "level", k - 1)
    c = lookup(t, "Saudi Arabia", "all", "qoq", k)
    add("Saudi Arabia", "all", k, a.value * (1 + c.value / 100), "Q1 2026 level x (1 + Q2 2026 qoq)")
    # Regions Q2 2026: from Q2 2025 level and the Q2 2026 annual change
    for _, y in t[(t.measure == "yoy") & (t.pk == k) & (t.geography != "Saudi Arabia")].iterrows():
        b = lookup(t, y.geography, "all", "level", k - 4)
        add(y.geography, "all", k, b.value * (1 + y.value / 100), "Q2 2025 level x (1 + Q2 2026 yoy)")
    d = pd.DataFrame(new)
    # cross-checks on the two national derivations
    q3 = d[(d.geography == "Saudi Arabia") & (d.period == "Q3 2025")].iloc[0].value
    alt = lookup(t, "Saudi Arabia", "all", "level", pkey("Q3 2024")).value * 1.013
    assert abs(q3 - alt) < 0.15, (q3, alt)
    q2 = d[(d.geography == "Saudi Arabia") & (d.period == LATEST)].iloc[0].value
    alt = lookup(t, "Saudi Arabia", "all", "level", pkey("Q2 2025")).value * 1.013
    assert abs(q2 - alt) < 0.15, (q2, alt)
    return d


def main():
    readings = pd.read_csv(RAW / "price_index_readings.csv", dtype={"value": str})
    readings["raw"] = readings["value"]
    readings["value"] = readings["value"].astype(float)
    sources = pd.read_csv(RAW / "sources.csv")
    assert set(readings.source_id) <= set(sources.source_id)
    assert not readings.duplicated(["period", "geography", "segment", "measure", "source_id"]).any()

    t = consolidate(readings, sources)
    checks = identity_checks(t)
    failed = checks[~checks.passed]
    assert failed.empty, f"identity checks failed:\n{failed}"
    t = pd.concat([t, derive_levels(t)], ignore_index=True)
    t["sector"] = t.segment.map(SECTOR).where(t.geography == "Saudi Arabia", "All")
    t["segment_label"] = t.segment.map(LABEL)
    t = t.sort_values(["measure", "geography", "segment", "pk"]).reset_index(drop=True)

    tidy = t[["period", "geography", "sector", "segment", "segment_label", "measure", "value",
              "value_basis", "n_documents", "n_publishers", "official_report", "source_check", "source_ids"]]
    tidy.to_csv(OUT / "price_index_tidy.csv", index=False)
    checks.to_csv(OUT / "identity_checks.csv", index=False)

    # national series
    nat = t[(t.geography == "Saudi Arabia") & (t.segment == "all")]
    wide = nat.pivot_table(index=["pk", "period"], columns="measure", values="value").reset_index()
    basis = nat[nat.measure == "level"].set_index("period").value_basis
    wide["level_basis"] = wide.period.map(basis)
    wide = wide.rename(columns={"level": "index_level", "yoy": "yoy_pct", "qoq": "qoq_pct"})
    wide = wide.sort_values("pk")[["period", "index_level", "level_basis", "yoy_pct", "qoq_pct"]]
    wide.to_csv(OUT / "national_index.csv", index=False)

    # segments, latest weights
    seg = t[(t.geography == "Saudi Arabia") & t.measure.isin(["yoy", "qoq"]) & (t.pk >= pkey("Q3 2024"))]
    sw = seg.pivot_table(index=["pk", "period", "sector", "segment", "segment_label"],
                         columns="measure", values="value").reset_index()
    chk = seg[seg.measure == "yoy"].set_index(["period", "segment"]).source_check
    sw["yoy_source_check"] = [chk.get((p, s), "") for p, s in zip(sw.period, sw.segment)]
    wt = t[(t.measure == "weight")].sort_values("pk").groupby("segment").value.last()
    sw["weight_pct"] = sw.segment.map(wt)
    sw.loc[sw.segment == "all", "weight_pct"] = 100.0
    sw = sw.rename(columns={"yoy": "yoy_pct", "qoq": "qoq_pct"}).sort_values(["pk", "segment"])
    sw[["period", "sector", "segment", "segment_label", "weight_pct", "yoy_pct", "qoq_pct",
        "yoy_source_check"]].to_csv(OUT / "segment_changes.csv", index=False)

    # regions
    reg = t[t.geography != "Saudi Arabia"]
    rw = reg.pivot_table(index=["pk", "period", "geography"], columns="measure", values="value").reset_index()
    lb = reg[reg.measure == "level"].set_index(["period", "geography"]).value_basis
    yc = reg[reg.measure == "yoy"].set_index(["period", "geography"]).source_check
    rw["level_basis"] = [lb.get((p, g), "") for p, g in zip(rw.period, rw.geography)]
    rw["yoy_source_check"] = [yc.get((p, g), "") for p, g in zip(rw.period, rw.geography)]
    rw = rw.rename(columns={"geography": "region", "level": "index_level", "yoy": "yoy_pct"})
    rw = rw.sort_values(["pk", "region"])
    rw[["period", "region", "index_level", "level_basis", "yoy_pct", "yoy_source_check"]].to_csv(
        OUT / "region_index.csv", index=False)

    # headline figures
    k = pkey(LATEST)
    def v(geo, seg, m, p=LATEST):
        return float(lookup(t, geo, seg, m, pkey(p)).value)
    s_latest = sw[sw.pk == k].set_index("segment")
    sub = s_latest.drop(index=["all", "residential", "commercial", "agricultural"])
    r_q1 = rw[(rw.period == "Q1 2026")].set_index("region")
    r_q3 = rw[(rw.period == "Q3 2024")].set_index("region")
    change_6q = ((r_q1.index_level / r_q3.index_level - 1) * 100).round(1)
    r_q2 = rw[(rw.period == LATEST) & rw.yoy_pct.notna()].set_index("region")
    head = {
        "national_level_q2_2026_derived": round(v("Saudi Arabia", "all", "level"), 2),
        "national_yoy_q2_2026": v("Saudi Arabia", "all", "yoy"),
        "national_qoq_q2_2026": v("Saudi Arabia", "all", "qoq"),
        "national_yoy_q4_2025": v("Saudi Arabia", "all", "yoy", "Q4 2025"),
        "national_yoy_q1_2026": v("Saudi Arabia", "all", "yoy", "Q1 2026"),
        "villa_yoy_q2_2026": v("Saudi Arabia", "villa", "yoy"),
        "villa_yoy_q1_2025": v("Saudi Arabia", "villa", "yoy", "Q1 2025"),
        "residential_land_yoy_q2_2026": v("Saudi Arabia", "residential_land", "yoy"),
        "apartment_yoy_q2_2026": v("Saudi Arabia", "apartment", "yoy"),
        "commercial_yoy_q2_2026": v("Saudi Arabia", "commercial", "yoy"),
        "residential_yoy_q2_2026": v("Saudi Arabia", "residential", "yoy"),
        "subsector_lowest_q2_2026": sub.yoy_pct.idxmin(),
        "subsector_highest_q2_2026": sub.yoy_pct.idxmax(),
        "regions_q1_2026_count": int(r_q1.yoy_pct.notna().sum()),
        "regions_q1_2026_rising": int((r_q1.yoy_pct > 0).sum()),
        "region_q1_2026_highest": r_q1.yoy_pct.idxmax(),
        "region_q1_2026_highest_pct": float(r_q1.yoy_pct.max()),
        "region_q1_2026_lowest": r_q1.yoy_pct.idxmin(),
        "region_q1_2026_lowest_pct": float(r_q1.yoy_pct.min()),
        "regions_q2_2026_published": int(len(r_q2)),
        "region_q2_2026_highest": r_q2.yoy_pct.idxmax(),
        "region_q2_2026_highest_pct": float(r_q2.yoy_pct.max()),
        "region_q2_2026_lowest": r_q2.yoy_pct.idxmin(),
        "region_q2_2026_lowest_pct": float(r_q2.yoy_pct.min()),
        "riyadh_level_q3_2024": float(r_q3.loc["Riyadh", "index_level"]),
        "riyadh_level_q1_2026": float(r_q1.loc["Riyadh", "index_level"]),
        "riyadh_yoy_q2_2026": float(r_q2.loc["Riyadh", "yoy_pct"]),
        "change_6q_highest_region": change_6q.idxmax(),
        "change_6q_highest_pct": float(change_6q.max()),
        "change_6q_lowest_region": change_6q.idxmin(),
        "change_6q_lowest_pct": float(change_6q.min()),
        "identity_checks_run": int(len(checks)),
        "readings": int(len(readings)),
        "readings_set_aside": int(readings.note.fillna("").str.startswith("set aside").sum()),
    }
    pd.Series(head, name="value").rename_axis("measure").to_csv(OUT / "headline_figures.csv")
    for k_, v_ in head.items():
        print(f"{k_:36s} {v_}")


if __name__ == "__main__":
    main()
