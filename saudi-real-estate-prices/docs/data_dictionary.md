# Data dictionary

All percentages are percent changes in the GASTAT Real Estate Price Index (base year 2023 = 100). Periods are calendar quarters written as `Q1 2026`.

Segment codes used in every file:

| Code | Meaning | Sector |
|---|---|---|
| `all` | Whole index | All |
| `residential` | Residential sector | Residential |
| `residential_land` | Residential land plots | Residential |
| `villa` | Villas | Residential |
| `apartment` | Apartments | Residential |
| `floor` | Residential floors (a floor of a building sold on its own) | Residential |
| `commercial` | Commercial sector | Commercial |
| `commercial_land` | Commercial land plots | Commercial |
| `commercial_building` | Commercial buildings | Commercial |
| `showroom_shop` | Showrooms and shops (GASTAT also writes "galleries and shops" and "exhibitions") | Commercial |
| `agricultural` | Agricultural sector | Agricultural |
| `agricultural_land` | Agricultural land | Agricultural |

## data/raw/sources.csv

26 rows, one per document.

| Column | Description |
|---|---|
| `source_id` | Short id used in the readings file. S = GASTAT, A = Argaam, M = Amlak, E = Enterprise, EM = Economy Middle East, RD = Riyadh Daily, AN = Arab News, O = Okaz, T = Trading Economics |
| `publisher` | Organisation that published the document |
| `kind` | `official` for GASTAT documents, `news` for reports of GASTAT releases |
| `title` | Title of the document |
| `date` | Publication date (month when the day is not printed) |
| `url` | Link to the document |

## data/raw/price_index_readings.csv

725 rows, one per figure per document.

| Column | Description |
|---|---|
| `period` | Quarter the figure refers to |
| `geography` | `Saudi Arabia` for national figures, or one of 13 administrative regions |
| `segment` | Segment code (regional figures are always `all`) |
| `measure` | `level` (index points), `yoy` (% change on the same quarter a year earlier), `qoq` (% change on the previous quarter), `weight` (% of the national index) |
| `value` | Figure as printed, declines negative |
| `source_id` | Document the figure was read from, see `sources.csv` |
| `note` | Empty, or a note. Readings starting with `set aside:` are kept for the record but not used; the note gives the reason |

## data/processed/price_index_tidy.csv

424 rows: 414 figures after the readings are consolidated, plus 10 derived index levels. Built for Power BI or Tableau.

| Column | Description |
|---|---|
| `period` | Quarter |
| `geography` | `Saudi Arabia` or region |
| `sector` | `All`, `Residential`, `Commercial` or `Agricultural` (regions: `All`) |
| `segment` | Segment code |
| `segment_label` | Readable segment name |
| `measure` | `level`, `yoy`, `qoq` or `weight` |
| `value` | Consolidated value. For levels printed with different decimals, the most precise reading |
| `value_basis` | `printed`, or `derived` when computed from a printed level and a printed change |
| `n_documents` | Number of documents that print the figure |
| `n_publishers` | Number of different publishers among them |
| `official_report` | `yes` if a GASTAT document prints the figure |
| `source_check` | `two-publishers`, `same-publisher` (two documents by one publisher), `one-document` or `derived` |
| `source_ids` | Ids of the documents, or for derived levels the formula used |

## data/processed/national_index.csv

22 rows, Q1 2021 to Q2 2026.

| Column | Description |
|---|---|
| `period` | Quarter |
| `index_level` | National index, 2023 = 100 |
| `level_basis` | `printed` or `derived` (Q3 2025 and Q2 2026) |
| `yoy_pct` | % change on the same quarter a year earlier (from Q1 2022) |
| `qoq_pct` | % change on the previous quarter (from Q4 2024) |

## data/processed/segment_changes.csv

92 rows: up to 12 segments by 8 quarters, Q3 2024 to Q2 2026 (9 segments have figures for Q4 2025, 11 for Q4 2024).

| Column | Description |
|---|---|
| `period` | Quarter |
| `sector` | Sector of the segment |
| `segment` | Segment code |
| `segment_label` | Readable segment name |
| `weight_pct` | Latest printed weight of the segment in the national index, %. Villa, apartment, floor, commercial building, showroom and agricultural weights are from Q3 2024 (Argaam); residential, residential land, commercial and commercial land weights from 2025 and 2026 GASTAT reports |
| `yoy_pct` | % change on the same quarter a year earlier |
| `qoq_pct` | % change on the previous quarter, where printed |
| `yoy_source_check` | How the annual change is confirmed (see `source_check` above) |

## data/processed/region_index.csv

99 rows: 13 regions by 8 quarters (8 regions in Q2 2026).

| Column | Description |
|---|---|
| `period` | Quarter |
| `region` | Administrative region |
| `index_level` | Regional index, 2023 = 100 |
| `level_basis` | `printed`, or `derived` for Q2 2026 (Q2 2025 level times one plus the Q2 2026 annual change) |
| `yoy_pct` | % change on the same quarter a year earlier |
| `yoy_source_check` | How the annual change is confirmed |

## data/processed/identity_checks.csv

92 rows, one per check. All pass.

| Column | Description |
|---|---|
| `check` | `yoy from levels`, `qoq from levels` or `yoy from four qoq` |
| `geography` | National or region |
| `segment` | Segment code |
| `period` | Quarter checked |
| `printed` | Printed change, % |
| `implied_low`, `implied_high` | Range of the change implied by the other printed figures, allowing for rounding, % |
| `passed` | `True` if the printed change lies in the implied range (within its own rounding) |

## data/processed/headline_figures.csv

34 rows. The figures quoted in the README and the post, as computed by the build script. The notebook recomputes each one and checks that it matches.

| Column | Description |
|---|---|
| `measure` | Name of the figure |
| `value` | Value |
