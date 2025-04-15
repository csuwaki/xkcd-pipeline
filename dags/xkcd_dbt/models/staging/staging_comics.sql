{{ config(
    materialized='incremental',
    unique_key='comic_id'
) }}

with source as (
    select 
        num as comic_id,
        month,
        year,
        day,
        link,
        news,
        safe_title,
        transcript,
        alt,
        img,
        title
    from raw_comics

    {% if is_incremental() %}
        where num > (select max(comic_id) from {{ this }})
    {% endif %}
)

select * from source


