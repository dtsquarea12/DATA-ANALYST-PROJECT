-- Saudi real estate prices: queries on the tidy tables.
-- Load data/processed/segment_changes.csv as table segment_changes,
-- data/processed/region_index.csv as table region_index,
-- data/processed/national_index.csv as table national_index
-- and data/processed/price_index_tidy.csv as table price_index_tidy.

-- 1. Annual change by property type in the latest quarter, lowest first
SELECT segment_label, sector, weight_pct, yoy_pct, qoq_pct, yoy_source_check
FROM segment_changes
WHERE period = 'Q2 2026'
  AND segment NOT IN ('all', 'residential', 'commercial', 'agricultural')
ORDER BY yoy_pct;

-- 2. Villas, residential land and apartments: annual change by quarter
SELECT period,
       MAX(CASE WHEN segment = 'villa' THEN yoy_pct END)            AS villa_yoy_pct,
       MAX(CASE WHEN segment = 'residential_land' THEN yoy_pct END) AS residential_land_yoy_pct,
       MAX(CASE WHEN segment = 'apartment' THEN yoy_pct END)        AS apartment_yoy_pct,
       MAX(CASE WHEN segment = 'all' THEN yoy_pct END)              AS all_property_yoy_pct
FROM segment_changes
GROUP BY period
ORDER BY CAST(substr(period, 4, 4) AS INTEGER), substr(period, 2, 1);

-- 3. Gap between the fastest- and slowest-moving property type in each quarter
SELECT period,
       MAX(yoy_pct) AS highest_yoy_pct,
       MIN(yoy_pct) AS lowest_yoy_pct,
       ROUND(MAX(yoy_pct) - MIN(yoy_pct), 1) AS gap_pct_points
FROM segment_changes
WHERE segment NOT IN ('all', 'residential', 'commercial', 'agricultural')
GROUP BY period
ORDER BY CAST(substr(period, 4, 4) AS INTEGER), substr(period, 2, 1);

-- 4. Regions in Q1 2026, the latest quarter with all 13 regions, ranked by annual change
SELECT region, index_level, yoy_pct,
       RANK() OVER (ORDER BY yoy_pct DESC) AS rank_by_change
FROM region_index
WHERE period = 'Q1 2026'
ORDER BY yoy_pct DESC;

-- 5. Change in each region's index level over six quarters, Q3 2024 to Q1 2026
SELECT a.region, a.index_level AS level_q3_2024, b.index_level AS level_q1_2026,
       ROUND(100.0 * (b.index_level - a.index_level) / a.index_level, 1) AS change_pct
FROM region_index a
JOIN region_index b ON b.region = a.region AND b.period = 'Q1 2026'
WHERE a.period = 'Q3 2024'
ORDER BY change_pct DESC;

-- 6. How many regions rose and fell on the year, by quarter
SELECT period,
       COUNT(yoy_pct) AS regions_with_figure,
       SUM(CASE WHEN yoy_pct > 0 THEN 1 ELSE 0 END) AS regions_rising,
       SUM(CASE WHEN yoy_pct < 0 THEN 1 ELSE 0 END) AS regions_falling
FROM region_index
GROUP BY period
ORDER BY CAST(substr(period, 4, 4) AS INTEGER), substr(period, 2, 1);

-- 7. National index level by quarter, with the basis of each level
SELECT period, index_level, level_basis, yoy_pct, qoq_pct
FROM national_index
ORDER BY CAST(substr(period, 4, 4) AS INTEGER), substr(period, 2, 1);

-- 8. How each figure is confirmed
SELECT measure, source_check, COUNT(*) AS figures
FROM price_index_tidy
GROUP BY measure, source_check
ORDER BY measure, figures DESC;
