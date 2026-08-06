SELECT user_id, user_segment
FROM {{ ref('mart_user_order_behaviour') }}
WHERE user_segment NOT IN ('High Value', 'Regular', 'Occasional')
   OR user_segment IS NULL
