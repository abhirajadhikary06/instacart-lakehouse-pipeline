from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from datetime import datetime
import zipfile
from pathlib import Path

DATASET      = "yasserh/instacart-online-grocery-basket-analysis-dataset"
DOWNLOAD_DIR = Path("/opt/airflow/data/downloads")
STAGING_DIR  = Path("/opt/airflow/data/staging")


def download_from_kaggle():
    import kaggle
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    STAGING_DIR.mkdir(parents=True, exist_ok=True)

    zip_files = list(DOWNLOAD_DIR.glob("*.zip"))
    if zip_files:
        print(f"Zip already present: {zip_files[0]}, skipping download.")
    else:
        kaggle.api.authenticate()
        kaggle.api.dataset_download_files(
            dataset=DATASET,
            path=str(DOWNLOAD_DIR),
            unzip=False,
            quiet=False,
        )

    if not list(STAGING_DIR.glob("*.csv")):
        zip_file = next(DOWNLOAD_DIR.glob("*.zip"))
        with zipfile.ZipFile(zip_file, "r") as zf:
            zf.extractall(STAGING_DIR)
        print("Extraction complete.")
    else:
        print("CSVs already present, skipping extraction.")


def run_dlt_pipeline():
    import sys
    import os
    sys.path.insert(0, "/opt/airflow/ingestion/dlt_pipeline")
    os.chdir("/opt/airflow/ingestion/dlt_pipeline")

    import dlt
    from dlt.sources.filesystem import filesystem, read_csv

    resources = []
    for csv_file in sorted(STAGING_DIR.glob("*.csv")):
        table_name = csv_file.stem
        resource = filesystem(
            bucket_url=STAGING_DIR.as_uri(),
            file_glob=csv_file.name,
        ) | read_csv()
        resource.apply_hints(table_name=table_name)
        resources.append(resource)

    pipeline = dlt.pipeline(
        pipeline_name="instacart_ingestion",
        destination="filesystem",
        dataset_name="instacart",
        pipelines_dir="/opt/airflow/data/.dlt",
    )
    load_info = pipeline.run(resources)
    print(load_info)
    load_info.raise_on_failed_jobs()


with DAG(
    dag_id="kaggle_ingest",
    description="Download Instacart dataset from Kaggle and load to MinIO raw via dlt",
    start_date=datetime(2026, 1, 1),
    schedule_interval="@weekly",
    catchup=False,
    tags=["ingestion", "kaggle", "dlt"],
) as dag:

    download_task = PythonOperator(
        task_id="download_from_kaggle",
        python_callable=download_from_kaggle,
    )

    dlt_task = PythonOperator(
        task_id="dlt_load_to_minio",
        python_callable=run_dlt_pipeline,
    )

    # Trigger the main pipeline DAG once ingestion is complete
    trigger_pipeline = TriggerDagRunOperator(
        task_id="trigger_lakehouse_pipeline",
        trigger_dag_id="instacart_lakehouse_pipeline",
        wait_for_completion=False,  
    )

    download_task >> dlt_task >> trigger_pipeline
