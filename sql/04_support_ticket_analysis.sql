-- ============================================================
-- BridgeIQ | Support Ticket Analysis
-- Purpose: Identify bottlenecks, SLA breaches, high-volume categories
-- ============================================================

-- Ticket volume and resolution time by category
SELECT
    category,
    COUNT(*)                                            AS total_tickets,
    COUNT(CASE WHEN status = 'Resolved' THEN 1 END)   AS resolved,
    COUNT(CASE WHEN status = 'Escalated' THEN 1 END)  AS escalated,
    ROUND(AVG(resolution_time_hours), 1)               AS avg_resolution_hrs,
    ROUND(MIN(resolution_time_hours), 1)               AS min_resolution_hrs,
    ROUND(MAX(resolution_time_hours), 1)               AS max_resolution_hrs,
    ROUND(AVG(satisfaction_score), 2)                  AS avg_satisfaction
FROM support_tickets
GROUP BY category
ORDER BY total_tickets DESC;

-- SLA breach analysis (Critical > 8hrs, High > 24hrs, Medium > 48hrs, Low > 96hrs)
SELECT
    priority,
    COUNT(*)                                            AS total_tickets,
    COUNT(CASE
        WHEN priority = 'Critical' AND resolution_time_hours > 8  THEN 1
        WHEN priority = 'High'     AND resolution_time_hours > 24 THEN 1
        WHEN priority = 'Medium'   AND resolution_time_hours > 48 THEN 1
        WHEN priority = 'Low'      AND resolution_time_hours > 96 THEN 1
    END)                                               AS sla_breaches,
    ROUND(COUNT(CASE
        WHEN priority = 'Critical' AND resolution_time_hours > 8  THEN 1
        WHEN priority = 'High'     AND resolution_time_hours > 24 THEN 1
        WHEN priority = 'Medium'   AND resolution_time_hours > 48 THEN 1
        WHEN priority = 'Low'      AND resolution_time_hours > 96 THEN 1
    END) * 100.0 / COUNT(*), 2)                        AS breach_rate_pct,
    ROUND(AVG(resolution_time_hours), 1)               AS avg_resolution_hrs
FROM support_tickets
GROUP BY priority
ORDER BY breach_rate_pct DESC;

-- Monthly ticket trend
SELECT
    strftime('%Y-%m', created_date)                    AS month,
    COUNT(*)                                           AS total_tickets,
    COUNT(CASE WHEN priority IN ('High','Critical') THEN 1 END) AS high_priority,
    ROUND(AVG(satisfaction_score), 2)                 AS avg_csat
FROM support_tickets
GROUP BY month
ORDER BY month;

-- Customers with most tickets (at-risk signal)
SELECT
    c.customer_id,
    c.company_name,
    c.plan_type,
    c.status,
    c.health_score,
    COUNT(t.ticket_id)                                 AS ticket_count,
    COUNT(CASE WHEN t.priority IN ('High','Critical') THEN 1 END) AS high_priority_tickets,
    ROUND(AVG(t.resolution_time_hours), 1)            AS avg_resolution_hrs,
    ROUND(AVG(t.satisfaction_score), 2)               AS avg_csat
FROM customers c
JOIN support_tickets t ON c.customer_id = t.customer_id
GROUP BY c.customer_id
HAVING ticket_count >= 10
ORDER BY ticket_count DESC
LIMIT 20;
