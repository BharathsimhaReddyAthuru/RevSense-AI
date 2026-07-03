{{ config(materialized='table') }}

WITH orders AS (
    SELECT
        order_id,
        customer_id,
        order_purchase_at,
        delivered_customer_at,
        updated_at,
        order_status
    FROM {{ ref('stg_orders') }}
),

items AS (
    SELECT
        order_id,
        order_item_id,
        price,
        freight_value,
        total_item_value
    FROM {{ ref('stg_order_items') }}
),

payments AS (
    SELECT
        order_id,
        payment_value
    FROM {{ ref('stg_order_payments') }}
),

customer_orders AS (
    SELECT
        o.customer_id,
        o.order_id,
        o.order_purchase_at,
        o.updated_at,
        o.order_status,
        SUM(i.total_item_value) AS order_value,
        SUM(p.payment_value) AS payment_value
    FROM orders o
    LEFT JOIN items i ON o.order_id = i.order_id
    LEFT JOIN payments p ON o.order_id = p.order_id
    GROUP BY 1, 2, 3, 4, 5
),

customer_agg AS (
    SELECT
        customer_id,
        MIN(order_purchase_at) AS first_order_at,
        MAX(order_purchase_at) AS last_order_at,
        COUNT(DISTINCT order_id) AS total_orders,
        SUM(order_value) AS total_revenue,
        SUM(payment_value) AS total_payment_value,
        AVG(order_value) AS avg_order_value,
        MAX(updated_at) AS last_activity_at
    FROM customer_orders
    WHERE order_status NOT IN ('canceled', 'cancelled')
    GROUP BY 1
)

SELECT
    customer_id,
    first_order_at,
    last_order_at,
    total_orders,
    total_revenue,
    total_payment_value,
    avg_order_value,
    DATEDIFF('day', first_order_at, last_order_at) AS customer_age_days,
    CASE
        WHEN total_orders > 1 THEN TRUE
        ELSE FALSE
    END AS is_repeat_customer,
    CASE
        WHEN total_revenue > 0 THEN total_revenue / NULLIF(total_orders, 0)
        ELSE 0
    END AS avg_revenue_per_order,
    last_activity_at
FROM customer_agg
