# Instacart Lakehouse Platform

## Objective

Build a production-grade batch data platform using Apache Spark and
Delta Lake following modern lakehouse principles. The emphasis is on
engineering reliable, observable, configurable, and maintainable
pipelines.

## Technology Stack

-   Apache Spark
-   Delta Lake
-   **dlt (data load tool)** — ingestion: extract, schema inference, and
    load into the raw bucket
-   Apache Airflow
-   MinIO (Data Lake)
-   PostgreSQL (Serving/Data Mart)
-   dbt
-   Metabase
-   Prometheus
-   Grafana
-   Docker Compose
-   GitHub Actions
-   Kaggle API (dataset acquisition)

# High-Level Architecture

``` text
Kaggle API
    │
Kaggle Downloader (auth + download + extract)
    │
    ▼
Temporary Download (local staging)
    │
    ▼
Row-Count Validation
    │
    ▼
dlt Pipeline (schema inference + load, Parquet)
    │
    ▼
MinIO Raw Bucket
    │
    ▼
Spark Bronze (Delta)
    │
    ▼
Spark Silver (Delta)
    │
    ▼
Spark Gold (Delta)
    │
    ▼
dbt
    │
    ▼
PostgreSQL
    │
    ▼
Metabase

Monitoring:
Prometheus + Grafana

Orchestration:
Airflow

CI/CD:
GitHub Actions
```

# Phases

## Phase 0 Infrastructure

Goal: Dockerized environment with Spark, Airflow, MinIO, PostgreSQL,
Metabase, Prometheus, Grafana.

## Phase 1 Dataset Acquisition

Goal: Automatically download with Kaggle API, validate, and load into the
MinIO raw bucket via a **dlt** pipeline (schema inference, audit columns,
idempotent load packages).

## Phase 2 Bronze

Goal: Parquet (dlt-loaded) → Delta, schema enforcement, audit columns,
ingestion metadata. Bronze carries forward dlt's `_dlt_load_id` /
`_dlt_id` columns (or maps them onto the platform's own audit-column
convention) so lineage from raw load through to Bronze is unbroken.

## Phase 3 Silver

Goal: Cleansing, joins, deduplication, validation, reusable Spark
transformations.

## Phase 4 Gold

Goal: Business-ready analytical tables.

## Phase 5 Incremental Processing

Goal: Idempotent loads, watermarking, Delta MERGE.

## Phase 6 Delta Lake Features

Goal: UPDATE, DELETE, MERGE, Time Travel, VACUUM, Schema Evolution.

## Phase 7 Spark Optimization

Goal: AQE, caching, explain plans, partitioning, broadcast joins,
benchmarking.

## Phase 8 Airflow

Goal: Production DAGs, retries, alerts, scheduling, backfills.

## Phase 9 dbt

Goal: Business models, tests, lineage, documentation.

## Phase 10 Serving

Goal: Load curated models into PostgreSQL.

## Phase 11 BI

Goal: Executive dashboards in Metabase.

## Phase 12 Observability

Goal: Metrics, logs, audit tables, Grafana dashboards.

## Phase 13 Testing

Goal: Unit, integration, Spark, dbt and data quality tests.

## Phase 14 CI/CD

Goal: Automated linting, tests and Docker builds.

## Phase 15 Documentation

Goal: Architecture, setup, design decisions, troubleshooting.

# Repository Structure

``` text
instacart-lakehouse-pipeline/
│
├── airflow/
│   ├── dags/
│   ├── plugins/
│   ├── include/
│   └── logs/
│
├── spark/
│   ├── bronze/
│   ├── silver/
│   ├── gold/
│   ├── common/
│   ├── configs/
│   └── tests/
│
├── ingestion/
│   ├── kaggle/          # Kaggle API auth + dataset download/extract
│   ├── dlt_pipeline/     # dlt resources/source + pipeline entrypoint + .dlt config
│   └── validators/       # pre-load row-count / file-presence checks
│
├── dbt/
├── infrastructure/
│   ├── docker/
│   ├── minio/
│   ├── postgres/
│   ├── prometheus/
│   └── grafana/
│
├── monitoring/
├── scripts/
├── configs/
├── docs/
├── tests/
├── data/
│   ├── downloads/
│   └── staging/
│
├── .github/
│   └── workflows/
│
├── docker-compose.yml
├── requirements.txt
├── README.md
└── .env.example
```

## Production Principles

-   Immutable raw data
-   Configuration-driven pipelines
-   Audit logging (dlt load-id lineage from raw through Bronze)
-   Data quality validation
-   Idempotent processing (dlt load packages + Delta MERGE)
-   Schema evolution & contracts (dlt-inferred schema, versioned)
-   Layer separation
-   Observability
-   Automated CI/CD
-   Reproducible local environment
