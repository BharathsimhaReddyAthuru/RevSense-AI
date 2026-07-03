with source as (

    select * from {{ source('raw', 'order_reviews') }}

),

cleaned as (

    select
        review_id,
        order_id,
        review_score,

        trim(review_comment_title) as review_title,
        trim(review_comment_message) as review_message,

        cast(review_creation_date as timestamp) as review_created_at,
        cast(review_answer_timestamp as timestamp) as review_answered_at

    from source

)

select * from cleaned