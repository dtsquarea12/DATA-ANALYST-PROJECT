"""Make the charts for the AI skills in job ads project."""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
IMG = ROOT / "images"
IMG.mkdir(exist_ok=True)
INK, MUTED, GRID = "#1f2328", "#5b636e", "#d9dde3"
BLUE, GREY, RED = "#1d5fa8", "#9aa4b1", "#b4442c"
AUTHOR = "Toheeb Adeboye, Data Analyst, Doha"
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.edgecolor": GRID, "axes.labelcolor": MUTED,
                     "xtick.color": MUTED, "ytick.color": INK})


def clean(ax):
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.xaxis.grid(True, color=GRID, lw=0.6)
    ax.set_axisbelow(True)


def frame(fig, title, subtitle, source):
    h = fig.get_size_inches()[1]
    fig.text(0.04, 1 - 0.3 / h, title, fontsize=21, fontweight="bold", color=INK, va="top")
    fig.text(0.04, 1 - 1.25 / h, subtitle, fontsize=12, color=MUTED, va="top", linespacing=1.4)
    fig.text(0.04, 0.02, f"{AUTHOR}  |  {source}", fontsize=9.5, color=MUTED, va="bottom")


def roles_chart():
    r = pd.read_csv(PROC / "gulf_ai_vacancies_by_role.csv").sort_values("share_of_ai_vacancies_pct")
    fig, ax = plt.subplots(figsize=(10, 6.2), dpi=200)
    fig.subplots_adjust(left=0.30, right=0.93, top=0.70, bottom=0.17)
    colors = [RED if "Building" in x else BLUE for x in r.role]
    labels = {"Implementing AI": "Implementing and rolling\nout AI in the business",
              "Using AI in the job": "Using AI as part\nof the day-to-day job",
              "Selling AI products and services": "Selling AI products\nand services",
              "Building and training AI models": "Building and training\nAI models"}
    ax.barh([labels[x] for x in r.role], r.share_of_ai_vacancies_pct, color=colors, height=0.62)
    for i, val in enumerate(r.share_of_ai_vacancies_pct):
        ax.text(val + 0.8, i, f"{val:.0f}%", va="center", fontsize=15, fontweight="bold", color=INK)
    ax.set_xlim(0, 40)
    ax.set_xlabel("Share of AI-linked vacancies (%)", fontsize=11)
    ax.tick_params(axis="y", labelsize=12.5)
    clean(ax)
    frame(fig, "Only 9 in 100 AI-linked Gulf job ads are for\npeople who build AI",
          "What AI-linked vacancies ask the worker to do with AI. UAE, Saudi Arabia and Qatar, first half of 2026.\n"
          "AI is mentioned in 3.4% of all professional vacancies, up from 1.2% in 2022.",
          "Source: GulfTalent analysis of 118,000 vacancies (Jan 2022 to Jun 2026), as reported July 2026")
    fig.savefig(IMG / "ai-skills-in-job-ads.png", facecolor="white")
    plt.close(fig)


def sector_chart():
    s = pd.read_csv(PROC / "gulf_ai_share_by_sector.csv")
    s = s.sort_values("ratio_pct")
    fig, ax = plt.subplots(figsize=(10, 6.6), dpi=200)
    fig.subplots_adjust(left=0.20, right=0.93, top=0.66, bottom=0.15)
    colors = [BLUE if v >= 3 else GREY for v in s.ratio_pct]
    ax.barh(s.sector, s.ratio_pct, color=colors, height=0.62)
    for i, row in enumerate(s.itertuples()):
        lab = f"about {row.published_ratio}" if "fewer" not in row.published_ratio else row.published_ratio
        ax.text(row.ratio_pct + 0.4, i, lab, va="center", fontsize=10.5, color=INK)
    ax.set_xlim(0, 42)
    ax.set_xlabel("Share of vacancies mentioning AI (%), as the ratio published", fontsize=10.5)
    clean(ax)
    frame(fig, "In the Gulf, AI shows up in tech and finance job ads,\nbarely in clinics, shops and hotels",
          "Share of professional vacancies that mention AI duties, skills or tools, by sector.\n"
          "UAE, Saudi Arabia and Qatar, first half of 2026.\n"
          "Bars show the published ratio (\"1 in 30\" = 3.3%); the bottom six sectors were published as one group.",
          "Source: GulfTalent, as reported by Zawya, TradeArabia, Fast Company ME and others, July 2026")
    fig.savefig(IMG / "gulf-ai-share-by-sector.png", facecolor="white")
    plt.close(fig)


def country_chart():
    c = pd.read_csv(PROC / "ai_share_by_country_2025.csv")
    c = c.iloc[::-1]
    fig, ax = plt.subplots(figsize=(10, 9.5), dpi=200)
    fig.subplots_adjust(left=0.30, right=0.93, top=0.80, bottom=0.10)
    colors = [RED if x == "Middle East" else BLUE if x == "Asia" else GREY for x in c.region]
    ax.barh([f"{n}  ({r})" for n, r in zip(c.country, c.region)], c.ai_share_pct_2025, color=colors, height=0.7)
    for i, val in enumerate(c.ai_share_pct_2025):
        ax.text(val + 0.05, i, f"{val:.2f}", va="center", fontsize=9.5, color=INK)
    ax.set_xlim(0, 5.4)
    ax.tick_params(axis="y", labelsize=9.5)
    ax.set_xlabel("AI job postings, % of all job postings, 2025", fontsize=10.5)
    clean(ax)
    frame(fig, "The UAE ranks 7th of 22 economies for job ads\nthat ask for AI skills",
          "AI job postings as a share of all online job postings, 2025. Grouped by region, Middle East first,\n"
          "then by value within each region. The AI Index publishes 22 economies;\n"
          "the UAE is the only Middle East economy among them.",
          "Source: Stanford AI Index Report 2026, Chapter 4 (Lightcast data)")
    fig.savefig(IMG / "ai-share-by-country-2025.png", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    roles_chart()
    sector_chart()
    country_chart()
    print("charts written")
