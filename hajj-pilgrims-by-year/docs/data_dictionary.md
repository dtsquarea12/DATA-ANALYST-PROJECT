# Data dictionary

Counts are numbers of pilgrims. A season is the Hajj of that Gregorian year (Hajj 2026 is 1447 AH).

- **External (from abroad):** pilgrims who arrived through air, land or sea entry points.
- **Internal (from inside Saudi Arabia):** citizens and residents of Saudi Arabia, of any nationality.

## data/raw/pilgrim_readings.csv

| Column | Type | Description |
|---|---|---|
| measure | text | `total`, `external`, `internal`, `male`, `female`, `arrival_air`, `arrival_land`, `arrival_sea` (arrival modes count external pilgrims only) |
| year | integer | Hajj season, Gregorian year |
| value | integer | Number of pilgrims as printed in the document |
| source_id | text | Document the figure was read from; see `sources.csv` |
| printed_as | text | The figure as printed |
| note | text | Why a reading is set aside ("set aside: ...") or used only as a rounding check; empty otherwise |

## data/raw/origin_readings.csv

| Column | Type | Description |
|---|---|---|
| year | integer | Hajj season |
| origin_group | text | Origin group of pilgrims from abroad, as named by GASTAT |
| external_pilgrims | integer | Count printed for the group (empty for 2024, when only shares were printed) |
| share_pct_printed | number | Share printed by GASTAT, percent (2024 only) |
| source_id | text | Document; see `sources.csv` |

## data/raw/sources.csv

| Column | Type | Description |
|---|---|---|
| source_id | text | Key used in the other files |
| publisher | text | GASTAT, or the outlet that printed or compiled GASTAT figures |
| title | text | Headline or document title |
| published | text | Publication date (year or year-month where the day is not printed) |
| url | text | Link |

## data/processed/figures_checked.csv

| Column | Type | Description |
|---|---|---|
| measure | text | As in `pilgrim_readings.csv` |
| year | integer | Hajj season |
| value | integer | Accepted value (all documents agree) |
| n_documents | integer | Number of documents printing the exact value |
| n_publishers | integer | Number of different publishers among them |
| source_check | text | `two-publishers`, `same-publisher` (two documents from one publisher), `one-document-plus-rounded-second`, or `one-document` |
| source_ids | text | Documents used, separated by `;`; `(rounded)` marks a rounding check |

## data/processed/pilgrims_by_year.csv

| Column | Type | Description |
|---|---|---|
| year | integer | Hajj season, 2008 to 2026 without 2020 and 2021 |
| total | integer | All pilgrims |
| external | integer | Pilgrims from abroad |
| internal | integer | Pilgrims from inside Saudi Arabia |
| internal_share_pct | number | internal / total x 100 |
| total_pct_of_2019 | number | total / total in 2019 x 100 |
| external_pct_of_2019 | number | external / external in 2019 x 100 |
| internal_pct_of_2019 | number | internal / internal in 2019 x 100 |
| total_change_pct | number | Change in total on the previous season, percent; empty when the previous calendar year is not in the series |
| split_source_check | text | `source_check` of the internal figure for that season |

## data/processed/pilgrims_tidy.csv

| Column | Type | Description |
|---|---|---|
| year | integer | Hajj season |
| pilgrim_group | text | `From abroad` or `From inside Saudi Arabia` |
| pilgrims | integer | Number of pilgrims |

## data/processed/external_by_origin.csv

| Column | Type | Description |
|---|---|---|
| year | integer | Hajj season (2017, 2018, 2019, 2024) |
| origin_group | text | Origin group as named by GASTAT |
| external_pilgrims | integer | Count (empty for 2024) |
| share_pct | number | Share of pilgrims from abroad, percent; computed from counts for 2017 to 2019, as printed for 2024 |
| source_id | text | First document carrying the figure |
| n_documents | integer | Number of documents carrying the figure |

## data/processed/identity_checks.csv

| Column | Type | Description |
|---|---|---|
| year | integer | Hajj season |
| identity | text | The identity tested |
| left | integer | Sum of the parts |
| right | integer | Published total |
| difference | integer | left - right |
| result | text | `pass` when the difference is zero |

## data/processed/headline_figures.csv

| Column | Type | Description |
|---|---|---|
| figure | text | Name of the headline figure |
| value | number | Value |
| unit | text | `pilgrims`, `percent` or `year` |
