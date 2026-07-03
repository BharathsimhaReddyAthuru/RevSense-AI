{{ config(materialized='table') }}

WITH seller_sales AS (
    SELECT
        i.seller_id,
        SUM(i.total_item_value) AS revenue,
        COUNT(DISTINCT i.order_id) AS order_count
    FROM {{ ref('stg_order_items') }} i
    JOIN {{ ref('stg_orders') }} o ON i.order_id = o.order_id
    WHERE o.order_status NOT IN ('canceled', 'cancelled')
    GROUP BY 1
)

SELECT
    ss.seller_id,
    sl.seller_city,
    sl.seller_state,
    ss.revenue,
    ss.order_count,
    CASE WHEN ss.order_count = 0 THEN 0 ELSE ss.revenue / ss.order_count END AS avg_order_value
FROM seller_sales ss
LEFT JOIN {{ ref('stg_sellers') }} sl ON ss.seller_id = sl.seller_id
ORDER BY revenue DESC
