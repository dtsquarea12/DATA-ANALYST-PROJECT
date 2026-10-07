-- Qatar food inflation: queries on the tidy table.
-- Table qatar_cpi  = data/processed/qatar_cpi_tidy.csv
-- Table cumulative = data/processed/cumulative_change_by_group.csv
-- Written for SQLite. Tested with Python's sqlite3 module.

-- 1. Year-on-year change by spending group in June 2026, highest first,
--    with the gap to the all-items rate.
SELECT g.group_label,
       g.value AS yoy_pct,
       ROUND(g.value - a.value, 2) AS gap_to_all_items_points,
       g.verification
FROM qatar_cpi g
JOIN qatar_cpi a
  ON a.month = g.month AND a.measure = g.measure AND a.cpi_group = 'all_items'
WHERE g.month = '2026-06' AND g.measure = 'yoy_pct'
  AND g.cpi_group NOT LIKE 'all_items%'
ORDER BY g.value DESC;

-- 2. Food and all-items year-on-year rates side by side for every month.
SELECT month,
       MAX(CASE WHEN cpi_group = 'food_beverages' THEN value END) AS food_yoy_pct,
       MAX(CASE WHEN cpi_group = 'all_items' THEN value END) AS all_items_yoy_pct
FROM qatar_cpi
WHERE measure = 'yoy_pct'
GROUP BY month
ORDER BY month;

-- 3. Month-on-month change in food prices with the previous month alongside (window function).
SELECT month,
       value AS food_mom_pct,
       LAG(value) OVER (ORDER BY month) AS previous_month_mom_pct,
       verification
FROM qatar_cpi
WHERE cpi_group = 'food_beverages' AND measure = 'mom_pct'
ORDER BY month;

-- 4. Cumulative change February to June 2026 by group, ranked.
SELECT RANK() OVER (ORDER BY cumulative_change_pct DESC) AS rank_highest_rise,
       group_label,
       cumulative_change_pct,
       single_publisher_months
FROM cumulative
WHERE "window" = 'since_feb_2026'
  AND method = 'chained monthly changes'
  AND cpi_group NOT LIKE 'all_items%'
ORDER BY cumulative_change_pct DESC;

-- 5. Sensitivity to the starting month: February 2026 against December 2025.
SELECT group_label,
       MAX(CASE WHEN "window" = 'since_feb_2026' THEN cumulative_change_pct END) AS since_feb_2026_pct,
       MAX(CASE WHEN "window" = 'since_dec_2025' THEN cumulative_change_pct END) AS since_dec_2025_pct
FROM cumulative
WHERE method = 'chained monthly changes'
GROUP BY group_label
ORDER BY since_feb_2026_pct DESC;

-- 6. Does the published index follow from the published monthly change? Largest gap should be under 0.02.
WITH idx AS (
  SELECT month,
         MAX(CASE WHEN measure = 'index' THEN value END) AS index_level,
         MAX(CASE WHEN measure = 'mom_pct' THEN value END) AS mom_pct
  FROM qatar_cpi
  WHERE cpi_group = 'all_items'
  GROUP BY month
)
SELECT month,
       index_level,
       ROUND(LAG(index_level) OVER (ORDER BY month) * (1 + mom_pct / 100.0), 2) AS implied_index,
       ROUND(ABS(index_level - LAG(index_level) OVER (ORDER BY month) * (1 + mom_pct / 100.0)), 3) AS gap
FROM idx
ORDER BY month;

-- 7. How much of the table rests on one publisher, by month and measure.
SELECT month, measure,
       SUM(CASE WHEN verification = 'single-publisher' THEN 1 ELSE 0 END) AS single_publisher_rows,
       COUNT(*) AS all_rows
FROM qatar_cpi
GROUP BY month, measure
HAVING single_publisher_rows > 0
ORDER BY month, measure;
