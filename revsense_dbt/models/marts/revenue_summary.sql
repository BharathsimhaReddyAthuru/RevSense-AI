{{ config(materialized='table') }}

WITH order_metrics AS (
    SELECT
        o.order_id,
        o.customer_id,
        o.order_status,
        o.order_purchase_at,
        i.total_item_value,
        p.payment_value
    FROM {{ ref('stg_orders') }} o
    LEFT JOIN {{ ref('stg_order_items') }} i ON o.order_id = i.order_id
    LEFT JOIN {{ ref('stg_order_payments') }} p ON o.order_id = p.order_id
    WHERE o.order_status NOT IN ('canceled', 'cancelled')
),

summary AS (
    SELECT
        COUNT(DISTINCT order_id) AS total_orders,
        SUM(total_item_value) AS total_revenue,
        AVG(total_item_value) AS average_order_value,
        COUNT(DISTINCT customer_id) AS active_customers
    FROM order_metrics
)

SELECT *
FROM summary
