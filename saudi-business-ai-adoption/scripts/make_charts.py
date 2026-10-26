"""Make the charts for the Saudi business AI adoption project."""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / "images"
IMG.mkdir(exist_ok=True)

INK, MUTED, GRID = "#1f2328", "#5b636e", "#d9dde3"
C24, C25 = "#9aa4b1", "#1d5fa8"
SOURCE = ("Source: GASTAT, Establishments ICT Access and Usage Statistics 2024 and 2025. "
          "Share of establishments using the Internet that used AI technologies.")
AUTHOR = "Toheeb Adeboye, Data Analyst, Doha"

plt.rcParams.update({"font.family": "DejaVu Sans", "axes.edgecolor": GRID,
                     "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": INK})

df = pd.read_csv(ROOT / "data" / "processed" / "ai_use_by_sector.csv")
nat = df[df.isic_section == "ALL"].iloc[0]
sec = df[df.isic_section != "ALL"].sort_values("pct_2025")
SHORT = {"Wholesale and retail trade; repair of motor vehicles": "Wholesale, retail, vehicle repair",
         "Professional, scientific and technical": "Professional and technical",
         "Administrative and support service": "Administrative and support",
         "Arts, entertainment and recreation": "Arts and entertainment",
         "Agriculture, forestry and fishing": "Agriculture and fishing",
         "Human health and social work": "Health and social work"}
labels = [SHORT.get(s, s) for s in sec.sector]


def dumbbell(path, width_px=2000, dpi=200):
    fig, ax = plt.subplots(figsize=(width_px / dpi, 12.5), dpi=dpi)
    y = range(len(sec))
    ax.hlines(y, sec.pct_2024, sec.pct_2025, color=GRID, lw=3, zorder=1)
    ax.scatter(sec.pct_2024, y, s=70, color=C24, zorder=2, label="2024", edgecolor="white", lw=1.5)
    ax.scatter(sec.pct_2025, y, s=90, color=C25, zorder=3, label="2025", edgecolor="white", lw=1.5)
    for yi, (a, b) in enumerate(zip(sec.pct_2024, sec.pct_2025)):
        ax.text(b + 1.0, yi, f"{b:.1f}%", va="center", fontsize=10.5, color=INK, zorder=4,
                bbox=dict(facecolor="white", edgecolor="none", pad=1))
        ax.text(a - 1.0, yi, f"{a:.1f}", va="center", ha="right", fontsize=9, color=MUTED)
    ax.axvline(nat.pct_2025, color=C25, ls="--", lw=1.2, alpha=0.7, zorder=0)
    ax.text(nat.pct_2025 + 0.4, len(sec) - 0.35, f"All establishments 2025: {nat.pct_2025:.1f}%\n(2024: {nat.pct_2024:.1f}%)",
            fontsize=9.5, color=C25, va="bottom")
    ax.set_yticks(list(y))
    ax.set_yticklabels(labels, fontsize=10.5)
    ax.set_xlim(14, 68)
    ax.set_ylim(-0.7, len(sec) + 0.9)
    ax.xaxis.grid(True, color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.tick_params(axis="y", length=0)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.set_xlabel("Share of establishments using AI (%)", fontsize=10)
    ax.legend(loc="lower right", frameon=False, fontsize=10.5)
    fig.suptitle("Every sector of Saudi business used more AI in 2025.\nRetail, real estate and support services still sit below the national rate.",
                 x=0.02, ha="left", fontsize=17, fontweight="bold", color=INK, y=0.985)
    fig.text(0.02, 0.905, "Share of establishments using AI technologies by economic activity, Saudi Arabia, 2024 and 2025 (%)",
             fontsize=11, color=MUTED)
    fig.text(0.02, 0.018, f"{SOURCE}\n{AUTHOR}", fontsize=8.5, color=MUTED)
    fig.subplots_adjust(left=0.25, right=0.97, top=0.88, bottom=0.09)
    fig.savefig(path, facecolor="white")
    plt.close(fig)


def change_bars(path):
    s = sec.sort_values("change_pts")
    fig, ax = plt.subplots(figsize=(10, 7.5), dpi=150)
    lab = [SHORT.get(x, x) for x in s.sector]
    ax.barh(lab, s.change_pts, color=C25, height=0.62)
    for i, v in enumerate(s.change_pts):
        ax.text(v + 0.12, i, f"+{v:.1f}", va="center", fontsize=9, color=INK, zorder=4,
                bbox=dict(facecolor="white", edgecolor="none", pad=1))
    nat_change = nat.pct_2025 - nat.pct_2024
    ax.axvline(nat_change, color=INK, ls="--", lw=1)
    ax.text(nat_change + 0.1, len(s) - 0.4, f"All establishments +{nat_change:.1f}", fontsize=9, color=INK)
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.xaxis.grid(True, color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.set_xlabel("Change in share using AI, 2024 to 2025 (percentage points)")
    ax.set_title("Real estate and health rose least; utilities and mining most", loc="left", fontsize=13, fontweight="bold", color=INK)
    fig.text(0.01, 0.01, SOURCE, fontsize=7.5, color=MUTED)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(path, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    dumbbell(IMG / "saudi-business-ai-use-by-sector.png")
    change_bars(IMG / "change-by-sector.png")
    print("charts written")
