# Data dictionary

Capacity is installed renewable power capacity at the end of the year, in megawatts (MW). 1,000 MW is 1 gigawatt (GW).

## data/raw/irena_2026_total_renewable_reading_b.csv (31 rows)

| Column | Type | Description |
|---|---|---|
| label_in_source | text | Row label as printed in the IRENA table "Total renewable energy" (for example "United Arab Em", "Iran IR", "Syrian AR", "Türkiye", "C America + Carib") |
| row_type | text | world, region (one of IRENA's nine regions), subtotal (European Union, a part of Europe) or country |
| 2016 to 2025 | whole number | Capacity at the end of that year, MW |

## data/raw/irena_2026_total_renewable_reading_a.csv (22 rows)

| Column | Type | Description |
|---|---|---|
| label_requested | text | Row name used in the first reading of the table: World, Middle East and the 20 economies |
| 2016 to 2025 | whole number | Capacity at the end of that year, MW, from a separate reading of the same table |

## data/raw/secondary_reports.csv (42 rows)

| Column | Type | Description |
|---|---|---|
| source | text | Document that prints the figure |
| entity | text | Country, region or World |
| measure | text | capacity_2025, capacity_2024, added_2025 or growth_2025_pct |
| published_value | number | Figure as printed |
| unit | text | GW, MW or pct |
| decimals | whole number | Number of decimal places printed, used to set the tolerance |
| note | text | Remark on the figure, if any |

## data/processed/renewable_capacity_tidy.csv (350 rows)

One row per entity per year: 20 countries, 4 sub-regions, the 20-economy total, 9 IRENA regions and the world, for 10 years.

| Column | Type | Description |
|---|---|---|
| entity | text | Country, sub-region, region or World |
| entity_type | text | country, sub_region (computed), aggregate_20 (computed), irena_region (printed by IRENA) or world |
| iso3 | text | Three-letter country code. Empty for groups |
| sub_region | text | Gulf, Levant and Iraq, Iran, Turkey and Yemen, or North Africa. Empty for regions and the world |
| in_irena_middle_east | True/False | True for the 14 countries IRENA prints under its Middle East heading |
| year | whole number | 2016 to 2025 |
| capacity_mw | whole number | Capacity at the end of the year, MW |
| change_mw | whole number | Capacity minus capacity a year earlier. Empty for 2016 |
| change_pct | number | Percentage change from a year earlier, one decimal. Empty for 2016 |
| label_in_source | text | IRENA row label. Empty for computed groups |
| read_twice | True/False | True when the row is in both readings of the table, or is computed from rows that are |

## data/processed/country_summary_2025.csv (20 rows)

| Column | Type | Description |
|---|---|---|
| country | text | Economy name |
| iso3 | text | Three-letter code |
| sub_region | text | One of the four sub-regions |
| in_irena_middle_east | True/False | As above |
| capacity_2016_mw, capacity_2024_mw, capacity_2025_mw | whole number | Capacity at the end of that year |
| added_2025_mw | whole number | capacity_2025_mw minus capacity_2024_mw |
| growth_2025_pct | number | Percentage change from 2024 to 2025 |
| added_2016_2025_mw | whole number | capacity_2025_mw minus capacity_2016_mw |
| multiple_of_2016 | number | capacity_2025_mw divided by capacity_2016_mw |
| check_status | text | two-publishers: the 2025 total or the 2025 addition is also printed, rounded, in a second document and agrees. irena-only: found in the IRENA table only (read twice) |
| rank_capacity_2025 | whole number | Rank among the 20 by capacity in 2025, 1 is largest |
| rank_added_2025 | whole number | Rank among the 20 by capacity added in 2025, 1 is largest |

## data/processed/group_summary.csv (15 rows)

Four sub-regions, the 20-economy total, nine IRENA regions and the world. Columns as in the country summary, with `entity`, `entity_type` and:

| Column | Type | Description |
|---|---|---|
| check_status | text | computed (a sum of country rows), two-publishers or irena-only |
| share_of_world_2025_pct | number | capacity_2025_mw as a percentage of the world total |

## data/processed/secondary_checks.csv (42 rows)

| Column | Type | Description |
|---|---|---|
| source, entity, measure, published_value, unit, note | | As in the raw file |
| irena_table_value | number | The same measure computed from the IRENA table, in the unit of the report |
| status | text | agrees when the two are within one unit of the last printed digit, otherwise differs |
