-- ============================================================
-- BridgeIQ | Churn Analysis
-- Purpose: Identify churn patterns by plan, industry, region, health score
-- ============================================================

-- Churn rate by plan type
SELECT
    plan_type,
    COUNT(*)                                                        AS total_customers,
    COUNT(CASE WHEN status = 'Churned' THEN 1 END)                AS churned,
    ROUND(COUNT(CASE WHEN status = 'Churned' THEN 1 END) * 100.0
          / COUNT(*), 2)                                           AS churn_rate_pct,
    ROUND(AVG(mrr), 2)                                            AS avg_mrr,
    ROUND(AVG(health_score), 1)                                   AS avg_health_score
FROM customers
GROUP BY plan_type
ORDER BY churn_rate_pct DESC;

-- Churn rate by industry
SELECT
    industry,
    COUNT(*)                                                        AS total,
    COUNT(CASE WHEN status = 'Churned' THEN 1 END)                AS churned,
    ROUND(COUNT(CASE WHEN status = 'Churned' THEN 1 END) * 100.0
          / COUNT(*), 2)                                           AS churn_rate_pct,
    ROUND(SUM(CASE WHEN status = 'Churned' THEN mrr ELSE 0 END), 2) AS mrr_lost
FROM customers
GROUP BY industry
ORDER BY churn_rate_pct DESC;

-- Churn rate by region
SELECT
    region,
    COUNT(*)                                                        AS total,
    COUNT(CASE WHEN status = 'Churned' THEN 1 END)                AS churned,
    ROUND(COUNT(CASE WHEN status = 'Churned' THEN 1 END) * 100.0
          / COUNT(*), 2)                                           AS churn_rate_pct
FROM customers
GROUP BY region
ORDER BY churn_rate_pct DESC;

-- Health score distribution for churned vs active
SELECT
    status,
    ROUND(AVG(health_score), 1)      AS avg_health_score,
    MIN(health_score)                 AS min_health_score,
    MAX(health_score)                 AS max_health_score,
    COUNT(CASE WHEN health_score < 60 THEN 1 END) AS at_risk_count
FROM customers
GROUP BY status;
