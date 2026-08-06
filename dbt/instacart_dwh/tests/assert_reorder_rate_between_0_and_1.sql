SELECT product_id, reorder_rate
FROM {{ ref('mart_product_popularity') }}
WHERE reorder_rate < 0 OR reorder_rate > 1
