# Data dictionary

## data/raw/qatar_cpi_readings_by_source.csv

One row per figure per publisher. 361 rows. Each row is a number read from a published report of a National Planning Council monthly Consumer Price Index release.

| Column | Type | Description |
|---|---|---|
| month | text, YYYY-MM | Reference month of the figure, 2025-12 to 2026-06 |
| cpi_group | text | Spending group code. Twelve CPI groups plus `all_items` and `all_items_ex_housing` |
| measure | text | `index` (index level, 2018=100), `mom_pct` (change on the previous month, %), `yoy_pct` (change on the same month a year earlier, %) |
| value | number | The figure as published. "Unchanged" is recorded as 0.00 |
| decimals_reported | integer | Decimal places the publisher printed (2, or 1 for FocusEconomics) |
| publisher | text | Outlet that reported the release |
| published_date | date | Date of the report |
| url | text | Link to the report |

## data/raw/qatar_cpi_quarterly_check.csv

Two rows from the first-quarter 2026 CPI release, used only as a cross-check on the monthly index levels.

| Column | Type | Description |
|---|---|---|
| period | text | 2026-Q1 |
| cpi_group | text | `all_items` |
| measure | text | `index` (quarterly average level) or `yoy_pct` |
| value | number | The figure as published |
| publisher, published_date, url | text | Source of the figure |

## data/processed/qatar_cpi_tidy.csv

One row per month, group and measure. 187 rows. Ready for Power BI or Tableau.

| Column | Type | Description |
|---|---|---|
| month | text, YYYY-MM | Reference month |
| month_start | date | First day of the month, for date axes |
| cpi_group | text | Spending group code |
| group_label | text | Spending group name for display |
| measure | text | `index`, `mom_pct` or `yoy_pct` |
| value | number | The figure, taken from the publisher that printed the most decimals |
| decimals_reported | integer | Decimal places of the value kept |
| n_publishers | integer | Number of publishers that reported this figure |
| publishers | text | Their names, separated by semicolons |
| verification | text | `two-publishers` when at least two outlets printed the same figure, otherwise `single-publisher` |
| base_year | text | Index base, 2018=100 for every row |

## data/processed/cumulative_change_by_group.csv

Cumulative price change per group over two windows. 30 rows. These are derived figures, not published ones.

| Column | Type | Description |
|---|---|---|
| window | text | `since_feb_2026` (February to June 2026) or `since_dec_2025` (December 2025 to June 2026) |
| start_month, end_month | text, YYYY-MM | Base month and final month |
| cpi_group, group_label | text | Spending group code and name |
| months_chained | integer | Number of monthly changes multiplied together |
| cumulative_change_pct | number | Change from the base month to the final month, % |
| index_start_100 | number | Price level in the final month with the base month set to 100 |
| single_publisher_months | integer | How many of the chained monthly changes rest on one publisher |
| method | text | `chained monthly changes`, or `ratio of published index levels` (all items only, as a check) |
