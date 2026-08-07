import zipfile
from pathlib import Path

import dlt
from dlt.sources.filesystem import filesystem, read_csv
from dotenv import load_dotenv

load_dotenv()

# Dataset config 
KAGGLE_DATASET = "yasserh/instacart-online-grocery-basket-analysis-dataset"
DOWNLOAD_DIR   = Path(__file__).resolve().parents[2] / "data" / "downloads"
STAGING_DIR    = Path(__file__).resolve().parents[2] / "data" / "staging"

# Downloading dataset to local directory
def download_dataset() -> None:
    import kaggle

    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    STAGING_DIR.mkdir(parents=True, exist_ok=True)

    zip_files = list(DOWNLOAD_DIR.glob("*.zip"))
    if zip_files:
        print(f"Zip already present at {zip_files[0]}, skipping download.")
    else:
        print(f"Downloading {KAGGLE_DATASET} ...")
        kaggle.api.authenticate()
        kaggle.api.dataset_download_files(
            dataset=KAGGLE_DATASET,
            path=str(DOWNLOAD_DIR),
            unzip=False,
            quiet=False,
        )

    # Zip Extraction
    if not list(STAGING_DIR.glob("*.csv")):
        zip_file = next(DOWNLOAD_DIR.glob("*.zip"))
        print(f"Extracting {zip_file.name} → {STAGING_DIR}")
        with zipfile.ZipFile(zip_file, "r") as zf:
            zf.extractall(STAGING_DIR)
        print("Extraction done.")
    else:
        print("CSVs already extracted, skipping.")

# Loading data from local to MinIO
def run_pipeline() -> None:
    pipeline = dlt.pipeline(
        pipeline_name="instacart_ingestion",
        destination="filesystem",
        dataset_name="instacart",
    )

    resources = []
    for csv_file in sorted(STAGING_DIR.glob("*.csv")):
        table_name = csv_file.stem
        resource = filesystem(
            bucket_url=STAGING_DIR.as_uri(),
            file_glob=csv_file.name,
        ) | read_csv()
        resource.apply_hints(table_name=table_name)
        resources.append(resource)

    print("Running dlt pipeline ...")
    load_info = pipeline.run(resources)
    print(load_info)


if __name__ == "__main__":
    download_dataset()  
    run_pipeline()      
