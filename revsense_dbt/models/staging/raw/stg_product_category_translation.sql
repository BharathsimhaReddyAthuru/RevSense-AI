with source as (
    select * from {{ source('raw', 'product_category_translation') }}
),

cleaned as (

    select
        product_category_name,
        lower(trim(product_category_name_english)) as product_category_name_english

    from source

)

select * from cleaned