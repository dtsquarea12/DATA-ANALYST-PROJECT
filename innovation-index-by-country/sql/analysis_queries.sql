-- Global Innovation Index 2025 and 2026: queries on data/processed/gii_tidy.csv
-- Load the CSV as a table named gii_tidy (SQLite, PostgreSQL or any SQL engine).

-- 1. Middle East economies in 2026, Gulf first, with the change in rank since 2025
SELECT sub_region, country, score_2026, rank_2026, rank_2025, rank_change
FROM gii_tidy
WHERE region = 'Middle East'
ORDER BY CASE sub_region WHEN 'Gulf' THEN 1 WHEN 'Levant and Iraq' THEN 2
                         WHEN 'Iran, Turkey and Yemen' THEN 3 ELSE 4 END, rank_2026;

-- 2. Mean 2026 score and number of economies by region, Middle East first
SELECT region, COUNT(*) AS economies, ROUND(AVG(score_2026), 2) AS mean_score_2026,
       SUM(CASE WHEN rank_2026 <= 50 THEN 1 ELSE 0 END) AS in_top_50
FROM gii_tidy
GROUP BY region
ORDER BY CASE region WHEN 'Middle East' THEN 0 ELSE 1 END, mean_score_2026 DESC;

-- 3. Largest climbs between the 2025 and 2026 editions, all economies
SELECT country, region, rank_2025, rank_2026, rank_change
FROM gii_tidy
WHERE rank_change IS NOT NULL
ORDER BY rank_change DESC, rank_2026
LIMIT 10;

-- 4. How many economies in each region moved up, moved down or kept their rank
SELECT region,
       SUM(CASE WHEN rank_change > 0 THEN 1 ELSE 0 END) AS moved_up,
       SUM(CASE WHEN rank_change < 0 THEN 1 ELSE 0 END) AS moved_down,
       SUM(CASE WHEN rank_change = 0 THEN 1 ELSE 0 END) AS unchanged
FROM gii_tidy
WHERE rank_change IS NOT NULL
GROUP BY region
ORDER BY CASE region WHEN 'Middle East' THEN 0 ELSE 1 END, region;

-- 5. Middle East economies scoring above the world mean in 2026
SELECT country, score_2026, rank_2026
FROM gii_tidy
WHERE region = 'Middle East'
  AND score_2026 > (SELECT AVG(score_2026) FROM gii_tidy)
ORDER BY score_2026 DESC;

-- 6. Rows whose figures rest on fewer than two documents (rank 2026) or where sources differ (2025)
SELECT country, rank_check_2026, check_2025
FROM gii_tidy
WHERE region = 'Middle East' AND (rank_check_2026 <> 'two-documents' OR check_2025 <> 'two-documents');
