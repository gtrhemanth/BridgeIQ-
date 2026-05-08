-- ============================================================
-- BridgeIQ | Product Usage Analysis
-- Purpose: Feature adoption, engagement, usage vs churn correlation
-- ============================================================

-- Feature adoption rates
SELECT
    feature,
    COUNT(DISTINCT customer_id)                          AS unique_users,
    COUNT(*)                                             AS total_sessions,
    ROUND(AVG(session_minutes), 1)                      AS avg_session_mins,
    ROUND(SUM(session_minutes), 0)                      AS total_time_spent_mins,
    ROUND(AVG(actions_count), 1)                        AS avg_actions_per_session
FROM product_usage
GROUP BY feature
ORDER BY unique_users DESC;

-- Usage engagement by customer status (Active vs Churned)
SELECT
    c.status,
    COUNT(DISTINCT u.customer_id)                        AS customers,
    ROUND(AVG(sessions_per_customer), 1)                AS avg_sessions,
    ROUND(AVG(total_mins), 1)                           AS avg_total_mins,
    ROUND(AVG(features_used), 1)                        AS avg_features_used
FROM customers c
JOIN (
    SELECT
        customer_id,
        COUNT(*)                   AS sessions_per_customer,
        SUM(session_minutes)       AS total_mins,
        COUNT(DISTINCT feature)    AS features_used
    FROM product_usage
    GROUP BY customer_id
) u ON c.customer_id = u.customer_id
GROUP BY c.status;

-- Low engagement customers (at-risk signal)
SELECT
    c.customer_id,
    c.company_name,
    c.plan_type,
    c.health_score,
    c.status,
    COUNT(u.usage_id)              AS total_sessions,
    ROUND(AVG(u.session_minutes), 1) AS avg_session_mins,
    COUNT(DISTINCT u.feature)     AS unique_features_used,
    MAX(u.usage_date)             AS last_active_date
FROM customers c
LEFT JOIN product_usage u ON c.customer_id = u.customer_id
WHERE c.status = 'Active'
GROUP BY c.customer_id
HAVING total_sessions < 5 OR unique_features_used < 2
ORDER BY total_sessions ASC
LIMIT 20;

-- Usage trend by month
SELECT
    strftime('%Y-%m', usage_date)       AS month,
    COUNT(*)                             AS total_sessions,
    COUNT(DISTINCT customer_id)         AS active_users,
    ROUND(AVG(session_minutes), 1)     AS avg_session_mins,
    ROUND(SUM(session_minutes) / 60, 1) AS total_hours_used
FROM product_usage
GROUP BY month
ORDER BY month;
