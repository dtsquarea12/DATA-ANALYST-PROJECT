-- Hajj pilgrims by season: queries on the tidy tables.
-- Load data/processed/pilgrims_by_year.csv as table pilgrims_by_year
-- and data/processed/pilgrims_tidy.csv as table pilgrims_tidy.

-- 1. Pilgrims by season, with the share from inside Saudi Arabia
SELECT year, total, external, internal,
       ROUND(100.0 * internal / total, 1) AS internal_share_pct
FROM pilgrims_by_year
ORDER BY year;

-- 2. Each season against 2019, the last season before COVID-19 limits
SELECT p.year,
       ROUND(100.0 * p.total    / b.total, 1)    AS total_pct_of_2019,
       ROUND(100.0 * p.external / b.external, 1) AS external_pct_of_2019,
       ROUND(100.0 * p.internal / b.internal, 1) AS internal_pct_of_2019
FROM pilgrims_by_year p
CROSS JOIN (SELECT * FROM pilgrims_by_year WHERE year = 2019) b
ORDER BY p.year;

-- 3. Change on the previous season (only where the previous calendar year is in the table)
SELECT c.year, c.total, p.total AS previous_total,
       ROUND(100.0 * (c.total - p.total) / p.total, 1) AS total_change_pct,
       ROUND(100.0 * (c.external - p.external) / p.external, 1) AS external_change_pct,
       ROUND(100.0 * (c.internal - p.internal) / p.internal, 1) AS internal_change_pct
FROM pilgrims_by_year c
JOIN pilgrims_by_year p ON p.year = c.year - 1
ORDER BY c.year;

-- 4. Seasons ranked by pilgrims from inside Saudi Arabia, lowest first
SELECT year, internal,
       RANK() OVER (ORDER BY internal) AS rank_lowest
FROM pilgrims_by_year
ORDER BY internal
LIMIT 5;

-- 5. Long table: total by group, before and after COVID-19
SELECT pilgrim_group,
       CASE WHEN year <= 2019 THEN '2008-2019' ELSE '2022-2026' END AS period,
       COUNT(*) AS seasons,
       ROUND(AVG(pilgrims)) AS average_pilgrims
FROM pilgrims_tidy
GROUP BY pilgrim_group, period
ORDER BY pilgrim_group, period;
