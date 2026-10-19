-- Middle East airport passengers, 2025
-- Runs on data/processed/passengers_tidy.csv loaded as table passengers_tidy
-- (columns: airport_code, airport, city, country, subregion, year, passengers, check, chosen_source)

-- 1. Airports ranked by passengers in 2025
SELECT airport_code, airport, country, passengers
FROM passengers_tidy
WHERE year = 2025
ORDER BY passengers DESC;

-- 2. Change on 2024, airports with both years, against the world figure of +3.6% (ACI World)
SELECT a.airport_code, a.airport,
       ROUND((a.passengers * 1.0 / b.passengers - 1) * 100, 1) AS change_vs_2024_pct,
       CASE WHEN (a.passengers * 1.0 / b.passengers - 1) * 100 > 3.6 THEN 'above world' ELSE 'at or below world' END AS against_world
FROM passengers_tidy a
JOIN passengers_tidy b ON a.airport_code = b.airport_code AND b.year = 2024
WHERE a.year = 2025
ORDER BY change_vs_2024_pct DESC;

-- 3. Change on 2019, airports with a published 2019 count
SELECT a.airport_code, a.airport,
       ROUND((a.passengers * 1.0 / b.passengers - 1) * 100, 1) AS change_vs_2019_pct
FROM passengers_tidy a
JOIN passengers_tidy b ON a.airport_code = b.airport_code AND b.year = 2019
WHERE a.year = 2025
ORDER BY change_vs_2019_pct DESC;

-- 4. Totals by subregion, airports with both 2024 and 2025
SELECT a.subregion, COUNT(*) AS airports,
       SUM(a.passengers) AS pax_2025, SUM(b.passengers) AS pax_2024,
       ROUND((SUM(a.passengers) * 1.0 / SUM(b.passengers) - 1) * 100, 1) AS change_vs_2024_pct
FROM passengers_tidy a
JOIN passengers_tidy b ON a.airport_code = b.airport_code AND b.year = 2024
WHERE a.year = 2025
GROUP BY a.subregion
ORDER BY pax_2025 DESC;

-- 5. How many 2025 figures rest on one document
SELECT "check", COUNT(*) AS figures
FROM passengers_tidy
WHERE year = 2025
GROUP BY "check";
