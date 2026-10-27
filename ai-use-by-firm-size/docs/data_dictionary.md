# Data dictionary

## data/raw/ai_use_readings.csv

One row per figure per document. Every printed reading is kept, including readings set aside.

| Column | Type | Description |
|---|---|---|
| economy | text | `Turkey` or `EU-27` |
| year | integer | Survey reference year |
| measure | text | `ai_use` (share of enterprises using at least one AI technology), `considered_not_used` (share of enterprises not using AI that had considered using it), `reason_not_used` (share of enterprises that considered AI but did not use it, citing the reason), `purpose` (share of AI-using enterprises using AI for the purpose) |
| item | text | Size class (`Small (10-49)`, `Medium (50-249)`, `Large (250+)`, `All (10+ employees)`), reason or purpose |
| value_printed | text | The figure exactly as printed in the document, in percent; kept as text so the number of decimals is preserved for the rounding check |
| source_id | text | Key to `sources.csv` |
| note | text | `set_aside: ...` when the reading is not used, with the reason |

## data/raw/sources.csv

| Column | Type | Description |
|---|---|---|
| source_id | text | Key used in the readings file. T = Turkey documents, E = EU documents |
| publisher | text | Who published the document |
| kind | text | `official` (statistics office or EU body) or `news` (outlet reprinting official figures) |
| title | text | Document title |
| date | text | Publication date, as precise as known |
| url | text | Link |

## data/processed/ai_use_tidy.csv

One row per figure, after the agreement check. Load this into Power BI, Tableau or SQL.

| Column | Type | Description |
|---|---|---|
| economy | text | `Turkey` or `EU-27` |
| year | integer | Survey reference year |
| measure | text | As in the raw file |
| item | text | As in the raw file |
| value | float | Percent. The most precise printed reading of the figure |
| n_sources | integer | Number of documents that print the figure (set-aside readings excluded) |
| verification | text | `two-or-more-documents` or `one-document` |
| source_ids | text | Documents that print the figure, separated by `;` |

## data/processed/ai_use_by_size.csv

One row per economy and year with all three size classes.

| Column | Type | Description |
|---|---|---|
| economy | text | `Turkey` or `EU-27` |
| year | integer | Turkey 2021 and 2025; EU 2024 and 2025 |
| small_pct | float | % of enterprises with 10 to 49 employees using AI |
| medium_pct | float | % of enterprises with 50 to 249 employees using AI |
| large_pct | float | % of enterprises with 250 or more employees using AI |
| all_pct | float | % of all enterprises with 10 or more employees using AI |
| gap_large_minus_small_pts | float | large_pct minus small_pct, percentage points |
| ratio_large_to_small | float | large_pct divided by small_pct |

## data/processed/headline_figures.csv

| Column | Type | Description |
|---|---|---|
| figure | text | Name of the headline figure, for example `turkey_gap_2025` |
| value | float | Its value (percent, points or ratio as the name says) |
