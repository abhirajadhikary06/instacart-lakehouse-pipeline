{% macro is_peak_hour(orders_col) %}
    case
        when {{ orders_col }} >= (
            select percentile_cont(0.75) within group (order by total_orders)
            from {{ ref('stg_order_time_analysis') }}
        ) then 'Peak'
        when {{ orders_col }} >= (
            select percentile_cont(0.50) within group (order by total_orders)
            from {{ ref('stg_order_time_analysis') }}
        ) then 'High'
        when {{ orders_col }} >= (
            select percentile_cont(0.25) within group (order by total_orders)
            from {{ ref('stg_order_time_analysis') }}
        ) then 'Moderate'
        else 'Low'
    end
{% endmacro %}
