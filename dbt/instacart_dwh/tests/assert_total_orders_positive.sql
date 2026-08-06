SELECT department, total_orders
FROM {{ ref('mart_department_summary') }}
WHERE total_orders <= 0
