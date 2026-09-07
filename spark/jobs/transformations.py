from pyspark.sql.functions import col


def clean_votes(df):

    return (
        df

        # Âge valide
        .filter(col("age").between(18, 120))

        # Champs obligatoires
        .filter(col("cni").isNotNull())
        .filter(col("nom").isNotNull())
        .filter(col("prenom").isNotNull())
        .filter(col("candidat").isNotNull())
        .filter(col("region").isNotNull())
        .filter(col("type_vote").isNotNull())

        # Types de vote autorisés
        .filter(col("type_vote").isin("National", "Diaspora"))

        # Un seul vote par CNI
        .dropDuplicates(["cni"])
    )