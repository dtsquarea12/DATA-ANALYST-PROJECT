"""Make the charts for the AI use by firm size project."""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / "images"
IMG.mkdir(exist_ok=True)

INK, MUTED, GRID = "#1f2328", "#5b636e", "#d9dde3"
C_TR, C_EU, C_OLD = "#b4442c", "#1d5fa8", "#c4cad3"
AUTHOR = "Toheeb Adeboye, Data Analyst, Doha"
SOURCE = ("Sources: TurkStat, Artificial Intelligence Statistics 2025 (as printed by Alomaliye, CNBC-e, Ensonhaber);\n"
          "Eurostat, Use of artificial intelligence in enterprises (2024 and 2025 data).\n"
          "Enterprises with 10 or more employees. Small 10 to 49, medium 50 to 249, large 250 or more employees.")

plt.rcParams.update({"font.family": "DejaVu Sans", "axes.edgecolor": GRID,
                     "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": INK})

use = pd.read_csv(ROOT / "data" / "processed" / "ai_use_by_size.csv")
tidy = pd.read_csv(ROOT / "data" / "processed" / "ai_use_tidy.csv")
SIZES = [("small_pct", "Small\n10 to 49 staff"), ("medium_pct", "Medium\n50 to 249 staff"), ("large_pct", "Large\n250+ staff")]


def clean(ax):
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.xaxis.grid(True, color=GRID, lw=0.6)
    ax.set_axisbelow(True)


def panel(ax, econ, latest, earlier, colour, title):
    a = use[(use.economy == econ) & (use.year == latest)].iloc[0]
    b = use[(use.economy == econ) & (use.year == earlier)].iloc[0]
    y = range(len(SIZES))
    ax.barh([i + 0.2 for i in y], [b[c] for c, _ in SIZES], height=0.36, color=C_OLD, label=str(earlier))
    ax.barh([i - 0.2 for i in y], [a[c] for c, _ in SIZES], height=0.36, color=colour, label=str(latest))
    for i, (c, _) in enumerate(SIZES):
        ax.text(a[c] + 0.8, i - 0.2, f"{a[c]:.1f}%", va="center", fontsize=12, fontweight="bold", color=INK)
        ax.text(b[c] + 0.8, i + 0.2, f"{b[c]:.1f}%", va="center", fontsize=10, color=MUTED)
    ax.set_yticks(list(y))
    ax.set_yticklabels([l for _, l in SIZES], fontsize=11)
    ax.invert_yaxis()
    ax.set_xlim(0, 64)
    ax.text(0, 1.11, title, transform=ax.transAxes, fontsize=13.5, fontweight="bold", color=INK, va="bottom")
    ax.text(0, 1.0, f"Large firms {a.large_pct / a.small_pct:.1f} times as likely as small firms; gap {a.gap_large_minus_small_pts:.1f} points "
            f"({earlier}: {b.gap_large_minus_small_pts:.1f})", transform=ax.transAxes, fontsize=10.5, color=MUTED, va="bottom")
    ax.legend(loc="lower right", frameon=False, fontsize=10.5)
    clean(ax)


def headline(path, width_px=2000, dpi=200):
    fig, axes = plt.subplots(2, 1, figsize=(width_px / dpi, 12), dpi=dpi)
    panel(axes[0], "Turkey", 2025, 2021, C_TR, "Turkey (Middle East)")
    panel(axes[1], "EU-27", 2025, 2024, C_EU, "European Union")
    axes[1].set_xlabel("Share of enterprises using at least one AI technology (%)", fontsize=10.5)
    fig.suptitle("Large firms are more than three times as likely\nto use AI as small firms. In points, the gap\ngrew in both Turkey and the EU.",
                 x=0.03, ha="left", fontsize=19, fontweight="bold", color=INK, y=0.985)
    fig.text(0.03, 0.845, "Share of enterprises using AI by number of employees, Turkey 2021 and 2025, EU 2024 and 2025 (%)",
             fontsize=11.5, color=MUTED)
    fig.text(0.03, 0.015, f"{SOURCE}\n{AUTHOR}", fontsize=8.5, color=MUTED)
    fig.subplots_adjust(left=0.17, right=0.97, top=0.75, bottom=0.13, hspace=0.6)
    fig.savefig(path, facecolor="white")
    plt.close(fig)


def reasons(path):
    r = tidy[tidy.measure == "reason_not_used"]
    fig, ax = plt.subplots(figsize=(10, 4.8), dpi=150)
    rows = [("Turkey", "Lack of relevant expertise"), ("EU-27", "Lack of relevant expertise"),
            ("Turkey", "Costs too high"), ("Turkey", "Legal uncertainty about liability for harm caused by AI"),
            ("EU-27", "Legal uncertainty about consequences"), ("EU-27", "Data protection and privacy concerns")]
    vals = [r[(r.economy == e) & (r["item"] == i)].value.iloc[0] for e, i in rows]
    labels = [f"{'Turkey' if e == 'Turkey' else 'EU'}: {i.replace('Legal uncertainty about liability for harm caused by AI', 'Legal uncertainty about liability')}" for e, i in rows]
    cols = [C_TR if e == "Turkey" else C_EU for e, _ in rows]
    ax.barh(labels, vals, color=cols, height=0.6)
    for i, v in enumerate(vals):
        ax.text(v + 1, i, f"{v:.1f}%", va="center", fontsize=10, color=INK)
    ax.invert_yaxis()
    ax.set_xlim(0, 90)
    clean(ax)
    ax.set_xlabel("Share of enterprises that considered AI but did not use it, citing the reason (%)", fontsize=9.5)
    fig.suptitle("Lack of expertise is the most cited reason for not using AI, 2025", x=0.02, ha="left",
                 fontsize=13, fontweight="bold", color=INK)
    fig.text(0.02, 0.01, "Sources: TurkStat 2025 (via Alomaliye, CNBC-e, Ensonhaber); Eurostat 2025 (confirmed in EESC policy note). "
             "Several reasons could be chosen.\nTurkStat's published list and Eurostat's published list differ, so only the reasons each printed are shown. "
             + AUTHOR, fontsize=7.5, color=MUTED)
    fig.subplots_adjust(left=0.4, right=0.97, top=0.88, bottom=0.2)
    fig.savefig(path, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    headline(IMG / "ai-use-by-firm-size.png")
    reasons(IMG / "reasons-not-using-ai.png")
    print("charts written")
