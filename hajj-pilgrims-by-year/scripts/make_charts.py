"""Draw the project charts from the tables in data/processed.

Run from the project folder:  python scripts/make_charts.py
"""
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Patch

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data", "processed")
IMG = os.path.join(HERE, "..", "images")
os.makedirs(IMG, exist_ok=True)

BLUE, LIGHT, ORANGE = "#2a78d6", "#9fc3ec", "#eb6834"
INK, SECOND, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#898781", "#e4e3df", "#fcfcfb"
SOURCE = ("Analysis: Toheeb Adeboye. Source: General Authority for Statistics (GASTAT), Saudi Arabia, Hajj releases and "
          "publications, with figures confirmed in Qatar Tribune, Argaam,\nGulf News, Africanews, Al Arabiya, Saudipedia and "
          "hajj.to. 2020 and 2021 are left out: those seasons were limited to residents because of COVID-19.\n"
          "2008 to 2011 and 2013 to 2015 splits rest on two Argaam articles (same publisher); 2023 split on one compilation "
          "plus a rounded second.")

fonts = {f.name for f in font_manager.fontManager.ttflist}
plt.rcParams.update({
    "font.family": "Inter" if "Inter" in fonts else "DejaVu Sans",
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False, "axes.spines.bottom": False,
    "axes.grid": True, "axes.grid.axis": "y", "grid.color": GRID, "grid.linewidth": 0.8,
    "xtick.color": SECOND, "ytick.color": MUTED, "xtick.labelsize": 11.5, "ytick.labelsize": 10.5,
    "xtick.major.size": 0, "ytick.major.size": 0, "axes.axisbelow": True,
})

s = pd.read_csv(os.path.join(DATA, "pilgrims_by_year.csv"))
head = pd.read_csv(os.path.join(DATA, "headline_figures.csv")).set_index("figure")["value"]


def frame(fig, title, subtitle, foot, gap=0.098):
    fig.text(0.04, 0.965, title, fontsize=21, fontweight="bold", color=INK, va="top", linespacing=1.12)
    fig.text(0.04, 0.965 - gap, subtitle, fontsize=12, color=SECOND, va="top", linespacing=1.45)
    fig.text(0.04, 0.02, foot, fontsize=9, color=MUTED, va="bottom", linespacing=1.4)


def positions():
    # leave one empty slot for the 2020 and 2021 gap
    pos, x = [], 0
    for y in s.year:
        if y == 2022:
            x += 1
        pos.append(x)
        x += 1
    return pos


def stacked_chart():
    """LinkedIn headline chart: pilgrims from abroad and from inside Saudi Arabia by season."""
    pos = positions()
    fig, ax = plt.subplots(figsize=(13.33, 8.6), dpi=150)
    fig.subplots_adjust(left=0.07, right=0.97, top=0.76, bottom=0.22)
    ext = s.external / 1e6
    inn = s.internal / 1e6
    ax.bar(pos, ext, color=BLUE, width=0.7)
    ax.bar(pos, inn, bottom=ext, color=ORANGE, width=0.7)
    for p, y, t in zip(pos, s.year, s.total / 1e6):
        if y in (2012, 2019, 2026):
            ax.text(p, t + 0.05, f"{t:.2f}m", ha="center", fontsize=11.5, color=INK, fontweight="bold")
    gap = pos[list(s.year).index(2022)] - 1
    ax.text(gap, 0.12, "2020-21\nCOVID-19\nseasons\nnot shown", ha="center", fontsize=9, color=MUTED)
    ax.set_xticks(pos)
    ax.set_xticklabels([str(y) for y in s.year], rotation=0, fontsize=10.5)
    ax.set_ylim(0, 3.5)
    ax.yaxis.set_major_formatter(lambda v, p: f"{v:.1f}m")
    ax.legend(handles=[Patch(color=BLUE, label="From abroad"), Patch(color=ORANGE, label="From inside Saudi Arabia")],
              loc="upper right", frameon=False, fontsize=11.5)
    r26, r19 = s.set_index("year").loc[2026], s.set_index("year").loc[2019]
    frame(fig, f"Hajj 2026: pilgrims from abroad were at {head['external_2026_pct_of_2019']:.0f}% of the 2019 level,\n"
               f"pilgrims from inside Saudi Arabia at {head['internal_2026_pct_of_2019']:.0f}%",
          f"Number of Hajj pilgrims by season, millions, 2008 to 2026. In 2026: {r26.external:,.0f} from abroad, "
          f"{r26.internal:,.0f} from inside Saudi Arabia\n(citizens and residents), {r26.total:,.0f} in total.",
          SOURCE)
    fig.savefig(os.path.join(IMG, "hajj-pilgrims-chart.png"), dpi=150)
    plt.close(fig)


def share_chart():
    """Share of pilgrims who came from inside Saudi Arabia."""
    pos = positions()
    fig, ax = plt.subplots(figsize=(13.33, 7.5), dpi=150)
    fig.subplots_adjust(left=0.07, right=0.97, top=0.76, bottom=0.2)
    pre = s.year <= 2019
    ax.plot([p for p, k in zip(pos, pre) if k], s.internal_share_pct[pre], color=ORANGE, lw=2.5, marker="o")
    ax.plot([p for p, k in zip(pos, pre) if not k], s.internal_share_pct[~pre], color=ORANGE, lw=2.5, marker="o")
    for p, y, v in zip(pos, s.year, s.internal_share_pct):
        if y in (2008, 2012, 2019, 2022, 2026):
            ax.text(p, v + 1.6, f"{v:.1f}%", ha="center", fontsize=11.5, color=INK, fontweight="bold")
    ax.set_xticks(pos)
    ax.set_xticklabels([str(y) for y in s.year], fontsize=10.5)
    ax.set_ylim(0, 50)
    ax.yaxis.set_major_formatter(lambda v, p: f"{v:.0f}%")
    frame(fig, "Fewer than 1 in 10 Hajj pilgrims in 2026 came from inside Saudi Arabia",
          "Pilgrims from inside Saudi Arabia (citizens and residents) as a share of all pilgrims, percent, "
          "2008 to 2026. 2020 and 2021 not shown.", SOURCE)
    fig.savefig(os.path.join(IMG, "internal-share.png"), dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    stacked_chart()
    share_chart()
    print("charts written to images/")
