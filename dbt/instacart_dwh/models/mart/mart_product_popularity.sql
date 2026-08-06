{{ config(materialized='view', schema='marts') }}

select *,
    RANK() OVER(PARTITION BY department ORDER BY reorder_rate DESC) as rank_in_department,
    RANK() OVER(ORDER BY reorder_rate DESC) as overall_rank
from {{ ref('stg_product_popularity') }}