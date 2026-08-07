from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("Gold to PostgreSQL").getOrCreate()

GOLD_BASE = "s3a://gold"

# PostgreSQL connection
JDBC_URL = "jdbc:postgresql://postgres-dwh:5432/instacart_dwh"
JDBC_PROPS = {"user": "dwh_user", "password": "dwh_password", "driver": "org.postgresql.Driver"}

# Map Gold Delta table path to PostgreSQL table name
GOLD_TABLES = {
    "gold_product_popularity": "gold_product_popularity",
    "gold_department_summary": "gold_department_summary",
    "gold_order_time_analysis": "gold_order_time_analysis",
    "gold_aisle_reorder_analysis": "gold_aisle_reorder_analysis",
    "gold_user_order_behaviour": "gold_user_order_behaviour",
}

for delta_name, pg_table in GOLD_TABLES.items():
    print(f"Loading {delta_name} → postgres:{pg_table} ...")
    df = spark.read.format("delta").load(f"{GOLD_BASE}/{delta_name}")
    df.write.jdbc(url=JDBC_URL, table=pg_table, mode="overwrite", properties=JDBC_PROPS)
    print(f"  Done — {df.count()} rows loaded.")

print("All Gold tables loaded into PostgreSQL.")
