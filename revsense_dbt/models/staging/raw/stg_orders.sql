with source as (
    select *
    from {{ source('raw', 'orders') }}
),

renamed as (
    select
        order_id,
        customer_id,
        order_status,

        cast(order_purchase_timestamp as timestamp) as order_purchase_at,
        cast(order_approved_at as timestamp) as order_approved_at,
        cast(order_delivered_carrier_date as timestamp) as delivered_carrier_at,
        cast(order_delivered_customer_date as timestamp) as delivered_customer_at,
        cast(order_estimated_delivery_date as timestamp) as estimated_delivery_at,
        GREATEST(
            CAST(order_purchase_timestamp AS TIMESTAMP),
            COALESCE(CAST(order_approved_at AS TIMESTAMP), CAST(order_purchase_timestamp AS TIMESTAMP)),
            COALESCE(CAST(order_delivered_carrier_date AS TIMESTAMP), CAST(order_purchase_timestamp AS TIMESTAMP)),
            COALESCE(CAST(order_delivered_customer_date AS TIMESTAMP), CAST(order_purchase_timestamp AS TIMESTAMP))
        ) AS updated_at
    from source
)

select * from renamed