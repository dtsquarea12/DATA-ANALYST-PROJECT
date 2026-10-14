-- Egypt remittances: queries on the tidy tables in data/processed.
-- Load remittances_tidy.csv as table remittances_tidy and fiscal_year_series.csv as fiscal_year_series.
-- Tested with SQLite.

-- 1. Fiscal-year totals with the change on the year before
SELECT period,
       value_usd_bn,
       ROUND(value_usd_bn - LAG(value_usd_bn) OVER (ORDER BY period_start), 1) AS change_usd_bn,
       ROUND(100.0 * (value_usd_bn / LAG(value_usd_bn) OVER (ORDER BY period_start) - 1), 1) AS change_pct
FROM remittances_tidy
WHERE measure = 'fiscal_year'
ORDER BY period_start;

-- 2. Latest fiscal year against the low point and the peak before the FY2022/23 fall
SELECT
  (SELECT value_usd_bn FROM fiscal_year_series ORDER BY period_start DESC LIMIT 1) AS latest_usd_bn,
  (SELECT MIN(value_usd_bn) FROM fiscal_year_series) AS low_usd_bn,
  ROUND((SELECT value_usd_bn FROM fiscal_year_series ORDER BY period_start DESC LIMIT 1)
        / (SELECT MIN(value_usd_bn) FROM fiscal_year_series), 2) AS multiple_of_low,
  (SELECT MAX(value_usd_bn) FROM fiscal_year_series WHERE period_start < '2022-07-01') AS peak_before_fall_usd_bn;

-- 3. How many figures rest on one document
SELECT source_check, COUNT(*) AS figures
FROM remittances_tidy
GROUP BY source_check
ORDER BY figures DESC;

-- 4. Published April to June quarters
SELECT period, value_usd_bn, source_check
FROM remittances_tidy
WHERE measure = 'quarter'
ORDER BY period_start;

-- 5. Same month a year apart, where both months are in the table
SELECT a.period AS month, a.value_usd_bn, b.period AS year_before, b.value_usd_bn AS year_before_usd_bn,
       ROUND(100.0 * (a.value_usd_bn / b.value_usd_bn - 1), 1) AS change_pct
FROM remittances_tidy a
JOIN remittances_tidy b
  ON b.measure = 'month' AND a.measure = 'month'
 AND CAST(SUBSTR(b.period, 1, 4) AS INTEGER) = CAST(SUBSTR(a.period, 1, 4) AS INTEGER) - 1
 AND SUBSTR(b.period, 6, 2) = SUBSTR(a.period, 6, 2)
ORDER BY a.period;
