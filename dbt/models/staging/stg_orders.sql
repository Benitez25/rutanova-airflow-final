select
    order_id,
    order_date,
    trim(city) as city,
    cast(revenue as number(14,2)) as revenue,
    cast(product_cost as number(14,2)) as product_cost,
    lower(trim(status)) as status
from {{ source('raw', 'orders') }}
