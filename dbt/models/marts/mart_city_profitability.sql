select
    order_date, city,
    count(*) as delivered_orders,
    sum(revenue) as total_revenue,
    sum(product_cost) as total_product_cost,
    sum(delivery_cost) as total_delivery_cost,
    sum(contribution_margin) as contribution_margin,
    round(100 * sum(contribution_margin) / nullif(sum(revenue), 0), 2) as margin_pct
from {{ ref('int_order_profitability') }}
group by order_date, city
