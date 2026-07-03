with source as (

    select * from {{ source('raw', 'customers') }}

),

cleaned as (

    select
        customer_id,
        customer_unique_id,
        customer_zip_code_prefix,
        lower(trim(customer_city)) as customer_city,
        lower(trim(customer_state)) as customer_state

    from source

)

select * from cleaned