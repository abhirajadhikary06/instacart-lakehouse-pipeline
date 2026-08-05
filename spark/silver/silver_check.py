from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.sql import functions as F

spark = SparkSession.builder.appName("Silver Checks -- before Transformation").getOrCreate()

BRONZE_BASE = "s3a://bronze"
SILVER_BASE = "s3a://silver"

# Load bronze tables
orders_df = spark.read.format("delta").load(f"{BRONZE_BASE}/orders")
aisles_df = spark.read.format("delta").load(f"{BRONZE_BASE}/aisles")
departments_df = spark.read.format("delta").load(f"{BRONZE_BASE}/departments")
products_df = spark.read.format("delta").load(f"{BRONZE_BASE}/products")
order_products__prior_df = spark.read.format("delta").load(f"{BRONZE_BASE}/order_products__prior")

# Map table name (DataFrame, primary key column(s))
col_map_dict = {
    "orders": (orders_df, "order_id"),
    "aisles": (aisles_df, "aisle_id"),
    "departments": (departments_df, "department_id"),
    "products": (products_df, "product_id"),
    "order_products__prior": (order_products__prior_df, ["order_id", "product_id"]),
}


def null_count(df, pk_col):
    if isinstance(pk_col, list):
        results = []
        for c in pk_col:
            cnt = df.filter(col(c).isNull()).count()
            results.append(f"{c}_null_count = {cnt}")
        return ", ".join(results)
    cnt = df.filter(col(pk_col).isNull()).count()
    return f"{pk_col}_null_count = {cnt}"


def duplicate(df, pk_col):
    pk_cols = pk_col if isinstance(pk_col, list) else [pk_col]
    dup_count = df.groupBy(pk_cols).count().filter("count > 1").count()
    return f"duplicate_count = {dup_count}"


if __name__ == "__main__":
    for table_name, (df, pk_col) in col_map_dict.items():
        print(f"\n--- {table_name} ---")
        print(null_count(df, pk_col))
        print(duplicate(df, pk_col))
