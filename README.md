# Instacart Lakehouse Pipeline

A production-grade lakehouse pipeline built on the Instacart Market Basket dataset. Though it's an old dataset, it was super useful for engineering a real lakehouse at scale — **3.4M orders, 32M order-product rows, 50K products** across 134 aisles and 21 departments.

---

## Architecture

```
Kaggle API
    │
    ▼
dlt (CSV → JSONL → MinIO raw/)
    │
    ▼
Apache Spark + Delta Lake
    ├── Bronze  (raw → typed Delta, audit columns)
    ├── Silver  (dedup, joins, derived flags)
    └── Gold    (5 aggregated analytical tables)
    │
    ▼
PostgreSQL DWH  ←  Spark JDBC
    │
    ▼
dbt  (staging views + mart views + tests)
    │
    ▼
Streamlit Dashboard
```

**Orchestration:** Apache Airflow — `kaggle_ingest` → `instacart_lakehouse_pipeline`  
**Observability:** Prometheus + Grafana (MinIO, PostgreSQL, Spark metrics)  
**CI/CD:** GitHub Actions (ruff, black, dbt build, Docker build)

---

## Tech Stack

| Layer | Tools |
|---|---|
| Ingestion | dltHub, Kaggle API |
| Storage | MinIO (S3-compatible), Delta Lake |
| Processing | Apache Spark 3.5.1, PySpark |
| Warehouse | PostgreSQL 16 |
| Modelling | dbt-core 1.8, dbt-postgres |
| BI | Streamlit, Plotly |
| Orchestration | Apache Airflow 2.9 |
| Observability | Prometheus, Grafana, postgres-exporter |
| CI/CD | GitHub Actions |
| Infrastructure | Docker Compose (9 containers) |

---

## Scale & Metrics

- **32.4M rows** processed through Delta Lake across all layers
- **5 Gold aggregation tables** powering the Streamlit dashboard
- **7 Airflow tasks** running in parallel at the Gold layer
- **45 dbt tests** — 4 singular SQL assertions and schema-level column tests
- **9 Docker containers** in a single Compose stack

---

## Project Structure

```
instacart-lakehouse-pipeline/
├── ingestion/
│   ├── dlt_pipeline/         # dlt source + pipeline entrypoint
│   └── validators/           # pre-load row-count / file-presence checks
├── spark/
│   ├── bronze/               # raw JSONL → typed Delta
│   ├── silver/               # dedup, joins, derived columns
│   └── gold/                 # 5 aggregation scripts + JDBC loader
├── dbt/
│   └── instacart_dwh/
│       ├── models/
│       │   ├── staging/      # views over Gold tables + schema tests
│       │   └── mart/         # business mart views with window functions
│       ├── tests/            # singular SQL assertion tests
│       └── macros/           # data-driven traffic categorisation macro
├── dashboard/
│   └── app.py                # Streamlit 5-page dashboard
├── airflow/
│   └── dags/                 # kaggle_ingest, instacart_lakehouse_pipeline
├── infrastructure/
│   ├── prometheus/           # prometheus.yml scrape config
│   └── grafana/              # auto-provisioned datasource + dashboard
├── .github/
│   └── workflows/ci.yml      # lint + dbt test + docker build
└── docker-compose.yml
```

---

## Quick Start

**Prerequisites:** Docker Desktop, Python 3.11+, Kaggle API key

```bash
# 1. Clone and configure
git clone https://github.com/your-username/instacart-lakehouse-pipeline
cd instacart-lakehouse-pipeline
cp .env.example .env        # fill in KAGGLE_USERNAME and KAGGLE_KEY

# 2. Start the stack
docker compose up --build -d

# 3. Run ingestion (Kaggle → MinIO)
cd ingestion/dlt_pipeline
python kaggle_pipeline.py

# 4. Run Spark transformations
winpty docker exec -it lakehouse-spark-master bash
spark-submit --master spark://spark-master:7077 /opt/spark-apps/bronze/bronze_transform.py
spark-submit --master spark://spark-master:7077 /opt/spark-apps/silver/silver_write.py
spark-submit --master spark://spark-master:7077 /opt/spark-apps/silver/silver_transform.py
spark-submit --master spark://spark-master:7077 /opt/spark-apps/gold/gold_to_postgres.py

# 5. Run dbt models and tests
cd dbt/instacart_dwh
dbt build

# 6. Launch the dashboard
cd dashboard
streamlit run app.py
```

---

## Services

| Service | URL |
|---|---|
| MinIO Console | http://localhost:9001 |
| Spark Master UI | http://localhost:8081 |
| Airflow UI | http://localhost:8080 |
| Streamlit Dashboard | http://localhost:8501 |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3001 |

---

## Key Engineering Decisions

- **Delta Lake MERGE** in Silver — upsert semantics, not blind overwrites
- **Broadcast joins** for small dimension tables (aisles: 134 rows, departments: 21 rows)
- **dlt `write_disposition: replace`** per resource — idempotent full reloads, safe to rerun
- **Spark JDBC** writes Gold Delta → PostgreSQL entirely within the Docker network
- **Data-driven traffic categorisation** in dbt using `percentile_cont` — no hardcoded hour ranges
- **Airflow `SparkSubmitOperator`** with explicit S3A JARs — Spark jobs submitted from Airflow container to the standalone cluster

---

## CI/CD

GitHub Actions runs on every push to `main`:

1. **Lint** — ruff (import order, unused imports) and black (formatting)
2. **dbt build** — full model run and test suite against an ephemeral PostgreSQL service seeded with fixture data
3. **Docker build** — Spark image build with layer caching
