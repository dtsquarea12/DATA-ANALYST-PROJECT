-- Saudi women in work: analysis queries
-- Table: labour (loaded from data/processed/saudi_labour_tidy.csv)
-- Columns: quarter, quarter_start, year, quarter_number, nationality, sex, indicator,
--          value_pct, n_documents, n_publishers, verification, survey_design
-- Written for SQLite

-- 1. The three rates side by side for Saudi women, with the share of all women who are unemployed
SELECT quarter,
       MAX(CASE WHEN indicator = 'participation_rate' THEN value_pct END)       AS participation,
       MAX(CASE WHEN indicator = 'employment_to_population' THEN value_pct END) AS in_work,
       MAX(CASE WHEN indicator = 'unemployment_rate' THEN value_pct END)        AS unemployment_rate,
       ROUND(MAX(CASE WHEN indicator = 'participation_rate' THEN value_pct END)
           - MAX(CASE WHEN indicator = 'employment_to_population' THEN value_pct END), 1) AS unemployed_share
FROM labour
WHERE nationality = 'Saudi' AND sex = 'Female' AND quarter >= '2023-Q4'
GROUP BY quarter
ORDER BY quarter;

-- 2. Change over two years (Q2 2024 to Q2 2026) for women and men, every indicator
SELECT e.sex, e.indicator,
       s.value_pct                          AS q2_2024,
       e.value_pct                          AS q2_2026,
       ROUND(e.value_pct - s.value_pct, 1)  AS change_pts
FROM labour e
JOIN labour s
  ON s.nationality = e.nationality AND s.sex = e.sex AND s.indicator = e.indicator
WHERE e.nationality = 'Saudi' AND e.sex IN ('Female', 'Male')
  AND s.quarter = '2024-Q2' AND e.quarter = '2026-Q2'
ORDER BY e.indicator, e.sex;

-- 3. Year-on-year change in women's participation, same quarter a year earlier
WITH f AS (
    SELECT quarter, year, quarter_number, value_pct
    FROM labour
    WHERE nationality = 'Saudi' AND sex = 'Female' AND indicator = 'participation_rate'
)
SELECT quarter, value_pct AS participation,
       ROUND(value_pct - LAG(value_pct, 4) OVER (ORDER BY quarter), 1) AS change_on_year_pts
FROM f
ORDER BY quarter;

-- 4. Highest and lowest quarters for women's participation since 2021
SELECT quarter, value_pct, verification,
       RANK() OVER (ORDER BY value_pct DESC) AS rank_high
FROM labour
WHERE nationality = 'Saudi' AND sex = 'Female' AND indicator = 'participation_rate'
ORDER BY value_pct DESC, quarter
LIMIT 5;

-- 5. Gap between men's and women's participation, and distance from the 40% ambition
SELECT m.quarter,
       m.value_pct                       AS men,
       w.value_pct                       AS women,
       ROUND(m.value_pct - w.value_pct, 1) AS gap_pts,
       ROUND(40 - w.value_pct, 1)        AS women_short_of_40_pts
FROM labour m
JOIN labour w ON w.quarter = m.quarter AND w.nationality = m.nationality AND w.indicator = m.indicator
WHERE m.nationality = 'Saudi' AND m.indicator = 'participation_rate'
  AND m.sex = 'Male' AND w.sex = 'Female' AND m.quarter_number = 2
ORDER BY m.quarter;

-- 6. How well each figure is verified, by indicator
SELECT indicator, verification, COUNT(*) AS figures
FROM labour
WHERE nationality = 'Saudi'
GROUP BY indicator, verification
ORDER BY indicator, figures DESC;

-- 7. The redesign check: participation of non-Saudi women either side of Q1 2025
SELECT survey_design, COUNT(*) AS quarters,
       ROUND(AVG(value_pct), 1) AS avg_participation,
       MIN(value_pct) AS lowest, MAX(value_pct) AS highest
FROM labour
WHERE nationality = 'Non-Saudi' AND sex = 'Female' AND quarter >= '2024-Q1'
GROUP BY survey_design
ORDER BY survey_design DESC;
