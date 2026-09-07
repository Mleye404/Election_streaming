from kafka import KafkaProducer
import json

TOPIC = "votes"

producer = KafkaProducer(
    bootstrap_servers="kafka:9092",
    value_serializer=lambda value: json.dumps(value).encode("utf-8"),
    retries=5
)


def send_vote(vote):

    producer.send(TOPIC, vote)
    producer.flush()

    print(
        f"[{vote['timestamp']}] "
        f"{vote['prenom']} {vote['nom']} | "
        f"{vote['lieu_vote']} | "
        f"{vote['centre_vote']} | "
        f"{vote['bureau_vote']} | "
        f"Vote : {vote['candidat']}"
    )