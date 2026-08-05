from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, lit, col, when
from pyspark.sql import functions as F

spark = SparkSession.builder.appName("Silver Write").getOrCreate()

BRONZE_BASE = "s3a://bronze"
SILVER_BASE = "s3a://silver"

# Load bronze tables 
orders_df = spark.read.format("delta").load(f"{BRONZE_BASE}/orders")
aisles_df = spark.read.format("delta").load(f"{BRONZE_BASE}/aisles")
departments_df = spark.read.format("delta").load(f"{BRONZE_BASE}/departments")
products_df = spark.read.format("delta").load(f"{BRONZE_BASE}/products")
order_products__prior_df = spark.read.format("delta").load(f"{BRONZE_BASE}/order_products__prior")


# Deduplication 
def deduplicate(df, pk_col):
    pk_cols = pk_col if isinstance(pk_col, list) else [pk_col]
    return df.dropDuplicates(pk_cols)


# Derived columns — orders 
orders_df = orders_df \
    .withColumn("is_first_order", when(col("order_number") == 1, True).otherwise(False)) \
    .withColumn("is_weekend", when((col("order_dow") == 0) | (col("order_dow") == 1), True).otherwise(False)) \
    .withColumn("is_reordered", when(col("order_number") > 1, True).otherwise(False))


# Write to silver 
def write_silver(df, table_name):
    df.write \
      .format("delta") \
      .mode("overwrite") \
      .option("overwriteSchema", "true") \
      .save(f"{SILVER_BASE}/{table_name}")
    print(f"Written: {SILVER_BASE}/{table_name}")


def main():
    write_silver(deduplicate(orders_df, "order_id"), "orders")
    write_silver(deduplicate(products_df, "product_id"), "products")
    write_silver(deduplicate(order_products__prior_df, ["order_id", "product_id"]), "order_products__prior")
    write_silver(deduplicate(aisles_df, "aisle_id"), "aisles")
    write_silver(deduplicate(departments_df, "department_id"), "departments")

main()


