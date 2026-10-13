-- Import tariffs by country: queries on data/processed/tariffs_tidy.csv loaded as table tariffs.
-- Tested with SQLite. mfn_applied_avg is the simple average MFN applied tariff, all products, in percent.

-- 1. Middle East economies with an applied figure, lowest first
SELECT country, sub_region, mfn_year, mfn_applied_avg, rank_low_to_high, economies_higher
FROM tariffs
WHERE region = 'Middle East' AND mfn_applied_avg IS NOT NULL
ORDER BY mfn_applied_avg, country;

-- 2. Economies, mean and range by region (each economy counts once, the EU is one entry)
SELECT region, COUNT(*) AS economies, ROUND(AVG(mfn_applied_avg), 2) AS mean_pct,
       MIN(mfn_applied_avg) AS min_pct, MAX(mfn_applied_avg) AS max_pct
FROM tariffs
WHERE mfn_applied_avg IS NOT NULL
GROUP BY region
ORDER BY mean_pct;

-- 3. Gulf average against the world mean
SELECT ROUND(AVG(CASE WHEN sub_region = 'Gulf' THEN mfn_applied_avg END), 2) AS gulf_mean_pct,
       ROUND(AVG(mfn_applied_avg), 2) AS world_mean_pct
FROM tariffs
WHERE mfn_applied_avg IS NOT NULL;

-- 4. Ten highest averages in the table
SELECT economy, region, mfn_year, mfn_applied_avg
FROM tariffs
WHERE mfn_applied_avg IS NOT NULL
ORDER BY mfn_applied_avg DESC, economy
LIMIT 10;

-- 5. Economies with a lower average than every Gulf state
SELECT COUNT(*) AS economies_below_gulf_minimum
FROM tariffs
WHERE mfn_applied_avg < (SELECT MIN(mfn_applied_avg) FROM tariffs WHERE sub_region = 'Gulf');

-- 6. Rows whose applied figure rests on one reading or is not from 2025
SELECT economy, mfn_year, mfn_applied_avg, readings, wto_profile_check
FROM tariffs
WHERE readings <> 'two' OR mfn_year <> 2025
ORDER BY economy;
