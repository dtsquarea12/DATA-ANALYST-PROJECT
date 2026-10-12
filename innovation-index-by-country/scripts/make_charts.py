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

BLUE, LIGHT, ORANGE, TEAL, GREY = "#2a78d6", "#9fc3ec", "#eb6834", "#1f9d8a", "#a9a7a1"
INK, SECOND, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#898781", "#e4e3df", "#fcfcfb"
SOURCE = ("Analysis: Toheeb Adeboye. Source: WIPO, Global Innovation Index 2025 and 2026 (139 economies in each "
          "edition).\nThe index combines indicators of innovation inputs and outputs into one score from 0 to 100.")

fonts = {f.name for f in font_manager.fontManager.ttflist}
plt.rcParams.update({
    "font.family": "Inter" if "Inter" in fonts else "DejaVu Sans",
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False, "axes.spines.bottom": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
    "xtick.color": MUTED, "ytick.color": SECOND, "xtick.labelsize": 10.5, "ytick.labelsize": 11,
    "xtick.major.size": 0, "ytick.major.size": 0, "axes.axisbelow": True,
})

df = pd.read_csv(os.path.join(DATA, "gii_tidy.csv"))
me = pd.read_csv(os.path.join(DATA, "middle_east.csv"))
summ = pd.read_csv(os.path.join(DATA, "region_summary.csv"))
SUB_ORDER = ["Gulf", "Levant and Iraq", "Iran, Turkey and Yemen", "North Africa"]
REGION_ORDER = ["Middle East", "Europe", "Rest of Asia", "Rest of Africa", "North America", "South America",
                "Oceania"]


def frame(fig, title, subtitle, foot, gap=0.062):
    fig.text(0.04, 0.965, title, fontsize=21, fontweight="bold", color=INK, va="top", linespacing=1.12)
    fig.text(0.04, 0.965 - gap, subtitle, fontsize=12, color=SECOND, va="top", linespacing=1.45)
    fig.text(0.04, 0.02, foot, fontsize=9, color=MUTED, va="bottom", linespacing=1.4)


def middle_east_chart():
    """LinkedIn headline chart: 2025 and 2026 rank of the 15 Middle East economies in the index."""
    m = me.copy()
    up = int((m.rank_change > 0).sum())
    kw = m[m.country == "Kuwait"].iloc[0]
    assert kw.rank_change == df.rank_change.max(), "Kuwait is no longer the largest climb"
    ypos, heads, y, prev = [], [], 0, None
    for _, r in m.iterrows():
        if r.sub_region != prev:
            if prev is not None:
                y += 0.9
            heads.append((y, r.sub_region))
            y += 0.85
            prev = r.sub_region
        ypos.append(y)
        y += 1
    fig = plt.figure(figsize=(10, 11.5), dpi=200)
    ax = fig.add_axes([0.25, 0.115, 0.69, 0.68])
    for yi, r in zip(ypos, m.itertuples()):
        color = BLUE if r.rank_change > 0 else (ORANGE if r.rank_change < 0 else GREY)
        ax.plot([r.rank_2025, r.rank_2026], [yi, yi], color=color, lw=2.6, zorder=3, solid_capstyle="round")
        ax.scatter([r.rank_2025], [yi], s=46, color=SURFACE, edgecolor=color, linewidth=1.8, zorder=4)
        ax.scatter([r.rank_2026], [yi], s=70, color=color, zorder=5)
        move = "no change" if r.rank_change == 0 else (f"up {int(r.rank_change)}" if r.rank_change > 0
                                                       else f"down {int(-r.rank_change)}")
        ax.text(max(r.rank_2025, r.rank_2026) + 3, yi, f"{int(r.rank_2026)}  ({move})", va="center",
                fontsize=10.5, color=INK, fontweight="bold" if r.country == "Kuwait" else "normal")
    ax.set_yticks(ypos)
    ax.set_yticklabels(m.country)
    for yh, name in heads:
        ax.text(-0.33, yh, name.upper(), transform=ax.get_yaxis_transform(), fontsize=9.5,
                fontweight="bold", color=SECOND, va="center")
    ax.set_ylim(max(ypos) + 0.8, -1.5)
    ax.set_xlim(1, 139)
    ax.set_xticks([1, 25, 50, 75, 100, 125, 139])
    ax.xaxis.tick_top()
    ax.text(0, 1.035, "Rank out of 139  (1 = most innovative)", transform=ax.transAxes, fontsize=10, color=MUTED)
    ax.grid(axis="y", visible=False)
    ax.scatter([], [], s=46, color=SURFACE, edgecolor=SECOND, linewidth=1.8, label="2025 rank")
    ax.scatter([], [], s=70, color=SECOND, label="2026 rank")
    ax.legend(loc="upper right", frameon=False, fontsize=10.5)
    frame(fig, f"{up} of 15 Middle East economies moved up the\nGlobal Innovation Index in 2026. "
               f"Kuwait climbed {int(kw.rank_change)}",
          "Rank in the Global Innovation Index, 2025 edition (open circle) and 2026 edition (filled circle).\n"
          f"Blue: moved up. Orange: moved down. Kuwait's climb from {int(kw.rank_2025)} to {int(kw.rank_2026)} "
          "was the largest of any economy in the index.",
          SOURCE + "\nIraq, Syria, Palestine, Yemen and Libya are not covered by the index.",
          gap=0.083)
    fig.savefig(os.path.join(IMG, "innovation-middle-east-chart.png"))
    plt.close(fig)


def region_chart():
    """Every economy's 2026 score as a dot, Middle East first, with the mean of each region."""
    fig = plt.figure(figsize=(10, 7.6), dpi=200)
    ax = fig.add_axes([0.21, 0.15, 0.72, 0.62])
    for i, region in enumerate(REGION_ORDER):
        g = df[df.region == region]
        ax.scatter(g.score_2026, [i] * len(g), s=40, color=BLUE if region == "Middle East" else LIGHT,
                   alpha=0.85, zorder=3, edgecolor=SURFACE, linewidth=0.6)
        mean = g.score_2026.mean()
        ax.plot([mean, mean], [i - 0.3, i + 0.3], color=INK, lw=2.2, zorder=4)
        ax.text(70, i, f"{mean:.1f}", va="center", fontsize=10.5, color=INK, fontweight="bold")
    world = df.score_2026.mean()
    ax.axvline(world, color=ORANGE, lw=1.6, zorder=2)
    ax.text(world + 0.6, -0.75, f"World mean {world:.1f}", fontsize=10, color=INK)
    ax.set_yticks(range(len(REGION_ORDER)))
    ax.set_yticklabels([f"{r} ({(df.region == r).sum()})" for r in REGION_ORDER])
    ax.set_ylim(len(REGION_ORDER) - 0.4, -1.2)
    ax.set_xlim(0, 74)
    ax.grid(axis="y", visible=False)
    frame(fig, "Middle East scores span 20.5 (Algeria) to 52.2 (Israel).\nThe region's mean sits just above the "
               "world's",
          "Global Innovation Index 2026 score (0 to 100), one dot per economy, number of economies in brackets.\n"
          "Black line and the figure on the right: mean of the region.",
          SOURCE, gap=0.105)
    fig.savefig(os.path.join(IMG, "innovation-score-by-region.png"))
    plt.close(fig)


if __name__ == "__main__":
    assert me.score_2026.min() == 20.5 and me.score_2026.max() == 52.2
    middle_east_chart()
    region_chart()
    print("charts written")
