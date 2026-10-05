select order_date, city
from {{ ref('mart_city_profitability') }}
group by order_date, city
having count(*) > 1
