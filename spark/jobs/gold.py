# NOTE : ce script est un job BATCH manuel (relit tout Silver une fois).
# Le pipeline principal (spark/app.py) calcule désormais ces mêmes
# agrégations en continu et les pousse automatiquement dans MinIO/PostgreSQL
# toutes les quelques secondes. Utilise ce script uniquement pour un
# recalcul ponctuel / un backfill manuel :
#   docker exec spark-master spark-submit \
#     --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.7,org.apache.hadoop:hadoop-aws:3.3.4 \
#     /app/spark/jobs/gold.py

from config import (
    SILVER_BUCKET,
    GOLD_BUCKET,
)

from sources.kafka_reader import create_spark_session

from jobs.aggregations import (
    votes_par_candidat,
    votes_par_region,
    votes_par_parti,
    participation_diaspora,
)

from sinks.postgres_writer import write_postgres


def main():

    spark = create_spark_session()

    print("=" * 60)
    print("Construction de la couche GOLD")
    print("=" * 60)

    # =====================================
    # Lecture Silver
    # =====================================

    silver_df = (
        spark.read
        .parquet(f"s3a://{SILVER_BUCKET}/data")
    )

    # =====================================
    # Agrégations
    # =====================================

    candidat_df = votes_par_candidat(silver_df)

    region_df = votes_par_region(silver_df)

    parti_df = votes_par_parti(silver_df)

    diaspora_df = participation_diaspora(silver_df)

    # =====================================
    # Écriture Gold (MinIO)
    # =====================================

    candidat_df.write \
        .mode("overwrite") \
        .parquet(f"s3a://{GOLD_BUCKET}/votes_par_candidat")

    region_df.write \
        .mode("overwrite") \
        .parquet(f"s3a://{GOLD_BUCKET}/votes_par_region")

    parti_df.write \
        .mode("overwrite") \
        .parquet(f"s3a://{GOLD_BUCKET}/votes_par_parti")

    diaspora_df.write \
        .mode("overwrite") \
        .parquet(f"s3a://{GOLD_BUCKET}/participation_diaspora")

    # =====================================
    # PostgreSQL
    # =====================================

    write_postgres(candidat_df, "votes_par_candidat")

    write_postgres(region_df, "votes_par_region")

    write_postgres(parti_df, "votes_par_parti")

    write_postgres(diaspora_df, "participation_diaspora")

    print("=" * 60)
    print("Couche GOLD générée.")
    print("MinIO : OK")
    print("PostgreSQL : OK")
    print("=" * 60)


if __name__ == "__main__":
    main()