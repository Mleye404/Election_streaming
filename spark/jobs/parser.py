from pyspark.sql.functions import col
from pyspark.sql.functions import from_json

from schema import vote_schema


def parse_votes(df):

    return (
        df
        .selectExpr("CAST(value AS STRING) AS value")
        .select(
            from_json(
                col("value"),
                vote_schema
            ).alias("vote")
        )
        .select("vote.*")
    )