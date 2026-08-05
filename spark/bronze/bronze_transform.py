from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, lit
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, ArrayType  
spark = SparkSession.builder.appName("Bronze Transformation").getOrCreate()

RAW_BASE    = "s3a://raw/instacart"
BRONZE_BASE = "s3a://bronze"

TABLES = {
    "aisles": {
        "schema": StructType([
            StructField("aisle_id", IntegerType(), nullable=False),
            StructField("aisle", StringType(), nullable=False)
        ])
    },
    "products": {
        "schema": StructType([
            StructField("product_id", IntegerType(), nullable=False),
            StructField("product_name", StringType(), nullable=False),
            StructField("aisle_id", IntegerType(), nullable=False),
            StructField("department_id", IntegerType(), nullable=False)
        ])
    },
    "orders": {
        "schema": StructType([
            StructField("order_id", IntegerType(), False),
            StructField("user_id", IntegerType(), False),
            StructField("eval_set", StringType(), False),
            StructField("order_number", IntegerType(), False),
            StructField("order_dow", IntegerType(), False),
            StructField("order_hour_of_day", IntegerType(), False),
            StructField("days_since_prior_order", IntegerType(), True)
        ])
    },
    "departments": {
        "schema": StructType([
            StructField("department_id", IntegerType(), nullable=False),
            StructField("department", StringType(), nullable=False)
        ])
    },
    "order_products__prior": {
        "schema": StructType([
            StructField("order_id", IntegerType(), nullable=False),
            StructField("product_id", IntegerType(), nullable=False),
            StructField("add_to_cart_order", IntegerType(), nullable=False),
            StructField("reordered", IntegerType(), nullable=False)
        ])
    }
}

def read_raw(read_path, table_name):
    return spark.read.schema(TABLES[table_name]["schema"]).json(read_path)

def write_bronze(df, write_path):
    df = df.withColumn("_ingested_at", current_timestamp()) \
           .withColumn("_source", lit("bronze"))
    df.write.format("delta").mode("overwrite").save(write_path)


if __name__ == "__main__":
    for table in TABLES:
        read_path  = f"{RAW_BASE}/{table}/"
        write_path = f"{BRONZE_BASE}/{table}/"
        df = read_raw(read_path, table)
        write_bronze(df, write_path)

