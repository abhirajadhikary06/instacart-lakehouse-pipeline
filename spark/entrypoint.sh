#!/usr/bin/env bash
set -euo pipefail

# Render spark-defaults.conf from the template using current env vars.
sed \
  -e "s|__MINIO_ENDPOINT__|${MINIO_ENDPOINT:-http://minio:9000}|g" \
  -e "s|__MINIO_ROOT_USER__|${MINIO_ROOT_USER:-minioadmin}|g" \
  -e "s|__MINIO_ROOT_PASSWORD__|${MINIO_ROOT_PASSWORD:-minioadmin123}|g" \
  /opt/spark/conf/spark-defaults.conf.template > /opt/spark/conf/spark-defaults.conf

exec "$@"
