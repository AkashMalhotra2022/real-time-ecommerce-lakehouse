select
    s.seller_id,
    s.seller_state,
    count(distinct foi.order_id)      as orders_fulfilled,
    count(*)                          as items_sold,
    round(sum(foi.item_revenue), 2)   as total_revenue,
    round(avg(foi.price), 2)          as avg_item_price,
    round(sum(foi.freight_value), 2)  as total_freight
from {{ source('gold','fact_order_items') }} foi
join {{ source('gold','dim_seller') }} s on foi.seller_id = s.seller_id
group by s.seller_id, s.seller_state