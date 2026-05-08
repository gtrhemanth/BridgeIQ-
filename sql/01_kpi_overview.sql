-- ============================================================
-- BridgeIQ | KPI Overview
-- Purpose: Top-level business health metrics for executive dashboard
-- ============================================================

-- Total Active Customers, MRR, ARR, Churn Rate
SELECT
    COUNT(CASE WHEN status = 'Active' THEN 1 END)                          AS active_customers,
    COUNT(CASE WHEN status = 'Churned' THEN 1 END)                         AS churned_customers,
    ROUND(COUNT(CASE WHEN status = 'Churned' THEN 1 END) * 100.0
          / COUNT(*), 2)                                                    AS churn_rate_pct,
    ROUND(SUM(CASE WHEN status = 'Active' THEN mrr ELSE 0 END), 2)         AS total_mrr,
    ROUND(SUM(CASE WHEN status = 'Active' THEN mrr * 12 ELSE 0 END), 2)   AS total_arr,
    ROUND(AVG(CASE WHEN status = 'Active' THEN mrr END), 2)               AS avg_mrr_per_customer,
    ROUND(AVG(CASE WHEN status = 'Active' THEN health_score END), 1)      AS avg_health_score,
    ROUND(AVG(CASE WHEN status = 'Active' THEN nps_score END), 1)         AS avg_nps
FROM customers;
