# Spark standalone image (master + worker share this image) with Delta Lake
# and the Hadoop S3A connector pre-installed so Spark can talk to MinIO.

FROM eclipse-temurin:17-jre-jammy

ARG SPARK_VERSION=3.5.1
ARG HADOOP_VERSION=3
ARG DELTA_VERSION=3.2.0
ARG SCALA_VERSION=2.12
ARG HADOOP_AWS_VERSION=3.3.4
ARG AWS_SDK_VERSION=1.12.262

ENV SPARK_HOME=/opt/spark \
    PATH=/opt/spark/bin:/opt/spark/sbin:$PATH \
    PYSPARK_PYTHON=python3

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl python3 python3-pip procps && \
    rm -rf /var/lib/apt/lists/*

# --- Spark ---
RUN curl -fsSL "https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz" \
    -o /tmp/spark.tgz && \
    tar -xzf /tmp/spark.tgz -C /opt && \
    mv /opt/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} /opt/spark && \
    rm /tmp/spark.tgz

# --- Delta Lake jars ---
RUN curl -fsSL "https://repo1.maven.org/maven2/io/delta/delta-spark_${SCALA_VERSION}/${DELTA_VERSION}/delta-spark_${SCALA_VERSION}-${DELTA_VERSION}.jar" \
    -o /opt/spark/jars/delta-spark_${SCALA_VERSION}-${DELTA_VERSION}.jar && \
    curl -fsSL "https://repo1.maven.org/maven2/io/delta/delta-storage/${DELTA_VERSION}/delta-storage-${DELTA_VERSION}.jar" \
    -o /opt/spark/jars/delta-storage-${DELTA_VERSION}.jar

# --- Hadoop S3A connector (lets Spark read/write MinIO via s3a://) ---
RUN curl -fsSL "https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/${HADOOP_AWS_VERSION}/hadoop-aws-${HADOOP_AWS_VERSION}.jar" \
    -o /opt/spark/jars/hadoop-aws-${HADOOP_AWS_VERSION}.jar && \
    curl -fsSL "https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/${AWS_SDK_VERSION}/aws-java-sdk-bundle-${AWS_SDK_VERSION}.jar" \
    -o /opt/spark/jars/aws-java-sdk-bundle-${AWS_SDK_VERSION}.jar

COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Default Spark conf: Delta SQL extensions + MinIO (S3A) endpoint, filled in
# from environment variables at container start via spark-defaults.conf.template
COPY spark-defaults.conf.template /opt/spark/conf/spark-defaults.conf.template
COPY entrypoint.sh /opt/entrypoint.sh
RUN chmod +x /opt/entrypoint.sh

WORKDIR /opt/spark-apps

ENTRYPOINT ["/opt/entrypoint.sh"]
CMD ["bash"]
