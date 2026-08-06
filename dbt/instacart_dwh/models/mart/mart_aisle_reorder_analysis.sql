{{ config(materialized='view', schema='marts') }}

select *,
    RANK() OVER(ORDER BY reorder_rate DESC) as reorder_rank
from {{ ref('stg_aisle_reorder_analysis') }}