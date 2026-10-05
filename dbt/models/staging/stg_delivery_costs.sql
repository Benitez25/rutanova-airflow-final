select order_id, cast(delivery_cost as number(14,2)) as delivery_cost, delivery_date
from {{ source('raw', 'delivery_costs') }}
