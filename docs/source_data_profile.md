##############################################################################
# OLIST DATA PROFILE
# source: /Users/akashmalhotra/Desktop/real-time-ecommerce-lakehouse/data/raw/historical
##############################################################################

==============================================================================
TABLE: customers   (olist_customers_dataset.csv)
==============================================================================
shape        : 99,441 rows x 5 cols   (~29.6 MB in memory)
duplicate rows: 0
PK 'customer_id': distinct=99,441, duplicate-key rows=0

column                                 dtype                nulls    null%
------------------------------------------------------------------------------
customer_id                             str                      0    0.00%
customer_unique_id                      str                      0    0.00%
customer_zip_code_prefix                int64                    0    0.00%
customer_city                           str                      0    0.00%
customer_state                          str                      0    0.00%

==============================================================================
TABLE: geolocation   (olist_geolocation_dataset.csv)
==============================================================================
shape        : 1,000,163 rows x 5 cols   (~145.2 MB in memory)
duplicate rows: 261,831

column                                 dtype                nulls    null%
------------------------------------------------------------------------------
geolocation_zip_code_prefix             int64                    0    0.00%
geolocation_lat                         float64                  0    0.00%
geolocation_lng                         float64                  0    0.00%
geolocation_city                        str                      0    0.00%
geolocation_state                       str                      0    0.00%

==============================================================================
TABLE: order_items   (olist_order_items_dataset.csv)
==============================================================================
shape        : 112,650 rows x 7 cols   (~39.4 MB in memory)
duplicate rows: 0
composite PK ('order_id', 'order_item_id'): duplicate-key rows=0

column                                 dtype                nulls    null%
------------------------------------------------------------------------------
order_id                                str                      0    0.00%
order_item_id                           int64                    0    0.00%
product_id                              str                      0    0.00%
seller_id                               str                      0    0.00%
shipping_limit_date                     str                      0    0.00%
price                                   float64                  0    0.00%
freight_value                           float64                  0    0.00%

date ranges:
  shipping_limit_date: 2016-09-19 00:15:34  ->  2020-04-09 22:35:08  (unparseable: 0)

==============================================================================
TABLE: order_payments   (olist_order_payments_dataset.csv)
==============================================================================
shape        : 103,886 rows x 5 cols   (~17.8 MB in memory)
duplicate rows: 0
composite PK ('order_id', 'payment_sequential'): duplicate-key rows=0

column                                 dtype                nulls    null%
------------------------------------------------------------------------------
order_id                                str                      0    0.00%
payment_sequential                      int64                    0    0.00%
payment_type                            str                      0    0.00%
payment_installments                    int64                    0    0.00%
payment_value                           float64                  0    0.00%

==============================================================================
TABLE: order_reviews   (olist_order_reviews_dataset.csv)
==============================================================================
shape        : 99,224 rows x 7 cols   (~42.7 MB in memory)
duplicate rows: 0
PK 'review_id': distinct=98,410, duplicate-key rows=814

column                                 dtype                nulls    null%
------------------------------------------------------------------------------
review_id                               str                      0    0.00%
order_id                                str                      0    0.00%
review_score                            int64                    0    0.00%
review_comment_title                    str                 87,656   88.34%
review_comment_message                  str                 58,247   58.70%
review_creation_date                    str                      0    0.00%
review_answer_timestamp                 str                      0    0.00%

date ranges:
  review_creation_date: 2016-10-02 00:00:00  ->  2018-08-31 00:00:00  (unparseable: 0)
  review_answer_timestamp: 2016-10-07 18:32:28  ->  2018-10-29 12:27:35  (unparseable: 0)

==============================================================================
TABLE: orders   (olist_orders_dataset.csv)
==============================================================================
shape        : 99,441 rows x 8 cols   (~59.0 MB in memory)
duplicate rows: 0
PK 'order_id': distinct=99,441, duplicate-key rows=0

column                                 dtype                nulls    null%
------------------------------------------------------------------------------
order_id                                str                      0    0.00%
customer_id                             str                      0    0.00%
order_status                            str                      0    0.00%
order_purchase_timestamp                str                      0    0.00%
order_approved_at                       str                    160    0.16%
order_delivered_carrier_date            str                  1,783    1.79%
order_delivered_customer_date           str                  2,965    2.98%
order_estimated_delivery_date           str                      0    0.00%

date ranges:
  order_purchase_timestamp: 2016-09-04 21:15:19  ->  2018-10-17 17:30:18  (unparseable: 0)
  order_delivered_carrier_date: 2016-10-08 10:34:01  ->  2018-09-11 19:48:28  (unparseable: 0)
  order_delivered_customer_date: 2016-10-11 13:46:32  ->  2018-10-17 13:22:46  (unparseable: 0)
  order_estimated_delivery_date: 2016-09-30 00:00:00  ->  2018-11-12 00:00:00  (unparseable: 0)

==============================================================================
TABLE: products   (olist_products_dataset.csv)
==============================================================================
shape        : 32,951 rows x 9 cols   (~6.8 MB in memory)
duplicate rows: 0
PK 'product_id': distinct=32,951, duplicate-key rows=0

column                                 dtype                nulls    null%
------------------------------------------------------------------------------
product_id                              str                      0    0.00%
product_category_name                   str                    610    1.85%
product_name_lenght                     float64                610    1.85%
product_description_lenght              float64                610    1.85%
product_photos_qty                      float64                610    1.85%
product_weight_g                        float64                  2    0.01%
product_length_cm                       float64                  2    0.01%
product_height_cm                       float64                  2    0.01%
product_width_cm                        float64                  2    0.01%

==============================================================================
TABLE: sellers   (olist_sellers_dataset.csv)
==============================================================================
shape        : 3,095 rows x 4 cols   (~0.7 MB in memory)
duplicate rows: 0
PK 'seller_id': distinct=3,095, duplicate-key rows=0

column                                 dtype                nulls    null%
------------------------------------------------------------------------------
seller_id                               str                      0    0.00%
seller_zip_code_prefix                  int64                    0    0.00%
seller_city                             str                      0    0.00%
seller_state                            str                      0    0.00%

==============================================================================
TABLE: category_translation   (product_category_name_translation.csv)
==============================================================================
shape        : 71 rows x 2 cols   (~0.0 MB in memory)
duplicate rows: 0
PK 'product_category_name': distinct=71, duplicate-key rows=0

column                                 dtype                nulls    null%
------------------------------------------------------------------------------
product_category_name                   str                      0    0.00%
product_category_name_english           str                      0    0.00%

==============================================================================
REFERENTIAL INTEGRITY  (orphan child rows whose key is absent in parent)
==============================================================================
  orders.customer_id -> customers.customer_id: 0 orphans (0.000%)  OK
  order_items.order_id -> orders.order_id: 0 orphans (0.000%)  OK
  order_items.product_id -> products.product_id: 0 orphans (0.000%)  OK
  order_items.seller_id -> sellers.seller_id: 0 orphans (0.000%)  OK
  order_payments.order_id -> orders.order_id: 0 orphans (0.000%)  OK
  order_reviews.order_id -> orders.order_id: 0 orphans (0.000%)  OK

##############################################################################
# Profiling complete. Use the null%, duplicate, and orphan figures above
# to author Silver-layer data-quality expectations (dbt tests / Spark checks).
##############################################################################