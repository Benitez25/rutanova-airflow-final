select order_date, city from {{ ref('mart_city_profitability') }}
where abs(contribution_margin - (total_revenue - total_product_cost - total_delivery_cost)) > 0.01
