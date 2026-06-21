================================================================================
TABLE: olist_sellers_dataset.csv
================================================================================
Shape:
(3095, 4)

Columns:
['seller_id', 'seller_zip_code_prefix', 'seller_city', 'seller_state']

Data Types:
seller_id                   str
seller_zip_code_prefix    int64
seller_city                 str
seller_state                str
dtype: object

Top Null Columns:
seller_id                 0
seller_zip_code_prefix    0
seller_city               0
seller_state              0
dtype: int64

Potential Unique Columns:
seller_id


================================================================================
TABLE: product_category_name_translation.csv
================================================================================
Shape:
(71, 2)

Columns:
['product_category_name', 'product_category_name_english']

Data Types:
product_category_name            str
product_category_name_english    str
dtype: object

Top Null Columns:
product_category_name            0
product_category_name_english    0
dtype: int64

Potential Unique Columns:
product_category_name
product_category_name_english


================================================================================
TABLE: olist_orders_dataset.csv
================================================================================
Shape:
(99441, 8)

Columns:
['order_id', 'customer_id', 'order_status', 'order_purchase_timestamp', 'order_approved_at', 'order_delivered_carrier_date', 'order_delivered_customer_date', 'order_estimated_delivery_date']

Data Types:
order_id                         str
customer_id                      str
order_status                     str
order_purchase_timestamp         str
order_approved_at                str
order_delivered_carrier_date     str
order_delivered_customer_date    str
order_estimated_delivery_date    str
dtype: object

Top Null Columns:
order_delivered_customer_date    2965
order_delivered_carrier_date     1783
order_approved_at                 160
order_id                            0
order_purchase_timestamp            0
dtype: int64

Potential Unique Columns:
order_id
customer_id


================================================================================
TABLE: olist_order_items_dataset.csv
================================================================================
Shape:
(112650, 7)

Columns:
['order_id', 'order_item_id', 'product_id', 'seller_id', 'shipping_limit_date', 'price', 'freight_value']

Data Types:
order_id                   str
order_item_id            int64
product_id                 str
seller_id                  str
shipping_limit_date        str
price                  float64
freight_value          float64
dtype: object

Top Null Columns:
order_id               0
order_item_id          0
product_id             0
seller_id              0
shipping_limit_date    0
dtype: int64

Potential Unique Columns:


================================================================================
TABLE: olist_customers_dataset.csv
================================================================================
Shape:
(99441, 5)

Columns:
['customer_id', 'customer_unique_id', 'customer_zip_code_prefix', 'customer_city', 'customer_state']

Data Types:
customer_id                   str
customer_unique_id            str
customer_zip_code_prefix    int64
customer_city                 str
customer_state                str
dtype: object

Top Null Columns:
customer_id                 0
customer_unique_id          0
customer_zip_code_prefix    0
customer_city               0
customer_state              0
dtype: int64

Potential Unique Columns:
customer_id


================================================================================
TABLE: olist_geolocation_dataset.csv
================================================================================
Shape:
(1000163, 5)

Columns:
['geolocation_zip_code_prefix', 'geolocation_lat', 'geolocation_lng', 'geolocation_city', 'geolocation_state']

Data Types:
geolocation_zip_code_prefix      int64
geolocation_lat                float64
geolocation_lng                float64
geolocation_city                   str
geolocation_state                  str
dtype: object

Top Null Columns:
geolocation_zip_code_prefix    0
geolocation_lat                0
geolocation_lng                0
geolocation_city               0
geolocation_state              0
dtype: int64

Potential Unique Columns:


================================================================================
TABLE: olist_order_payments_dataset.csv
================================================================================
Shape:
(103886, 5)

Columns:
['order_id', 'payment_sequential', 'payment_type', 'payment_installments', 'payment_value']

Data Types:
order_id                    str
payment_sequential        int64
payment_type                str
payment_installments      int64
payment_value           float64
dtype: object

Top Null Columns:
order_id                0
payment_sequential      0
payment_type            0
payment_installments    0
payment_value           0
dtype: int64

Potential Unique Columns:


================================================================================
TABLE: olist_order_reviews_dataset.csv
================================================================================
Shape:
(99224, 7)

Columns:
['review_id', 'order_id', 'review_score', 'review_comment_title', 'review_comment_message', 'review_creation_date', 'review_answer_timestamp']

Data Types:
review_id                    str
order_id                     str
review_score               int64
review_comment_title         str
review_comment_message       str
review_creation_date         str
review_answer_timestamp      str
dtype: object

Top Null Columns:
review_comment_title      87656
review_comment_message    58247
review_id                     0
review_score                  0
order_id                      0
dtype: int64

Potential Unique Columns:


================================================================================
TABLE: olist_products_dataset.csv
================================================================================
Shape:
(32951, 9)

Columns:
['product_id', 'product_category_name', 'product_name_lenght', 'product_description_lenght', 'product_photos_qty', 'product_weight_g', 'product_length_cm', 'product_height_cm', 'product_width_cm']

Data Types:
product_id                        str
product_category_name             str
product_name_lenght           float64
product_description_lenght    float64
product_photos_qty            float64
product_weight_g              float64
product_length_cm             float64
product_height_cm             float64
product_width_cm              float64
dtype: object

Top Null Columns:
product_category_name         610
product_description_lenght    610
product_name_lenght           610
product_photos_qty            610
product_weight_g                2
dtype: int64

Potential Unique Columns:
product_id


