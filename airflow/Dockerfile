FROM apache/airflow:2.9.3-python3.11

ARG SPARK_VERSION=3.5.1
ARG HADOOP_VERSION=3

USER root

# Java is required by the SparkSubmitOperator / local spark-submit client,
# curl/procps are convenience utilities.
RUN apt-get update && \
    apt-get install -y --no-install-recommends openjdk-17-jre-headless curl procps && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64 \
    SPARK_HOME=/opt/spark \
    PATH=/opt/spark/bin:$PATH

# Lightweight local Spark client so SparkSubmitOperator can shell out to
# `spark-submit` and hand the job off to the spark-master service over the
# network (spark://spark-master:7077).
RUN curl -fsSL "https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz" \
    -o /tmp/spark.tgz && \
    tar -xzf /tmp/spark.tgz -C /opt && \
    mv /opt/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} /opt/spark && \
    rm /tmp/spark.tgz && \
    chown -R airflow:root /opt/spark

USER airflow

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt
