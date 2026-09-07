FROM eclipse-temurin:17-jdk-jammy

# =====================================
# Dépendances système
# =====================================
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    wget \
    curl \
    procps \
    net-tools \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# =====================================
# Variables d'environnement
# =====================================
ENV SPARK_VERSION=3.5.7
ENV HADOOP_VERSION=3

ENV SPARK_HOME=/opt/spark
ENV PATH=$SPARK_HOME/bin:$SPARK_HOME/sbin:$PATH

ENV PYSPARK_PYTHON=python3
ENV PYSPARK_DRIVER_PYTHON=python3

# =====================================
# Installation Spark
# =====================================
RUN wget -q https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz && \
    tar -xzf spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz && \
    mv spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} ${SPARK_HOME} && \
    rm spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz

# =====================================
# Hadoop AWS + AWS SDK (MinIO / S3A)
# =====================================
RUN wget -P ${SPARK_HOME}/jars \
https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar

RUN wget -P ${SPARK_HOME}/jars \
https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.262/aws-java-sdk-bundle-1.12.262.jar

# =====================================
# PostgreSQL JDBC Driver
# =====================================
RUN wget -P ${SPARK_HOME}/jars \
https://jdbc.postgresql.org/download/postgresql-42.7.4.jar

# =====================================
# Ivy
# =====================================
RUN mkdir -p /root/.ivy2

# =====================================
# Dépendances Python
# =====================================
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# =====================================
# Script de démarrage
# =====================================
COPY scripts/start-spark.sh /start-spark.sh
RUN chmod +x /start-spark.sh

# =====================================
# Répertoire de travail
# =====================================
WORKDIR /app

# =====================================
# Démarrage
# =====================================
CMD ["/start-spark.sh"]