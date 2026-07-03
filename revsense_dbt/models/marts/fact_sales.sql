{{ config(
    materialized='incremental',
    unique_key=['order_id', 'order_item_id']
) }}

WITH orders AS (
    SELECT * FROM {{ ref('stg_orders') }}

    -- THE TRUE INCREMENTAL LOGIC
    -- This now correctly pulls ANY order that was modified recently, 
    -- regardless of when it was originally purchased!
    {% if is_incremental() %}
        WHERE updated_at > (SELECT MAX(updated_at) FROM {{ this }})
    {% endif %}
),
items AS (
    SELECT * FROM {{ ref('stg_order_items') }}
)

SELECT
    i.order_id,
    i.order_item_id,
    o.customer_id,
    i.product_id,
    i.seller_id,
    o.order_purchase_at,
    o.delivered_customer_at,
    o.updated_at, 
    i.price,
    i.freight_value,
    i.total_item_value
FROM items i
JOIN orders o ON i.order_id = o.order_id