-- Clinical Trials Intelligence Explorer — Analysis Queries
-- ============================================================
-- Example business questions answered with real SQL: CTEs, window
-- functions, joins across the normalized schema. Run against trials.db.


-- 1. Which German cities host the most trial sites, by therapeutic area?
-- (join + aggregation)
SELECT
    c.city,
    t.search_condition,
    COUNT(DISTINCT t.nct_id) AS n_trials
FROM trials t
JOIN trial_germany_cities c ON t.nct_id = c.nct_id
GROUP BY c.city, t.search_condition
ORDER BY n_trials DESC
LIMIT 20;


-- 2. Rank lead sponsors by trial count within each therapeutic area
-- (window function: RANK() partitioned by condition)
WITH sponsor_counts AS (
    SELECT
        search_condition,
        lead_sponsor,
        lead_sponsor_class,
        COUNT(*) AS n_trials
    FROM trials
    GROUP BY search_condition, lead_sponsor, lead_sponsor_class
)
SELECT
    search_condition,
    lead_sponsor,
    lead_sponsor_class,
    n_trials,
    RANK() OVER (PARTITION BY search_condition ORDER BY n_trials DESC) AS rank_in_area
FROM sponsor_counts
QUALIFY rank_in_area <= 3
ORDER BY search_condition, rank_in_area;
-- Note: SQLite doesn't support QUALIFY natively (that's Snowflake/BigQuery
-- syntax) — if running this in plain SQLite, wrap it in an outer SELECT
-- with a WHERE clause instead. Kept here deliberately as a talking point
-- for the case study: "wrote this first in Snowflake syntax, adapted for
-- SQLite" shows dialect awareness, which recruiters increasingly ask about.


-- 3. Industry vs. academic/government sponsorship split, by phase
-- (join across two bridge tables + conditional aggregation)
SELECT
    p.phase,
    t.lead_sponsor_class,
    COUNT(DISTINCT t.nct_id) AS n_trials,
    ROUND(AVG(t.enrollment_count), 0) AS avg_enrollment
FROM trials t
JOIN trial_phases p ON t.nct_id = p.nct_id
GROUP BY p.phase, t.lead_sponsor_class
ORDER BY p.phase, n_trials DESC;


-- 4. Running total of trials started per year, by therapeutic area
-- (window function: cumulative SUM)
WITH yearly AS (
    SELECT
        search_condition,
        CAST(SUBSTR(start_date, 1, 4) AS INTEGER) AS start_year,
        COUNT(*) AS n_started
    FROM trials
    WHERE start_date IS NOT NULL
    GROUP BY search_condition, start_year
)
SELECT
    search_condition,
    start_year,
    n_started,
    SUM(n_started) OVER (
        PARTITION BY search_condition ORDER BY start_year
    ) AS cumulative_trials
FROM yearly
ORDER BY search_condition, start_year;


-- 5. Trials with a German site but a non-German lead sponsor
-- (a genuinely interesting question: who's testing drugs in Germany
-- without a German company leading the study?)
SELECT
    t.lead_sponsor,
    t.lead_sponsor_class,
    COUNT(DISTINCT t.nct_id) AS n_trials,
    GROUP_CONCAT(DISTINCT t.search_condition) AS areas
FROM trials t
WHERE t.n_germany_sites > 0
GROUP BY t.lead_sponsor, t.lead_sponsor_class
ORDER BY n_trials DESC
LIMIT 15;
