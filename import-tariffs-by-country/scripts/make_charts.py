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
SOURCE = ("Analysis: Toheeb Adeboye. Source: WTO, ITC and UNCTAD, World Tariff Profiles 2026, summary table "
          "\"All products\" (152 economies, 132 with an applied average).\nSimple average of MFN applied tariff rates "
          "across all tariff lines, 2025 (2024 for 12 economies). Preferential rates under trade agreements are not "
          "included.")

fonts = {f.name for f in font_manager.fontManager.ttflist}
plt.rcParams.update({
    "font.family": "Inter" if "Inter" in fonts else "DejaVu Sans",
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False, "axes.spines.bottom": False,
    "axes.grid": True, "axes.grid.axis": "x", "grid.color": GRID, "grid.linewidth": 0.8,
    "xtick.color": MUTED, "ytick.color": SECOND, "xtick.labelsize": 10.5, "ytick.labelsize": 11.5,
    "xtick.major.size": 0, "ytick.major.size": 0, "axes.axisbelow": True,
})

me = pd.read_csv(os.path.join(DATA, "middle_east.csv"))
summ = pd.read_csv(os.path.join(DATA, "region_summary.csv"))
world = summ[(summ.region == "World") & (summ.basis == "EU counted once")].iloc[0]
SUB_ORDER = ["Gulf", "Levant and Iraq", "Iran, Turkey and Yemen", "North Africa"]
SUB_LABEL = {"Gulf": "Gulf", "Levant and Iraq": "Levant", "Iran, Turkey and Yemen": "Turkey",
             "North Africa": "North Africa"}


def frame(fig, title, subtitle, foot, gap=0.058):
    fig.text(0.04, 0.965, title, fontsize=21, fontweight="bold", color=INK, va="top", linespacing=1.12)
    fig.text(0.04, 0.965 - gap, subtitle, fontsize=12, color=SECOND, va="top", linespacing=1.45)
    fig.text(0.04, 0.02, foot, fontsize=9, color=MUTED, va="bottom", linespacing=1.4)


def middle_east_chart():
    """LinkedIn headline chart: applied tariff average of the 12 Middle East economies with a figure."""
    m = me[me.mfn_applied_avg.notna()].copy()
    gulf = m[m.sub_region == "Gulf"]
    assert gulf.mfn_applied_avg.max() < world["median"], "a Gulf state is no longer below the world median"
    ypos, labels, heads, y, prev = [], [], [], 0, None
    for _, r in m.iterrows():
        if r.sub_region != prev:
            if prev is not None:
                y += 0.7
            heads.append((y, SUB_LABEL[r.sub_region]))
            y += 0.8
            prev = r.sub_region
        ypos.append(y)
        y += 1
    fig, ax = plt.subplots(figsize=(13.33, 9.6), dpi=150)
    fig.subplots_adjust(left=0.2, right=0.93, top=0.8, bottom=0.14)
    colors = [BLUE if s == "Gulf" else LIGHT for s in m.sub_region]
    ax.barh(ypos, m.mfn_applied_avg, color=colors, height=0.68)
    for yy, v in zip(ypos, m.mfn_applied_avg):
        ax.text(v + 0.25, yy, f"{v:.1f}%", va="center", fontsize=11.5, color=INK)
    ax.set_yticks(ypos)
    ax.set_yticklabels(m.country)
    for yy, h in heads:
        ax.text(-0.01, yy, h.upper(), transform=ax.get_yaxis_transform(), ha="right", va="center", fontsize=10,
                fontweight="bold", color=MUTED)
    ax.axvline(world["median"], color=ORANGE, lw=1.8, ls="--")
    ax.text(world["median"] + 0.2, -0.9, f"World median {world['median']:.1f}% ({int(world['economies'])} economies)",
            color=ORANGE, fontsize=11, va="center")
    ax.set_ylim(y, -1.6)
    ax.set_xlim(0, 22)
    ax.set_xticks(range(0, 21, 2))
    ax.xaxis.set_major_formatter(lambda v, p: f"{v:.0f}%")
    frame(fig, "Every Gulf state charges about 5% on a typical import,\nbelow the world median of 7.7%",
          "Simple average MFN applied import tariff, all products, 2025. Middle East economies in the WTO table. "
          "Egypt and Yemen\nhave no applied figure in this edition; Algeria, Iran, Iraq, Lebanon, Palestine and "
          "Syria are not in the table.", SOURCE, gap=0.098)
    fig.savefig(os.path.join(IMG, "middle-east-import-tariffs-chart.png"), dpi=150)
    plt.close(fig)


def region_chart():
    """Median applied tariff by region, Middle East first."""
    s = summ[(summ.basis == "EU counted once") & (summ.region != "Gulf (6)")].copy()
    fig, ax = plt.subplots(figsize=(13.33, 7.5), dpi=150)
    fig.subplots_adjust(left=0.17, right=0.93, top=0.78, bottom=0.17)
    y = range(len(s))
    colors = [BLUE if r == "Middle East" else (ORANGE if r == "World" else LIGHT) for r in s.region]
    ax.barh(list(y), s["median"], color=colors, height=0.66)
    for yy, (v, n) in enumerate(zip(s["median"], s.economies)):
        ax.text(v + 0.15, yy, f"{v:.2f}%  ({n} economies)", va="center", fontsize=11, color=INK)
    ax.set_yticks(list(y))
    ax.set_yticklabels(s.region)
    ax.set_ylim(len(s) - 0.4, -0.6)
    ax.set_xlim(0, 16)
    ax.set_xticks(range(0, 15, 2))
    ax.xaxis.set_major_formatter(lambda v, p: f"{v:.0f}%")
    frame(fig, "Median applied import tariff by region",
          "Median of economy averages, all products, 2025. Each economy counts once; the European Union is one "
          "entry.", SOURCE)
    fig.savefig(os.path.join(IMG, "import-tariffs-by-region.png"), dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    middle_east_chart()
    region_chart()
    print("charts written to images/")
