-- Mobile internet speed by country: queries on the processed tables.
-- Table speed   = data/processed/speed_by_country.csv (one row per country)
-- Table tidy    = data/processed/speed_tidy.csv       (one row per country and network)
-- Written for SQLite. Tested with Python's sqlite3 module.

-- 1. World top 20 for median mobile download speed, with Gulf Cooperation Council members flagged.
SELECT mobile_rank_published AS world_rank, country, gcc_member, mobile_mbps
FROM speed
WHERE mobile_rank_published <= 20
ORDER BY mobile_rank_published;

-- 2. How many of the top 20 does each region hold?
SELECT region,
       COUNT(*) AS countries_in_top_20,
       SUM(CASE WHEN gcc_member = 'yes' THEN 1 ELSE 0 END) AS of_which_gcc
FROM speed
WHERE mobile_rank_published <= 20
GROUP BY region
ORDER BY countries_in_top_20 DESC;

-- 3. Gulf states: mobile against fixed broadband.
SELECT country, mobile_rank_published AS world_rank, mobile_mbps, fixed_mbps, mobile_to_fixed_ratio
FROM speed
WHERE gcc_member = 'yes'
ORDER BY mobile_mbps DESC;

-- 4. Middle East and North Africa first, then the other regions: every country collected, fastest mobile first.
SELECT region, country, mobile_mbps, fixed_mbps, faster_network
FROM speed
ORDER BY CASE region WHEN 'Middle East and North Africa' THEN 0 ELSE 1 END, region, mobile_mbps DESC;

-- 5. Where is fixed broadband more than twice as fast as mobile? Ranked with a window function.
SELECT RANK() OVER (ORDER BY mobile_to_fixed_ratio) AS rank_most_fixed_led,
       country, mobile_mbps, fixed_mbps, mobile_to_fixed_ratio
FROM speed
WHERE mobile_to_fixed_ratio < 0.5
ORDER BY mobile_to_fixed_ratio;

-- 6. How many times faster is the UAE's median mobile speed than selected markets?
SELECT country, mobile_mbps, uae_mobile_multiple
FROM speed
WHERE country IN ('United States', 'India', 'United Kingdom', 'Germany', 'Japan', 'Nigeria', 'Egypt', 'South Africa')
ORDER BY uae_mobile_multiple;

-- 7. Which network is faster, counted by region.
SELECT region,
       SUM(CASE WHEN faster_network = 'mobile' THEN 1 ELSE 0 END) AS mobile_faster,
       SUM(CASE WHEN faster_network = 'fixed' THEN 1 ELSE 0 END) AS fixed_faster
FROM speed
GROUP BY region
ORDER BY region;

-- 8. Figures confirmed in a second source.
SELECT country, network, median_download_mbps, n_sources
FROM tidy
WHERE verification = 'two-sources'
ORDER BY network, median_download_mbps DESC;
