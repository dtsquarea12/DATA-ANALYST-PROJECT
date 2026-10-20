"""Draw the project charts from the tables in data/processed.

Run from the project folder:  python scripts/make_charts.py
"""
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.lines import Line2D
from matplotlib.ticker import MultipleLocator

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data", "processed")
IMG = os.path.join(HERE, "..", "images")
os.makedirs(IMG, exist_ok=True)

BLUE, LIGHT, ORANGE, GREY = "#2a78d6", "#9fc3ec", "#eb6834", "#b9b7b1"
INK, SECOND, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#898781", "#e4e3df", "#fcfcfb"
SOURCE = ("Analysis: Toheeb Adeboye. Source: General Authority for Statistics (GASTAT), Saudi Arabia, Real Estate Price Index "
          "(base 2023 = 100), quarterly releases, with figures confirmed in\nArgaam, Enterprise, Arab News, Okaz, Amlak, "
          "Riyadh Daily, Economy Middle East and Trading Economics. The index measures prices of property sold, "
          "not rents.")

fonts = {f.name for f in font_manager.fontManager.ttflist}
plt.rcParams.update({
    "font.family": "Inter" if "Inter" in fonts else "DejaVu Sans",
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False, "axes.spines.bottom": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
    "xtick.color": SECOND, "ytick.color": SECOND, "xtick.labelsize": 11, "ytick.labelsize": 11.5,
    "xtick.major.size": 0, "ytick.major.size": 0, "axes.axisbelow": True,
})

seg = pd.read_csv(os.path.join(DATA, "segment_changes.csv"))
reg = pd.read_csv(os.path.join(DATA, "region_index.csv"))
nat = pd.read_csv(os.path.join(DATA, "national_index.csv"))
head = pd.read_csv(os.path.join(DATA, "headline_figures.csv")).set_index("measure")["value"]
SECTORS = ["all", "residential", "commercial", "agricultural"]


def frame(fig, title, subtitle, foot, gap=0.098):
    fig.text(0.04, 0.965, title, fontsize=21, fontweight="bold", color=INK, va="top", linespacing=1.12)
    fig.text(0.04, 0.965 - gap, subtitle, fontsize=12, color=SECOND, va="top", linespacing=1.45)
    fig.text(0.04, 0.02, foot, fontsize=9, color=MUTED, va="bottom", linespacing=1.4)


def pct(v):
    return f"{v:+.1f}%".replace("+0.0", "0.0")


def subsector_chart():
    """LinkedIn headline chart: annual change by property type, Q2 2026."""
    d = seg[(seg.period == "Q2 2026") & ~seg.segment.isin(SECTORS)].sort_values("yoy_pct")
    allp = seg[(seg.period == "Q2 2026") & (seg.segment == "all")].yoy_pct.iloc[0]
    fig, ax = plt.subplots(figsize=(13.33, 8.6), dpi=150)
    fig.subplots_adjust(left=0.29, right=0.95, top=0.76, bottom=0.17)
    ax.grid(axis="y", visible=False)
    y = range(len(d))
    colors = [ORANGE if v < 0 else BLUE for v in d.yoy_pct]
    ax.barh(list(y), d.yoy_pct, color=colors, height=0.66)
    for i, (v, w) in enumerate(zip(d.yoy_pct, d.weight_pct)):
        ax.text(v + (0.3 if v >= 0 else -0.3), i, pct(v), va="center", ha="left" if v >= 0 else "right",
                fontsize=12.5, fontweight="bold", color=INK)
    labels = [f"{l}  ({w:.1f}% of index)"
              for l, w in zip(d.segment_label, d.weight_pct)]
    ax.set_yticks(list(y))
    ax.set_yticklabels(labels, fontsize=12)
    ax.axvline(0, color=SECOND, linewidth=1)
    ax.axvline(allp, color=MUTED, linewidth=1, linestyle=(0, (4, 3)))
    ax.text(allp + 0.2, len(d) - 0.35, f"All property {pct(allp)}", fontsize=10.5, color=SECOND, va="center")
    ax.set_xlim(-13, 14.5)
    ax.xaxis.set_major_formatter(lambda v, p: f"{v:+.0f}%".replace("+0%", "0%"))
    frame(fig, f"Saudi villa prices fell {abs(float(head['villa_yoy_q2_2026'])):.1f}% in a year, while residential land\n"
               f"rose {float(head['residential_land_yoy_q2_2026']):.1f}%",
          "Change in the GASTAT Real Estate Price Index by property type, Q2 2026 against Q2 2025, %. "
          "Weights are each type's share of\nthe national index. The whole index rose 1.3%, after falls of 0.7% "
          "and 1.6% in the two quarters before.",
          SOURCE + "\nAll changes on this chart are printed in at least two publications of the same GASTAT release. The villa, apartment, floor, building, "
          "shop and agricultural weights rest on one article (Argaam).")
    fig.savefig(os.path.join(IMG, "saudi-property-prices-by-type.png"), dpi=150)
    plt.close(fig)


def trend_chart():
    """Annual change for the three largest residential types, Q3 2024 to Q2 2026."""
    periods = list(dict.fromkeys(seg[seg.segment == "all"].period))
    fig, ax = plt.subplots(figsize=(13.33, 7.5), dpi=150)
    fig.subplots_adjust(left=0.07, right=0.86, top=0.76, bottom=0.2)
    ax.grid(axis="x", visible=False)
    style = {"villa": (ORANGE, "Villas"), "residential_land": (BLUE, "Residential land"),
             "apartment": (LIGHT, "Apartments"), "all": (GREY, "All property")}
    for s, (c, lab) in style.items():
        d = seg[seg.segment == s].set_index("period").reindex(periods)
        ax.plot(range(len(periods)), d.yoy_pct, color=c, linewidth=3 if s != "all" else 2,
                linestyle="-" if s != "all" else (0, (4, 3)), marker="o", markersize=6)
        last = d.yoy_pct.iloc[-1]
        off = {"villa": 0, "residential_land": 0, "apartment": -0.45, "all": 0.45}[s]
        ax.text(len(periods) - 1 + 0.15, last + off, f"{lab} {pct(last)}", color=c if s != "apartment" else "#5f97d6",
                fontsize=11.5, fontweight="bold", va="center")
    ax.axhline(0, color=SECOND, linewidth=1)
    ax.set_xticks(range(len(periods)))
    ax.set_xticklabels(periods)
    ax.yaxis.set_major_locator(MultipleLocator(2))
    ax.yaxis.set_major_formatter(lambda v, p: f"{v:+.0f}%".replace("+0%", "0%"))
    frame(fig, "Villas went from the fastest-rising home type to the fastest-falling in five quarters",
          "Change on the same quarter a year earlier, GASTAT Real Estate Price Index, Saudi Arabia, Q3 2024 to Q2 2026, %.",
          SOURCE, gap=0.075)
    fig.savefig(os.path.join(IMG, "residential-types-trend.png"), dpi=150)
    plt.close(fig)


def region_chart():
    """Annual change by region: Q1 2026 for all 13, Q2 2026 where published."""
    q1 = reg[reg.period == "Q1 2026"].set_index("region")
    q2 = reg[(reg.period == "Q2 2026") & reg.yoy_pct.notna()].set_index("region")
    d = q1.sort_values("yoy_pct")
    fig, ax = plt.subplots(figsize=(13.33, 8.6), dpi=150)
    fig.subplots_adjust(left=0.15, right=0.95, top=0.76, bottom=0.17)
    ax.grid(axis="y", visible=False)
    y = list(range(len(d)))
    ax.barh(y, d.yoy_pct, color=[ORANGE if v < 0 else BLUE for v in d.yoy_pct], height=0.6, alpha=0.9)
    for i, (r, v) in enumerate(d.yoy_pct.items()):
        ax.text(v + 0.25 if v >= 0 else -12.3, i, pct(v), va="center", ha="left",
                fontsize=11, color=INK if v >= 0 else "#b4471d", fontweight="bold")
        if r in q2.index:
            ax.plot(q2.loc[r, "yoy_pct"], i, marker="D", markerfacecolor=SURFACE, markeredgecolor=INK, markeredgewidth=2, markersize=9, linestyle="none", zorder=5)
    ax.set_yticks(y)
    ax.set_yticklabels(d.index, fontsize=12)
    ax.axvline(0, color=SECOND, linewidth=1)
    ax.set_xlim(-12.5, 12)
    ax.xaxis.set_major_formatter(lambda v, p: f"{v:+.0f}%".replace("+0%", "0%"))
    ax.legend(handles=[Line2D([], [], color=BLUE, linewidth=10, label="Q1 2026 (all 13 regions)"),
                       Line2D([], [], marker="D", markerfacecolor=SURFACE, markeredgecolor=INK, markeredgewidth=2, linestyle="none", markersize=9,
                              label="Q2 2026 (8 regions named in reports)")],
              loc="lower right", frameon=False, fontsize=11)
    frame(fig, "Property prices moved in opposite directions across Saudi regions",
          "Change in the GASTAT Real Estate Price Index by administrative region, on the same quarter a year earlier, %.\n"
          "Q2 2026 regional figures were reported for 8 of the 13 regions only.",
          SOURCE, gap=0.075)
    fig.savefig(os.path.join(IMG, "regions-annual-change.png"), dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    subsector_chart()
    trend_chart()
    region_chart()
    print("charts written to", os.path.abspath(IMG))
