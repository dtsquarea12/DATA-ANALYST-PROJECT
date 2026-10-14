# Data dictionary

All values are in US$ billion unless stated. Egypt's fiscal year (FY) runs from 1 July to 30 June; FY2025/26 is July 2025 to June 2026.

## data/raw/remittance_readings.csv

| Column | Type | Description |
|---|---|---|
| measure | text | `fiscal_year`, `calendar_year`, `cumulative_fy` (from 1 July to the month named), `quarter` or `month` |
| period | text | Label of the period, for example `FY2025/26`, `2025`, `FY2025/26 Jul-Mar`, `Apr-Jun 2025`, `2026-06` |
| period_start | date | First day of the period |
| period_end | date | Last day of the period |
| value_usd_bn | number | Remittances from Egyptians working abroad, as printed in the document |
| source_id | text | Document the figure was read from; see `sources.csv` |
| printed_as | text | The figure as printed, including words such as "about" |
| note | text | Why a reading is set aside or treated differently; empty otherwise |

## data/raw/published_growth_rates.csv

| Column | Type | Description |
|---|---|---|
| measure | text | As above |
| period | text | Period the rate refers to |
| compared_with | text | Period it is compared with |
| growth_pct | number | Published change, percent |
| source_id | text | Document the rate was read from |

## data/raw/sources.csv

| Column | Type | Description |
|---|---|---|
| source_id | text | Key used in the other files |
| publisher | text | Outlet that printed the CBE figures |
| title | text | Headline |
| published | text | Publication date (year-month where the day is not printed) |
| url | text | Link |

## data/processed/remittances_tidy.csv

| Column | Type | Description |
|---|---|---|
| measure, period, period_start, period_end | | As in the raw file |
| value_usd_bn | number | Agreed value across all documents that print it |
| n_documents | integer | Number of documents that print the figure |
| n_publishers | integer | Number of different publishers among them |
| source_check | text | `two-publishers`, `two-documents-same-publisher`, `one-document`, or `one-document-plus-rounded-second` |
| source_ids | text | Documents used, separated by `;` |

## data/processed/fiscal_year_series.csv

| Column | Type | Description |
|---|---|---|
| period, period_start, period_end, value_usd_bn | | As above, fiscal years FY2018/19 to FY2025/26 |
| change_usd_bn | number | Change on the previous fiscal year |
| change_pct | number | Percent change on the previous fiscal year, from rounded totals |
| index_fy2018_19_100 | number | Total as an index, FY2018/19 = 100 |
| is_record_so_far | boolean | True if the total is the highest in the series up to that year |
| source_check, source_ids | | As above |

## data/processed/derived_figures.csv

| Column | Type | Description |
|---|---|---|
| period | text | Derived period |
| value_usd_bn | number | Derived value, rounded to 0.1 |
| method | text | How it was computed from published figures |

## data/processed/growth_rate_checks.csv

| Column | Type | Description |
|---|---|---|
| measure, period, compared_with, growth_pct, source_id | | As in `published_growth_rates.csv` |
| computed_lo, computed_hi | number | Lowest and highest growth rate (percent) consistent with the two values rounded to 0.1 |
| result | text | `pass`, `FAIL`, or `base not in table` when the comparison period is not in the tidy table |

## data/processed/identity_checks.csv

| Column | Type | Description |
|---|---|---|
| identity | text | The relationship tested |
| left, right | number | The two sides |
| difference | number | left minus right |
| tolerance | number | Allowed difference given rounding |
| result | text | `pass` or `FAIL` |

## data/processed/headline_figures.csv

| Column | Type | Description |
|---|---|---|
| measure | text | Name of the headline figure (for example `fy2025_26_usd_bn`, `two_year_multiple`) |
| value | number | Its value |
