select
    d.year,
    d.month,
    count(*)                                                          as total_orders,
    sum(case when fo.order_status = 'delivered' then 1 else 0 end)    as delivered_orders,
    sum(case when fo.is_late then 1 else 0 end)                       as late_orders,
    round(100.0 * sum(case when fo.is_late then 1 else 0 end)
          / nullif(sum(case when fo.order_status='delivered' then 1 else 0 end), 0), 2) as late_delivery_rate_pct,
    round(avg(fo.delivery_days), 1)                                   as avg_delivery_days,
    round(avg(fo.delivery_delay_days), 1)                             as avg_delay_vs_estimate
from {{ source('gold','fact_orders') }} fo
join {{ source('gold','dim_date') }} d on fo.order_date_key = d.date_key
group by d.year, d.month