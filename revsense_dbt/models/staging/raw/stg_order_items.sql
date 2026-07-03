with source as (

    select * from {{ source('raw', 'order_items') }}

),

cleaned as (

    select
        order_id,
        order_item_id,
        product_id,
        seller_id,
        price,
        freight_value,
        (price + freight_value) AS total_item_value

    from source

)

select * from cleaned