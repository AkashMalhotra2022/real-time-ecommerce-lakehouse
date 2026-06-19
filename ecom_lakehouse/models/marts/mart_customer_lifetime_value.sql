select
    dc.customer_unique_id,
    count(distinct fo.order_id)              as total_orders,
    round(sum(fo.order_payment_total), 2)    as lifetime_value,
    round(avg(fo.order_payment_total), 2)    as avg_order_value,
    min(fo.order_purchase_timestamp)         as first_order_at,
    max(fo.order_purchase_timestamp)         as last_order_at,
    count(distinct fo.order_id) > 1          as is_repeat_customer
from {{ source('gold','fact_orders') }} fo
join {{ source('gold','dim_customer') }} dc on fo.customer_id = dc.customer_id
group by dc.customer_unique_id