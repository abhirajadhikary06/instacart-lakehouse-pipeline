{{ config(materialized='view', schema='marts') }}

select
    order_dow,
    case order_dow
        when 0 then 'Saturday'
        when 1 then 'Sunday'
        when 2 then 'Monday'
        when 3 then 'Tuesday'
        when 4 then 'Wednesday'
        when 5 then 'Thursday'
        when 6 then 'Friday'
    end as day_of_week,
    order_hour_of_day as hour_of_day,
    total_orders,
    avg_basket_size,
    {{ is_peak_hour('total_orders') }} as traffic_category,
    RANK() OVER(ORDER BY total_orders DESC) as order_vol_rank
from {{ ref('stg_order_time_analysis') }}
