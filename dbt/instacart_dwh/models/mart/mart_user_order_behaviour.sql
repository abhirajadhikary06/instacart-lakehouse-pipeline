{{ config(materialized='view', schema='marts') }}
select
    user_id,
    total_orders,
    total_products_ordered,
    avg_add_to_cart_position,
    max_days_since_prior_order,
    unique_products_count,
    avg_basket_size,
    avg_days_between_orders,
    case
        when total_orders >= 10 then 'High Value'
        when total_orders >= 5 then 'Regular'
        else 'Occasional'
    end as user_segment,
    RANK() OVER(ORDER BY total_orders DESC) as order_freq_rank, 
    RANK() OVER(ORDER BY unique_products_count DESC) as product_diversity_rank
from {{ ref('stg_user_order_behaviour') }}