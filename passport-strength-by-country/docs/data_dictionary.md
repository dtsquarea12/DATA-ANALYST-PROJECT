# Data dictionary

A score is the number of destinations, out of 227, that the holder of a passport can enter without arranging a visa before travel. Visa on arrival, a visitor's permit and an electronic travel authority count as access. A visa or e-visa that needs approval before departure does not.

## data/raw/

### henley_2026_april_reading_wikipedia.csv (199 rows)

The 2026 rank table on the Wikipedia page for the Henley Passport Index, read on 10 October 2026. Its top ten equals the 13 April 2026 update.

| Column | Type | Description |
|---|---|---|
| rank | integer | Rank as printed. Tied passports share a rank. |
| country | text | Passport, as named on the page. |
| visa_free_score | integer | Destinations open without a prior visa. |

### henley_2026_april_reading_packzup.txt (101 lines, 199 passports)

The same edition as printed by Packzup. One line per distinct score: `score|rank|passport;passport;...`.

### henley_2026_edition_readings.csv (108 rows)

Figures printed in individual documents, one row per figure per document.

| Column | Type | Description |
|---|---|---|
| edition | text | Edition of the index the figure belongs to: `2026-04` or `2026-07`. |
| country | text | Passport. |
| rank | integer | Rank printed in the document. Empty if the document prints none. |
| visa_free_score | integer | Score printed in the document. Empty if the document prints only a rank. |
| source_id | text | Document, keyed to `sources.csv`. |

### published_figures.csv (9 rows)

Totals and averages printed by the publisher or the press, used as checks.

| Column | Type | Description |
|---|---|---|
| figure | text | Name of the figure. |
| value | number | Value as printed. |
| edition | text | Edition or year the figure refers to. |
| source_id | text | Document, keyed to `sources.csv`. |
| note | text | Where else the figure is printed. |

### country_reference.csv (199 rows)

| Column | Type | Description |
|---|---|---|
| country | text | Passport name used in the April table. |
| iso3 | text | Three-letter country code. |
| region | text | Middle East, Europe, Rest of Asia, Rest of Africa, North America, South America or Oceania. |

### sources.csv (12 rows)

| Column | Type | Description |
|---|---|---|
| source_id | text | Short key used in the other raw files. |
| publisher | text | Publisher of the document. |
| title | text | Title of the page or article. |
| published | text | Publication date, or the date the page was read. |
| edition | text | Edition of the index the document reports. |
| url | text | Link. |

## data/processed/

### passport_tidy.csv (199 rows, one per passport)

| Column | Type | Description |
|---|---|---|
| iso3 | text | Three-letter country code. |
| country | text | Passport. |
| region | text | One of seven regions. The Middle East is taken out of Asia and Africa. |
| sub_region | text | For the Middle East: Gulf, Levant and Iraq, North Africa, or Iran, Turkey and Yemen. Otherwise equal to region. |
| score_apr_2026 | integer | Score in the April 2026 edition. |
| rank_apr_2026 | integer | Rank in the April 2026 edition (dense rank of the score, equal to the printed rank). |
| share_of_destinations_pct | number | score_apr_2026 as a percentage of 227 destinations. |
| vs_world_mean_apr | number | score_apr_2026 minus the mean of all 199 April scores (107.21). |
| apr_check | text | `two-publishers` if both readings print the same score and rank. `publishers-differ` if they do not (Bangladesh). |
| apr_article_checks | integer | Number of news articles that also print an April figure for the passport, all equal to the table. |
| score_jul_2026 | integer | Score in the July 2026 edition. Empty if no document printing it was found. |
| rank_jul_2026 | integer | Rank in the July 2026 edition. Empty if not found, or if documents print different ranks. |
| change_apr_to_jul | integer | score_jul_2026 minus score_apr_2026. |
| jul_check | text | Number of publishers that print the July score: `one-publisher`, `2-publishers` and so on, or `no-july-figure`. |
| jul_documents | integer | The same count as a number. |
| jul_sources | text | Keys of the documents that print the July score. |
| jul_rank_note | text | Filled when documents print different July ranks. |
| latest_score | integer | July score if one was found, otherwise the April score. |
| latest_edition | text | Edition of latest_score: `2026-07` or `2026-04`. |
| score_wikipedia | integer | April score in the Wikipedia reading. |
| score_packzup | integer | April score in the Packzup reading. |

### middle_east_editions.csv (40 rows: 20 passports, two editions)

| Column | Type | Description |
|---|---|---|
| iso3, country, sub_region | text | As above. |
| edition | text | `2026-04` or `2026-07`. |
| score | integer | Score in that edition. Empty if not found. |
| rank | integer | Rank in that edition. Empty if not found or disputed. |
| check | text | apr_check or jul_check for that edition. |

### region_summary.csv (12 rows)

April 2026 scores summarised for seven regions, four Middle East sub-regions and the world.

| Column | Type | Description |
|---|---|---|
| level | text | `region`, `middle_east_sub_region` or `world`. |
| group | text | Name of the group. |
| passports | integer | Passports in the group. |
| mean_score, median_score | number | Mean and median April score. |
| min_score, max_score | integer | Lowest and highest April score. |
| above_world_mean | integer | Passports above the mean of all 199 scores. |
| score_150_or_more | integer | Passports with a score of 150 or more. |
| score_below_60 | integer | Passports with a score below 60. |

### source_checks.csv (4 rows)

| Column | Type | Description |
|---|---|---|
| check | text | Published figure tested. |
| published_value | number | Value as printed. |
| computed_value | number | Value computed from the table. |
| rule | text | `exact`, or `within 1` for the rounded July average against the April mean. |
| result | text | `match`. The build stops on any other outcome. |
