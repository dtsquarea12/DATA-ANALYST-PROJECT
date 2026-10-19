"""Draw the charts for middle-east-airport-passengers from data/processed."""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "data" / "processed"
IMG = ROOT / "images"
IMG.mkdir(exist_ok=True)

FAST, SLOW, INK, MUTED = "#1f6f8b", "#a9c4cf", "#1d2327", "#5f6b73"
WORLD = 3.6
FOOT = ("Toheeb Adeboye, Data Analyst  |  Sources: airport operators, GASTAT, ACI World (preliminary 2025), "
        "Anadolu Agency, NTV, Reuters, AACO, Gulf News, Petra, Zawya")

plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False})


def main_chart():
    s = pd.read_csv(P / "airports_2025.csv").sort_values("pax_2025")
    fig, ax = plt.subplots(figsize=(10, 7.2), dpi=200)
    colors = ["#d5d9dc" if c != c else (FAST if c > WORLD else SLOW) for c in s["change_vs_2024_pct"]]
    labels = [f"{a} ({c})" for a, c in zip(s["airport"], s["airport_code"])]
    ax.barh(labels, s["pax_2025_m"], color=colors, height=0.68)
    for y, (v, c) in enumerate(zip(s["pax_2025_m"], s["change_vs_2024_pct"])):
        g = "2024 not available" if c != c else f"{c:+.1f}%"
        ax.text(v + 1, y, f"{v:.1f}m   {g}", va="center", fontsize=9.5, color=INK)
    ax.set_xlim(0, 118)
    ax.set_xlabel("Passengers in 2025, millions", color=MUTED)
    ax.tick_params(axis="y", labelsize=9.5, colors=INK, length=0)
    ax.tick_params(axis="x", colors=MUTED)
    fig.suptitle("Dubai led the Middle East with 95.2 million passengers in 2025.\n9 of 12 airports grew faster than the world's +3.6%.",
                 x=0.02, y=0.985, ha="left", fontsize=15, fontweight="bold", color=INK)
    fig.text(0.02, 0.885, "Total passengers in 2025 and % change on 2024, 13 airports. Dark bars: growth above the world figure of +3.6% (ACI World).",
             fontsize=9.5, color=MUTED)
    fig.text(0.02, 0.012, FOOT, fontsize=7.2, color=MUTED)
    fig.subplots_adjust(left=0.34, right=0.97, top=0.86, bottom=0.10)
    fig.savefig(IMG / "middle-east-airports-2025.png")
    plt.close(fig)


def vs_2019_chart():
    s = pd.read_csv(P / "airports_2025.csv").dropna(subset=["change_vs_2019_pct"]).sort_values("change_vs_2019_pct")
    fig, ax = plt.subplots(figsize=(10, 5), dpi=200)
    labels = [f"{a} ({c})" for a, c in zip(s["airport"], s["airport_code"])]
    ax.barh(labels, s["change_vs_2019_pct"], color=FAST, height=0.6)
    ax.axvline(7.3, color=INK, lw=1, ls="--")
    ax.text(7.8, -0.55, "World +7.3%", fontsize=9, color=INK)
    for y, v in enumerate(s["change_vs_2019_pct"]):
        ax.text(v + 0.8, y, f"{v:+.1f}%", va="center", fontsize=9.5, color=INK)
    ax.set_xlim(0, 52)
    ax.set_xlabel("Passengers in 2025 against 2019, % change", color=MUTED)
    ax.tick_params(axis="y", length=0)
    fig.suptitle("Passengers in 2025 against 2019, airports with a published 2019 count",
                 x=0.02, y=0.97, ha="left", fontsize=13, fontweight="bold", color=INK)
    fig.text(0.02, 0.015, FOOT, fontsize=6.5, color=MUTED)
    fig.subplots_adjust(left=0.30, right=0.97, top=0.86, bottom=0.16)
    fig.savefig(IMG / "change-vs-2019.png")
    plt.close(fig)


if __name__ == "__main__":
    main_chart()
    vs_2019_chart()
