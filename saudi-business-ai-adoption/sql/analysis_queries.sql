-- Queries on data/processed/ai_use_tidy.csv, loaded as table ai_use
-- Columns: year, isic_section, sector, pct_using_ai, n_documents, n_publishers, verification, sources

-- 1. National share of establishments using AI, by year
SELECT year, pct_using_ai
FROM ai_use
WHERE isic_section = 'ALL'
ORDER BY year;

-- 2. Sectors ranked by share using AI in 2025
SELECT sector, pct_using_ai,
       RANK() OVER (ORDER BY pct_using_ai DESC) AS rank_2025
FROM ai_use
WHERE year = 2025 AND isic_section <> 'ALL'
ORDER BY pct_using_ai DESC;

-- 3. Change by sector, 2024 to 2025, in percentage points
SELECT a.sector,
       a.pct_using_ai AS pct_2024,
       b.pct_using_ai AS pct_2025,
       ROUND(b.pct_using_ai - a.pct_using_ai, 1) AS change_pts
FROM ai_use a
JOIN ai_use b ON a.isic_section = b.isic_section AND b.year = 2025
WHERE a.year = 2024 AND a.isic_section <> 'ALL'
ORDER BY change_pts DESC;

-- 4. Sectors below the national rate in 2025
SELECT s.sector, s.pct_using_ai, ROUND(s.pct_using_ai - n.pct_using_ai, 1) AS gap_pts
FROM ai_use s
JOIN ai_use n ON n.year = s.year AND n.isic_section = 'ALL'
WHERE s.year = 2025 AND s.isic_section <> 'ALL' AND s.pct_using_ai < n.pct_using_ai
ORDER BY s.pct_using_ai;

-- 5. How many figures rest on one document
SELECT year, verification, COUNT(*) AS figures
FROM ai_use
GROUP BY year, verification
ORDER BY year, verification;
