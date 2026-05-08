-- ============================================================
-- BridgeIQ | Workforce Analysis
-- Purpose: Headcount by department, salary benchmarks, tenure
-- ============================================================

-- Headcount and salary by department
SELECT
    department,
    COUNT(*)                              AS headcount,
    ROUND(AVG(salary), 2)               AS avg_salary,
    ROUND(MIN(salary), 2)               AS min_salary,
    ROUND(MAX(salary), 2)               AS max_salary,
    ROUND(SUM(salary), 2)               AS total_salary_spend
FROM employees
GROUP BY department
ORDER BY headcount DESC;

-- Average tenure by department (years)
SELECT
    department,
    ROUND(AVG(
        (julianday('now') - julianday(hire_date)) / 365.25
    ), 1)                               AS avg_tenure_years,
    COUNT(CASE WHEN
        julianday('now') - julianday(hire_date) < 365 THEN 1 END) AS new_hires_lt_1yr
FROM employees
GROUP BY department
ORDER BY avg_tenure_years DESC;

-- Location distribution
SELECT
    location,
    COUNT(*)                            AS headcount,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM employees), 1) AS pct_of_workforce,
    ROUND(AVG(salary), 2)             AS avg_salary
FROM employees
GROUP BY location
ORDER BY headcount DESC;
