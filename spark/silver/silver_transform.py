from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, lit, col, when, broadcast
from pyspark.sql import functions as F
from delta.tables import DeltaTable

spark = SparkSession.builder.appName("Silver Transformations -- Join").getOrCreate()

SILVER_BASE = "s3a://silver"

# Load silver tables
slv_orders_df = spark.read.format("delta").load(f"{SILVER_BASE}/orders")
slv_aisles_df = spark.read.format("delta").load(f"{SILVER_BASE}/aisles")
slv_departments_df = spark.read.format("delta").load(f"{SILVER_BASE}/departments")
slv_products_df = spark.read.format("delta").load(f"{SILVER_BASE}/products")
slv_order_products__prior_df = spark.read.format("delta").load(f"{SILVER_BASE}/order_products__prior")

# Join-1 products and aisles and departments
products_join_df = slv_products_df \
    .join(broadcast(slv_aisles_df.select("aisle_id", "aisle")), "aisle_id") \
    .join(broadcast(slv_departments_df.select("department_id", "department")), "department_id")

products_join_df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(f"{SILVER_BASE}/slv_products_enriched")
slv_products_enriched_df = spark.read.format("delta").load(f"{SILVER_BASE}/slv_products_enriched")

# Join-2 order_products__prior and enriched products
order_products_prior_join_df = slv_order_products__prior_df \
    .join(
        broadcast(slv_products_enriched_df.select("product_id", "product_name", "aisle_id", "aisle", "department_id", "department")),
        "product_id"
    )

order_products_prior_join_df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(f"{SILVER_BASE}/slv_order_products_prior_enriched")
order_products_prior_enriched_df = spark.read.format("delta").load(f"{SILVER_BASE}/slv_order_products_prior_enriched")

# Join-3 enriched order_products and orders
order_products_full_df = order_products_prior_enriched_df \
    .join(
        slv_orders_df.select("order_id", "user_id", "order_number", "order_dow", "order_hour_of_day", "days_since_prior_order", "is_first_order", "is_weekend", "is_reordered"),
        "order_id"
    )
order_products_full_df = order_products_full_df.drop("reordered")
order_products_full_df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(f"{SILVER_BASE}/slv_order_products_full")

print("Silver transformations complete.")
