# Data dictionary

All shares are percentages of people aged 15 to 64 who used a generative AI product during the period, as estimated by the Microsoft AI Economy Institute. Periods: `2025-H1` (January to June 2025), `2025-H2` (July to December 2025), `2026-Q1` (January to March 2026), `2026-Q2` (April to June 2026).

## data/raw/ai_diffusion_readings.csv

One row per economy, period and document. 1,084 rows.

| Column | Type | Description |
|---|---|---|
| economy | text | Economy name as used in this project (spellings harmonised across reports, for example Czechia to Czech Republic, Türkiye to Turkey) |
| period | text | Period the figure refers to |
| ai_diffusion_pct | number | Share of working-age people using generative AI, as printed in the document |
| published_rank | integer | Rank printed or implied by the document's ordering, where available; blank otherwise |
| document | text | Document the figure was read from |
| publisher | text | Organisation that published the document |
| url | text | Link to the document |

## data/raw/aggregate_readings.csv

World, Global North and Global South figures. 48 rows.

| Column | Type | Description |
|---|---|---|
| group | text | World, Global North or Global South |
| period | text | Period the figure refers to |
| ai_diffusion_pct | number | Published share, weighted by working-age population |
| document | text | Document the figure was read from |
| url | text | Link to the document |

## data/processed/ai_use_tidy.csv

One row per economy and period. 588 rows (147 economies by 4 periods).

| Column | Type | Description |
|---|---|---|
| economy | text | Economy |
| period | text | Period |
| ai_diffusion_pct | number | Share used in the analysis: the value printed in the newest Microsoft report that covers the period |
| documents | integer | Number of documents that print this figure |
| publishers | integer | Number of different publishers that print this figure |
| verification | text | `two-publishers`: printed by Microsoft and at least one other publisher, all equal. `two-reports`: printed in two Microsoft reports, equal. `revised`: two Microsoft reports differ by 0.1 point; the later value is used. `single-document`: printed in one document only |
| earlier_report_value | number | For `revised` rows, the value printed in the earlier report |
| region | text | Middle East, Europe, Asia, Oceania, Americas or Sub-Saharan Africa |
| sub_region | text | For the Middle East: Gulf, Levant and Iraq, North Africa, or Iran and Turkey. Otherwise the region |
| shared_value_group | text | Set when the economy has exactly the same value as other economies in all four periods (a shared regional estimate); blank otherwise |
| own_estimate | text | `yes` if the economy has its own figure, `no` if it shares a regional estimate |

## data/processed/ai_use_by_economy.csv

One row per economy. 147 rows, sorted by Q2 2026 rank.

| Column | Type | Description |
|---|---|---|
| economy, region, sub_region | text | As above |
| h1_2025_pct, h2_2025_pct, q1_2026_pct, q2_2026_pct | number | Share in each period |
| rank_q2_2026 | integer | Position in the Q2 2026 report's table (1 = highest) |
| rank_q1_2026_report | integer | Position in the Q1 2026 report's table |
| change_q1_to_q2_pp | number | q2_2026_pct minus q1_2026_pct, percentage points |
| change_h1_2025_to_q2_2026_pp | number | q2_2026_pct minus h1_2025_pct, percentage points |
| shared_value_group, own_estimate | text | As above |
| q2_2026_verification | text | Verification label of the Q2 2026 figure |

## data/processed/region_summary.csv

One row per region, Middle East sub-region and for all economies. 11 rows.

| Column | Type | Description |
|---|---|---|
| group | text | Region, Middle East sub-region, or all 147 economies |
| economies | integer | Economies in the group |
| economies_own_estimate | integer | Economies with their own figure |
| median_q2_2026_pct | number | Unweighted median share, Q2 2026 |
| median_change_q1_to_q2_pp | number | Unweighted median change, Q1 to Q2 2026, points |
| highest, highest_q2_2026_pct | text, number | Economy with the highest share and its value |
| lowest, lowest_q2_2026_pct | text, number | Economy with the lowest share and its value |
| economies_above_world_pct | integer | Economies above the published world figure for Q2 2026 (18.8%) |

## data/processed/world_aggregates.csv

One row per period. 4 rows.

| Column | Type | Description |
|---|---|---|
| period | text | Period |
| world_pct, global_north_pct, global_south_pct | number | Published shares, weighted by working-age population |
| north_south_gap_pp | number | global_north_pct minus global_south_pct |
| documents_world | integer | Documents that print the world figure for the period |

## data/processed/source_checks.csv

Count of economies by period and verification label. 4 rows.
