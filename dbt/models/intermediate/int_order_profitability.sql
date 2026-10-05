select
    o.order_id, o.order_date, o.city, o.revenue, o.product_cost,
    c.delivery_cost,
    o.revenue - o.product_cost - c.delivery_cost as contribution_margin,
    round(100 * (o.revenue - o.product_cost - c.delivery_cost) / nullif(o.revenue, 0), 2) as margin_pct
from {{ ref('stg_orders') }} o
left join {{ ref('stg_delivery_costs') }} c on o.order_id = c.order_id
where o.status = 'delivered'
