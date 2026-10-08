-- AI use by country: queries on the processed tables.
-- Load data/processed/ai_use_by_economy.csv as table ai_use_by_economy
-- and data/processed/ai_use_tidy.csv as table ai_use_tidy (SQLite, Power BI or any SQL engine).
-- Shares are percentages of people aged 15 to 64 who used a generative AI product in the period.

-- 1. Middle East economies, Q2 2026, by sub-region and value
SELECT sub_region, economy, q2_2026_pct, rank_q2_2026, change_q1_to_q2_pp
FROM ai_use_by_economy
WHERE region = 'Middle East'
ORDER BY CASE sub_region WHEN 'Gulf' THEN 1 WHEN 'Levant and Iraq' THEN 2
                         WHEN 'Iran and Turkey' THEN 3 ELSE 4 END,
         q2_2026_pct DESC;

-- 2. Region summary, Middle East first: count, economies above the world figure (18.8%), highest value
SELECT region,
       COUNT(*)                                              AS economies,
       SUM(CASE WHEN own_estimate = 'yes' THEN 1 ELSE 0 END) AS economies_own_estimate,
       SUM(CASE WHEN q2_2026_pct > 18.8 THEN 1 ELSE 0 END)   AS above_world,
       ROUND(AVG(q2_2026_pct), 1)                            AS simple_mean_q2_2026_pct,
       MAX(q2_2026_pct)                                      AS highest_q2_2026_pct
FROM ai_use_by_economy
GROUP BY region
ORDER BY CASE region WHEN 'Middle East' THEN 1 WHEN 'Europe' THEN 2 WHEN 'Asia' THEN 3
                     WHEN 'Oceania' THEN 4 WHEN 'Americas' THEN 5 ELSE 6 END;

-- 3. Largest gains from Q1 2026 to Q2 2026 among economies with their own estimate
SELECT economy, region, q1_2026_pct, q2_2026_pct, change_q1_to_q2_pp
FROM ai_use_by_economy
WHERE own_estimate = 'yes'
ORDER BY change_q1_to_q2_pp DESC, economy
LIMIT 10;

-- 4. Economies whose share fell between Q1 and Q2 2026
SELECT economy, region, q1_2026_pct, q2_2026_pct, change_q1_to_q2_pp
FROM ai_use_by_economy
WHERE change_q1_to_q2_pp < 0;

-- 5. Economies that carry a shared regional estimate rather than their own figure
SELECT shared_value_group, COUNT(*) AS economies, MIN(q2_2026_pct) AS q2_2026_pct,
       GROUP_CONCAT(economy, ', ') AS members
FROM ai_use_by_economy
WHERE own_estimate = 'no'
GROUP BY shared_value_group
ORDER BY q2_2026_pct DESC;

-- 6. Gulf economies over all four periods (long table)
SELECT economy, period, ai_diffusion_pct, verification
FROM ai_use_tidy
WHERE sub_region = 'Gulf'
ORDER BY economy, period;

-- 7. How each Q2 2026 figure was checked
SELECT verification, COUNT(*) AS economies
FROM ai_use_tidy
WHERE period = '2026-Q2'
GROUP BY verification;
