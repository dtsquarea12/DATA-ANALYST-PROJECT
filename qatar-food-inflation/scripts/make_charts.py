"""Draw the project charts from data/processed/.

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

BLUE, ORANGE = "#2a78d6", "#eb6834"
INK, SECOND, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#898781", "#e4e3df", "#fcfcfb"
FOOT = ("Analysis: Toheeb Adeboye. Source: National Planning Council of Qatar, monthly Consumer Price Index "
        "releases (base 2018=100),\nas reported by Qatar News Agency, Gulf Times, Qatar Tribune, The Peninsula and Arab News.")

fonts = {f.name for f in font_manager.fontManager.ttflist}
plt.rcParams.update({
    "font.family": "Inter" if "Inter" in fonts else "DejaVu Sans",
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False, "axes.spines.bottom": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
    "xtick.color": MUTED, "ytick.color": SECOND, "xtick.labelsize": 10, "ytick.labelsize": 11,
    "xtick.major.size": 0, "ytick.major.size": 0, "axes.axisbelow": True,
})

tidy = pd.read_csv(os.path.join(DATA, "qatar_cpi_tidy.csv"), dtype={"month": str})
cum = pd.read_csv(os.path.join(DATA, "cumulative_change_by_group.csv"), dtype=str)
cum["cumulative_change_pct"] = cum.cumulative_change_pct.astype(float)
GROUPS = [g for g in tidy.cpi_group.unique() if not g.startswith("all_items")]
MONTH_NAMES = {"2025-12": "Dec\n2025", "2026-01": "Jan\n2026", "2026-02": "Feb", "2026-03": "Mar",
               "2026-04": "Apr", "2026-05": "May", "2026-06": "Jun"}


def value(month, group, measure):
    r = tidy[(tidy.month == month) & (tidy.cpi_group == group) & (tidy.measure == measure)]
    return float(r.value.iloc[0])


def frame(fig, title, subtitle, top=0.955, gap=0.085):
    fig.text(0.04, top, title, fontsize=21, fontweight="bold", color=INK, va="top", linespacing=1.12)
    fig.text(0.04, top - gap, subtitle, fontsize=12, color=SECOND, va="top", linespacing=1.45)
    fig.text(0.04, 0.025, FOOT, fontsize=9, color=MUTED, va="bottom", linespacing=1.4)


def signed(v, dp=2):
    return f"{v:+.{dp}f}%" if v else "0%"


def hbar(ax, labels, values, highlight):
    y = range(len(labels))
    colors = [ORANGE if h else BLUE for h in highlight]
    ax.barh(y, values, height=0.62, color=colors, zorder=3)
    ax.set_yticks(list(y))
    ax.set_yticklabels(labels)
    for lab, h in zip(ax.get_yticklabels(), highlight):
        lab.set_color(INK if h else SECOND)
        lab.set_fontweight("bold" if h else "normal")
    ax.invert_yaxis()
    ax.grid(axis="y", visible=False)
    ax.axvline(0, color=MUTED, linewidth=1, zorder=4)
    span = max(values) - min(values)
    for yi, v, h in zip(y, values, highlight):
        ax.text(v + (span * 0.012 if v >= 0 else -span * 0.012), yi, signed(v), va="center",
                ha="left" if v >= 0 else "right", fontsize=10.5, color=INK if h else SECOND,
                fontweight="bold" if h else "normal", zorder=6,
                bbox=dict(facecolor=SURFACE, edgecolor="none", pad=1.5))
    ax.xaxis.set_major_formatter(lambda v, _: f"{v:+.0f}%" if v else "0%")


def headline_chart():
    d = tidy[(tidy.month == "2026-06") & (tidy.measure == "yoy_pct") & tidy.cpi_group.isin(GROUPS)]
    d = d.sort_values("value", ascending=False)
    allitems = value("2026-06", "all_items", "yoy_pct")
    food = value("2026-06", "food_beverages", "yoy_pct")
    fig = plt.figure(figsize=(10, 7), dpi=200)
    ax = fig.add_axes([0.335, 0.13, 0.615, 0.60])
    hbar(ax, list(d.group_label), list(d.value), list(d.cpi_group == "food_beverages"))
    ax.set_xlim(-9.5, 15)
    ax.axvline(allitems, color=INK, linewidth=1.2, linestyle=(0, (4, 3)), zorder=2)
    ax.text(allitems + 0.25, len(d) - 0.75, f"All items {signed(allitems)}", fontsize=10.5, color=INK,
            fontweight="bold", va="center", ha="left")
    frame(fig, f"Qatar's inflation rate is {allitems:.1f}%.\nFood is up {food:.1f}%.",
          "Change in consumer prices by spending group, June 2026 compared with June 2025.\n"
          "The dashed line is the all-items rate that makes the headline.", gap=0.125)
    fig.savefig(os.path.join(IMG, "qatar-food-inflation-chart.png"))
    plt.close(fig)


def monthly_chart():
    months = list(MONTH_NAMES)
    x = range(len(months))
    fig = plt.figure(figsize=(10, 6.25), dpi=200)
    ax = fig.add_axes([0.07, 0.24, 0.68, 0.50])
    for grp, color, name in (("food_beverages", ORANGE, "Food and beverages"), ("all_items", BLUE, "All items")):
        s = tidy[(tidy.cpi_group == grp) & (tidy.measure == "yoy_pct")].set_index("month").value.reindex(months)
        known = s.dropna()
        xs = [months.index(m) for m in known.index]
        # Dotted bridge across the month with no published annual figure, solid elsewhere.
        ax.plot(xs, known.values, color=color, linewidth=1.4, linestyle=(0, (1, 2.5)), zorder=2)
        ax.plot(list(x), s.values, color=color, linewidth=2.2, marker="o", markersize=6,
                markeredgecolor=SURFACE, markeredgewidth=1.3, zorder=3)
        ax.text(xs[-1] + 0.18, known.values[-1], name, color=INK, fontsize=11, va="center", fontweight="bold")
        for m in ("2026-02", "2026-06"):
            up = (grp == "food_beverages") == (m == "2026-06")
            ax.text(months.index(m), s[m] + (0.8 if up else -0.85), f"{s[m]:.2f}%",
                    ha="center", va="center", fontsize=10.5, color=INK)
    ax.text(months.index("2026-03") - 0.45, 9.6, "March: annual rates\nnot found in a\npublished report",
            ha="center", va="center", fontsize=9, color=MUTED, linespacing=1.3)
    ax.set_xticks(list(x))
    ax.set_xticklabels([MONTH_NAMES[m] for m in months])
    ax.set_ylim(-1, 14.5)
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
    ax.tick_params(axis="y", labelsize=10, colors=MUTED)
    ax.grid(axis="x", visible=False)
    frame(fig, "Food inflation went from 2% to 12.7% in four months",
          "Year-on-year change in consumer prices in Qatar, December 2025 to June 2026.\n"
          "The all-items rate stayed between 1.95% and 2.62% throughout.", gap=0.075)
    fig.savefig(os.path.join(IMG, "food_vs_all_items_yoy.png"))
    plt.close(fig)


def cumulative_chart():
    d = cum[(cum.window == "since_feb_2026") & cum.cpi_group.isin(GROUPS)].sort_values("cumulative_change_pct", ascending=False)
    fig = plt.figure(figsize=(10, 7), dpi=200)
    ax = fig.add_axes([0.335, 0.13, 0.615, 0.58])
    hbar(ax, list(d.group_label), list(d.cumulative_change_pct), list(d.cpi_group == "food_beverages"))
    ax.set_xlim(-14, 14.5)
    frame(fig, "Since February, food rose 11.6% and\nrecreation fell 10.9%",
          "Cumulative change in prices by spending group, February to June 2026, from chained monthly changes.\n"
          "The all-items index moved from 110.60 to 110.12 over the same months, a change of -0.43%.", gap=0.125)
    fig.savefig(os.path.join(IMG, "cumulative_change_since_february.png"))
    plt.close(fig)


if __name__ == "__main__":
    headline_chart()
    monthly_chart()
    cumulative_chart()
    print("charts written to images/")
