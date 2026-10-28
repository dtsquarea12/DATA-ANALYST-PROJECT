"""Build the processed tables for the AI productivity at work project.

Reads every printed reading in data/raw/effect_readings.csv (one row per figure per document),
checks that documents agree within rounding, keeps the most precise reading, tests the
identities the studies print, and writes data/processed/. Fails if two documents disagree.
"""
from decimal import Decimal
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)
KEY = ["study_id", "version", "measure", "group"]


def interval(printed: str):
    """A figure printed to d decimals stands for anything within half a unit of its last digit."""
    d = Decimal(printed)
    half = Decimal(5) * Decimal(10) ** (d.as_tuple().exponent - 1)
    return d - half, d + half


def build():
    raw = pd.read_csv(RAW / "effect_readings.csv", dtype={"value_printed": str}).fillna({"note": ""})
    studies = pd.read_csv(RAW / "studies.csv")
    sources = pd.read_csv(RAW / "sources.csv")
    assert not raw.duplicated(KEY + ["source_id"]).any(), "duplicate reading"
    assert set(raw.source_id) <= set(sources.source_id), "reading cites an unknown source"
    assert set(raw.study_id) == set(studies.study_id), "study list does not match readings"

    used = raw[~raw.note.str.startswith("set_aside")]
    rows = []
    for key, g in used.groupby(KEY, sort=False):
        lo = max(interval(v)[0] for v in g.value_printed)
        hi = min(interval(v)[1] for v in g.value_printed)
        if lo > hi:
            raise ValueError(f"documents disagree for {key}: {list(g.value_printed)}")
        best = max(g.value_printed, key=lambda v: -Decimal(v).as_tuple().exponent)
        n = g.source_id.nunique()
        rows.append(dict(zip(KEY, key), value=float(best), n_sources=n,
                         verification="two-or-more-documents" if n >= 2 else "one-document",
                         source_ids=";".join(g.source_id),
                         note=next((x for x in g.note if x), "")))
    tidy = pd.DataFrame(rows)
    tidy.to_csv(OUT / "effects_tidy.csv", index=False)

    def v(study, measure, group, version=None):
        t = tidy[(tidy.study_id == study) & (tidy.measure == measure) & (tidy["group"] == group)]
        if version:
            t = t[t.version == version]
        assert len(t) == 1, (study, measure, group, version)
        return t.value.iloc[0]

    # Identity 1: the coding test prints 55.8% less time and the two group means.
    with_ai, without_ai = v("coding_test", "minutes_to_complete", "with_ai"), v("coding_test", "minutes_to_complete", "without_ai")
    cut = 100 * (without_ai - with_ai) / without_ai
    assert round(cut, 1) == -v("coding_test", "time_change_pct", "all"), cut
    # Identity 2: St. Louis Fed prints 5.4% of hours and about 2.2 hours of a 40-hour week.
    assert round(v("us_survey", "time_saved_share_of_hours_pct", "ai_users") * 40 / 100, 1) == v("us_survey", "hours_saved_per_40h_week", "ai_users")

    # One headline row per study: the main measured effect, written as a gain.
    spec = [
        ("coding_test", "time_change_pct", "all", None, "less time on one coding task", -1),
        ("writing", "time_change_pct", "all", None, "less time per writing task", -1),
        ("developers_field", "tasks_completed_change_pct", "all", None, "more tasks completed per week", 1),
        ("consulting", "speed_gain_pct", "all", None, "faster on consulting tasks", 1),
        ("support", "resolutions_per_hour_change_pct", "all", "QJE 2025", "more chats resolved per hour", 1),
        ("us_survey", "time_saved_share_of_hours_pct", "ai_users", None, "of work hours saved, US workers using AI", 1),
        ("denmark", "time_saved_share_of_hours_pct", "ai_users", None, "of work hours saved, Danish workers using AI", 1),
    ]
    head = []
    for study, m, g, ver, label, sign in spec:
        row = tidy[(tidy.study_id == study) & (tidy.measure == m) & (tidy["group"] == g)]
        if ver:
            row = row[row.version == ver]
        r = row.iloc[0]
        s = studies.set_index("study_id").loc[study]
        n = v(study, "sample_size", "all", ver) if ((tidy.study_id == study) & (tidy.measure == "sample_size")).any() else None
        head.append(dict(study_id=study, study=s.study, published=s.published, scope=s.scope, design=s.design,
                         measure=m, effect_label=label, gain_pct=sign * r.value, sample_size=n,
                         verification=r.verification, n_sources=r.n_sources))
    head = pd.DataFrame(head)
    head.to_csv(OUT / "study_headlines.csv", index=False)

    # Least versus most experienced staff, where a study prints both or a range.
    exp = pd.DataFrame([
        dict(study_id="consulting", study="Consultants (graded performance)", least_low=v("consulting", "performance_change_pct", "least_experienced"),
             least_high=v("consulting", "performance_change_pct", "least_experienced"), most_low=v("consulting", "performance_change_pct", "most_experienced"),
             most_high=v("consulting", "performance_change_pct", "most_experienced"), note="below-average vs top performers"),
        dict(study_id="developers_field", study="Software developers (tasks per week)", least_low=v("developers_field", "tasks_completed_change_pct_low", "least_experienced"),
             least_high=v("developers_field", "tasks_completed_change_pct_high", "least_experienced"), most_low=v("developers_field", "tasks_completed_change_pct_low", "most_experienced"),
             most_high=v("developers_field", "tasks_completed_change_pct_high", "most_experienced"), note="recent hires and juniors vs seniors; ranges across the three experiments"),
        dict(study_id="support", study="Customer support (chats per hour)", least_low=v("support", "resolutions_per_hour_change_pct", "least_experienced", "QJE 2025"),
             least_high=v("support", "resolutions_per_hour_change_pct", "least_experienced", "QJE 2025"), most_low=None, most_high=None,
             note="most experienced: 'small gains in speed and small declines in quality', no figure printed"),
    ])
    exp.to_csv(OUT / "gain_by_experience.csv", index=False)

    task = head[head.scope != "whole job"].gain_pct
    job = head[head.scope == "whole job"].gain_pct
    figures = {
        "task_gain_min_pct": task.min(), "task_gain_max_pct": task.max(),
        "whole_job_saving_min_pct": job.min(), "whole_job_saving_max_pct": job.max(),
        "support_gain_all_pct": v("support", "resolutions_per_hour_change_pct", "all", "QJE 2025"),
        "support_gain_least_experienced_pct": v("support", "resolutions_per_hour_change_pct", "least_experienced", "QJE 2025"),
        "consulting_least_pct": v("consulting", "performance_change_pct", "least_experienced"),
        "consulting_most_pct": v("consulting", "performance_change_pct", "most_experienced"),
        "consulting_outside_frontier_pts": v("consulting", "correct_answer_change_pts", "outside_frontier"),
        "coding_minutes_with_ai": with_ai, "coding_minutes_without_ai": without_ai,
        "coding_time_cut_pct_recomputed": round(cut, 2),
        "us_all_workers_saving_pct": v("us_survey", "time_saved_share_of_hours_pct", "all_workers"),
        "readings": len(raw), "readings_set_aside": int(raw.note.str.startswith("set_aside").sum()),
        "figures": len(tidy), "figures_two_or_more_documents": int((tidy.n_sources >= 2).sum()),
    }
    pd.Series(figures, name="value").rename_axis("figure").to_csv(OUT / "headline_figures.csv")
    return tidy, head, exp, figures


if __name__ == "__main__":
    tidy, head, exp, figures = build()
    print(head[["study_id", "gain_pct", "effect_label", "verification"]].to_string(index=False))
    for k, x in figures.items():
        print(k, x)
