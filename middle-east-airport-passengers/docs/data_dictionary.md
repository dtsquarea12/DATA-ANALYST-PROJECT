# Data dictionary

## data/raw/passenger_readings.csv

One row per passenger figure per document, exactly as printed.

| Column | Description |
|---|---|
| airport_code | IATA code of the airport |
| airport | Airport name |
| city | City served |
| country | Country |
| subregion | Gulf, Levant, North Africa or Turkey |
| year | Calendar year the figure covers |
| measure | total, international or domestic passengers |
| passengers | The printed figure as a whole number (for example "95.2 million" = 95200000) |
| printed_as | The figure as printed in the document |
| rounding_unit | Precision of the printed figure in passengers (1 = exact count, 100000 = one decimal of a million) |
| use | yes if the reading enters the checks; no if it was printed before year end, is a forecast, or is set aside (reason in note) |
| source_id | Key to data/raw/sources.csv |
| note | Context for the reading |

## data/raw/sources.csv

| Column | Description |
|---|---|
| source_id | Key used in the readings files |
| publisher | Organisation that published the document |
| title_or_subject | Title or subject of the document |
| url | Link to the document |
| published | Publication date, where printed |

## data/raw/world_top10_2025.csv and data/processed/world_top10_2025.csv

ACI World preliminary 2025 rankings, top 10 by total and by international passengers.

| Column | Description |
|---|---|
| ranking | total or international |
| rank_2025 | Rank in 2025 |
| airport_code | IATA code |
| airport | Airport name |
| country | Country |
| region | Middle East, Europe, Asia-Pacific or North America |
| passengers_2025 | Passengers in 2025 (total or international, as the ranking says) |
| pct_change_vs_2024 | % change on 2024 as printed by CNN from the ACI release (total ranking only) |
| source_id | Documents the row comes from |
| check | two-documents or one-document |

## data/processed/figures_checked.csv

| Column | Description |
|---|---|
| airport_code, year, measure | Key |
| passengers | Chosen figure: the most precise reading that every other reading agrees with |
| chosen_source | Document the chosen figure comes from |
| documents | Number of documents printing a consistent figure |
| check | two-documents, one-document, or derived (Muscat total = international + domestic) |

## data/processed/passengers_tidy.csv (for Power BI, Tableau and the SQL file)

| Column | Description |
|---|---|
| airport_code, airport, city, country, subregion | As in the raw file |
| year | 2019, 2024 or 2025 |
| passengers | Total passengers in the year |
| check | two-documents, one-document or derived |
| chosen_source | Document the figure comes from |

## data/processed/airports_2025.csv

| Column | Description |
|---|---|
| airport_code, airport, city, country, subregion | As above |
| rank_2025 | Rank among the 13 airports by 2025 passengers |
| pax_2019, pax_2024, pax_2025 | Total passengers; empty where no figure was found |
| check_2019, check_2024, check_2025 | Verification status of each figure |
| pax_2025_m | 2025 passengers in millions, 2 decimals |
| change_vs_2024_pct | (pax_2025 / pax_2024 - 1) x 100, 1 decimal |
| change_vs_2019_pct | (pax_2025 / pax_2019 - 1) x 100, 1 decimal |
| added_vs_2024_m | Passengers added on 2024, millions |
| above_world_growth | True if change_vs_2024_pct is above the world figure of +3.6% |

## data/processed/headline_figures.csv

| Column | Description |
|---|---|
| measure | Name of the headline figure |
| value | Value computed by scripts/build_data.py and re-checked in the notebook |
