{{ config(materialized='table') }}

WITH orders AS (
    SELECT
        order_id,
        customer_id,
        order_purchase_at,
        updated_at,
        order_status
    FROM {{ ref('stg_orders') }}
    WHERE order_status NOT IN ('canceled', 'cancelled')
),

customer_orders AS (
    SELECT
        customer_id,
        order_id,
        order_purchase_at,
        updated_at,
        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_purchase_at DESC) AS order_rank
    FROM orders
),

latest_order AS (
    SELECT
        customer_id,
        order_id,
        order_purchase_at AS last_order_at
    FROM customer_orders
    WHERE order_rank = 1
),

previous_order AS (
    SELECT
        customer_id,
        order_purchase_at AS second_last_order_at
    FROM customer_orders
    WHERE order_rank = 2
),

customer_intervals AS (
    SELECT
        l.customer_id,
        l.last_order_at,
        p.second_last_order_at,
        DATEDIFF('day', p.second_last_order_at, l.last_order_at) AS days_since_last_order,
        CASE
            WHEN DATEDIFF('day', p.second_last_order_at, l.last_order_at) > 90 THEN 1
            ELSE 0
        END AS churn_label
    FROM latest_order l
    LEFT JOIN previous_order p ON l.customer_id = p.customer_id
)

SELECT
    customer_id,
    last_order_at,
    second_last_order_at,
    days_since_last_order,
    churn_label
FROM customer_intervals
