{{ config(materialized='table') }}

with staging_comics as (
    select * from {{ ref('staging_comics') }}  
)

select
    comic_id,
    title,
    safe_title,
    link,
    img,
    alt,
    transcript
from staging_comics