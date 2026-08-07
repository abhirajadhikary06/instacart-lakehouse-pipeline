from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("Gold -- Product Popularity").getOrCreate()

SILVER_BASE = "s3a://silver"
GOLD_BASE = "s3a://gold"

# Which products are ordered most and reordered most.
product_popularity_df = spark.read.format("delta").load(f"{SILVER_BASE}/slv_order_products_full")
product_popularity_df.createOrReplaceTempView("order_products_full")

result_df = spark.sql("""
    SELECT
        product_id,
        product_name,
        department_id,
        department,
        COUNT(order_id) AS times_ordered,
        SUM(CAST(is_reordered AS INT)) AS times_reordered,
        ROUND(SUM(CAST(is_reordered AS INT)) / COUNT(order_id), 4) AS reorder_rate
    FROM order_products_full
    GROUP BY product_id, product_name, department
""")

result_df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").partitionBy(
    "department"
).save(f"{GOLD_BASE}/gold_product_popularity")
