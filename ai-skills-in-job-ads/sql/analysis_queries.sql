-- AI skills in job ads: queries on the tidy tables in data/processed/.
-- Load each CSV as a table named after the file (for example ai_share_by_country_2025).
-- Tested with SQLite 3.

-- 1. Economies in the AI Index 2025 table, Middle East first, then by region and value.
SELECT region, country, ai_share_pct_2025, rank
FROM ai_share_by_country_2025
ORDER BY CASE region WHEN 'Middle East' THEN 1 WHEN 'Asia' THEN 2 WHEN 'Europe' THEN 3
                     WHEN 'Americas' THEN 4 ELSE 5 END,
         ai_share_pct_2025 DESC;

-- 2. Economies above and below the UAE in 2025.
SELECT SUM(ai_share_pct_2025 > (SELECT ai_share_pct_2025 FROM ai_share_by_country_2025 WHERE country = 'United Arab Emirates')) AS above_uae,
       SUM(ai_share_pct_2025 < (SELECT ai_share_pct_2025 FROM ai_share_by_country_2025 WHERE country = 'United Arab Emirates')) AS below_uae,
       COUNT(*) AS economies
FROM ai_share_by_country_2025;

-- 3. Average and range by region (2025).
SELECT region, COUNT(*) AS economies, ROUND(AVG(ai_share_pct_2025), 2) AS mean_pct,
       MIN(ai_share_pct_2025) AS min_pct, MAX(ai_share_pct_2025) AS max_pct
FROM ai_share_by_country_2025
GROUP BY region
ORDER BY mean_pct DESC;

-- 4. Gulf: how AI-linked vacancies split by what the job does with AI (sums to 100).
SELECT role, share_of_ai_vacancies_pct,
       SUM(share_of_ai_vacancies_pct) OVER () AS total_pct
FROM gulf_ai_vacancies_by_role
ORDER BY share_of_ai_vacancies_pct DESC;

-- 5. Gulf sectors grouped by the ratio GulfTalent published.
SELECT published_ratio, GROUP_CONCAT(sector, ', ') AS sectors, MAX(ratio_pct) AS ratio_pct
FROM gulf_ai_share_by_sector
GROUP BY published_ratio
ORDER BY ratio_pct DESC;

-- 6. US sectors: change in AI share of postings, 2024 to 2025, fastest first.
SELECT sector, share_2024_pct, share_2025_pct, change_pts,
       ROUND(100.0 * change_pts / share_2024_pct, 1) AS change_pct
FROM us_ai_share_by_sector
ORDER BY change_pts DESC;

-- 7. Change in AI share of postings, first to last period, by series.
SELECT series, MIN(period) AS first_period, MAX(period) AS last_period,
       MAX(CASE WHEN period = (SELECT MIN(period) FROM ai_share_trend t2 WHERE t2.series = t.series) THEN share_pct END) AS first_pct,
       MAX(CASE WHEN period = (SELECT MAX(period) FROM ai_share_trend t2 WHERE t2.series = t.series) THEN share_pct END) AS last_pct
FROM ai_share_trend t
GROUP BY series;

-- 8. How many figures rest on one document.
SELECT dataset, verification, COUNT(*) AS figures
FROM readings_tidy
GROUP BY dataset, verification
ORDER BY dataset, verification;
