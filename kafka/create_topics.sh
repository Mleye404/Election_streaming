#!/bin/bash
# Crée le topic Kafka "votes" explicitement.
# Non indispensable : KAFKA_AUTO_CREATE_TOPICS_ENABLE=true dans docker-compose.yml
# crée déjà le topic automatiquement au premier message envoyé.
# Utile si tu veux fixer le nombre de partitions/replicas manuellement.

set -e

docker exec kafka /opt/kafka/bin/kafka-topics.sh \
    --create \
    --if-not-exists \
    --topic votes \
    --bootstrap-server localhost:9092 \
    --partitions 3 \
    --replication-factor 1

docker exec kafka /opt/kafka/bin/kafka-topics.sh \
    --list \
    --bootstrap-server localhost:9092
