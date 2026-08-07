from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("Gold -- Aisle Reorder Analysis").getOrCreate()

SILVER_BASE = "s3a://silver"
GOLD_BASE = "s3a://gold"

# Which aisles have the highest reorder rates — shows habitual purchase categories.
product_popularity_df = spark.read.format("delta").load(f"{SILVER_BASE}/slv_order_products_full")
product_popularity_df.createOrReplaceTempView("order_products_full")

result_df = spark.sql("""
    SELECT
        aisle_id,
        aisle,
        department,
        COUNT(DISTINCT order_id) AS total_orders,
        SUM(CAST(is_reordered AS INT)) AS total_reorders,
        ROUND(SUM(CAST(is_reordered AS INT)) / COUNT(*), 4) AS reorder_rate
    FROM order_products_full
    GROUP BY aisle_id, aisle, department
    ORDER BY reorder_rate DESC, total_reorders DESC
""")

result_df.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .partitionBy("department") \
    .save(f"{GOLD_BASE}/gold_aisle_reorder_analysis")