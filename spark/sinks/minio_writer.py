from pyspark.sql import DataFrame


def write_minio(df: DataFrame, bucket: str, folder: str, checkpoint: str, output_mode: str = "append"):
    """
    Écrit un stream Spark vers MinIO (S3A) au format Parquet.

    - bucket / folder : destination s3a://{bucket}/{folder}
    - checkpoint       : dossier de checkpoint Spark (obligatoire en streaming)
    - output_mode      : "append" pour Bronze/Silver (écriture incrémentale)
    """

    return (
        df.writeStream
        .format("parquet")
        .option("path", f"s3a://{bucket}/{folder}")
        .option("checkpointLocation", checkpoint)
        .outputMode(output_mode)
        .start()
    )
