-- ============================================================
-- BridgeIQ | Cohort Retention Analysis
-- Purpose: Track retention of customer cohorts over time (by signup quarter)
-- ============================================================

-- Customer cohorts by signup quarter
WITH cohorts AS (
    SELECT
        customer_id,
        mrr,
        status,
        strftime('%Y-Q', contract_start) ||
            CASE
                WHEN CAST(strftime('%m', contract_start) AS INTEGER) BETWEEN 1  AND 3  THEN '1'
                WHEN CAST(strftime('%m', contract_start) AS INTEGER) BETWEEN 4  AND 6  THEN '2'
                WHEN CAST(strftime('%m', contract_start) AS INTEGER) BETWEEN 7  AND 9  THEN '3'
                ELSE '4'
            END                          AS cohort_quarter,
        churn_date
    FROM customers
)
SELECT
    cohort_quarter,
    COUNT(*)                                                    AS cohort_size,
    COUNT(CASE WHEN status = 'Active' THEN 1 END)             AS still_active,
    COUNT(CASE WHEN status = 'Churned' THEN 1 END)            AS churned,
    ROUND(COUNT(CASE WHEN status = 'Active' THEN 1 END) * 100.0
          / COUNT(*), 2)                                        AS retention_rate_pct,
    ROUND(SUM(CASE WHEN status = 'Active' THEN mrr ELSE 0 END), 2) AS retained_mrr
FROM cohorts
GROUP BY cohort_quarter
ORDER BY cohort_quarter;

-- Average customer lifespan before churn
SELECT
    plan_type,
    ROUND(AVG(
        julianday(churn_date) - julianday(contract_start)
    ), 0)                                                       AS avg_days_before_churn,
    ROUND(AVG(
        julianday(churn_date) - julianday(contract_start)
    ) / 30.0, 1)                                               AS avg_months_before_churn
FROM customers
WHERE status = 'Churned'
GROUP BY plan_type
ORDER BY avg_days_before_churn DESC;
