# Data dictionary

## data/raw/wtp2026_all_products_reading_a.txt

Lines starting with `#` are notes. Each other line: economy name in quotes, then every number printed on that row of the World Tariff Profiles 2026 "All products" summary table, in printed order. Blank cells are not printed. `scripts/build_data.py` reads only the first numbers:

| Row type | How it is recognised | Numbers used |
|---|---|---|
| WTO member with an applied rate | year (2024 or 2025) first, 15 or more numbers after it | year, binding coverage %, bound simple average %, MFN applied simple average % |
| Not a WTO member | year first, 10 or fewer numbers after it | year, MFN applied simple average % |
| WTO member, no applied rate | no year | binding coverage %, bound simple average % |

## data/raw/wtp2026_all_products_reading_b.txt

Same table from a second copy of the report, first four numbers on each row only.

## data/raw/wto_ttd_profiles.csv

| Column | Description |
|---|---|
| economy | Name as in the WTO table |
| mfn_applied_simple_avg | Simple average MFN applied tariff on the WTO Tariff & Trade Data profile, % |
| mfn_year | Year the profile gives for that figure |
| mfn_duty_free_share | Share of tariff lines duty free under MFN, % |
| bound_simple_avg | Simple average bound tariff, % (empty for non-members) |
| binding_coverage | Share of tariff lines with a bound rate, % |
| url | Profile page |
| read_on | Date read |

## data/raw/country_reference.csv

| Column | Description |
|---|---|
| country | Short country name |
| iso3 | ISO 3166 alpha-3 code (EUU for the European Union) |
| region | Middle East, Europe, Rest of Asia, Rest of Africa, North America, South America or Oceania |

## data/raw/sources.csv

source, publisher, url, used_for.

## data/processed/tariffs_tidy.csv

| Column | Description |
|---|---|
| economy | Name as printed by WTO |
| country | Short name |
| iso3 | ISO code |
| region | Region from country_reference.csv |
| sub_region | Gulf, Levant and Iraq, Iran, Turkey and Yemen, or North Africa (Middle East only) |
| wto_member | True if the row has bound tariffs (WTO member) |
| mfn_year | Year of the MFN applied figure (empty if none) |
| mfn_applied_avg | Simple average MFN applied tariff, all products, % |
| bound_avg | Simple average bound tariff, all products, % |
| binding_coverage | Share of tariff lines bound, % |
| rank_low_to_high | Rank among the 132 economies with a figure, 1 = lowest, ties share the lower rank |
| economies_higher | Number of economies with a strictly higher average |
| share_economies_lower_pct | Share of the 132 economies with a strictly lower average, % |
| readings | "two" if both readings agree, "one (B)" if only reading B has the row |
| wto_profile_check | Result of the comparison with the WTO country profile, or "not checked" |

## data/processed/middle_east.csv

The 20 Middle East economies. Columns as in the tidy table, plus `in_table` (False for economies not in the WTO table).

## data/processed/region_summary.csv

| Column | Description |
|---|---|
| region | Gulf (6), a region, or World |
| economies | Economies with an applied figure |
| mean, median, min, max | Of economy averages, % |
| basis | "EU counted once" or "EU as 27 members" |

## data/processed/source_checks.csv

| Column | Description |
|---|---|
| economy | Name as printed by WTO |
| mfn_applied_avg_wtp, mfn_year_wtp | Figure and year in World Tariff Profiles 2026 |
| mfn_applied_avg_ttd, mfn_year_ttd | Figure and year on the WTO country profile |
| check | confirmed: same value and year; confirmed value: profile labels another year; differs: profile shows another year; differs: same year |
