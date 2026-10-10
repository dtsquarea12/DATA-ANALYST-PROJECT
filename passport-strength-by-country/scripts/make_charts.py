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

BLUE, LIGHT, ORANGE = "#2a78d6", "#9fc3ec", "#eb6834"
INK, SECOND, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#898781", "#e4e3df", "#fcfcfb"
SOURCE = ("Analysis: Toheeb Adeboye. Source: Henley Passport Index 2026 (199 passports, 227 destinations), April and "
          "July editions,\nas printed by Henley & Partners, The Peninsula, Tuniscope, Wikipedia and Packzup.")

fonts = {f.name for f in font_manager.fontManager.ttflist}
plt.rcParams.update({
    "font.family": "Inter" if "Inter" in fonts else "DejaVu Sans",
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False, "axes.spines.bottom": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
    "xtick.color": MUTED, "ytick.color": SECOND, "xtick.labelsize": 10, "ytick.labelsize": 11,
    "xtick.major.size": 0, "ytick.major.size": 0, "axes.axisbelow": True,
})

df = pd.read_csv(os.path.join(DATA, "passport_tidy.csv"))
checks = pd.read_csv(os.path.join(DATA, "source_checks.csv")).set_index("check")
WORLD_JUL = int(checks.loc["world_average_score", "published_value"])   # published, July 2026
WORLD_APR = round(df.score_apr_2026.mean(), 1)                            # computed from the April table
SUB_ORDER = ["Gulf", "Levant and Iraq", "Iran, Turkey and Yemen", "North Africa"]
REGION_ORDER = ["Middle East", "Europe", "Rest of Asia", "Rest of Africa", "North America", "South America",
                "Oceania"]


def frame(fig, title, subtitle, foot, gap=0.062):
    fig.text(0.04, 0.965, title, fontsize=21, fontweight="bold", color=INK, va="top", linespacing=1.12)
    fig.text(0.04, 0.965 - gap, subtitle, fontsize=12, color=SECOND, va="top", linespacing=1.45)
    fig.text(0.04, 0.02, foot, fontsize=9, color=MUTED, va="bottom", linespacing=1.4)


def middle_east_chart():
    """LinkedIn headline chart: the 20 Middle East passports, grouped by sub-region, latest edition available."""
    me = df[df.region == "Middle East"].copy()
    me["sub_order"] = me.sub_region.map({s: i for i, s in enumerate(SUB_ORDER)})
    me = me.sort_values(["sub_order", "latest_score", "country"], ascending=[True, False, True])
    ypos, heads, y, prev = [], [], 0, None
    for _, r in me.iterrows():
        if r.sub_region != prev:
            if prev is not None:
                y += 0.9
            heads.append((y, r.sub_region))
            y += 0.85
            prev = r.sub_region
        ypos.append(y)
        y += 1
    fig = plt.figure(figsize=(10, 12), dpi=200)
    ax = fig.add_axes([0.25, 0.105, 0.69, 0.70])
    july = me.latest_edition == "2026-07"
    ax.barh(ypos, me.latest_score, height=0.68, color=[BLUE if j else LIGHT for j in july], zorder=3)
    ax.set_yticks(ypos)
    ax.set_yticklabels(me.country)
    for yi, v, j in zip(ypos, me.latest_score, july):
        label = f"{v}" if j else f"{v} (April)"
        x = v + 2.5
        if v <= WORLD_JUL <= v + 2.5 + 7 * len(label):
            x = max(x, WORLD_JUL + 2.5)  # keep labels clear of the world line
        ax.text(x, yi, label, va="center", fontsize=10.5, color=INK, zorder=6,
                bbox=dict(facecolor=SURFACE, edgecolor="none", pad=1.5))
    for yh, name in heads:
        ax.text(-0.33, yh, name.upper(), transform=ax.get_yaxis_transform(), fontsize=9.5,
                fontweight="bold", color=SECOND, va="center")
    ax.axvline(WORLD_JUL, color=ORANGE, lw=2, zorder=4)
    ax.text(WORLD_JUL + 2.5, -0.9, f"World average {WORLD_JUL}", color=INK, fontsize=10, va="center")
    ax.set_ylim(max(ypos) + 0.8, -1.5)
    ax.set_xlim(0, 227)
    ax.set_xticks([0, 50, 100, 150, 200, 227])
    ax.grid(axis="y", visible=False)
    frame(fig, "A UAE passport opens 188 destinations without a\nprior visa. The world average is 108",
          "Destinations a holder can enter without arranging a visa before travel, out of 227. Henley Passport\n"
          "Index, July 2026 edition. Light bars: no July figure was found, so the April 2026 figure is shown.",
          SOURCE + "\nVisa on arrival and electronic travel authorities count as access. E-visas that need approval "
          "before travel do not.", gap=0.078)
    fig.savefig(os.path.join(IMG, "passport-middle-east-chart.png"))
    plt.close(fig)


def region_chart():
    """Every passport as a dot, Middle East first, with the mean of each region. April 2026 full table."""
    fig = plt.figure(figsize=(10, 7.6), dpi=200)
    ax = fig.add_axes([0.22, 0.15, 0.73, 0.58])
    for i, region in enumerate(REGION_ORDER):
        g = df[df.region == region].sort_values("score_apr_2026")
        seen, ys = {}, []
        for v in g.score_apr_2026:  # stack equal scores so every passport stays visible
            k = seen.get(v, 0)
            seen[v] = k + 1
            ys.append(i + ((k + 1) // 2) * (0.05 if k % 2 else -0.05))
        ax.scatter(g.score_apr_2026, ys, s=26, color=BLUE, edgecolor=SURFACE, linewidth=0.6, zorder=3, alpha=0.9)
        mean = g.score_apr_2026.mean()
        ax.plot([mean, mean], [i - 0.4, i + 0.4], color=INK, lw=2.2, zorder=4)
        ax.text(226, i, f"{mean:.1f}", fontsize=10.5, color=INK, va="center", ha="right")
    ax.text(226, -0.9, "Mean", fontsize=9.5, color=SECOND, va="center", ha="right", fontweight="bold")
    ax.axvline(WORLD_APR, color=ORANGE, lw=2, zorder=2)
    ax.text(WORLD_APR + 2, -0.9, f"World average {WORLD_APR}", fontsize=10, color=INK, va="center")
    ax.set_yticks(range(len(REGION_ORDER)))
    ax.set_yticklabels([f"{r} ({(df.region == r).sum()})" for r in REGION_ORDER])
    ax.set_ylim(len(REGION_ORDER) - 0.4, -1.3)
    ax.set_xlim(0, 228)
    ax.set_xticks([0, 50, 100, 150, 200])
    ax.grid(axis="y", visible=False)
    frame(fig, "Each region holds a wide spread of passports.\nThe Middle East runs from 26 to 187",
          "Destinations open without a prior visa, April 2026 edition (the latest full table found). One dot per\n"
          "passport, number of passports in brackets. Black line and the figure on the right: mean of the region.",
          SOURCE, gap=0.115)
    fig.savefig(os.path.join(IMG, "passport-by-region.png"))
    plt.close(fig)


def gulf_chart():
    """The six Gulf passports in April and July 2026: every score rose, five of six ranks fell."""
    g = df[df.sub_region == "Gulf"].sort_values("score_jul_2026", ascending=False)
    fig = plt.figure(figsize=(10, 6.6), dpi=200)
    ax = fig.add_axes([0.25, 0.15, 0.50, 0.55])
    y = list(range(len(g)))
    ax.barh(y, g.score_jul_2026, height=0.62, color=BLUE, zorder=3)
    for yi, (_, r) in zip(y, g.iterrows()):
        label = f"{int(r.score_apr_2026)} to {int(r.score_jul_2026)}"
        x = r.score_jul_2026 + 3
        if r.score_jul_2026 <= WORLD_JUL <= x + 40:
            x = WORLD_JUL + 3  # keep labels clear of the world line
        ax.text(x, yi, label, va="center", fontsize=10.5, color=INK, zorder=6)
        ax.text(1.24, yi, f"{int(r.rank_apr_2026)} to {int(r.rank_jul_2026)}", va="center", ha="center",
                fontsize=10.5, color=INK, transform=ax.get_yaxis_transform())
    ax.text(1.24, -0.85, "Rank, April to July", fontsize=9.5, fontweight="bold", color=SECOND, va="center",
            ha="center", transform=ax.get_yaxis_transform())
    ax.axvline(WORLD_JUL, color=ORANGE, lw=2, zorder=4)
    ax.text(WORLD_JUL + 3, -0.85, f"World average {WORLD_JUL}", fontsize=10, color=INK, va="center")
    ax.set_yticks(y)
    ax.set_yticklabels(g.country)
    ax.set_ylim(len(g) - 0.5, -1.25)
    ax.set_xlim(0, 227)
    ax.set_xticks([0, 50, 100, 150, 200])
    ax.grid(axis="y", visible=False)
    frame(fig, "Every Gulf passport gained destinations between\nApril and July. Five of the six ranks still fell",
          "Destinations open without a prior visa, Henley Passport Index. Bars show the July 2026 edition.\n"
          "Labels show the April and July scores, and the rank among 199 passports in each edition.",
          SOURCE, gap=0.135)
    fig.savefig(os.path.join(IMG, "passport-gulf-april-july.png"))
    plt.close(fig)


if __name__ == "__main__":
    middle_east_chart()
    region_chart()
    gulf_chart()
    print("charts written to images/")
