-- Renewable power capacity by country: queries on the processed table.
-- Load data/processed/renewable_capacity_tidy.csv as table renewable_capacity (SQLite, Power BI or any SQL engine).
-- capacity_mw is installed renewable power capacity at the end of the year, in megawatts.

-- 1. Gulf states: capacity at the end of 2024 and 2025, capacity added and growth
SELECT entity AS country,
       MAX(CASE WHEN year = 2024 THEN capacity_mw END) AS capacity_2024_mw,
       MAX(CASE WHEN year = 2025 THEN capacity_mw END) AS capacity_2025_mw,
       MAX(CASE WHEN year = 2025 THEN change_mw END)   AS added_2025_mw,
       MAX(CASE WHEN year = 2025 THEN change_pct END)  AS growth_2025_pct
FROM renewable_capacity
WHERE entity_type = 'country' AND sub_region = 'Gulf'
GROUP BY entity
ORDER BY capacity_2025_mw DESC;

-- 2. Gulf total by year
SELECT year, SUM(capacity_mw) AS gulf_capacity_mw
FROM renewable_capacity
WHERE entity_type = 'country' AND sub_region = 'Gulf'
GROUP BY year
ORDER BY year;

-- 3. Share of the capacity the Gulf added in 2025 that each state added
SELECT entity AS country,
       change_mw AS added_2025_mw,
       ROUND(100.0 * change_mw / (SELECT SUM(change_mw) FROM renewable_capacity
                                  WHERE entity_type = 'country' AND sub_region = 'Gulf' AND year = 2025), 1)
           AS share_of_gulf_additions_pct
FROM renewable_capacity
WHERE entity_type = 'country' AND sub_region = 'Gulf' AND year = 2025
ORDER BY change_mw DESC;

-- 4. The 20 Middle East and North Africa economies ranked by capacity added in 2025
SELECT RANK() OVER (ORDER BY change_mw DESC) AS rank_added,
       entity AS country, sub_region, change_mw AS added_2025_mw, capacity_mw AS capacity_2025_mw, change_pct
FROM renewable_capacity
WHERE entity_type = 'country' AND year = 2025
ORDER BY change_mw DESC, capacity_mw DESC;

-- 5. Sub-region totals, 2016, 2024 and 2025
SELECT sub_region,
       COUNT(DISTINCT entity)                                AS economies,
       SUM(CASE WHEN year = 2016 THEN capacity_mw END)       AS capacity_2016_mw,
       SUM(CASE WHEN year = 2024 THEN capacity_mw END)       AS capacity_2024_mw,
       SUM(CASE WHEN year = 2025 THEN capacity_mw END)       AS capacity_2025_mw
FROM renewable_capacity
WHERE entity_type = 'country'
GROUP BY sub_region
ORDER BY CASE sub_region WHEN 'Gulf' THEN 1 WHEN 'Levant and Iraq' THEN 2
                         WHEN 'Iran, Turkey and Yemen' THEN 3 ELSE 4 END;

-- 6. IRENA regions and the world in 2025, Middle East first, then by growth
SELECT entity AS region, capacity_mw AS capacity_2025_mw, change_mw AS added_2025_mw, change_pct AS growth_2025_pct,
       ROUND(100.0 * capacity_mw / (SELECT capacity_mw FROM renewable_capacity
                                    WHERE entity_type = 'world' AND year = 2025), 2) AS share_of_world_pct
FROM renewable_capacity
WHERE entity_type IN ('irena_region', 'world') AND year = 2025
ORDER BY CASE WHEN entity = 'Middle East' THEN 0 WHEN entity = 'World' THEN 2 ELSE 1 END, change_pct DESC;

-- 7. Check: the IRENA Middle East total against the sum of its 14 countries, by year
SELECT r.year, r.capacity_mw AS printed_total_mw, c.sum_mw AS sum_of_countries_mw, r.capacity_mw - c.sum_mw AS gap_mw
FROM renewable_capacity r
JOIN (SELECT year, SUM(capacity_mw) AS sum_mw FROM renewable_capacity
      WHERE entity_type = 'country' AND in_irena_middle_east = 'True' GROUP BY year) c ON c.year = r.year
WHERE r.entity = 'Middle East' AND r.entity_type = 'irena_region'
ORDER BY r.year;

-- 8. Economies with no change recorded in 2025
SELECT entity AS country, capacity_mw AS capacity_2025_mw
FROM renewable_capacity
WHERE entity_type = 'country' AND year = 2025 AND change_mw = 0
ORDER BY capacity_mw DESC;
