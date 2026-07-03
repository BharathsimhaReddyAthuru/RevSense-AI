{{ config(materialized='table') }}

WITH order_values AS (
    SELECT
        DATE_TRUNC('month', order_purchase_at) AS order_month,
        SUM(price + freight_value) AS revenue
    FROM {{ ref('stg_order_items') }} i
    JOIN {{ ref('stg_orders') }} o ON i.order_id = o.order_id
    WHERE o.order_status NOT IN ('canceled', 'cancelled')
    GROUP BY 1
),

month_stats AS (
    SELECT
        order_month,
        revenue,
        LAG(revenue, 1) OVER (ORDER BY order_month) AS prior_month_revenue,
        LEAD(revenue, 1) OVER (ORDER BY order_month) AS next_month_revenue
    FROM order_values
)

SELECT
    order_month,
    revenue,
    COALESCE(prior_month_revenue, 0) AS prior_month_revenue,
    COALESCE(next_month_revenue, 0) AS next_month_revenue,
    CASE
        WHEN prior_month_revenue IS NULL THEN revenue
        WHEN prior_month_revenue = 0 THEN revenue
        ELSE revenue * 1.02
    END AS forecast_revenue
FROM month_stats
ORDER BY order_month
