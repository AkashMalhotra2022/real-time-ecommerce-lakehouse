select
    d.date_day,
    d.year,
    d.month,
    count(distinct fo.order_id)                  as order_count,
    round(sum(fo.order_payment_total), 2)        as gross_revenue,
    round(avg(fo.order_payment_total), 2)        as avg_order_value,
    sum(case when fo.is_late then 1 else 0 end)  as late_deliveries,
    round(avg(fo.delivery_days), 1)              as avg_delivery_days
from {{ source('gold', 'fact_orders') }} fo
join {{ source('gold', 'dim_date') }} d
    on fo.order_date_key = d.date_key
group by d.date_day, d.year, d.month