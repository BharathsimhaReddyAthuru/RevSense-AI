{{ config(materialized='table') }}

WITH orders AS (
    SELECT
        DATE_TRUNC('month', order_purchase_at) AS order_month,
        order_id
    FROM {{ ref('stg_orders') }}
    WHERE order_status NOT IN ('canceled', 'cancelled')
),

monthly_counts AS (
    SELECT
        order_month,
        COUNT(DISTINCT order_id) AS order_volume
    FROM orders
    GROUP BY 1
    ORDER BY 1
),

forecasts AS (
    SELECT
        order_month,
        order_volume,
        LAG(order_volume, 1) OVER (ORDER BY order_month) AS prior_month_volume,
        CASE
            WHEN LAG(order_volume, 1) OVER (ORDER BY order_month) IS NULL THEN order_volume
            ELSE order_volume * 1.02
        END AS forecast_volume
    FROM monthly_counts
)

SELECT *
FROM forecasts
