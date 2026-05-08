-- ============================================================
-- BridgeIQ | Executive Summary View
-- Purpose: Single query for C-suite dashboard — all critical KPIs in one result
-- ============================================================

SELECT
    -- Customer Metrics
    (SELECT COUNT(*) FROM customers WHERE status = 'Active')                AS active_customers,
    (SELECT ROUND(SUM(mrr), 2) FROM customers WHERE status = 'Active')     AS total_mrr,
    (SELECT ROUND(SUM(mrr * 12), 2) FROM customers WHERE status = 'Active') AS total_arr,
    (SELECT ROUND(COUNT(CASE WHEN status='Churned' THEN 1 END) * 100.0
                  / COUNT(*), 2) FROM customers)                            AS overall_churn_rate,

    -- Support Health
    (SELECT COUNT(*) FROM support_tickets WHERE status IN ('Open','In Progress')) AS open_tickets,
    (SELECT ROUND(AVG(resolution_time_hours), 1) FROM support_tickets)     AS avg_resolution_hrs,
    (SELECT ROUND(AVG(satisfaction_score), 2) FROM support_tickets
     WHERE satisfaction_score IS NOT NULL)                                  AS avg_csat,

    -- Onboarding
    (SELECT ROUND(COUNT(CASE WHEN completed=1 THEN 1 END) * 100.0
                  / COUNT(*), 2) FROM onboarding)                          AS onboarding_completion_pct,

    -- Product Engagement
    (SELECT COUNT(DISTINCT customer_id) FROM product_usage
     WHERE usage_date >= date('now', '-30 days'))                          AS mau_last_30d,

    -- Revenue
    (SELECT ROUND(SUM(amount), 2) FROM transactions
     WHERE status = 'Completed'
     AND strftime('%Y-%m', transaction_date) = strftime('%Y-%m', 'now'))   AS revenue_this_month,

    -- At-Risk
    (SELECT COUNT(*) FROM customers
     WHERE status = 'Active' AND health_score < 60)                        AS at_risk_customers;
