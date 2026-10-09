-- Corporate tax rates by country: queries on the processed table.
-- Load data/processed/corporate_tax_tidy.csv as table corporate_tax (SQLite, Power BI or any SQL engine).
-- Rates are the standard top statutory corporate income tax rate in 2025, in percent.

-- 1. Middle East economies by sub-region and rate
SELECT sub_region, country, rate_2025_pct, rate_with_min_tax_2025_pct, check_status
FROM corporate_tax
WHERE region = 'Middle East'
ORDER BY CASE sub_region WHEN 'Gulf' THEN 1 WHEN 'Levant and Iraq' THEN 2
                         WHEN 'Iran, Turkey and Yemen' THEN 3 ELSE 4 END,
         rate_2025_pct, country;

-- 2. Region summary, Middle East first: count, simple mean, lowest and highest rate
SELECT region,
       COUNT(*)                                             AS jurisdictions,
       ROUND(AVG(rate_2025_pct), 2)                         AS mean_rate_pct,
       MIN(rate_2025_pct)                                   AS min_rate_pct,
       MAX(rate_2025_pct)                                   AS max_rate_pct,
       SUM(CASE WHEN rate_2025_pct <= 15 THEN 1 ELSE 0 END) AS at_or_below_15_pct
FROM corporate_tax
GROUP BY region
ORDER BY CASE region WHEN 'Middle East' THEN 1 WHEN 'Europe' THEN 2 WHEN 'Rest of Asia' THEN 3
                     WHEN 'Rest of Africa' THEN 4 WHEN 'North America' THEN 5
                     WHEN 'South America' THEN 6 ELSE 7 END;

-- 3. Gulf states: mean rate before and after the 15% minimum tax on large multinational groups
SELECT COUNT(*)                                   AS gulf_states,
       ROUND(AVG(rate_2025_pct), 2)               AS mean_rate_pct,
       ROUND(AVG(rate_with_min_tax_2025_pct), 2)  AS mean_rate_with_min_tax_pct,
       MIN(rate_with_min_tax_2025_pct)            AS lowest_rate_with_min_tax_pct
FROM corporate_tax
WHERE sub_region = 'Gulf';

-- 4. World mean and the number of Middle East economies below it
SELECT ROUND((SELECT AVG(rate_2025_pct) FROM corporate_tax), 2) AS world_mean_pct,
       SUM(CASE WHEN rate_2025_pct < (SELECT AVG(rate_2025_pct) FROM corporate_tax) THEN 1 ELSE 0 END)
                                                                 AS middle_east_below_world,
       COUNT(*)                                                  AS middle_east_economies
FROM corporate_tax
WHERE region = 'Middle East';

-- 5. The lowest rates above zero in the world
SELECT country, region, rate_2025_pct, rate_with_min_tax_2025_pct
FROM corporate_tax
WHERE rate_2025_pct > 0
ORDER BY rate_2025_pct, country
LIMIT 12;

-- 6. Jurisdictions where the 15% minimum tax raises the rate for large multinational groups
SELECT country, region, rate_2025_pct, rate_with_min_tax_2025_pct, min_tax_uplift_pts
FROM corporate_tax
WHERE min_tax_uplift_pts > 0
ORDER BY min_tax_uplift_pts DESC, country;

-- 7. How many rates match a second listing, by region
SELECT region, check_status, COUNT(*) AS jurisdictions
FROM corporate_tax
GROUP BY region, check_status
ORDER BY region, check_status;

-- 8. Middle East rates that are not confirmed in a second listing
SELECT country, rate_2025_pct, pwc_rate_2026_pct, te_rate_2026_pct, check_status
FROM corporate_tax
WHERE region = 'Middle East' AND check_status <> 'confirmed';
