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

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data", "processed")
IMG = os.path.join(HERE, "..", "images")
os.makedirs(IMG, exist_ok=True)

BLUE, ORANGE = "#2a78d6", "#eb6834"
INK, SECOND, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#898781", "#e4e3df", "#fcfcfb"
SOURCE = ("Analysis: Toheeb Adeboye. Source: Microsoft AI Economy Institute, Global AI Diffusion reports "
          "(H2 2025, Q1 2026 and Q2 2026 editions).")

fonts = {f.name for f in font_manager.fontManager.ttflist}
plt.rcParams.update({
    "font.family": "Inter" if "Inter" in fonts else "DejaVu Sans",
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False, "axes.spines.bottom": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
    "xtick.color": MUTED, "ytick.color": SECOND, "xtick.labelsize": 10, "ytick.labelsize": 11,
    "xtick.major.size": 0, "ytick.major.size": 0, "axes.axisbelow": True,
})

eco = pd.read_csv(os.path.join(DATA, "ai_use_by_economy.csv"))
agg = pd.read_csv(os.path.join(DATA, "world_aggregates.csv")).set_index("period")
WORLD = agg.loc["2026-Q2", "world_pct"]
SUB_ORDER = ["Gulf", "Levant and Iraq", "Iran and Turkey", "North Africa"]
REGION_ORDER = ["Middle East", "Europe", "Asia", "Oceania", "Americas", "Sub-Saharan Africa"]


def frame(fig, title, subtitle, foot, gap=0.062):
    fig.text(0.04, 0.965, title, fontsize=21, fontweight="bold", color=INK, va="top", linespacing=1.12)
    fig.text(0.04, 0.965 - gap, subtitle, fontsize=12, color=SECOND, va="top", linespacing=1.45)
    fig.text(0.04, 0.02, foot, fontsize=9, color=MUTED, va="bottom", linespacing=1.4)


def middle_east_ordered():
    me = eco[eco.region == "Middle East"].copy()
    me["sub_order"] = me.sub_region.map({s: i for i, s in enumerate(SUB_ORDER)})
    return me.sort_values(["sub_order", "q2_2026_pct"], ascending=[True, False])


def middle_east_chart():
    """LinkedIn headline chart: every Middle East economy in the report, grouped by sub-region."""
    me = middle_east_ordered()
    ypos, labels, y, prev = [], [], 0, None
    heads = []
    for _, r in me.iterrows():
        if r.sub_region != prev:
            if prev is not None:
                y += 0.9
            heads.append((y, r.sub_region))
            y += 0.85
            prev = r.sub_region
        ypos.append(y)
        y += 1
    fig = plt.figure(figsize=(10, 11), dpi=200)
    ax = fig.add_axes([0.25, 0.1, 0.69, 0.71])
    above = me.q2_2026_pct > WORLD
    ax.barh(ypos, me.q2_2026_pct, height=0.68, color=[BLUE if a else "#9fc3ec" for a in above], zorder=3)
    ax.set_yticks(ypos)
    ax.set_yticklabels(me.economy)
    for yi, v, rank in zip(ypos, me.q2_2026_pct, me.rank_q2_2026):
        x = max(v, WORLD) + 0.8  # keep labels clear of the world line
        ax.text(x, yi, f"{v:.1f}%", va="center", fontsize=10.5, color=INK)
        ax.text(x + 6.8, yi, f"world #{rank}", va="center", fontsize=9, color=MUTED)
    for yh, name in heads:
        ax.text(-0.36, yh, name.upper(), transform=ax.get_yaxis_transform(), fontsize=9.5,
                fontweight="bold", color=SECOND, va="center")
    ax.axvline(WORLD, color=ORANGE, lw=2, zorder=4)
    ax.text(WORLD + 0.6, -0.9, f"World {WORLD:.1f}%", color=INK, fontsize=10, va="center")
    ax.set_ylim(max(ypos) + 0.8, -1.5)
    ax.set_xlim(0, 88)
    ax.set_xticks(range(0, 81, 20))
    ax.set_xticklabels([f"{t}%" for t in range(0, 81, 20)])
    ax.grid(axis="y", visible=False)
    frame(fig, "AI use in the Middle East runs from 73% of\nworking-age people in the UAE to 7% in Syria",
          "Share of people aged 15 to 64 who used a generative AI product, Q2 2026 (April to June).\n"
          "Darker bars are above the world figure. Bahrain and Yemen are not covered by the report.",
          SOURCE + "\nEstimates from device telemetry, adjusted for device share, internet use and population.",
          gap=0.085)
    fig.savefig(os.path.join(IMG, "ai-use-middle-east-chart.png"))
    plt.close(fig)


def region_chart():
    """Every economy as a dot, Middle East first. Hollow dots carry a shared regional estimate."""
    fig = plt.figure(figsize=(10, 7.2), dpi=200)
    ax = fig.add_axes([0.2, 0.15, 0.75, 0.62])
    for i, region in enumerate(REGION_ORDER):
        g = eco[eco.region == region]
        own, shared = g[g.own_estimate == "yes"], g[g.own_estimate == "no"]
        jitter = [((k * 37) % 11 - 5) * 0.035 for k in range(len(g))]
        jo, js = jitter[:len(own)], jitter[len(own):]
        ax.scatter(own.q2_2026_pct, [i + j for j in jo], s=46, color=BLUE, edgecolor=SURFACE, linewidth=1.2, zorder=3)
        ax.scatter(shared.q2_2026_pct, [i + j for j in js], s=46, facecolor="none", edgecolor=BLUE, linewidth=1.2, zorder=3)
        med = g.q2_2026_pct.median()
        ax.plot([med, med], [i - 0.32, i + 0.32], color=INK, lw=2, zorder=4)
        top = g.loc[g.q2_2026_pct.idxmax()]
        right = top.q2_2026_pct < 60
        ax.text(top.q2_2026_pct + (1.2 if right else -1.2), i + (0 if right else 0.3),
                f"{top.economy} {top.q2_2026_pct:.1f}%", fontsize=9, color=SECOND, va="center",
                ha="left" if right else "right")
    ax.axvline(WORLD, color=ORANGE, lw=2, zorder=2)
    ax.text(WORLD + 0.6, -0.7, f"World {WORLD:.1f}%", fontsize=10, color=INK, va="center")
    ax.set_yticks(range(len(REGION_ORDER)))
    ax.set_yticklabels([f"{r} ({(eco.region == r).sum()})" for r in REGION_ORDER])
    ax.set_ylim(len(REGION_ORDER) - 0.5, -1.1)
    ax.set_xlim(0, 85)
    ax.set_xticks(range(0, 81, 20))
    ax.set_xticklabels([f"{t}%" for t in range(0, 81, 20)])
    ax.grid(axis="y", visible=False)
    handles = [Line2D([], [], marker="o", ls="", color=BLUE, markersize=7, label="Own estimate"),
               Line2D([], [], marker="o", ls="", markerfacecolor="none", markeredgecolor=BLUE, markersize=7,
                      label="Shares a regional estimate with neighbours"),
               Line2D([], [], color=INK, lw=2, label="Median of the region")]
    fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.035, 0.835), ncol=3, frameon=False,
               fontsize=10, labelcolor=SECOND)
    frame(fig, "Middle East first: AI use by region, Q2 2026",
          "Share of people aged 15 to 64 who used a generative AI product. One dot per economy, 147 economies.",
          SOURCE + "\nRegion medians are unweighted. The world figure is weighted by working-age population.")
    fig.savefig(os.path.join(IMG, "ai-use-by-region.png"))
    plt.close(fig)


def change_chart():
    """Middle East: first half of 2025 against Q2 2026."""
    me = middle_east_ordered().sort_values("q2_2026_pct", ascending=False)
    fig = plt.figure(figsize=(10, 8.6), dpi=200)
    ax = fig.add_axes([0.22, 0.1, 0.72, 0.68])
    y = list(range(len(me)))
    ax.hlines(y, me.h1_2025_pct, me.q2_2026_pct, color=GRID, lw=3, zorder=2)
    ax.scatter(me.h1_2025_pct, y, s=60, facecolor=SURFACE, edgecolor=BLUE, linewidth=1.6, zorder=3, label="H1 2025")
    ax.scatter(me.q2_2026_pct, y, s=60, color=BLUE, zorder=3, label="Q2 2026")
    for yi, v, d in zip(y, me.q2_2026_pct, me.change_h1_2025_to_q2_2026_pp):
        ax.text(v + 1.3, yi, f"{d:+.1f} pts", va="center", fontsize=10, color=INK)
    ax.set_yticks(y)
    ax.set_yticklabels(me.economy)
    ax.set_ylim(len(me) - 0.4, -0.8)
    ax.set_xlim(0, 85)
    ax.set_xticks(range(0, 81, 20))
    ax.set_xticklabels([f"{t}%" for t in range(0, 81, 20)])
    ax.grid(axis="y", visible=False)
    fig.legend(loc="upper left", bbox_to_anchor=(0.035, 0.835), ncol=2, frameon=False, fontsize=10.5, labelcolor=SECOND)
    w0, w1 = agg.loc["2025-H1", "world_pct"], WORLD
    frame(fig, "Since early 2025, every Middle East economy but Syria\ngained at least 1.5 points; the UAE gained 13.9",
          f"Share of people aged 15 to 64 using generative AI, H1 2025 and Q2 2026. World: {w0:.1f}% to {w1:.1f}%.",
          SOURCE, gap=0.1)
    fig.savefig(os.path.join(IMG, "ai-use-change-middle-east.png"))
    plt.close(fig)


if __name__ == "__main__":
    middle_east_chart()
    region_chart()
    change_chart()
    print("charts written to", os.path.abspath(IMG))
