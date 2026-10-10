-- Passport strength by country: queries on data/processed/passport_tidy.csv loaded as table passport.
-- Tested with SQLite. Scores are destinations open without a prior visa, out of 227.

-- 1. The 20 Middle East passports, latest figure available, highest first.
SELECT country, sub_region, score_apr_2026, score_jul_2026, latest_score, latest_edition, jul_check
FROM passport
WHERE region = 'Middle East'
ORDER BY latest_score DESC, country;

-- 2. Summary by region on the full April 2026 table, Middle East first.
SELECT region,
       COUNT(*)                                   AS passports,
       ROUND(AVG(score_apr_2026), 2)              AS mean_score,
       MIN(score_apr_2026)                        AS min_score,
       MAX(score_apr_2026)                        AS max_score,
       SUM(score_apr_2026 > (SELECT AVG(score_apr_2026) FROM passport)) AS above_world_mean
FROM passport
GROUP BY region
ORDER BY CASE region WHEN 'Middle East' THEN 0 ELSE 1 END, mean_score DESC;

-- 3. Middle East sub-regions.
SELECT sub_region,
       COUNT(*)                      AS passports,
       ROUND(AVG(score_apr_2026), 2) AS mean_score,
       MIN(score_apr_2026)           AS min_score,
       MAX(score_apr_2026)           AS max_score
FROM passport
WHERE region = 'Middle East'
GROUP BY sub_region
ORDER BY mean_score DESC;

-- 4. Gulf passports: score and rank in April and July 2026.
SELECT country, score_apr_2026, score_jul_2026, change_apr_to_jul, rank_apr_2026, rank_jul_2026,
       rank_jul_2026 - rank_apr_2026 AS rank_places_lower
FROM passport
WHERE sub_region = 'Gulf'
ORDER BY score_jul_2026 DESC;

-- 5. Where each Middle East passport sits in the world: number of passports with a higher April score.
SELECT p.country, p.score_apr_2026, p.rank_apr_2026,
       (SELECT COUNT(*) FROM passport q WHERE q.score_apr_2026 > p.score_apr_2026) AS passports_with_higher_score
FROM passport p
WHERE p.region = 'Middle East'
ORDER BY p.score_apr_2026 DESC, p.country;

-- 6. Passports outside the Middle East with the same April score band as Qatar (within 10 destinations).
SELECT country, region, score_apr_2026
FROM passport
WHERE ABS(score_apr_2026 - (SELECT score_apr_2026 FROM passport WHERE country = 'Qatar')) <= 10
ORDER BY score_apr_2026 DESC, country;

-- 7. How far each figure is checked: April rows by check status, July rows by number of publishers.
SELECT 'April 2026' AS edition, apr_check AS status, COUNT(*) AS passports FROM passport GROUP BY apr_check
UNION ALL
SELECT 'July 2026', jul_check, COUNT(*) FROM passport WHERE jul_check <> 'no-july-figure' GROUP BY jul_check;
