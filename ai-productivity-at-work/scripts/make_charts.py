"""Make the charts for the AI productivity at work project."""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / "images"
IMG.mkdir(exist_ok=True)
INK, MUTED, GRID = "#1f2328", "#5b636e", "#d9dde3"
C_TASK, C_JOB, C_LEAST, C_MOST = "#1d5fa8", "#b4442c", "#1d5fa8", "#9aa4b1"
AUTHOR = "Toheeb Adeboye, Data Analyst, Doha"
SOURCE = ("Sources: Peng et al. (arXiv 2023); Noy and Zhang (Science 2023); Cui et al. (Management Science 2025); Dell'Acqua et al. (Organization Science 2025);\n"
          "Brynjolfsson, Li and Raymond (QJE 2025); Federal Reserve Bank of St. Louis (2025, Real-Time Population Survey); Humlum and Vestergaard (BFI working paper 2025).\n"
          "Each figure is the study's own published estimate; measures differ between studies and are not averaged.")
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.edgecolor": GRID, "axes.labelcolor": MUTED,
                     "xtick.color": MUTED, "ytick.color": INK})

head = pd.read_csv(ROOT / "data" / "processed" / "study_headlines.csv")
exp = pd.read_csv(ROOT / "data" / "processed" / "gain_by_experience.csv")
NAMES = {"coding_test": "Programming test task\n95 developers recruited, randomised",
         "writing": "Professional writing tasks\n453 professionals, randomised",
         "developers_field": "Developers at three companies\n4,867 developers, randomised",
         "consulting": "Consultants on 18 consulting tasks\n758 consultants, randomised",
         "support": "Customer support chats\n5,172 agents at one firm",
         "us_survey": "US workers who use AI\nnational survey, Nov 2024",
         "denmark": "Danish workers who use AI\n25,000 workers, 11 occupations"}


def clean(ax):
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.xaxis.grid(True, color=GRID, lw=0.6)
    ax.set_axisbelow(True)


def headline(path, width_px=2000, dpi=200):
    fig, ax = plt.subplots(figsize=(width_px / dpi, 11), dpi=dpi)
    y = list(range(len(head)))
    cols = [C_JOB if s == "whole job" else C_TASK for s in head.scope]
    ax.barh(y, head.gain_pct, color=cols, height=0.62)
    for i, r in head.iterrows():
        val = f"{r.gain_pct:.1f}%" if r.gain_pct % 1 else f"{r.gain_pct:.0f}%"
        ax.text(r.gain_pct + 0.8, i, f"{val} {r.effect_label.split(',')[0]}", va="center", fontsize=10.5, color=INK,
                fontweight="bold")
    ax.set_yticks(y)
    ax.set_yticklabels([NAMES[s] for s in head.study_id], fontsize=10)
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.axhline(4.5, color=MUTED, lw=0.8, ls=(0, (3, 3)))
    ax.text(99, 4.4, "Controlled studies of one kind of work", ha="right", va="bottom", fontsize=10, color=C_TASK, fontweight="bold")
    ax.text(99, 4.6, "Surveys of the whole working week", ha="right", va="top", fontsize=10, color=C_JOB, fontweight="bold")
    ax.set_xlabel("Measured effect of AI assistance (%)", fontsize=10.5)
    clean(ax)
    fig.suptitle("Give AI one defined task and studies measure improvements of 15% to 56%.\nAcross the whole working week, users save 3% to 5% of their hours.",
                 x=0.03, ha="left", fontsize=16, fontweight="bold", color=INK, y=0.975)
    fig.text(0.03, 0.885, "Published estimates from five controlled studies and two worker surveys, 2023 to 2025. Each bar uses the study's own measure.",
             fontsize=10.5, color=MUTED)
    fig.text(0.03, 0.012, f"{SOURCE}\n{AUTHOR}", fontsize=7.6, color=MUTED)
    fig.subplots_adjust(left=0.33, right=0.97, top=0.86, bottom=0.15)
    fig.savefig(path, facecolor="white")
    plt.close(fig)


def by_experience(path):
    fig, ax = plt.subplots(figsize=(10, 4.6), dpi=150)
    for i, r in exp.iterrows():
        ax.plot([r.least_low, r.least_high], [i - 0.15] * 2, color=C_LEAST, lw=10, solid_capstyle="butt")
        ax.plot([r.least_low], [i - 0.15], "o", color=C_LEAST, ms=9)
        lab = f"{r.least_low:.0f}%" if r.least_low == r.least_high else f"{r.least_low:.0f}% to {r.least_high:.0f}%"
        ax.text(r.least_high + 1.2, i - 0.15, f"least experienced {lab}", va="center", fontsize=9.5, color=C_LEAST)
        if pd.notna(r.most_low):
            ax.plot([r.most_low, r.most_high], [i + 0.18] * 2, color=C_MOST, lw=10, solid_capstyle="butt")
            ax.plot([r.most_low], [i + 0.18], "o", color=C_MOST, ms=9)
            lab = f"{r.most_low:.0f}%" if r.most_low == r.most_high else f"{r.most_low:.0f}% to {r.most_high:.0f}%"
            ax.text(r.most_high + 1.2, i + 0.18, f"most experienced {lab}", va="center", fontsize=9.5, color=MUTED)
        else:
            ax.text(0.5, i + 0.18, "most experienced: small gains in speed, small declines in quality (no figure printed)",
                    va="center", fontsize=9, color=MUTED, style="italic")
    ax.set_yticks(range(len(exp)))
    ax.set_yticklabels(exp.study, fontsize=10)
    ax.set_ylim(2.6, -0.6)
    ax.set_xlim(0, 70)
    ax.set_xlabel("Measured gain with AI assistance (%)")
    ax.set_title("The least experienced staff gain the most", loc="left", fontsize=13, fontweight="bold", color=INK)
    clean(ax)
    fig.text(0.01, 0.01, "Sources: Dell'Acqua et al. 2025; Cui et al. 2025 (ranges across three experiments, MIT Sloan summary); Brynjolfsson, Li and Raymond 2025. "
             + AUTHOR, fontsize=7, color=MUTED)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(path, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    headline(IMG / "ai-productivity-at-work.png")
    by_experience(IMG / "gain-by-experience.png")
    print("charts written")
