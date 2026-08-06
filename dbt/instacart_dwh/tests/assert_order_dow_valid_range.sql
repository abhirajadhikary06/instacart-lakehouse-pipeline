SELECT order_dow, hour_of_day, total_orders
FROM {{ ref('mart_order_time_analysis') }}
WHERE order_dow < 0 OR order_dow > 6
