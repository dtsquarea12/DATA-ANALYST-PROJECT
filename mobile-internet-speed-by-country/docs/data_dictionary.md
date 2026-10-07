# Data dictionary

## data/raw/speedtest_readings_march_2026.csv

One row per country, network and source. 157 rows, 75 countries. Median download speeds from the Ookla Speedtest Global Index for March 2026.

| Column | Type | Description |
|---|---|---|
| country | text | Country or territory name |
| region | text | Middle East and North Africa, Europe, Asia-Pacific, Americas or Sub-Saharan Africa |
| gcc_member | text | `yes` for the six Gulf Cooperation Council states, otherwise `no` |
| network | text | `mobile` or `fixed` (fixed broadband) |
| median_download_mbps | number | Median download speed in megabits per second |
| published_rank | integer | World rank for mobile as published, for ranks 1 to 40. Empty otherwise |
| index_month | text, YYYY-MM | Month of the index, 2026-03 for every row |
| source | text | Where the figure was read |
| url | text | Link to the source |

## data/raw/speedtest_other_months.csv

Fifteen readings of the same index for other months (December 2023, October 2025, September 2026), kept for context. Not used in the main analysis.

| Column | Type | Description |
|---|---|---|
| country | text | Country, or `World` for the global median |
| network | text | `mobile` |
| median_download_mbps | number | Median download speed in megabits per second. Some sources round to a whole number |
| index_month | text, YYYY-MM | Month of the index |
| source, url | text | Where the figure was read |

## data/processed/speed_by_country.csv

One row per country. 75 rows. Ready for Power BI or Tableau.

| Column | Type | Description |
|---|---|---|
| country, region, gcc_member, index_month | text | As in the raw file |
| mobile_rank_published | integer | Published world rank for mobile, ranks 1 to 40 only |
| mobile_mbps | number | Median mobile download speed, Mbps |
| fixed_mbps | number | Median fixed broadband download speed, Mbps |
| mobile_to_fixed_ratio | number | mobile_mbps divided by fixed_mbps. Above 1 means mobile is faster |
| faster_network | text | `mobile` or `fixed` |
| uae_mobile_multiple | number | UAE mobile median divided by this country's mobile median |
| mobile_verification, fixed_verification | text | `two-sources` when a second source printed the same figure, otherwise `single-source` |

## data/processed/speed_tidy.csv

One row per country and network. 150 rows. Long format of the same data with `median_download_mbps`, `published_rank`, `n_sources` and `verification`.

## data/processed/group_summary.csv

Seven rows: the GCC states, each region and all countries collected.

| Column | Type | Description |
|---|---|---|
| group | text | Group name. Regional rows say "countries collected" because the sample is not the full index |
| countries | integer | Countries in the group |
| median_mobile_mbps, median_fixed_mbps | number | Median of the country medians in the group |
| min_mobile_mbps, max_mobile_mbps | number | Lowest and highest country mobile median in the group |
| countries_mobile_faster | integer | Countries in the group where mobile is faster than fixed |
