"""Draw the project charts from the tables in data/processed.

Run from the project folder:  python scripts/make_charts.py
"""
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data", "processed")
IMG = os.path.join(HERE, "..", "images")
os.makedirs(IMG, exist_ok=True)

BLUE, LIGHT, ORANGE, GREY = "#2a78d6", "#9fc3ec", "#eb6834", "#a9a7a1"
INK, SECOND, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#898781", "#e4e3df", "#fcfcfb"
SOURCE = ("Analysis: Toheeb Adeboye. Source: Central Bank of Egypt figures as reported by Ahram Online, Zawya, "
          "Daily News Egypt, Enterprise, AGBI,\nBusiness Today Egypt, Amwal Al Ghad and others; each total confirmed "
          "in two publishers except FY2018/19 (one document plus a rounded second).\nRemittances from Egyptians "
          "working abroad, US dollars. Egypt's fiscal year runs from July to June.")

QSOURCE = ("Analysis: Toheeb Adeboye. Source: Central Bank of Egypt figures as reported by Amwal Al Ghad, Ahram "
           "Online, AGBI, Business Today Egypt, Daily News Egypt,\nEnterprise and WeeTracker. April to June 2019 rests "
           "on one document. April to June 2026 = FY 2025/26 total ($47.3bn) minus July to March ($34.9bn,\none "
           "document). US$ billion.")

fonts = {f.name for f in font_manager.fontManager.ttflist}
plt.rcParams.update({
    "font.family": "Inter" if "Inter" in fonts else "DejaVu Sans",
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False, "axes.spines.bottom": False,
    "axes.grid": True, "axes.grid.axis": "y", "grid.color": GRID, "grid.linewidth": 0.8,
    "xtick.color": SECOND, "ytick.color": MUTED, "xtick.labelsize": 11.5, "ytick.labelsize": 10.5,
    "xtick.major.size": 0, "ytick.major.size": 0, "axes.axisbelow": True,
})

fy = pd.read_csv(os.path.join(DATA, "fiscal_year_series.csv"))
tidy = pd.read_csv(os.path.join(DATA, "remittances_tidy.csv"))
derived = pd.read_csv(os.path.join(DATA, "derived_figures.csv"))


def frame(fig, title, subtitle, foot, gap=0.098):
    fig.text(0.04, 0.965, title, fontsize=21, fontweight="bold", color=INK, va="top", linespacing=1.12)
    fig.text(0.04, 0.965 - gap, subtitle, fontsize=12, color=SECOND, va="top", linespacing=1.45)
    fig.text(0.04, 0.02, foot, fontsize=9, color=MUTED, va="bottom", linespacing=1.4)


def fiscal_year_chart():
    """LinkedIn headline chart: remittances by fiscal year."""
    last, low = fy.iloc[-1], fy.loc[fy.period == "FY2023/24"].iloc[0]
    assert last.value_usd_bn == fy.value_usd_bn.max(), "latest year is no longer the record"
    fig, ax = plt.subplots(figsize=(13.33, 8.6), dpi=150)
    fig.subplots_adjust(left=0.07, right=0.97, top=0.76, bottom=0.2)
    colors = [BLUE if p == last.period else (ORANGE if p == low.period else LIGHT) for p in fy.period]
    x = range(len(fy))
    ax.bar(list(x), fy.value_usd_bn, color=colors, width=0.66)
    for xx, v in zip(x, fy.value_usd_bn):
        ax.text(xx, v + 0.7, f"${v:.1f}bn", ha="center", fontsize=12.5, color=INK, fontweight="bold")
    ax.set_xticks(list(x))
    ax.set_xticklabels([p.replace("FY", "FY ") for p in fy.period])
    ax.set_ylim(0, 54)
    ax.set_yticks(range(0, 51, 10))
    ax.yaxis.set_major_formatter(lambda v, p: f"${v:.0f}bn")
    mult = last.value_usd_bn / low.value_usd_bn
    ax.text(len(fy) - 2, 44.5, f"FY 2025/26 is {mult:.1f} times\nthe FY 2023/24 total", fontsize=11.5,
            color=SECOND, ha="center", va="center")
    frame(fig, f"Egyptians abroad sent home a record ${last.value_usd_bn:.1f} billion in FY 2025/26,\n"
               f"more than twice the total two years earlier",
          "Remittances from Egyptians working abroad by fiscal year (July to June), US$ billion, "
          "FY 2018/19 to FY 2025/26.", SOURCE)
    fig.savefig(os.path.join(IMG, "egypt-remittances-chart.png"), dpi=150)
    plt.close(fig)


def quarter_chart():
    """April to June quarter in each year, from published quarters and one derived quarter."""
    q = tidy[tidy.measure == "quarter"][["period", "value_usd_bn"]].copy()
    q["kind"] = "published"
    d = derived[derived.period == "Apr-Jun 2026"][["period", "value_usd_bn"]].assign(kind="derived")
    q = pd.concat([q, d, pd.DataFrame([{"period": "Apr-Jun 2023", "value_usd_bn": None, "kind": "missing"}])])
    q["year"] = q.period.str[-4:].astype(int)
    q = q.sort_values("year").reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(13.33, 7.5), dpi=150)
    fig.subplots_adjust(left=0.07, right=0.97, top=0.76, bottom=0.2)
    for i, r in q.iterrows():
        if r.kind == "missing":
            ax.text(i, 0.6, "not found", ha="center", fontsize=10.5, color=MUTED)
            continue
        ax.bar(i, r.value_usd_bn, color=BLUE if r.kind == "derived" else LIGHT, width=0.66,
               hatch="//" if r.kind == "derived" else None, edgecolor=SURFACE)
        ax.text(i, r.value_usd_bn + 0.2, f"${r.value_usd_bn:.1f}bn", ha="center", fontsize=12, color=INK)
    ax.set_xticks(range(len(q)))
    ax.set_xticklabels([f"Apr-Jun\n{y}" for y in q.year])
    ax.set_ylim(0, 14)
    ax.yaxis.set_major_formatter(lambda v, p: f"${v:.0f}bn")
    frame(fig, "The April to June quarter has almost doubled since 2019",
          "Remittances in the last quarter of each fiscal year, US$ billion. 2026 is derived: FY 2025/26 total "
          "minus July to March.\nNo published figure for April to June 2023 was found.", QSOURCE)
    fig.savefig(os.path.join(IMG, "april-june-quarter.png"), dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    fiscal_year_chart()
    quarter_chart()
    print("charts written to images/")
