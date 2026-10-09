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
SOURCE = ("Analysis: Toheeb Adeboye. Source: Tax Foundation, Corporate Tax Rates around the World 2025 "
          "(226 jurisdictions),\nchecked against PwC Worldwide Tax Summaries and Trading Economics listings.")

fonts = {f.name for f in font_manager.fontManager.ttflist}
plt.rcParams.update({
    "font.family": "Inter" if "Inter" in fonts else "DejaVu Sans",
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False, "axes.spines.bottom": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
    "xtick.color": MUTED, "ytick.color": SECOND, "xtick.labelsize": 10, "ytick.labelsize": 11,
    "xtick.major.size": 0, "ytick.major.size": 0, "axes.axisbelow": True,
})

df = pd.read_csv(os.path.join(DATA, "corporate_tax_tidy.csv"))
WORLD = round(df.rate_2025_pct.mean(), 2)
SUB_ORDER = ["Gulf", "Levant and Iraq", "Iran, Turkey and Yemen", "North Africa"]
REGION_ORDER = ["Middle East", "Europe", "Rest of Asia", "Rest of Africa", "North America", "South America",
                "Oceania"]


def frame(fig, title, subtitle, foot, gap=0.062):
    fig.text(0.04, 0.965, title, fontsize=21, fontweight="bold", color=INK, va="top", linespacing=1.12)
    fig.text(0.04, 0.965 - gap, subtitle, fontsize=12, color=SECOND, va="top", linespacing=1.45)
    fig.text(0.04, 0.02, foot, fontsize=9, color=MUTED, va="bottom", linespacing=1.4)


def pct(v):
    return f"{v:g}%"


def middle_east_chart():
    """LinkedIn headline chart: the 20 Middle East economies, grouped by sub-region."""
    me = df[df.region == "Middle East"].copy()
    me["sub_order"] = me.sub_region.map({s: i for i, s in enumerate(SUB_ORDER)})
    me = me.sort_values(["sub_order", "rate_2025_pct", "country"])
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
    ax = fig.add_axes([0.25, 0.115, 0.69, 0.685])
    uplift = me.min_tax_uplift_pts.fillna(0)
    ax.barh(ypos, me.rate_2025_pct, height=0.68, color=BLUE, zorder=3)
    ax.barh(ypos, uplift, left=me.rate_2025_pct, height=0.68, color=SURFACE, edgecolor=BLUE, linewidth=1.3,
            hatch="////", zorder=3)
    ax.set_yticks(ypos)
    ax.set_yticklabels(me.country)
    for yi, v, u in zip(ypos, me.rate_2025_pct, uplift):
        label = pct(v) if u == 0 else f"{pct(v)}, or 15% for large multinationals"
        x = v + u + 0.5
        if abs(x - 0.5 - WORLD) < 1.2 or (x - 0.5 < WORLD < x + 4.5 and u == 0):
            x = max(x, WORLD + 0.5)  # keep labels clear of the world line
        ax.text(x, yi, label, va="center", fontsize=10.5, color=INK, zorder=6,
                bbox=dict(facecolor=SURFACE, edgecolor="none", pad=1.5))
    for yh, name in heads:
        ax.text(-0.33, yh, name.upper(), transform=ax.get_yaxis_transform(), fontsize=9.5,
                fontweight="bold", color=SECOND, va="center")
    ax.axvline(WORLD, color=ORANGE, lw=2, zorder=4)
    ax.text(WORLD + 0.4, -0.9, f"World average {WORLD:.1f}%", color=INK, fontsize=10, va="center")
    ax.set_ylim(max(ypos) + 0.8, -1.5)
    ax.set_xlim(0, 40)
    ax.set_xticks(range(0, 41, 10))
    ax.set_xticklabels([f"{t}%" for t in range(0, 41, 10)])
    ax.grid(axis="y", visible=False)
    frame(fig, "Corporate tax in the Middle East runs from\n0% in Bahrain to 34% in Morocco",
          "Standard top rate of tax on company profits, 2025. Hatched bars show the 15% minimum tax that\n"
          "applies to large multinational groups in Bahrain, the UAE and Qatar. The world average is the\n"
          "simple mean of 226 jurisdictions.",
          SOURCE + "\nSpecial regimes, free zones, small-business rates and oil and gas rates are not included.",
          gap=0.078)
    fig.savefig(os.path.join(IMG, "corporate-tax-middle-east-chart.png"))
    plt.close(fig)


def region_chart():
    """Every jurisdiction as a dot, Middle East first, with the median of each region."""
    fig = plt.figure(figsize=(10, 7.6), dpi=200)
    ax = fig.add_axes([0.22, 0.15, 0.73, 0.58])
    for i, region in enumerate(REGION_ORDER):
        g = df[df.region == region].sort_values("rate_2025_pct")
        seen = {}
        ys = []
        for v in g.rate_2025_pct:  # stack equal rates so every jurisdiction stays visible
            k = seen.get(v, 0)
            seen[v] = k + 1
            ys.append(i + ((k + 1) // 2) * (0.045 if k % 2 else -0.045))
        ax.scatter(g.rate_2025_pct, ys, s=26, color=BLUE, edgecolor=SURFACE, linewidth=0.6, zorder=3, alpha=0.9)
        mean = g.rate_2025_pct.mean()
        ax.plot([mean, mean], [i - 0.38, i + 0.38], color=INK, lw=2.2, zorder=4)
        ax.text(58.5, i, f"{mean:.1f}%", fontsize=10.5, color=INK, va="center", ha="right")
    ax.text(58.5, -0.85, "Mean", fontsize=9.5, color=SECOND, va="center", ha="right", fontweight="bold")
    ax.axvline(WORLD, color=ORANGE, lw=2, zorder=2)
    ax.text(WORLD + 0.4, -0.85, f"World average {WORLD:.1f}%", fontsize=10, color=INK, va="center")
    ax.set_yticks(range(len(REGION_ORDER)))
    ax.set_yticklabels([f"{r} ({(df.region == r).sum()})" for r in REGION_ORDER])
    ax.set_ylim(len(REGION_ORDER) - 0.4, -1.25)
    ax.set_xlim(-1, 59)
    ax.set_xticks(range(0, 51, 10))
    ax.set_xticklabels([f"{t}%" for t in range(0, 51, 10)])
    ax.grid(axis="y", visible=False)
    frame(fig, "The Middle East average sits below the world.\nAfrica and South America sit above it",
          "Standard top corporate tax rate in 2025. One dot per jurisdiction, number of jurisdictions in brackets.\n"
          "Black line and the figure on the right: simple mean of the region.",
          SOURCE, gap=0.115)
    fig.savefig(os.path.join(IMG, "corporate-tax-by-region.png"))
    plt.close(fig)


def gulf_chart():
    """The six Gulf states next to economies a firm might compare them with (rates confirmed in a second listing)."""
    names = ["Bahrain", "United Arab Emirates", "Hungary", "Qatar", "Ireland", "Kuwait", "Oman", "Singapore",
             "Saudi Arabia", "Turkey", "United Kingdom", "China", "South Africa", "Nigeria", "Kenya"]
    g = df[df.country.isin(names)].sort_values(["rate_2025_pct", "country"])
    assert len(g) == len(names) and (g.check_status == "confirmed").all()
    fig = plt.figure(figsize=(10, 8.4), dpi=200)
    ax = fig.add_axes([0.25, 0.13, 0.69, 0.63])
    y = range(len(g))
    gulf = g.sub_region == "Gulf"
    ax.barh(y, g.rate_2025_pct, height=0.68, color=[BLUE if a else LIGHT for a in gulf], zorder=3)
    for yi, v in zip(y, g.rate_2025_pct):
        ax.text(v + 0.4, yi, pct(v), va="center", fontsize=10.5, color=INK)
    ax.set_yticks(list(y))
    ax.set_yticklabels(g.country)
    ax.set_ylim(len(g) - 0.4, -0.6)
    ax.set_xlim(0, 34)
    ax.set_xticks(range(0, 31, 10))
    ax.set_xticklabels([f"{t}%" for t in range(0, 31, 10)])
    ax.grid(axis="y", visible=False)
    ax.legend(handles=[Patch(color=BLUE, label="Gulf state"), Patch(color=LIGHT, label="Other economy")],
              loc="upper right", frameon=False, fontsize=10)
    frame(fig, "Five of the six Gulf states tax company\nprofits at 15% or less",
          "Standard top corporate tax rate in 2025, Gulf states next to a selection of other economies.\n"
          "Every rate shown matches a second listing.",
          SOURCE, gap=0.105)
    fig.savefig(os.path.join(IMG, "corporate-tax-gulf-comparison.png"))
    plt.close(fig)


if __name__ == "__main__":
    middle_east_chart()
    region_chart()
    gulf_chart()
    print("charts written to images/")
