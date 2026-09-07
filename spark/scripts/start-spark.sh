#!/bin/bash

set -e

echo "===================================="
echo "        Spark starting..."
echo "Mode : $SPARK_MODE"
echo "===================================="

PACKAGES="org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.7,org.apache.hadoop:hadoop-aws:3.3.4"

if [ "$SPARK_MODE" = "master" ]; then

    echo "Starting Spark Master..."

    $SPARK_HOME/sbin/start-master.sh

    echo "Waiting Spark Master..."
    sleep 10

    echo "Starting Streaming Pipeline..."

    spark-submit \
        --master spark://spark-master:7077 \
        --packages $PACKAGES \
        /app/spark/app.py

    echo "Spark application stopped."

    tail -f /dev/null

elif [ "$SPARK_MODE" = "worker" ]; then

    echo "Starting Spark Worker..."

    $SPARK_HOME/sbin/start-worker.sh spark://spark-master:7077

    tail -f $SPARK_HOME/logs/*

else

    echo "Unknown mode : $SPARK_MODE"
    exit 1

fi