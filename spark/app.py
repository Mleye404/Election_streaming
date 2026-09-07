from config import (
    BRONZE_BUCKET,
    SILVER_BUCKET,
    GOLD_BUCKET,
    CHECKPOINT_LOCATION,
    AGGREGATION_TRIGGER_INTERVAL,
)

from sources.kafka_reader import (
    create_spark_session,
    read_kafka_stream,
)

from jobs.parser import parse_votes
from jobs.transformations import clean_votes
from jobs.aggregations import (
    votes_par_candidat,
    votes_par_region,
    votes_par_parti,
    participation_diaspora,
)

from sinks.minio_writer import write_minio
from sinks.postgres_writer import write_postgres


# =====================================
# Spark
# =====================================

spark = create_spark_session()

print("=" * 60)
print("Election Streaming - pipeline temps réel")
print("=" * 60)

# =====================================
# Lecture Kafka
# =====================================

raw_df = read_kafka_stream(spark)

# =====================================
# Bronze
# =====================================

bronze_df = parse_votes(raw_df)

# =====================================
# Silver
# =====================================

silver_df = clean_votes(bronze_df)

active_queries = []

# =====================================
# Écriture Bronze (MinIO, brut)
# =====================================

active_queries.append(
    write_minio(
        bronze_df,
        BRONZE_BUCKET,
        "data",
        f"{CHECKPOINT_LOCATION}/bronze",
        "append",
    )
)

# =====================================
# Écriture Silver (MinIO, nettoyé)
# =====================================

active_queries.append(
    write_minio(
        silver_df,
        SILVER_BUCKET,
        "data",
        f"{CHECKPOINT_LOCATION}/silver",
        "append",
    )
)


# =====================================
# Gold : agrégations en temps réel
# -> snapshot Parquet dans MinIO
# -> table PostgreSQL rafraîchie à
#    intervalle régulier (par défaut
#    toutes les AGGREGATION_TRIGGER_INTERVAL)
# =====================================

def make_gold_sink(agg_df, table_name: str, checkpoint_suffix: str):
    """
    Attache un foreachBatch à une agrégation streaming (mode "complete") :
    à chaque micro-batch, l'état agrégé complet est réécrit dans MinIO
    (couche Gold) puis dans PostgreSQL, ce qui rend le dashboard "temps réel".
    """

    def save_batch(batch_df, batch_id):
        batch_df.persist()
        nb_lignes = batch_df.count()

        # Snapshot Gold (MinIO)
        (
            batch_df.coalesce(1)
            .write
            .mode("overwrite")
            .parquet(f"s3a://{GOLD_BUCKET}/{table_name}")
        )

        # PostgreSQL (source du dashboard)
        write_postgres(batch_df, table_name)

        batch_df.unpersist()

        print(f"[GOLD] batch {batch_id} -> {table_name} ({nb_lignes} lignes)")

    return (
        agg_df.writeStream
        .foreachBatch(save_batch)
        .outputMode("complete")
        .option("checkpointLocation", f"{CHECKPOINT_LOCATION}/gold_{checkpoint_suffix}")
        .trigger(processingTime=AGGREGATION_TRIGGER_INTERVAL)
        .start()
    )


active_queries.append(
    make_gold_sink(votes_par_candidat(silver_df), "votes_par_candidat", "candidat")
)
active_queries.append(
    make_gold_sink(votes_par_region(silver_df), "votes_par_region", "region")
)
active_queries.append(
    make_gold_sink(votes_par_parti(silver_df), "votes_par_parti", "parti")
)
active_queries.append(
    make_gold_sink(participation_diaspora(silver_df), "participation_diaspora", "diaspora")
)

print("Pipeline démarré :")
print("  Kafka -> Bronze/Silver (MinIO, append)")
print(f"  Kafka -> Gold (MinIO + PostgreSQL, rafraîchi toutes les {AGGREGATION_TRIGGER_INTERVAL})")

# =====================================
# Attente : le driver reste vivant tant
# qu'une des requêtes streaming tourne
# =====================================

spark.streams.awaitAnyTermination()
