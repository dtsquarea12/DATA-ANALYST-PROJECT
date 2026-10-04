# Data dictionary

## data/processed/fuel_prices_tidy.csv

The main analysis table. One row per country, month and fuel.

| Column | Type | Description |
|---|---|---|
| `country` | text | Country name |
| `group` | text | `Gulf` for the six Middle East countries studied, `Comparison` for the rest |
| `continent` | text | Middle East, North America, Europe, Asia, Africa, South America or Oceania |
| `month` | text (YYYY-MM) | Month of the reading |
| `period` | text | `pre-war` for January and February 2026, `since war` from March 2026 |
| `fuel` | text | `gasoline` or `diesel` |
| `price_usd_per_litre` | number | Retail pump price in US dollars per litre, tax included |
| `basis` | text | What the figure is: source series, grade, exchange rate, and whether it is a monthly average or a single-day reading |

Gasoline is 95 octane for the Gulf and Europe and regular grade for North America. Iran is the middle quota tier (30,000 rials a litre) at the open-market exchange rate.

## data/processed/benchmarks.csv

| Column | Type | Description |
|---|---|---|
| `month` | text (YYYY-MM) | Month |
| `brent_usd_per_bbl` | number | Brent crude spot, monthly average, US dollars per barrel. EIA for January to August, World Bank for September |
| `usgc_gasoline_spot_usd_per_litre` | number | US Gulf Coast conventional regular gasoline spot price, converted from dollars per gallon |
| `usgc_diesel_spot_usd_per_litre` | number | US Gulf Coast ultra-low-sulphur diesel spot price, converted from dollars per gallon |

September product prices are the mean of four weekly averages. October is blank because the month was not complete.

## data/processed/subsidy_estimates.csv

One row per Gulf country and fuel.

| Column | Type | Description |
|---|---|---|
| `country` | text | Gulf country |
| `fuel` | text | `gasoline` or `diesel` |
| `gap_prewar_regional_usd_l` | number | Average gap per litre in January and February, regional reference price |
| `gap_sincewar_regional_usd_l` | number | Average gap per litre from March, regional reference price |
| `gap_prewar_international_usd_l` | number | Same, international reference price |
| `gap_sincewar_international_usd_l` | number | Same, international reference price |
| `annual_volume_bn_litres_2023` | number | Annual sales in billions of litres, 2023 |
| `annualised_subsidy_regional_usd_bn` | number | Since-war gap multiplied by annual volume, US dollars billions a year |
| `annualised_subsidy_international_usd_bn` | number | Same, international reference price |

A gap is the reference price including local VAT, minus the pump price. A positive gap means the pump price is below the market price.

## data/raw/gulf_prices_local_currency.csv

Official prices as announced, before conversion.

| Column | Type | Description |
|---|---|---|
| `country` | text | Gulf country |
| `month` | text (YYYY-MM) | Month the price applied |
| `grade` | text | Fuel grade as named locally, for example Super 98 or Mumtaz 95 |
| `price_local` | number | Price in local currency per litre |
| `currency` | text | ISO currency code |
| `unit` | text | Unit of the price |
| `source_url` | text | Link to the source |
| `confidence` | text | `verified-2-sources`, `single-source` or `MISSING` |
| `note` | text | Effective dates and caveats |

## data/raw/comparison_prices_sources.csv

| Column | Type | Description |
|---|---|---|
| `country` | text | Comparison country |
| `continent` | text | Continent |
| `month_or_date` | text | Month (YYYY-MM) for averages, or a date for single-day readings |
| `fuel` | text | `gasoline` or `diesel` |
| `price_local` | number | Price in local currency |
| `currency` | text | ISO currency code |
| `unit` | text | Per litre, or per US gallon for the United States |
| `fx_rate_to_usd` | number | Local currency units per US dollar used for conversion |
| `price_usd_per_litre` | number | Converted price |
| `source_url` | text | Link to the source |
| `note` | text | Monthly average, point-in-time, or MISSING |
