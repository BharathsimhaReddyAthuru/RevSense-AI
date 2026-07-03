{{ config(materialized='table') }}

WITH items AS (
    SELECT
        i.order_id,
        i.product_id,
        i.total_item_value,
        p.product_category_name
    FROM {{ ref('stg_order_items') }} i
    JOIN {{ ref('stg_products') }} p ON i.product_id = p.product_id
),

categories AS (
    SELECT
        product_category_name,
        COALESCE(product_category_name_english, product_category_name) AS category_name
    FROM {{ ref('stg_product_category_translation') }}
),

sales AS (
    SELECT
        itm.product_category_name,
        cat.category_name,
        SUM(itm.total_item_value) AS revenue,
        COUNT(DISTINCT itm.order_id) AS order_count
    FROM items itm
    LEFT JOIN categories cat ON itm.product_category_name = cat.product_category_name
    GROUP BY 1, 2
)

SELECT
    category_name,
    revenue,
    order_count,
    CASE WHEN order_count = 0 THEN 0 ELSE revenue / order_count END AS avg_order_value
FROM sales
ORDER BY revenue DESC
