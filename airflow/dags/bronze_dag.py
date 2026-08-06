from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from datetime import datetime

SPARK_CONN = "spark_default"
SPARK_BASE = "/opt/airflow/spark"

with DAG(
    dag_id="bronze_dag",
    description="Read raw JSONL from MinIO and write Delta tables to bronze/",
    start_date=datetime(2026, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["bronze", "spark"],
) as dag:

    bronze_transform = SparkSubmitOperator(
        task_id="bronze_transform",
        application=f"{SPARK_BASE}/bronze/bronze_transform.py",
        conn_id=SPARK_CONN,
        name="bronze_transform",
        verbose=False,
    )

    trigger_silver = TriggerDagRunOperator(
        task_id="trigger_silver_dag",
        trigger_dag_id="silver_dag",
        wait_for_completion=False,
    )

    bronze_transform >> trigger_silver
