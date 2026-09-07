from pyspark.sql import DataFrame


URL = "jdbc:postgresql://postgres:5432/elections"

PROPERTIES = {
    "user": "postgres",
    "password": "postgres",
    "driver": "org.postgresql.Driver"
}


def write_postgres(df: DataFrame, table: str, mode: str = "overwrite"):
    """
    Écrit un DataFrame (batch) dans PostgreSQL.

    En mode "overwrite", on utilise l'option "truncate" pour vider la table
    et réinsérer les données sans la détruire/recréer : ça préserve la
    clé primaire et les types définis dans postgres/init.sql, et c'est
    nécessaire ici car write_postgres est rappelé toutes les quelques
    secondes (foreachBatch) pour rafraîchir les agrégations en temps réel.
    """

    writer = df.write.mode(mode)

    if mode == "overwrite":
        writer = writer.option("truncate", "true")

    writer.jdbc(
        url=URL,
        table=table,
        properties=PROPERTIES
    )
