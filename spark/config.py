# =====================================
# Spark
# =====================================

APP_NAME = "ElectionStreaming"

SPARK_MASTER = "spark://spark-master:7077"

CHECKPOINT_LOCATION = "/tmp/checkpoints"

# Fréquence de rafraîchissement des agrégations Gold -> PostgreSQL
AGGREGATION_TRIGGER_INTERVAL = "5 seconds"


# =====================================
# Kafka
# =====================================

KAFKA_BOOTSTRAP_SERVERS = "kafka:9092"

KAFKA_TOPIC = "votes"


# =====================================
# MinIO
# =====================================

MINIO_ENDPOINT = "http://minio:9000"

MINIO_ACCESS_KEY = "minioadmin"

MINIO_SECRET_KEY = "minioadmin"

BRONZE_BUCKET = "bronze"

SILVER_BUCKET = "silver"

GOLD_BUCKET = "gold"