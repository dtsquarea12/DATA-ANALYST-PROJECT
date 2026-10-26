# Data dictionary

## data/raw/ai_use_readings.csv

One row per figure per document per reading (138 rows).

| Column | Type | Description |
|---|---|---|
| year | integer | Survey year the figure refers to (2024 or 2025) |
| isic_section | text | ISIC Rev.4 section letter of the economic activity; `ALL` for all establishments |
| sector | text | Name of the economic activity |
| raw | text | Value exactly as printed (percent, one decimal) |
| value | number | Value as a number |
| source_id | text | Document the value was read from, see `sources.csv` |
| reading | text | `a` or `b`; GASTAT documents were read twice with different requests |
| note | text | Where the value was found (chart label, text). Rows starting `set aside` are excluded, with the reason |

## data/raw/sources.csv

| Column | Type | Description |
|---|---|---|
| source_id | text | Identifier used in the readings file |
| publisher | text | Organisation that published the document |
| kind | text | `official` (GASTAT) or `news` |
| title | text | Document title |
| date | text | Publication date (year-month or full date) |
| url | text | Link to the document |

## data/processed/ai_use_tidy.csv

One row per year and sector (38 rows: 2 years x 18 sectors plus the national figure). Use this file in Power BI or Tableau.

| Column | Type | Description |
|---|---|---|
| year | integer | Survey year |
| isic_section | text | ISIC section letter, `ALL` for all establishments |
| sector | text | Economic activity |
| pct_using_ai | number | Share of establishments using AI technologies, among establishments using the Internet (%) |
| n_documents | integer | Number of documents that print this value |
| n_publishers | integer | Number of different publishers that print this value |
| verification | text | `official-and-press`: GASTAT plus at least one news report of the release; `one-document`: one GASTAT document only (read twice) |
| sources | text | Source ids, separated by `;` |

## data/processed/ai_use_by_sector.csv

One row per sector plus the national row (19 rows).

| Column | Type | Description |
|---|---|---|
| isic_section | text | ISIC section letter, `ALL` for all establishments |
| sector | text | Economic activity |
| pct_2024 | number | Share using AI in 2024 (%) |
| pct_2025 | number | Share using AI in 2025 (%) |
| verification_2024 | text | Verification of the 2024 value |
| verification_2025 | text | Verification of the 2025 value |
| change_pts | number | pct_2025 minus pct_2024, percentage points |
| change_rel_pct | number | Relative change, pct_2025 / pct_2024 - 1, in percent |
| rank_2025 | integer | Rank among the 18 sectors in 2025 (1 = highest share) |
| rank_2024 | integer | Rank among the 18 sectors in 2024 |
| gap_to_national_2025_pts | number | pct_2025 minus the national 2025 rate, percentage points |

## data/processed/headline_figures.csv

| Column | Type | Description |
|---|---|---|
| measure | text | Name of the headline figure |
| value | text | Value (number, or sector name and number) |
