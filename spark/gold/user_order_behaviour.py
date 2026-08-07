from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("Gold -- User Order Behaviour").getOrCreate()

SILVER_BASE = "s3a://silver"
GOLD_BASE = "s3a://gold"

# Per-user purchasing patterns — useful for segmentation.
product_popularity_df = spark.read.format("delta").load(f"{SILVER_BASE}/slv_order_products_full")
product_popularity_df.createOrReplaceTempView("order_products_full")

result_df = spark.sql("""
    SELECT
        user_id,
        COUNT(DISTINCT order_id) AS total_orders,
        COUNT(product_id) AS total_products_ordered,
        ROUND(AVG(add_to_cart_order), 2) AS avg_add_to_cart_position,
        MAX(days_since_prior_order) AS max_days_since_prior_order,
        COUNT(DISTINCT product_id) AS unique_products_count,
        ROUND(COUNT(product_id) / COUNT(DISTINCT order_id), 2) AS avg_basket_size,
        ROUND(AVG(days_since_prior_order), 2) AS avg_days_between_orders
    FROM order_products_full
    GROUP BY user_id
""")

result_df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(
    f"{GOLD_BASE}/gold_user_order_behaviour"
)
