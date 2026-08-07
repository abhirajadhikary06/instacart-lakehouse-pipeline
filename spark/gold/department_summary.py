from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("Gold -- Department Summary").getOrCreate()

SILVER_BASE = "s3a://silver"
GOLD_BASE = "s3a://gold"

# Sales volume and reorder behaviour by department.
product_popularity_df = spark.read.format("delta").load(f"{SILVER_BASE}/slv_order_products_full")
product_popularity_df.createOrReplaceTempView("order_products_full")

result_df = spark.sql("""
    SELECT
        department,
        department_id,
        COUNT(*) AS total_orders,
        COUNT(DISTINCT product_id) AS unique_products_ordered,
        ROUND(SUM(CAST(is_reordered AS INT)) / COUNT(*), 4) AS reorder_rate
    FROM order_products_full
    GROUP BY department_id, department
""")

result_df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").partitionBy(
    "department"
).save(f"{GOLD_BASE}/gold_department_summary")
