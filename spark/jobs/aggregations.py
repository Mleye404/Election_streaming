from pyspark.sql.functions import count


def votes_par_candidat(df):
    return (
        df.groupBy("candidat")
        .agg(count("*").alias("nombre_votes"))
        .orderBy("nombre_votes", ascending=False)
    )


def votes_par_region(df):
    return (
        df.groupBy("region")
        .agg(count("*").alias("nombre_votes"))
        .orderBy("nombre_votes", ascending=False)
    )


def votes_par_parti(df):
    return (
        df.groupBy("parti")
        .agg(count("*").alias("nombre_votes"))
        .orderBy("nombre_votes", ascending=False)
    )


def participation_diaspora(df):
    return (
        df.groupBy("type_vote")
        .agg(count("*").alias("nombre_votes"))
        .orderBy("nombre_votes", ascending=False)
    )