-- ============================================================
-- BridgeIQ | Revenue Trends
-- Purpose: Monthly revenue, growth rate, transaction analysis
-- ============================================================

-- Monthly revenue trend
SELECT
    strftime('%Y-%m', transaction_date)          AS month,
    COUNT(*)                                      AS transaction_count,
    ROUND(SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END), 2)  AS gross_revenue,
    ROUND(SUM(CASE WHEN amount < 0 THEN amount ELSE 0 END), 2)  AS refunds,
    ROUND(SUM(amount), 2)                         AS net_revenue,
    COUNT(DISTINCT customer_id)                   AS unique_paying_customers
FROM transactions
WHERE status = 'Completed'
GROUP BY month
ORDER BY month;

-- Revenue by transaction type
SELECT
    transaction_type,
    COUNT(*)                             AS count,
    ROUND(SUM(amount), 2)               AS total_amount,
    ROUND(AVG(amount), 2)               AS avg_amount
FROM transactions
WHERE status = 'Completed'
GROUP BY transaction_type
ORDER BY total_amount DESC;

-- Top 10 customers by revenue
SELECT
    c.customer_id,
    c.company_name,
    c.plan_type,
    c.industry,
    c.status,
    ROUND(SUM(t.amount), 2)            AS lifetime_value,
    COUNT(t.transaction_id)            AS transaction_count
FROM customers c
JOIN transactions t ON c.customer_id = t.customer_id
WHERE t.status = 'Completed'
GROUP BY c.customer_id
ORDER BY lifetime_value DESC
LIMIT 10;

-- Revenue by plan type with MoM growth (window function)
SELECT
    month,
    plan_type,
    net_revenue,
    LAG(net_revenue) OVER (PARTITION BY plan_type ORDER BY month) AS prev_month_revenue,
    ROUND((net_revenue - LAG(net_revenue) OVER (PARTITION BY plan_type ORDER BY month))
          * 100.0 / NULLIF(LAG(net_revenue) OVER (PARTITION BY plan_type ORDER BY month), 0), 2) AS mom_growth_pct
FROM (
    SELECT
        strftime('%Y-%m', t.transaction_date) AS month,
        c.plan_type,
        ROUND(SUM(t.amount), 2) AS net_revenue
    FROM transactions t
    JOIN customers c ON t.customer_id = c.customer_id
    WHERE t.status = 'Completed'
    GROUP BY month, c.plan_type
) monthly_plan
ORDER BY plan_type, month;
