def write_console(df):

    return (
        df.writeStream
          .format("console")
          .outputMode("complete")
          .option("truncate", False)
          .option("numRows", 50)
          .start()
    )