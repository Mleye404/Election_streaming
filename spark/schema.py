from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    IntegerType,
)

vote_schema = StructType([

    StructField("cni", StringType(), True),
    StructField("nom", StringType(), True),
    StructField("prenom", StringType(), True),

    StructField("sexe", StringType(), True),
    StructField("age", IntegerType(), True),

    StructField("lieu_vote", StringType(), True),
    StructField("region", StringType(), True),
    StructField("departement", StringType(), True),

    StructField("centre_vote", StringType(), True),
    StructField("bureau_vote", StringType(), True),

    StructField("type_vote", StringType(), True),

    StructField("candidat", StringType(), True),
    StructField("parti", StringType(), True),

    StructField("timestamp", StringType(), True),
])