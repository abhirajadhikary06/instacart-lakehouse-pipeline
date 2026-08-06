from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from datetime import datetime

SPARK_CONN = "spark_default"
SPARK_BASE = "/opt/airflow/spark"

with DAG(
    dag_id="silver_dag",
    description="Bronze Delta → Silver Delta (write + enrich/join)",
    start_date=datetime(2026, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["silver", "spark"],
) as dag:

    silver_write = SparkSubmitOperator(
        task_id="silver_write",
        application=f"{SPARK_BASE}/silver/silver_write.py",
        conn_id=SPARK_CONN,
        name="silver_write",
        verbose=False,
    )

    silver_transform = SparkSubmitOperator(
        task_id="silver_transform",
        application=f"{SPARK_BASE}/silver/silver_transform.py",
        conn_id=SPARK_CONN,
        name="silver_transform",
        verbose=False,
    )

    trigger_gold = TriggerDagRunOperator(
        task_id="trigger_gold_dag",
        trigger_dag_id="gold_dag",
        wait_for_completion=False,
    )

    silver_write >> silver_transform >> trigger_gold
