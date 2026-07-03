{{ config(materialized='table') }}

WITH order_customers AS (
    SELECT
        o.order_id,
        c.customer_state,
        i.total_item_value
    FROM {{ ref('stg_orders') }} o
    LEFT JOIN {{ ref('stg_customers') }} c ON o.customer_id = c.customer_id
    LEFT JOIN {{ ref('stg_order_items') }} i ON o.order_id = i.order_id
    WHERE o.order_status NOT IN ('canceled', 'cancelled')
),

state_revenue AS (
    SELECT
        customer_state,
        SUM(total_item_value) AS revenue,
        COUNT(DISTINCT order_id) AS order_count
    FROM order_customers
    GROUP BY 1
)

SELECT
    customer_state,
    revenue,
    order_count,
    CASE WHEN order_count = 0 THEN 0 ELSE revenue / order_count END AS avg_order_value
FROM state_revenue
ORDER BY revenue DESC
