from pyspark.sql import DataFrame


def write_gold(df: DataFrame, bucket, folder, checkpoint):

    def save_batch(batch_df, batch_id):
        print(f"Writing batch {batch_id} -> {folder}")

        (
            batch_df.coalesce(1)
            .write
            .mode("overwrite")
            .parquet(f"s3a://{bucket}/{folder}")
        )

        print(f"Batch {batch_id} written.")

    return (
        df.writeStream
        .foreachBatch(save_batch)
        .outputMode("complete")
        .option("checkpointLocation", checkpoint)
        .start()
    )