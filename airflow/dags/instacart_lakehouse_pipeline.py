from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.operators.bash import BashOperator
from datetime import datetime

SPARK_CONN = "spark_default"
SPARK_BASE = "/opt/airflow/spark"
DBT_BASE   = "/opt/airflow/dbt/instacart_dwh"

# S3A JARs pre-installed in the Spark image — required for s3a:// access to MinIO
S3A_JARS = (
    "/opt/spark/jars/hadoop-aws-3.3.4.jar,"
    "/opt/spark/jars/aws-java-sdk-bundle-1.12.262.jar"
)

def spark_op(task_id, script, name):
    return SparkSubmitOperator(
        task_id=task_id,
        application=f"{SPARK_BASE}/{script}",
        conn_id=SPARK_CONN,
        name=name,
        jars=S3A_JARS,
        verbose=False,
    )

with DAG(
    dag_id="instacart_lakehouse_pipeline",
    description="Bronze → Silver → Gold → Postgres → dbt end-to-end pipeline",
    start_date=datetime(2026, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["bronze", "silver", "gold", "dbt", "spark"],
) as dag:

    bronze_transform         = spark_op("bronze_transform", "bronze/bronze_transform.py",       "bronze_transform")
    silver_write             = spark_op("silver_write", "silver/silver_write.py",            "silver_write")
    silver_transform         = spark_op("silver_transform", "silver/silver_transform.py",        "silver_transform")
    gold_product_popularity  = spark_op("gold_product_popularity", "gold/product_popularity.py",        "gold_product_popularity")
    gold_department_summary  = spark_op("gold_department_summary", "gold/department_summary.py",        "gold_department_summary")
    gold_order_time_analysis = spark_op("gold_order_time_analysis", "gold/order_time_analysis.py",       "gold_order_time_analysis")
    gold_aisle_reorder       = spark_op("gold_aisle_reorder", "gold/aisle_reorder_analysis.py",    "gold_aisle_reorder")
    gold_user_behaviour      = spark_op("gold_user_behaviour", "gold/user_order_behaviour.py",      "gold_user_behaviour")
    gold_to_postgres         = spark_op("gold_to_postgres", "gold/gold_to_postgres.py",          "gold_to_postgres")

    dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command=f"cd {DBT_BASE} && dbt build --profiles-dir {DBT_BASE}",
    )

    # Dependencies
    bronze_transform >> silver_write >> silver_transform

    silver_transform >> [
        gold_product_popularity,
        gold_department_summary,
        gold_order_time_analysis,
        gold_aisle_reorder,
        gold_user_behaviour,
    ]

    [
        gold_product_popularity,
        gold_department_summary,
        gold_order_time_analysis,
        gold_aisle_reorder,
        gold_user_behaviour,
    ] >> gold_to_postgres >> dbt_build
