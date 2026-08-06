from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.operators.bash import BashOperator
from datetime import datetime

SPARK_CONN = "spark_default"
SPARK_BASE = "/opt/airflow/spark"
DBT_BASE   = "/opt/airflow/dbt/instacart_dwh"

with DAG(
    dag_id="gold_dag",
    description="Silver Delta → Gold aggregations → PostgreSQL → dbt build",
    start_date=datetime(2026, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["gold", "spark", "dbt"],
) as dag:

    # 5 gold aggregation jobs — run in parallel
    gold_product_popularity = SparkSubmitOperator(
        task_id="gold_product_popularity",
        application=f"{SPARK_BASE}/gold/product_popularity.py",
        conn_id=SPARK_CONN,
        name="gold_product_popularity",
        verbose=False,
    )

    gold_department_summary = SparkSubmitOperator(
        task_id="gold_department_summary",
        application=f"{SPARK_BASE}/gold/department_summary.py",
        conn_id=SPARK_CONN,
        name="gold_department_summary",
        verbose=False,
    )

    gold_order_time_analysis = SparkSubmitOperator(
        task_id="gold_order_time_analysis",
        application=f"{SPARK_BASE}/gold/order_time_analysis.py",
        conn_id=SPARK_CONN,
        name="gold_order_time_analysis",
        verbose=False,
    )

    gold_aisle_reorder_analysis = SparkSubmitOperator(
        task_id="gold_aisle_reorder_analysis",
        application=f"{SPARK_BASE}/gold/aisle_reorder_analysis.py",
        conn_id=SPARK_CONN,
        name="gold_aisle_reorder_analysis",
        verbose=False,
    )

    gold_user_order_behaviour = SparkSubmitOperator(
        task_id="gold_user_order_behaviour",
        application=f"{SPARK_BASE}/gold/user_order_behaviour.py",
        conn_id=SPARK_CONN,
        name="gold_user_order_behaviour",
        verbose=False,
    )

    # Load all gold Delta tables into PostgreSQL
    gold_to_postgres = SparkSubmitOperator(
        task_id="gold_to_postgres",
        application=f"{SPARK_BASE}/gold/gold_to_postgres.py",
        conn_id=SPARK_CONN,
        name="gold_to_postgres",
        verbose=False,
    )

    # dbt build — staging and mart models and tests
    dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command=f"cd {DBT_BASE} && dbt build --profiles-dir {DBT_BASE}",
    )

    # All 5 gold jobs run in parallel, then postgres, then dbt
    [
        gold_product_popularity,
        gold_department_summary,
        gold_order_time_analysis,
        gold_aisle_reorder_analysis,
        gold_user_order_behaviour,
    ] >> gold_to_postgres >> dbt_build
