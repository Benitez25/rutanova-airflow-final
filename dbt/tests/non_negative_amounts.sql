-- Negative margins ARE valid; negative revenue or costs are not.
select order_id from {{ ref('int_order_profitability') }}
where revenue < 0 or product_cost < 0 or delivery_cost < 0
