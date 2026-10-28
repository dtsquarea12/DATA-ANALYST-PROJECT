# Data dictionary

## data/raw/effect_readings.csv

One row per figure per document (75 rows).

| Column | Type | Description |
|---|---|---|
| study_id | text | Short id of the study (see `studies.csv`) |
| version | text | Version of the study the figure belongs to (for example `QJE 2025` or `WP 2023` for the customer support study) |
| measure | text | What the figure measures (see list below) |
| group | text | Who the figure covers: `all`, `least_experienced`, `most_experienced`, `ai_users`, `all_workers`, `with_ai`, `without_ai`, `outside_frontier` |
| value_printed | text | The figure exactly as the document printed it, kept as text so its precision is known |
| source_id | text | Document the reading comes from (see `sources.csv`) |
| note | text | Context; a note starting with `set_aside` marks a reading left out of the agreement check |

Measures:

| Measure | Unit | Meaning |
|---|---|---|
| sample_size | people | Workers or participants in the study (Denmark: workers) |
| workplaces | count | Workplaces covered (Denmark) |
| occupations | count | Occupations covered (Denmark) |
| resolutions_per_hour_change_pct | % | Change in customer support chats resolved per hour with AI assistance |
| time_change_pct | % | Change in time taken per task with AI (negative = less time) |
| quality_change_pct | % | Change in graded quality of the work |
| minutes_to_complete | minutes | Average time to finish the coding task, by group |
| tasks_completed_change_pct | % | Change in the number of tasks completed |
| tasks_completed_change_pct_low / _high | % | Low and high end of a range printed for a sub-group |
| speed_gain_pct | % | How much faster tasks were completed, as printed |
| performance_change_pct | % | Change in graded performance for a sub-group |
| correct_answer_change_pts | percentage points | Change in the chance of reaching the correct answer on a task outside what the AI did well |
| time_saved_share_of_hours_pct | % of work hours | Time saved by AI as a share of all work hours |
| hours_saved_per_40h_week | hours | The same saving expressed for a 40-hour week |
| earnings_effect_upper_bound_pct | % | Average effect on earnings or hours that the study rules out above this size |

## data/raw/studies.csv

| Column | Description |
|---|---|
| study_id | Short id |
| study | Plain description of the study |
| authors | Authors |
| published | Where and when it was published |
| design | Randomised experiment, field experiment, survey |
| setting | What work was studied and where |
| country | Country when the sources read state it |
| unit_of_work | What was measured |
| scope | `single task`, `day-to-day coding work` or `whole job` |

## data/raw/sources.csv

| Column | Description |
|---|---|
| source_id | Id used in `effect_readings.csv` |
| study_id | Study the document covers |
| publisher | Publisher of the document |
| kind | Paper, paper page, abstract reprint, news, research note, blog |
| title | Title |
| date | Publication date as far as known |
| url | Link |

## data/processed/effects_tidy.csv

One row per figure after the agreement check (34 rows). Columns `study_id`, `version`, `measure`, `group` as above, plus:

| Column | Description |
|---|---|
| value | The figure (most precise agreeing reading) |
| n_sources | Number of documents that print it |
| verification | `two-or-more-documents` or `one-document` |
| source_ids | Documents that print it, separated by `;` |
| note | First note attached to the readings |

## data/processed/study_headlines.csv

One row per study with its main effect, written as a gain (7 rows).

| Column | Description |
|---|---|
| study_id, study, published, scope, design | From `studies.csv` |
| measure | Measure the headline uses |
| effect_label | Plain description of the effect |
| gain_pct | The effect as a positive improvement in % (a time cut of 40% is shown as 40) |
| sample_size | Participants, where printed |
| verification, n_sources | From `effects_tidy.csv` |

## data/processed/gain_by_experience.csv

| Column | Description |
|---|---|
| study_id, study | Study |
| least_low, least_high | Gain for the least experienced or lowest-performing staff (%); equal when a single figure is printed |
| most_low, most_high | Gain for the most experienced or top-performing staff (%); empty when no figure is printed |
| note | How each group is defined |

## data/processed/headline_figures.csv

| Column | Description |
|---|---|
| figure | Name of a headline figure used in the README |
| value | Its value |
