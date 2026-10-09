# Data dictionary

All rates are percentages of taxable company profit.

## data/raw/tax_foundation_2025_reading_a.csv (226 rows)

| Column | Type | Description |
|---|---|---|
| iso3 | text | Three-letter code used in the source table (XKX for Kosovo) |
| country | text | Jurisdiction name as printed in the source |
| rate_pct | number | Standard top statutory corporate income tax rate, 2025 |
| rate_with_gmt_pct | number | Rate for large multinational groups once a 15% minimum top-up tax is counted. Empty for Poland (cut off in the page) |

## data/raw/tax_foundation_2025_reading_b.csv (226 rows)

| Column | Type | Description |
|---|---|---|
| iso3 | text | Three-letter code |
| continent_code | text | AF Africa, AS Asia, EU Europe, NO North America, SA South America, OC Oceania |
| rate_pct | number | Same rate as reading A, from a second reading of the table |

## data/raw/tax_foundation_2025_published_checks.csv (18 rows)

| Column | Type | Description |
|---|---|---|
| check | text | Name of the total or average |
| published_value | number | Value printed in the Tax Foundation text |
| note | text | Where it is printed |

## data/raw/pwc_quick_chart_2026.csv (146 rows)

| Column | Type | Description |
|---|---|---|
| territory | text | Territory name used by PwC |
| headline_cit_rate_text | text | Headline corporate income tax rate as text, shortened but with every number kept |
| last_reviewed | text | Date PwC last reviewed the entry |

## data/raw/trading_economics_2026.csv (162 rows)

| Column | Type | Description |
|---|---|---|
| country | text | Country name used by Trading Economics (includes Euro area and European Union, which are dropped) |
| last_pct | number | Latest corporate tax rate listed |
| previous_pct | number | Previous rate listed |

## data/processed/corporate_tax_tidy.csv (226 rows)

| Column | Type | Description |
|---|---|---|
| iso3 | text | Three-letter code |
| country | text | Short name used in charts and tables |
| region | text | Middle East, Europe, Rest of Asia, Rest of Africa, North America, South America or Oceania |
| sub_region | text | Gulf, Levant and Iraq, Iran, Turkey and Yemen, North Africa. Equal to region outside the Middle East |
| rate_2025_pct | number | Standard top statutory corporate income tax rate, 2025 |
| rate_with_min_tax_2025_pct | number | Rate for large multinational groups with the 15% minimum tax. Empty for Poland |
| min_tax_uplift_pts | number | rate_with_min_tax_2025_pct minus rate_2025_pct, in percentage points |
| rank_lowest | integer | Rank from the lowest rate (1 = lowest, ties share a rank) |
| rank_highest | integer | Rank from the highest rate (1 = highest, ties share a rank) |
| pwc_rate_2026_pct | number | General rate taken from the PwC text. Empty when not covered or when the text gives no single general rate |
| te_rate_2026_pct | number | Trading Economics latest rate. Empty when not covered |
| check_status | text | confirmed, differs or single-source (see README, Method) |
| pwc_text | text | PwC headline text for reference |
| name_in_source | text | Name as printed by the Tax Foundation |

## data/processed/region_summary.csv (12 rows)

| Column | Type | Description |
|---|---|---|
| level | text | region, middle_east_sub_region or world |
| group | text | Name of the region or sub-region |
| jurisdictions | integer | Number of jurisdictions in the group |
| mean_rate_pct | number | Simple mean of rate_2025_pct |
| median_rate_pct | number | Median of rate_2025_pct |
| min_rate_pct | number | Lowest rate in the group |
| max_rate_pct | number | Highest rate in the group |
| at_or_below_15_pct | integer | Jurisdictions with a rate of 15% or less |
| confirmed | integer | Jurisdictions whose rate matches a second listing |

## data/processed/published_checks.csv (18 rows)

| Column | Type | Description |
|---|---|---|
| check | text | Name of the total or average |
| published_value | number | Value printed in the Tax Foundation text |
| note | text | Where it is printed |
| computed_value | number | Value recomputed from the 226-row table. Empty where GDP data would be needed |
| result | text | match, MISMATCH, or not recomputed |
