-- Gulf Fuel Subsidy Tracker: analysis queries
-- Table: fuel_prices (loaded from data/processed/fuel_prices_tidy.csv)
-- Columns: country, "group", continent, month, period, fuel, price_usd_per_litre, basis
-- Written for SQLite

-- 1. Pre-war and since-war average pump price by country, with percentage change
WITH avg_price AS (
    SELECT country, "group", fuel, period, AVG(price_usd_per_litre) AS avg_usd
    FROM fuel_prices
    GROUP BY country, "group", fuel, period
)
SELECT b.country, b."group", b.fuel,
       ROUND(b.avg_usd, 3)                           AS prewar_usd_l,
       ROUND(a.avg_usd, 3)                           AS sincewar_usd_l,
       ROUND(100.0 * (a.avg_usd / b.avg_usd - 1), 1) AS pct_change
FROM avg_price b
JOIN avg_price a
  ON a.country = b.country AND a.fuel = b.fuel
WHERE b.period = 'pre-war' AND a.period = 'since war' AND b.fuel = 'gasoline'
ORDER BY sincewar_usd_l DESC;

-- 2. Latest reading per country and its rank, cheapest first
WITH latest AS (
    SELECT country, "group", fuel, month, price_usd_per_litre,
           ROW_NUMBER() OVER (PARTITION BY country, fuel ORDER BY month DESC) AS rn
    FROM fuel_prices
)
SELECT RANK() OVER (ORDER BY price_usd_per_litre) AS cheapest_rank,
       country, "group", month, ROUND(price_usd_per_litre, 3) AS usd_per_litre
FROM latest
WHERE rn = 1 AND fuel = 'gasoline'
ORDER BY cheapest_rank;

-- 3. Monthly subsidy gap per litre against the regional reference price
--    Reference = UAE pump price before 5% VAT, plus the local VAT rate
WITH ref AS (
    SELECT month, fuel, price_usd_per_litre / 1.05 AS ref_ex_vat
    FROM fuel_prices
    WHERE country = 'UAE'
),
vat AS (
    SELECT 'Saudi Arabia' AS country, 0.15 AS rate UNION ALL
    SELECT 'UAE', 0.05 UNION ALL SELECT 'Qatar', 0.0 UNION ALL
    SELECT 'Kuwait', 0.0 UNION ALL SELECT 'Bahrain', 0.0 UNION ALL SELECT 'Iran', 0.0
)
SELECT p.country, p.fuel, p.month,
       ROUND(r.ref_ex_vat * (1 + v.rate) - p.price_usd_per_litre, 3) AS gap_usd_per_litre
FROM fuel_prices p
JOIN ref r ON r.month = p.month AND r.fuel = p.fuel
JOIN vat v ON v.country = p.country
WHERE p."group" = 'Gulf'
ORDER BY p.country, p.fuel, p.month;

-- 4. Gulf average against comparison-country average, by month
SELECT month, fuel,
       ROUND(AVG(CASE WHEN "group" = 'Gulf' THEN price_usd_per_litre END), 3)       AS gulf_avg,
       ROUND(AVG(CASE WHEN "group" = 'Comparison' THEN price_usd_per_litre END), 3) AS comparison_avg
FROM fuel_prices
WHERE fuel = 'gasoline'
GROUP BY month, fuel
ORDER BY month;
