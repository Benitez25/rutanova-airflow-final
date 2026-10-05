select 'row_count_mismatch' as issue
where (select count(*) from {{ ref('int_order_profitability') }})
   <> (select count(*) from {{ ref('stg_orders') }} where status = 'delivered')
