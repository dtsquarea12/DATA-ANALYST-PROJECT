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
FOOT = ("Analysis: Toheeb Adeboye. Source: General Authority for Statistics (GASTAT) Labour Force Survey, "
        "quarterly releases to Q2 2026.")

fonts = {f.name for f in font_manager.fontManager.ttflist}
plt.rcParams.update({
    "font.family": "Inter" if "Inter" in fonts else "DejaVu Sans",
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False,
    "axes.edgecolor": GRID, "axes.grid": True, "axes.grid.axis": "y", "grid.color": GRID, "grid.linewidth": 0.8,
    "xtick.color": MUTED, "ytick.color": MUTED, "xtick.labelsize": 10, "ytick.labelsize": 10,
    "xtick.major.size": 0, "ytick.major.size": 0, "axes.axisbelow": True,
})

tidy = pd.read_csv(os.path.join(DATA, "saudi_labour_tidy.csv"))
comp = pd.read_csv(os.path.join(DATA, "window_comparisons.csv"))


def series(sex, indicator, nationality="Saudi"):
    s = tidy[(tidy.nationality == nationality) & (tidy.sex == sex) & (tidy.indicator == indicator)]
    return s.set_index("quarter").sort_index()


def label(q):
    return f"Q{q[-1]}\n{q[:4]}" if q.endswith("1") else f"Q{q[-1]}"


def frame(fig, title, subtitle, top=0.955):
    fig.text(0.045, top, title, fontsize=21, fontweight="bold", color=INK, va="top", linespacing=1.12)
    fig.text(0.045, top - 0.15, subtitle, fontsize=12, color=SECOND, va="top", linespacing=1.45)
    fig.text(0.045, 0.03, FOOT, fontsize=9.5, color=MUTED, va="bottom")


def headline_chart():
    lf = series("Female", "participation_rate").loc["2023-Q4":]
    ep = series("Female", "employment_to_population").loc["2023-Q4":]
    ur = series("Female", "unemployment_rate")
    qs = list(lf.index)
    x = range(len(qs))
    fig = plt.figure(figsize=(10, 6.25), dpi=200)
    ax = fig.add_axes([0.07, 0.15, 0.72, 0.53])
    ax.fill_between(x, ep.value_pct, lf.value_pct, color=BLUE, alpha=0.10, linewidth=0)
    ax.plot(x, lf.value_pct, color=BLUE, linewidth=2.2, marker="o", markersize=5, markeredgecolor=SURFACE, markeredgewidth=1.2)
    ax.plot(x, ep.value_pct, color=ORANGE, linewidth=2.2, marker="o", markersize=5, markeredgecolor=SURFACE, markeredgewidth=1.2)
    for q in ("2024-Q2", "2026-Q2"):
        i = qs.index(q)
        ax.annotate(f"{lf.value_pct[q]:.1f}%", (i, lf.value_pct[q]), xytext=(0, 9), textcoords="offset points", ha="center", fontsize=11, fontweight="bold", color=INK)
        ax.annotate(f"{ep.value_pct[q]:.1f}%", (i, ep.value_pct[q]), xytext=(0, -17), textcoords="offset points", ha="center", fontsize=11, fontweight="bold", color=INK)
        mid = (lf.value_pct[q] + ep.value_pct[q]) / 2
        ax.annotate(f"Unemployment\nrate {ur.value_pct[q]:.1f}%", (i - (0.75 if q == "2026-Q2" else 0), mid), ha="center", va="center", fontsize=9, color=SECOND, linespacing=1.25)
    n = len(qs) - 1
    ax.text(n + 0.55, lf.value_pct.iloc[-1], "In the labour force\n(working or looking)", color=INK, fontsize=10.5, va="center", linespacing=1.3)
    ax.text(n + 0.55, ep.value_pct.iloc[-1], "In work", color=INK, fontsize=10.5, va="center")
    r = qs.index("2025-Q1")
    ax.axvline(r, color=MUTED, linewidth=0.9, linestyle=(0, (2, 3)))
    ax.text(r + 0.1, 37.6, "Survey questionnaire\nredesigned, Q1 2025", fontsize=9, color=MUTED, va="top", linespacing=1.3)
    ax.set_ylim(28, 38)
    ax.set_xlim(-0.4, n + 0.2)
    ax.set_yticks(range(28, 39, 2))
    ax.set_yticklabels([f"{v}%" for v in range(28, 39, 2)])
    ax.set_xticks(list(x))
    ax.set_xticklabels([label(q) for q in qs])
    frame(fig,
          "Unemployment among Saudi women fell from 12.8% to 9.6%\nin two years. The share of them in work did not rise.",
          "Saudi women aged 15 and over, as a share of all women in that group, Q4 2023 to Q2 2026.\n"
          "The shaded gap is women who are unemployed and looking for work.")
    fig.savefig(os.path.join(IMG, "saudi-women-work-chart.png"))
    plt.close(fig)


def long_run_chart():
    lf = series("Female", "participation_rate")
    qs = list(lf.index)
    x = list(range(len(qs)))
    fig = plt.figure(figsize=(10, 6.25), dpi=200)
    ax = fig.add_axes([0.07, 0.15, 0.80, 0.55])
    ax.plot(x, lf.value_pct, color=BLUE, linewidth=2.2)
    single = lf.verification == "single-document"
    ax.plot([i for i, s in zip(x, single) if not s], lf.value_pct[~single], linestyle="none", marker="o", markersize=5.5, color=BLUE, markeredgecolor=SURFACE, markeredgewidth=1.2)
    ax.plot([i for i, s in zip(x, single) if s], lf.value_pct[single], linestyle="none", marker="o", markersize=5.5, markerfacecolor=SURFACE, markeredgecolor=BLUE, markeredgewidth=1.4)
    for level, text in ((30, "Vision 2030 original target, 30%"), (40, "Ambition stated in October 2024, around 40%")):
        ax.axhline(level, color=SECOND, linewidth=1, linestyle=(0, (4, 3)))
        ax.text(0, level + 0.25, text, fontsize=9.5, color=SECOND, va="bottom")
    for q in ("2021-Q1", "2025-Q1", "2026-Q2"):
        i = qs.index(q)
        ax.annotate(f"{lf.value_pct[q]:.1f}%", (i, lf.value_pct[q]), xytext=(0, 10 if q != "2026-Q2" else -19), textcoords="offset points", ha="center", fontsize=11, fontweight="bold", color=INK)
    r = qs.index("2025-Q1")
    ax.axvline(r, color=MUTED, linewidth=0.9, linestyle=(0, (2, 3)))
    ax.text(r + 0.15, 32.4, "Questionnaire\nredesigned", fontsize=9, color=MUTED, va="top", linespacing=1.3)
    ax.set_ylim(28, 41.5)
    ax.set_xlim(-0.5, len(qs) + 2.2)
    ax.set_yticks(range(28, 42, 2))
    ax.set_yticklabels([f"{v}%" for v in range(28, 42, 2)])
    ax.set_xticks([i for i, q in zip(x, qs) if q.endswith("1")])
    ax.set_xticklabels([q[:4] for q in qs if q.endswith("1")])
    ax.text(len(qs) - 0.3, lf.value_pct.iloc[-1] + 0.9, "Saudi women in\nthe labour force", fontsize=10.5, color=INK, va="center", linespacing=1.3)
    frame(fig,
          "Participation by Saudi women passed the 30% target early.\nIt is now 6.3 points short of the 40% ambition.",
          "Labour force participation rate, Saudi women aged 15 and over, Q1 2021 to Q2 2026.\n"
          "Hollow points rest on one compiled table (GLMM); filled points were confirmed in a second document.")
    fig.savefig(os.path.join(IMG, "participation_since_2021.png"))
    plt.close(fig)


def change_chart():
    c = comp[comp.window == "two years"].set_index("sex")
    measures = [("participation_change_pts", "Participation rate"),
                ("employment_ratio_change_pts", "Share in work"),
                ("unemployment_rate_change_pts", "Unemployment rate")]
    fig = plt.figure(figsize=(10, 6.25), dpi=200)
    ax = fig.add_axes([0.20, 0.17, 0.72, 0.51])
    h = 0.34
    for k, (col, name) in enumerate(measures):
        y = len(measures) - 1 - k
        for sex, colour, off in (("Female", BLUE, h / 2 + 0.02), ("Male", ORANGE, -h / 2 - 0.02)):
            v = c.loc[sex, col]
            ax.barh(y + off, v, height=h, color=colour)
            ax.text(v + (0.08 if v >= 0 else -0.08), y + off, f"{v:+.1f}", va="center", ha="left" if v >= 0 else "right", fontsize=11, fontweight="bold", color=INK)
    ax.axvline(0, color=SECOND, linewidth=1)
    ax.set_yticks(range(len(measures)))
    ax.set_yticklabels([m[1] for m in measures][::-1], fontsize=11.5, color=INK)
    ax.set_xlim(-4, 1.6)
    ax.set_xticks(range(-4, 2))
    ax.set_xticklabels([f"{v:+d}" if v else "0" for v in range(-4, 2)])
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("Change in percentage points, Q2 2024 to Q2 2026", fontsize=10, color=MUTED, labelpad=8)
    handles = [plt.Rectangle((0, 0), 1, 1, color=BLUE), plt.Rectangle((0, 0), 1, 1, color=ORANGE)]
    fig.legend(handles, ["Saudi women", "Saudi men"], loc="upper left", bbox_to_anchor=(0.19, 0.745), ncol=2, frameon=False, fontsize=11, handlelength=1.1, handleheight=0.9, columnspacing=1.6)
    frame(fig,
          "Over two years the share of Saudi men in work fell 2.8 points.\nFor Saudi women it fell 0.3.",
          "Change in three labour market rates for Saudi nationals aged 15 and over, Q2 2024 to Q2 2026.", top=0.955)
    fig.savefig(os.path.join(IMG, "change_women_vs_men.png"))
    plt.close(fig)


if __name__ == "__main__":
    headline_chart()
    long_run_chart()
    change_chart()
    print("Charts written to images/")
