with source as (

    select * from {{ source('raw', 'geolocation') }}

),

cleaned as (

    select
        geolocation_zip_code_prefix,
        geolocation_lat,
        geolocation_lng,
        lower(trim(geolocation_city)) as geolocation_city,
        lower(trim(geolocation_state)) as geolocation_state

    from source

)

select * from cleaned