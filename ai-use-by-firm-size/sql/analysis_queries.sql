-- Queries on data/processed/ai_use_tidy.csv, loaded as table ai_use_tidy.
-- Columns: economy, year, measure, item, value, n_sources, verification, source_ids
-- Tested with SQLite 3.

-- 1. Share of enterprises using AI by size class, latest year for each economy
SELECT economy, year, item AS size_class, value AS pct_using_ai
FROM ai_use_tidy
WHERE measure = 'ai_use'
  AND year = (SELECT MAX(year) FROM ai_use_tidy t WHERE t.economy = ai_use_tidy.economy AND t.measure = 'ai_use')
ORDER BY CASE economy WHEN 'Turkey' THEN 1 ELSE 2 END, value;

-- 2. Gap between large and small firms, in points and as a ratio, by economy and year
SELECT s.economy, s.year,
       l.value AS large_pct, s.value AS small_pct,
       ROUND(l.value - s.value, 2) AS gap_pts,
       ROUND(l.value / s.value, 2) AS ratio_large_to_small
FROM ai_use_tidy s
JOIN ai_use_tidy l
  ON l.economy = s.economy AND l.year = s.year AND l.measure = 'ai_use' AND l.item = 'Large (250+)'
WHERE s.measure = 'ai_use' AND s.item = 'Small (10-49)'
ORDER BY CASE s.economy WHEN 'Turkey' THEN 1 ELSE 2 END, s.year;

-- 3. Change between the two years shown, by size class, in points and percent
SELECT a.economy, a.item AS size_class, b.year AS from_year, a.year AS to_year,
       b.value AS from_pct, a.value AS to_pct,
       ROUND(a.value - b.value, 2) AS change_pts,
       ROUND(100.0 * (a.value - b.value) / b.value, 1) AS change_pct
FROM ai_use_tidy a
JOIN ai_use_tidy b
  ON b.economy = a.economy AND b.item = a.item AND b.measure = 'ai_use'
 AND b.year = (SELECT MIN(year) FROM ai_use_tidy t WHERE t.economy = a.economy AND t.measure = 'ai_use' AND t.item = 'Small (10-49)')
WHERE a.measure = 'ai_use' AND a.year = 2025 AND a.item <> 'All (10+ employees)'
ORDER BY CASE a.economy WHEN 'Turkey' THEN 1 ELSE 2 END, a.value;

-- 4. Non-users that considered AI, by size class, 2025
SELECT economy, item AS size_class, value AS pct_of_non_users_considered
FROM ai_use_tidy
WHERE measure = 'considered_not_used'
ORDER BY CASE economy WHEN 'Turkey' THEN 1 ELSE 2 END, value;

-- 5. Reasons for not using AI among enterprises that considered it, 2025
SELECT economy, item AS reason, value AS pct, verification
FROM ai_use_tidy
WHERE measure = 'reason_not_used'
ORDER BY CASE economy WHEN 'Turkey' THEN 1 ELSE 2 END, value DESC;

-- 6. What AI-using enterprises use AI for, 2025
SELECT economy, item AS purpose, value AS pct_of_ai_users, verification
FROM ai_use_tidy
WHERE measure = 'purpose'
ORDER BY CASE economy WHEN 'Turkey' THEN 1 ELSE 2 END, value DESC;

-- 7. How many figures rest on one document
SELECT verification, COUNT(*) AS figures
FROM ai_use_tidy
GROUP BY verification;
