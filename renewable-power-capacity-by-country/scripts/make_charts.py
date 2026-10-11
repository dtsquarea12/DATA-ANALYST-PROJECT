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

BLUE, LIGHT, ORANGE, TEAL, PURPLE, GREY = "#2a78d6", "#9fc3ec", "#eb6834", "#1f9d8a", "#8a5cc7", "#a9a7a1"
INK, SECOND, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#898781", "#e4e3df", "#fcfcfb"
SOURCE = ("Analysis: Toheeb Adeboye. Source: IRENA, Renewable Capacity Statistics 2026 (total renewable energy,\n"
          "installed capacity at year end). Hydropower, solar, wind and bioenergy are included; pure pumped storage "
          "is not.")

fonts = {f.name for f in font_manager.fontManager.ttflist}
plt.rcParams.update({
    "font.family": "Inter" if "Inter" in fonts else "DejaVu Sans",
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False, "axes.spines.bottom": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
    "xtick.color": MUTED, "ytick.color": SECOND, "xtick.labelsize": 10.5, "ytick.labelsize": 11,
    "xtick.major.size": 0, "ytick.major.size": 0, "axes.axisbelow": True,
})

tidy = pd.read_csv(os.path.join(DATA, "renewable_capacity_tidy.csv"))
countries = pd.read_csv(os.path.join(DATA, "country_summary_2025.csv"))
groups = pd.read_csv(os.path.join(DATA, "group_summary.csv"))
SUB_ORDER = ["Gulf", "Levant and Iraq", "Iran, Turkey and Yemen", "North Africa"]


def frame(fig, title, subtitle, foot, gap=0.062):
    fig.text(0.04, 0.965, title, fontsize=21, fontweight="bold", color=INK, va="top", linespacing=1.12)
    fig.text(0.04, 0.965 - gap, subtitle, fontsize=12, color=SECOND, va="top", linespacing=1.45)
    fig.text(0.04, 0.02, foot, fontsize=9, color=MUTED, va="bottom", linespacing=1.4)


def gulf_chart():
    """LinkedIn headline chart: Gulf capacity by year, stacked by country."""
    g = tidy[(tidy.entity_type == "country") & (tidy.sub_region == "Gulf")]
    w = g.pivot(index="year", columns="entity", values="capacity_mw")
    w["Bahrain and Kuwait"] = w["Bahrain"] + w["Kuwait"]
    series = [("Saudi Arabia", BLUE), ("United Arab Emirates", ORANGE), ("Oman", TEAL), ("Qatar", PURPLE),
              ("Bahrain and Kuwait", GREY)]
    total = w[[s for s, _ in series]].sum(axis=1)
    gulf = tidy[tidy.entity == "Gulf"].set_index("year").capacity_mw
    assert (total == gulf).all()
    fig = plt.figure(figsize=(10, 10), dpi=200)
    ax = fig.add_axes([0.09, 0.115, 0.66, 0.70])
    bottom = pd.Series(0, index=w.index)
    for name, color in series:
        ax.bar(w.index, w[name], bottom=bottom, width=0.72, color=color, edgecolor=SURFACE, linewidth=1.2,
               zorder=3)
        mid = bottom[2025] + w.loc[2025, name] / 2
        ax.text(2025.52, mid if name != "Bahrain and Kuwait" else mid + 1150,
                f"{name}\n{w.loc[2025, name]:,} MW", color=color if color != GREY else SECOND, fontsize=10.5,
                va="center", fontweight="bold", linespacing=1.3)
        bottom = bottom + w[name]
    for y, v in total.items():
        ax.text(y, v + 320, f"{v:,}", ha="center", fontsize=10.5, color=INK,
                fontweight="bold" if y in (2016, 2025) else "normal")
    ax.set_xticks(list(w.index))
    ax.set_xlim(2015.4, 2025.55)
    ax.set_ylim(0, 27000)
    ax.set_yticks(range(0, 25001, 5000))
    ax.set_yticklabels([f"{t:,}" for t in range(0, 25001, 5000)])
    ax.tick_params(axis="y", labelsize=10, labelcolor=MUTED)
    ax.grid(axis="x", visible=False)
    frame(fig, f"Gulf renewable power capacity grew from\n{total[2016]:,} MW in 2016 to {total[2025]:,} MW in 2025",
          "Installed renewable power capacity at the end of each year, megawatts, six Gulf states.\n"
          f"Saudi Arabia added {w.loc[2025, 'Saudi Arabia'] - w.loc[2024, 'Saudi Arabia']:,} MW in 2025, "
          "about two thirds of what the six states added that year.",
          SOURCE, gap=0.085)
    fig.savefig(os.path.join(IMG, "renewable-capacity-gulf-chart.png"))
    plt.close(fig)


def added_chart():
    """Capacity added in 2025 in the 20 economies, grouped by sub-region."""
    me = countries.copy()
    me["sub_order"] = me.sub_region.map({s: i for i, s in enumerate(SUB_ORDER)})
    me = me.sort_values(["sub_order", "added_2025_mw", "capacity_2025_mw"], ascending=[True, False, False])
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
    ax = fig.add_axes([0.25, 0.10, 0.69, 0.725])
    ax.barh(ypos, me.added_2025_mw, height=0.68, color=BLUE, zorder=3)
    ax.set_yticks(ypos)
    ax.set_yticklabels(me.country)
    for yi, a, c in zip(ypos, me.added_2025_mw, me.capacity_2025_mw):
        label = f"+{a:,} MW, to {c:,}" if a > 0 else f"no change, {c:,}"
        ax.text(a + 90, yi, label, va="center", fontsize=10.5, color=INK)
    for yh, name in heads:
        ax.text(-0.33, yh, name.upper(), transform=ax.get_yaxis_transform(), fontsize=9.5,
                fontweight="bold", color=SECOND, va="center")
    ax.set_ylim(max(ypos) + 0.8, -0.6)
    ax.set_xlim(0, 10200)
    ax.set_xticks(range(0, 8001, 2000))
    ax.set_xticklabels([f"{t:,}" for t in range(0, 8001, 2000)])
    ax.grid(axis="y", visible=False)
    frame(fig, "Turkey and Saudi Arabia added the most\nrenewable power capacity in 2025",
          "Renewable power capacity added during 2025 in 20 Middle East and North Africa economies,\n"
          "megawatts, with the total installed at the end of 2025.",
          SOURCE, gap=0.075)
    fig.savefig(os.path.join(IMG, "renewable-capacity-added-2025.png"))
    plt.close(fig)


def region_chart():
    """Growth in 2025 by IRENA region, Middle East first."""
    r = groups[groups.entity_type == "irena_region"].copy()
    world = groups[groups.entity_type == "world"].iloc[0]
    me = r[r.entity == "Middle East"]
    rest = r[r.entity != "Middle East"].sort_values("growth_2025_pct", ascending=False)
    r = pd.concat([me, rest])
    fig = plt.figure(figsize=(10, 7.6), dpi=200)
    ax = fig.add_axes([0.32, 0.14, 0.63, 0.60])
    y = range(len(r))
    ax.barh(y, r.growth_2025_pct, height=0.68, color=[BLUE if e == "Middle East" else LIGHT for e in r.entity],
            zorder=3)
    for yi, v, a, c in zip(y, r.growth_2025_pct, r.added_2025_mw, r.capacity_2025_mw):
        ax.text(v + 0.4, yi, f"{v:.1f}%   +{a / 1000:,.1f} GW, to {c / 1000:,.1f} GW", va="center", fontsize=10.5,
                color=INK, zorder=6, bbox=dict(facecolor=SURFACE, edgecolor="none", pad=1.5))
    ax.axvline(world.growth_2025_pct, color=ORANGE, lw=2, zorder=4)
    ax.text(world.growth_2025_pct + 0.4, -0.95, f"World {world.growth_2025_pct:.1f}%", fontsize=10, color=INK,
            va="center")
    ax.set_yticks(list(y))
    ax.set_yticklabels(r.entity)
    ax.set_ylim(len(r) - 0.4, -1.4)
    ax.set_xlim(0, 46)
    ax.set_xticks(range(0, 31, 10))
    ax.set_xticklabels([f"{t}%" for t in range(0, 31, 10)])
    ax.grid(axis="y", visible=False)
    frame(fig, "The Middle East had the fastest growth in\nrenewable power capacity of any region in 2025",
          "Change in installed renewable power capacity from the end of 2024 to the end of 2025, with the\n"
          "capacity added and the total. Regions as defined by IRENA: its Middle East has 14 countries and\n"
          "does not include North Africa or Turkey.",
          SOURCE, gap=0.115)
    fig.savefig(os.path.join(IMG, "renewable-capacity-growth-by-region.png"))
    plt.close(fig)


if __name__ == "__main__":
    gulf_chart()
    added_chart()
    region_chart()
    print("charts written to images/")
