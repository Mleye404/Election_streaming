from faker import Faker
from datetime import datetime
import random
import csv
import os

fake = Faker("fr_FR")

# Les données sont montées dans Docker avec :
# volumes:
#   - ./data:/data
DATA_DIR = "/data"


# ==========================
# Chargement des candidats
# ==========================
def load_candidates():
    with open(os.path.join(DATA_DIR, "candidates.csv"), encoding="utf-8") as file:
        return list(csv.DictReader(file))


# ==========================
# Chargement des centres
# ==========================
def load_centres():
    with open(os.path.join(DATA_DIR, "centres.csv"), encoding="utf-8") as file:
        return list(csv.DictReader(file))


candidates = load_candidates()
centres = load_centres()

used_cni = set()


# ==========================
# Génération CNI unique
# ==========================
def generate_cni():

    while True:

        cni = "".join(random.choices("0123456789", k=13))

        if cni not in used_cni:
            used_cni.add(cni)
            return cni


# ==========================
# Génération d'un vote
# ==========================
def generate_vote():

    centre = random.choice(centres)

    candidate = random.choice(candidates)

    vote = {

        "cni": generate_cni(),

        "nom": fake.last_name(),

        "prenom": fake.first_name(),

        "sexe": random.choice(["Homme", "Femme"]),

        "age": random.randint(18, 95),

        # Champ demandé dans le sujet
        "lieu_vote": centre["region"],

        # Infos supplémentaires pour les statistiques
        "region": centre["region"],

        "departement": centre["departement"],

        "centre_vote": centre["centre_vote"],

        "bureau_vote": centre["bureau_vote"],

        "type_vote": centre["type_vote"],

        "candidat": candidate["nom"],

        "parti": candidate["parti"],

        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    }

    return vote


if __name__ == "__main__":

    for _ in range(5):
        print(generate_vote())