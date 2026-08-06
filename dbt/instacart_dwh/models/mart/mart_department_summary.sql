{{ config(materialized='view', schema='marts') }}

select *,
    case
        when reorder_rate >= 0.6 then 'High'
        when reorder_rate >= 0.4 then 'Medium'
        else 'Low'
    end as reorder_performance,
    RANK() OVER(PARTITION BY department ORDER BY reorder_rate DESC) as rank_in_department
from {{ ref('stg_department_summary') }}
