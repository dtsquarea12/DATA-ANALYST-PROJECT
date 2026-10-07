"""Draw the project charts from data/processed/speed_by_country.csv.

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

BLUE, ORANGE = "#2a78d6", "#eb6834"
INK, SECOND, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#898781", "#e4e3df", "#fcfcfb"
FOOT = ("Analysis: Toheeb Adeboye. Source: Ookla Speedtest Global Index, March 2026, median download speed by country.\n"
        "Medians of tests run by Speedtest users, so they describe typical tested connections, not coverage.")

fonts = {f.name for f in font_manager.fontManager.ttflist}
plt.rcParams.update({
    "font.family": "Inter" if "Inter" in fonts else "DejaVu Sans",
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False, "axes.spines.bottom": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
    "xtick.color": MUTED, "ytick.color": SECOND, "xtick.labelsize": 10, "ytick.labelsize": 11,
    "xtick.major.size": 0, "ytick.major.size": 0, "axes.axisbelow": True,
})

country = pd.read_csv(os.path.join(DATA, "speed_by_country.csv"))


def frame(fig, title, subtitle, gap):
    fig.text(0.04, 0.96, title, fontsize=21, fontweight="bold", color=INK, va="top", linespacing=1.12)
    fig.text(0.04, 0.96 - gap, subtitle, fontsize=12, color=SECOND, va="top", linespacing=1.45)
    fig.text(0.04, 0.022, FOOT, fontsize=9, color=MUTED, va="bottom", linespacing=1.4)


def legend(fig, entries, y):
    fig.legend(handles=[Patch(facecolor=c, label=l) for l, c in entries], loc="upper left",
               bbox_to_anchor=(0.035, y), ncol=len(entries), frameon=False, fontsize=11, labelcolor=SECOND,
               handlelength=1.1, handleheight=0.9, columnspacing=1.8)


def top20_chart():
    d = country[country.mobile_rank_published <= 20].sort_values("mobile_rank_published")
    gcc = list(d.gcc_member == "yes")
    fig = plt.figure(figsize=(10, 9), dpi=200)
    ax = fig.add_axes([0.27, 0.115, 0.67, 0.655])
    y = range(len(d))
    ax.barh(y, d.mobile_mbps, height=0.66, color=[ORANGE if g else BLUE for g in gcc], zorder=3)
    ax.set_yticks(list(y))
    ax.set_yticklabels([f"{int(r)}. {c}" for c, r in zip(d.country, d.mobile_rank_published)])
    for lab, g in zip(ax.get_yticklabels(), gcc):
        lab.set_color(INK if g else SECOND)
        lab.set_fontweight("bold" if g else "normal")
    for yi, v, g in zip(y, d.mobile_mbps, gcc):
        ax.text(v + 8, yi, f"{v:.0f}", va="center", ha="left", fontsize=10.5, color=INK if g else SECOND,
                fontweight="bold" if g else "normal")
    ax.invert_yaxis()
    ax.set_ylim(len(d) - 0.4, -0.6)
    ax.set_xlim(0, 720)
    ax.grid(axis="y", visible=False)
    frame(fig, "All six Gulf states are in the world's top 20\nfor mobile internet speed",
          "Median mobile download speed in megabits per second, March 2026. The number before each\n"
          "country is its world rank. The UAE's median is three times that of the United States.", gap=0.092)
    legend(fig, [("Gulf Cooperation Council states", ORANGE), ("Other countries", BLUE)], 0.815)
    fig.savefig(os.path.join(IMG, "mobile-internet-speed-chart.png"))
    plt.close(fig)


def mobile_vs_fixed_chart():
    names = ["United Arab Emirates", "Qatar", "Kuwait", "Bahrain", "Saudi Arabia", "Oman",
             "India", "Nigeria", "South Korea", "Germany", "United States", "Singapore",
             "United Kingdom", "France", "Japan"]
    d = country.set_index("country").loc[names]
    fig = plt.figure(figsize=(10, 9.4), dpi=200)
    ax = fig.add_axes([0.25, 0.11, 0.69, 0.665])
    h = 0.36
    for i, (name, r) in enumerate(d.iterrows()):
        ax.barh(i - h / 2 - 0.02, r.mobile_mbps, height=h, color=BLUE, zorder=3)
        ax.barh(i + h / 2 + 0.02, r.fixed_mbps, height=h, color=ORANGE, zorder=3)
        ax.text(r.mobile_mbps + 8, i - h / 2 - 0.02, f"{r.mobile_mbps:.0f}", va="center", fontsize=9.5, color=SECOND)
        ax.text(r.fixed_mbps + 8, i + h / 2 + 0.02, f"{r.fixed_mbps:.0f}", va="center", fontsize=9.5, color=SECOND)
    ax.set_yticks(range(len(names)))
    ax.set_yticklabels(names)
    ax.axhline(5.5, color=GRID, linewidth=1.2)
    ax.invert_yaxis()
    ax.set_ylim(len(names) - 0.4, -0.6)
    ax.set_xlim(0, 720)
    ax.grid(axis="y", visible=False)
    frame(fig, "In the Gulf, mobile is faster than fixed broadband.\nIn Singapore, France and Japan it is the reverse.",
          "Median download speed in megabits per second, March 2026. Gulf states first,\n"
          "then nine other countries ordered from mobile-led to fixed-led.", gap=0.09)
    legend(fig, [("Mobile", BLUE), ("Fixed broadband", ORANGE)], 0.822)
    fig.savefig(os.path.join(IMG, "mobile_vs_fixed.png"))
    plt.close(fig)


if __name__ == "__main__":
    top20_chart()
    mobile_vs_fixed_chart()
    print("charts written to images/")
