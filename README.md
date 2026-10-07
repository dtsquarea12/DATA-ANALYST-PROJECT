# Data Analysis Portfolio

**Toheeb Adeboye** · Data Analyst · Doha, Qatar · [LinkedIn](https://www.linkedin.com/in/dtsquarea/)

Public-data analysis projects. Each one starts with a single question, uses open sources, and ends with a written answer, a notebook that reproduces it, and where useful an interactive dashboard.

## Projects

| Project | Question | Tools | Links |
|---|---|---|---|
| [Gulf Fuel Subsidy Tracker](gulf-fuel-subsidy-tracker/) | Who is paying for cheap fuel in the Gulf since the 2026 Iran war began? | Python, SQL, JavaScript | [Dashboard](https://dtsquarea12.github.io/DATA-ANALYST-PROJECT/gulf-fuel-subsidy-tracker/) · [Write-up](gulf-fuel-subsidy-tracker/README.md) · [Notebook](gulf-fuel-subsidy-tracker/notebooks/fuel_subsidy_analysis.ipynb) |
| [Saudi Women in Work](saudi-women-workforce/) | Unemployment among Saudi women has fallen for two years. Are more of them working, or are fewer looking for work? | Python, SQL | [Write-up](saudi-women-workforce/README.md) · [Notebook](saudi-women-workforce/notebooks/saudi_women_work_analysis.ipynb) · [SQL](saudi-women-workforce/sql/analysis_queries.sql) |
| [Mobile Internet Speed by Country](mobile-internet-speed-by-country/) | Where in the world is mobile internet fastest, and how does it compare with fixed broadband in the same country? | Python, SQL | [Write-up](mobile-internet-speed-by-country/README.md) · [Notebook](mobile-internet-speed-by-country/notebooks/mobile_internet_speed_analysis.ipynb) · [SQL](mobile-internet-speed-by-country/sql/analysis_queries.sql) |

## Skills

- **Analysis:** data cleaning, exploratory analysis, comparison across time periods and countries, statistical checks on small or noisy series
- **Tools:** Python (pandas, matplotlib), SQL, Jupyter, JavaScript for interactive charts
- **Communication:** a written answer to each question, with the method, limitations and sources stated

## Repository layout

Each project folder follows the same structure:

```
project/
├── README.md        # question, findings, method, limitations, sources
├── notebooks/       # full analysis, reproducible end to end
├── sql/             # analysis queries
├── scripts/         # data build and chart scripts
├── data/raw/        # source data as downloaded
├── data/processed/  # cleaned and tidy outputs
├── docs/            # data dictionary
└── images/          # charts used in the write-up
```

## Example

![Gasoline pump price by month, Gulf countries against comparison countries](gulf-fuel-subsidy-tracker/images/gulf-fuel-prices-chart.png)

## License

Released under the [MIT License](LICENSE).
