with source as (

    select * from {{ source('raw', 'order_payments') }}

),

cleaned as (

    select
        order_id,
        payment_sequential,
        lower(payment_type) as payment_type,
        payment_installments,
        payment_value

    from source

)

select * from cleaned