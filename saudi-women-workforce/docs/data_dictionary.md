# Data dictionary

All rates are percentages for people aged 15 and over, from the Labour Force Survey of the General Authority for Statistics (GASTAT), Saudi Arabia.

## data/processed/saudi_labour_tidy.csv

The main analysis table. One row per quarter, nationality, sex and indicator. 160 rows.

| Column | Type | Description |
|---|---|---|
| `quarter` | text (YYYY-Qn) | Calendar quarter of the survey, for example `2026-Q2` |
| `quarter_start` | date (YYYY-MM-DD) | First day of the quarter, for use as a date axis in Power BI or Tableau |
| `year` | integer | Calendar year |
| `quarter_number` | integer | 1 to 4 |
| `nationality` | text | `Saudi` or `Non-Saudi` |
| `sex` | text | `Female`, `Male` or `Total`. Non-Saudi rows are `Female` only |
| `indicator` | text | `participation_rate`, `employment_to_population` or `unemployment_rate` (defined below) |
| `value_pct` | number | The rate in percent, one decimal, as published |
| `n_documents` | integer | Number of separate documents in the raw file that report this figure |
| `n_publishers` | integer | Number of separate publishers among those documents |
| `verification` | text | `two-publishers`: GASTAT and at least one other publisher agree. `two-gastat-releases`: repeated in two GASTAT releases. `single-document`: read from one document only |
| `survey_design` | text | `earlier questionnaire` up to Q4 2024, `2025 questionnaire` from Q1 2025, when GASTAT redesigned the questionnaire and drew a new sample |

**Indicators**

| Indicator | Definition |
|---|---|
| `participation_rate` | People working or looking for work, as a share of everyone aged 15 and over in the group |
| `employment_to_population` | People working, as a share of everyone aged 15 and over in the group. Called "share in work" in the write-up |
| `unemployment_rate` | People looking for work, as a share of the labour force (those working or looking) |

**Coverage.** Participation: Q1 2021 to Q2 2026, 22 quarters. Employment ratio and unemployment rate: Q2 2023 and Q4 2023 to Q2 2026, 12 quarters. Q3 2023 is not in the documents collected and is left missing.

## data/processed/window_comparisons.csv

Start-to-end comparisons for Saudi women and Saudi men over three windows. 6 rows.

| Column | Type | Description |
|---|---|---|
| `window` | text | `two years` (Q2 2024 to Q2 2026), `one year` (Q2 2025 to Q2 2026) or `since 2025 redesign` (Q1 2025 to Q2 2026) |
| `sex` | text | `Female` or `Male`, Saudi nationals |
| `start_quarter`, `end_quarter` | text | The two quarters compared |
| `participation_start`, `participation_end` | number | Participation rate at each end, percent |
| `participation_change_pts` | number | End minus start, percentage points |
| `employment_ratio_start`, `employment_ratio_end` | number | Employment-to-population ratio at each end, percent |
| `employment_ratio_change_pts` | number | End minus start, percentage points |
| `unemployment_rate_start`, `unemployment_rate_end` | number | Unemployment rate at each end, percent |
| `unemployment_rate_change_pts` | number | End minus start, percentage points |
| `unemployed_share_start`, `unemployed_share_end` | number | Participation rate minus employment ratio: unemployed people as a share of everyone aged 15 and over in the group |
| `unemployment_rate_end_if_participation_unchanged` | number | `100 x (1 - employment ratio at end / participation rate at start)`. The unemployment rate the end-quarter employment level would give if participation had not moved. A calculation, not a published figure |

## data/raw/saudi_labour_readings_by_source.csv

Every figure as read from each document. 337 rows from 15 documents. The same figure appears once for each document that reports it, which is what allows the cross-check.

| Column | Type | Description |
|---|---|---|
| `quarter` | text (YYYY-Qn) | Quarter the figure refers to, not the publication date |
| `nationality` | text | `Saudi` or `Non-Saudi` |
| `sex` | text | `Female`, `Male` or `Total` |
| `indicator` | text | As defined above |
| `value_pct` | number | The rate in percent |
| `source` | text | Document the figure was read from |
| `source_type` | text | `official release`, `official news item`, `news report`, `research compilation`, `bank research` or `independent analysis` |
| `source_url` | text | Link to the document |
| `note` | text | Table reference or caveat. The Q2 2026 GASTAT release was read from a copy of the PDF hosted by a news site |
