# Data dictionary

All shares are percentages (3.4 means 3.4%).

## data/raw/readings.csv

One row per figure per document. 291 rows from 16 documents.

| Column | Description |
|---|---|
| dataset | `gulftalent` (GulfTalent vacancy analysis), `pwc_lightcast` (PwC 2026 AI Jobs Barometer, Lightcast data), `ai_index_lightcast` (Stanford AI Index 2026, Lightcast data) |
| geography | Country, group of countries or average the figure covers |
| segment | What part of the job market the figure covers: all vacancies, a sector, a seniority level, a role type, or a count of AI-skill postings |
| period | Year, or `2026H1` for January to June 2026 |
| measure | `share_pct` exact share; `share_ratio` share printed as "1 in N"; `share_pct_max` upper bound ("1% or less"); `share_pct_approx` ("nearly 10%"); `role_share_pct` and `role_share_ratio` share of AI-linked vacancies by role type; `postings_thousand` AI-skill postings in thousands; `postings_change_thousand` change in thousands; `vacancies_analysed`, `vacancies_classified` sample sizes |
| value_printed | The number as printed, kept as text so its precision is preserved; empty for ratio rows |
| ratio_printed | The ratio as printed, for example `1 in 30`; empty for number rows |
| source_id | Document the figure was read from (see sources.csv) |
| note | Context. Rows starting `set_aside` are kept for the record but not used |

## data/raw/sources.csv

| Column | Description |
|---|---|
| source_id | Key used in readings.csv |
| publisher | Who published the document |
| kind | report PDF, report page or news |
| title | Document title |
| date | Publication date (month when the day is not printed) |
| url | Link |

## data/processed/readings_tidy.csv

One row per figure after the documents are reconciled (104 rows).

| Column | Description |
|---|---|
| dataset, geography, segment, period, measure | As in readings.csv |
| value | Most precise printed value; for ratio rows, 100 / N |
| ratio_printed | Ratio wording, for ratio rows |
| n_sources | Number of documents printing the figure |
| verification | `two-or-more-documents` or `one-document` |
| source_ids | Documents, separated by `;` |
| note | First note attached to the readings |

## data/processed/ai_share_trend.csv

| Column | Description |
|---|---|
| series | Data series and geography |
| source | GulfTalent or PwC AI Jobs Barometer 2026 |
| period | Year or `2026H1` |
| share_pct | Share of vacancies or postings that mention AI skills |
| verification | As above |

## data/processed/gulf_ai_share_by_sector.csv

UAE, Saudi Arabia and Qatar combined, H1 2026 (GulfTalent).

| Column | Description |
|---|---|
| sector | Sector as named by GulfTalent |
| published_ratio | Ratio printed by most reports |
| ratio_pct | Ratio as a percentage (1 in 30 = 3.33) |
| exact_pct | Exact percentage, printed by one outlet (Middle East AI News); empty where only an upper bound was printed |
| exact_is_upper_bound | True where the exact figure is printed only as "1% or less" for a group of sectors |
| ratio_sources, exact_sources | Number of documents printing each |

## data/processed/gulf_ai_vacancies_by_role.csv

| Column | Description |
|---|---|
| role | What the AI-linked vacancy asks the worker to do with AI |
| share_of_ai_vacancies_pct | Share of AI-linked vacancies (420 classified, H1 2026); the four add to 100 |
| n_sources | Documents printing the exact figure |

## data/processed/ai_share_by_country_2025.csv

| Column | Description |
|---|---|
| region | Middle East, Asia, Europe, Americas, Oceania |
| country | Economy as named in the AI Index |
| ai_share_pct_2025 | AI job postings as a share of all job postings, 2025 |
| rank | Rank among the 22 economies (1 = highest) |
| n_sources, verification | As above |

## data/processed/us_ai_share_by_sector.csv

| Column | Description |
|---|---|
| sector | US industry sector (NAICS-based names as printed) |
| share_2024_pct, share_2025_pct | AI job postings as a share of all postings in the sector |
| change_pts | Change in percentage points |

## data/processed/headline_figures.csv

| Column | Description |
|---|---|
| figure | Name of the headline figure |
| value | Value used in the README and post |
