from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, lit, col, when, broadcast
from pyspark.sql import functions as F

spark = SparkSession.builder.appName("Gold -- Order Time Analysis").getOrCreate()

SILVER_BASE = "s3a://silver"
GOLD_BASE = "s3a://gold"

# When do people shop — by day of week and hour of day.
product_popularity_df = spark.read.format("delta").load(f"{SILVER_BASE}/slv_order_products_full")
product_popularity_df.createOrReplaceTempView("order_products_full")

result_df = spark.sql("""
    SELECT
        order_dow,
        order_hour_of_day,
        COUNT(DISTINCT order_id) AS total_orders,
        ROUND(COUNT(product_id) / COUNT(DISTINCT order_id), 2) AS avg_basket_size
    FROM order_products_full
    GROUP BY order_dow, order_hour_of_day
    ORDER BY order_dow, order_hour_of_day
""")

result_df.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .partitionBy("order_dow") \
    .save(f"{GOLD_BASE}/gold_order_time_analysis")