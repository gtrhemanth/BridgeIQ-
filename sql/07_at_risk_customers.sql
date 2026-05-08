-- ============================================================
-- BridgeIQ | At-Risk Customer Identification
-- Purpose: Multi-signal composite risk scoring for proactive CS intervention
-- Business Rule: Risk = low health + high tickets + low usage + incomplete onboarding
-- ============================================================

WITH customer_tickets AS (
    SELECT
        customer_id,
        COUNT(*)                                                AS ticket_count,
        COUNT(CASE WHEN priority IN ('High','Critical') THEN 1 END) AS high_priority_tickets,
        ROUND(AVG(satisfaction_score), 2)                      AS avg_csat
    FROM support_tickets
    GROUP BY customer_id
),
customer_usage AS (
    SELECT
        customer_id,
        COUNT(*)                                               AS total_sessions,
        COUNT(DISTINCT feature)                               AS features_used,
        MAX(usage_date)                                       AS last_active_date,
        ROUND(AVG(session_minutes), 1)                       AS avg_session_mins
    FROM product_usage
    GROUP BY customer_id
),
customer_onboarding AS (
    SELECT customer_id, completed, blocker
    FROM onboarding
)
SELECT
    c.customer_id,
    c.company_name,
    c.plan_type,
    c.mrr,
    c.industry,
    c.region,
    c.health_score,
    c.nps_score,
    COALESCE(t.ticket_count, 0)              AS ticket_count,
    COALESCE(t.high_priority_tickets, 0)     AS high_priority_tickets,
    COALESCE(t.avg_csat, 0)                  AS avg_csat,
    COALESCE(u.total_sessions, 0)            AS usage_sessions,
    COALESCE(u.features_used, 0)            AS features_used,
    u.last_active_date,
    COALESCE(o.completed, 0)                AS onboarding_complete,
    -- Composite risk score (0-100, higher = more at risk)
    ROUND(
        (CASE WHEN c.health_score < 60 THEN 30
              WHEN c.health_score < 75 THEN 15
              ELSE 0 END)
        + (CASE WHEN COALESCE(t.ticket_count, 0) > 15 THEN 20
                WHEN COALESCE(t.ticket_count, 0) > 8  THEN 10
                ELSE 0 END)
        + (CASE WHEN COALESCE(u.total_sessions, 0) < 3 THEN 25
                WHEN COALESCE(u.total_sessions, 0) < 8 THEN 12
                ELSE 0 END)
        + (CASE WHEN COALESCE(o.completed, 0) = 0 THEN 15 ELSE 0 END)
        + (CASE WHEN c.nps_score < 5 THEN 10 ELSE 0 END)
    , 0)                                    AS composite_risk_score
FROM customers c
LEFT JOIN customer_tickets   t ON c.customer_id = t.customer_id
LEFT JOIN customer_usage     u ON c.customer_id = u.customer_id
LEFT JOIN customer_onboarding o ON c.customer_id = o.customer_id
WHERE c.status = 'Active'
ORDER BY composite_risk_score DESC, mrr DESC
LIMIT 30;
