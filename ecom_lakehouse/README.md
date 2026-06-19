# ecom_lakehouse (dbt)

The **serving layer** of the [Real-Time E-Commerce Lakehouse](../README.md). This dbt project builds business marts on top of the Gold star schema produced by the Databricks medallion pipeline, and tests the Gold tables for integrity.

## Sources

Defined in [`models/sources.yml`](models/sources.yml) — the `ecom_gold` schema produced by the Spark pipeline (`dim_customer`, `dim_date`, `dim_product`, `dim_seller`, `fact_orders`, `fact_order_items`). Source tests enforce `not_null` / `unique` on primary keys, `accepted_values` on `order_status`, and `relationships` (orphan) checks across the facts and dimensions.

## Marts (`models/marts/`, materialized as tables)

| Mart | Description |
|------|-------------|
| `mart_daily_revenue` | Daily revenue, order count, AOV, and late deliveries. |
| `mart_customer_lifetime_value` | LTV and repeat-purchase behavior per unique customer. |
| `mart_product_performance` | Units, revenue, and avg price by product / category. |
| `mart_seller_performance` | Orders, revenue, and freight by seller and state. |
| `mart_fulfillment_performance` | Late-delivery rate and delivery vs. estimate by month. |

## Usage

```bash
dbt run     # build the marts
dbt test    # run source + model tests
```

Requires a `ecom_lakehouse` profile in `~/.dbt/profiles.yml` pointing at your Databricks workspace.
