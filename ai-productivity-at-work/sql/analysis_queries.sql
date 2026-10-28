-- AI productivity at work: queries on the tidy tables.
-- Load data/processed/effects_tidy.csv as table effects_tidy and
-- data/processed/study_headlines.csv as table study_headlines (tested with SQLite).

-- 1. Headline effect per study, largest first, split by scope.
SELECT study_id, scope, ROUND(gain_pct, 2) AS gain_pct, effect_label, verification
FROM study_headlines
ORDER BY CASE WHEN scope = 'whole job' THEN 1 ELSE 0 END, gain_pct DESC;

-- 2. Range of headline effects: controlled studies of one kind of work vs whole-job surveys.
SELECT CASE WHEN scope = 'whole job' THEN 'whole job survey' ELSE 'controlled study' END AS kind,
       COUNT(*) AS studies, MIN(gain_pct) AS min_pct, MAX(gain_pct) AS max_pct
FROM study_headlines
GROUP BY kind;

-- 3. Gains for the least and most experienced staff, where printed.
SELECT study_id, version, "group", measure, value
FROM effects_tidy
WHERE "group" IN ('least_experienced', 'most_experienced')
ORDER BY study_id, "group", measure;

-- 4. Coding test: recompute the time cut from the two group means.
SELECT ROUND(100.0 * (w.value - a.value) / w.value, 2) AS time_cut_pct
FROM effects_tidy a JOIN effects_tidy w
  ON a.study_id = w.study_id AND a.measure = w.measure
WHERE a.study_id = 'coding_test' AND a.measure = 'minutes_to_complete'
  AND a."group" = 'with_ai' AND w."group" = 'without_ai';

-- 5. How many figures rest on one document.
SELECT verification, COUNT(*) AS figures
FROM effects_tidy
GROUP BY verification;

-- 6. Customer support: published version against the earlier working paper.
SELECT version, "group", value
FROM effects_tidy
WHERE study_id = 'support' AND measure = 'resolutions_per_hour_change_pct'
ORDER BY version, "group";
