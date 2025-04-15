{{ config(
    materialized='table' 
) }}

with date_data as (
    select
        generate_series(
            '1980-01-01'::date, 
            '2100-01-01'::date, 
            '1 day'::interval   
        ) as date
)
select
    to_char(date, 'YYYY-MM-DD') as date,
    to_char(date, 'YYYYMMDD') as id, 
    extract(year from date) as year,
    extract(month from date) as month,
    extract(day from date) as day,
    trim(to_char(date, 'Day')) as day_of_week
from date_data
