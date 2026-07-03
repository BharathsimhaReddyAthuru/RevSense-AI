{{ config(materialized='table') }}

WITH review_items AS (
    SELECT
        r.review_id,
        r.order_id,
        r.review_score,
        r.review_created_at,
        i.product_id
    FROM {{ ref('stg_order_reviews') }} r
    JOIN {{ ref('stg_order_items') }} i ON r.order_id = i.order_id
),

product_reviews AS (
    SELECT
        product_id,
        COUNT(review_id) AS review_count,
        AVG(review_score) AS avg_review_score,
        SUM(CASE WHEN review_score <= 2 THEN 1 ELSE 0 END) AS negative_review_count
    FROM review_items
    GROUP BY 1
)

SELECT
    product_id,
    review_count,
    avg_review_score,
    negative_review_count,
    CASE WHEN review_count = 0 THEN 0 ELSE negative_review_count::FLOAT / review_count END AS negative_review_ratio
FROM product_reviews
ORDER BY avg_review_score ASC, review_count DESC
