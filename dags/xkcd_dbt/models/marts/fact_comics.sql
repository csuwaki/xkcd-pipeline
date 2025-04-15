{{ config(materialized='table') }}

with fact_comics as (
    select 
        sc.comic_id,
        concat(
                    cast(sc.year as varchar), 
                    lpad(cast(sc.month as varchar), 2, '0'), 
                    lpad(cast(sc.day as varchar), 2, '0')
                ) as date_id,
        sc.title
    from {{ ref('staging_comics') }} sc
)
select
    comic_id,
    date_id,
    length(title)*5 as cost,
    round(cast((random() * 9) + 1 as numeric), 1) as customer_reviews,
    (random()*10000)::int as customer_views
from fact_comics

