# Data dictionary

## data/processed/gii_tidy.csv

One row per economy in the Global Innovation Index 2026 (139 rows).

| Column | Type | Description |
|---|---|---|
| iso3 | text | ISO 3166-1 alpha-3 code |
| country | text | Economy name used across this portfolio |
| region | text | Middle East, Europe, Rest of Asia, Rest of Africa, North America (with Central America and the Caribbean), South America, Oceania |
| sub_region | text | Middle East sub-region (Gulf; Levant and Iraq; Iran, Turkey and Yemen; North Africa), otherwise the region |
| wipo_nawa | boolean | True if WIPO places the economy in its region Northern Africa and Western Asia |
| score_2026 | number | GII 2026 score, 0 to 100 |
| rank_2026 | integer | GII 2026 rank, 1 to 139 |
| income_group_rank_2026 | integer | Rank within World Bank income group, 2026; empty for unclassified economies |
| wipo_region_rank_2026 | integer | Rank within WIPO region, 2026 |
| score_2025 | number | GII 2025 score; empty if not in the 2025 edition |
| rank_2025 | integer | GII 2025 rank; empty if not in the 2025 edition |
| rank_change | integer | rank_2025 minus rank_2026; positive means moved up |
| score_change | number | score_2026 minus score_2025 |
| rank_check_2026 | text | two-documents: 2026 rank also printed in the WIPO results web page or a news report; one-document-read-twice: executive version only |
| check_2025 | text | two-documents: WIPO and Wikipedia agree; sources-differ: they differ and the WIPO figure is used; empty if not in 2025 |

## data/processed/middle_east.csv

The 15 Middle East economies in the index, Gulf first. Columns iso3, country, sub_region, score_2026, rank_2026, rank_2025, rank_change, score_2025, score_change as above, plus:

| Column | Type | Description |
|---|---|---|
| rank_in_middle_east | integer | Rank among the 15 Middle East economies by 2026 rank |

## data/processed/region_summary.csv

| Column | Type | Description |
|---|---|---|
| level | text | world, region, middle_east_sub_region or wipo_region |
| group | text | Name of the group |
| economies | integer | Economies in the group in 2026 |
| mean_score_2026 | number | Mean 2026 score, two decimals |
| median_rank_2026 | number | Median 2026 rank |
| best | text | Highest-ranked economy in the group |
| best_rank | integer | Its 2026 rank |
| moved_up | integer | Economies whose rank improved from 2025 |
| moved_down | integer | Economies whose rank fell from 2025 |
| unchanged | integer | Economies with the same rank |
| new_in_2026 | integer | Economies not in the 2025 edition |
| in_top_50 | integer | Economies ranked 1 to 50 in 2026 |

## data/processed/source_checks.csv

| Column | Type | Description |
|---|---|---|
| source_id | text | Source, see data/raw/sources.csv |
| country | text | Economy |
| edition | integer | GII edition year |
| metric | text | gii_rank or region_rank |
| published | integer | Figure printed in the source |
| table | integer | Figure in the tidy table |
| agrees | boolean | True if they match |

## data/raw

| File | Columns |
|---|---|
| gii_2026_reading_a.csv | gii_rank, economy (WIPO name), score, income_group_rank, region_rank |
| gii_2026_reading_b.csv | economy, score, gii_rank, income_group_rank, region_rank |
| gii_2026_web_page_ranks.csv | gii_rank, economy as named in the web page text |
| gii_2025_wipo.csv | gii_rank, economy, score, income_group_rank, region_rank |
| gii_2025_wikipedia.csv | economy (Wikipedia name), rank_2025, score_2025 |
| published_figures.csv | source_id, economy, edition, metric, value |
| country_reference.csv | country, iso3, region |
| sources.csv | source_id, publisher, title, url, used_for |
