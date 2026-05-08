-- ============================================================
-- BridgeIQ | Onboarding Analysis
-- Purpose: Identify onboarding bottlenecks, completion rates, impact on churn
-- ============================================================

-- Onboarding completion rate overall
SELECT
    COUNT(*)                                                    AS total_customers,
    COUNT(CASE WHEN completed = 1 THEN 1 END)                  AS completed_onboarding,
    COUNT(CASE WHEN completed = 0 THEN 1 END)                  AS incomplete_onboarding,
    ROUND(COUNT(CASE WHEN completed = 1 THEN 1 END) * 100.0
          / COUNT(*), 2)                                        AS completion_rate_pct,
    ROUND(AVG(CASE WHEN completed = 1 THEN days_to_complete END), 1) AS avg_days_to_complete
FROM onboarding;

-- Blockers causing incomplete onboarding
SELECT
    blocker,
    COUNT(*)                             AS occurrences,
    ROUND(COUNT(*) * 100.0 / (
        SELECT COUNT(*) FROM onboarding WHERE completed = 0
    ), 2)                               AS pct_of_incomplete
FROM onboarding
WHERE completed = 0
GROUP BY blocker
ORDER BY occurrences DESC;

-- Impact of incomplete onboarding on churn
SELECT
    o.completed,
    COUNT(c.customer_id)                 AS customer_count,
    COUNT(CASE WHEN c.status = 'Churned' THEN 1 END) AS churned,
    ROUND(COUNT(CASE WHEN c.status = 'Churned' THEN 1 END) * 100.0
          / COUNT(*), 2)                AS churn_rate_pct,
    ROUND(AVG(c.health_score), 1)       AS avg_health_score
FROM onboarding o
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY o.completed;

-- Onboarding completion rate by plan
SELECT
    c.plan_type,
    COUNT(o.onboarding_id)              AS total,
    COUNT(CASE WHEN o.completed = 1 THEN 1 END) AS completed,
    ROUND(COUNT(CASE WHEN o.completed = 1 THEN 1 END) * 100.0
          / COUNT(*), 2)               AS completion_rate_pct,
    ROUND(AVG(CASE WHEN o.completed = 1 THEN o.days_to_complete END), 1) AS avg_days
FROM onboarding o
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.plan_type
ORDER BY completion_rate_pct DESC;

-- Current stage distribution (where are incomplete customers stuck?)
SELECT
    stage,
    COUNT(*)                            AS customers_stuck,
    ROUND(COUNT(*) * 100.0 / (
        SELECT COUNT(*) FROM onboarding WHERE completed = 0
    ), 2)                              AS pct_of_incomplete
FROM onboarding
WHERE completed = 0
GROUP BY stage
ORDER BY customers_stuck DESC;
