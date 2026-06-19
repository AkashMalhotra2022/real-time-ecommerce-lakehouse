select
    p.product_id,
    p.product_category_name_english as category,
    count(distinct foi.order_id)     as orders,
    count(*)                         as units_sold,
    round(sum(foi.item_revenue), 2)  as total_revenue,
    round(avg(foi.price), 2)         as avg_price
from {{ source('gold','fact_order_items') }} foi
join {{ source('gold','dim_product') }} p on foi.product_id = p.product_id
group by p.product_id, p.product_category_name_english