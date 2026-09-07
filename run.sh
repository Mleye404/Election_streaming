#!/bin/bash
# =====================================
# Election Streaming — lancement complet
# Kafka + Producer + Spark + PostgreSQL + MinIO + Dashboard
# =====================================
set -e
cd "$(dirname "$0")"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

step() { echo -e "\n${YELLOW}==> $1${NC}"; }
ok()   { echo -e "${GREEN}✓ $1${NC}"; }
fail() { echo -e "${RED}✗ $1${NC}"; exit 1; }

# =====================================
# 1. Docker actif ?
# =====================================
step "Vérification de Docker"
docker info > /dev/null 2>&1 || fail "Docker n'est pas démarré. Lance Docker Desktop (ou le service Docker) puis relance ce script."
ok "Docker est actif"

# =====================================
# 2. Build + démarrage de tous les services
# =====================================
step "Construction des images et démarrage des services"
docker compose up --build -d
ok "Conteneurs démarrés (kafka, producer, spark-master, spark-worker, postgres, minio, dashboard)"

# =====================================
# 3. Attente PostgreSQL
# =====================================
step "Attente de PostgreSQL"
ready=false
for i in $(seq 1 30); do
    if docker exec postgres pg_isready -U postgres > /dev/null 2>&1; then
        ready=true
        break
    fi
    sleep 2
done
$ready && ok "PostgreSQL prêt" || fail "PostgreSQL n'a pas répondu à temps. Vérifie : docker logs postgres"

# =====================================
# 4. Attente Kafka
# =====================================
step "Attente de Kafka"
ready=false
for i in $(seq 1 30); do
    if docker exec kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --list > /dev/null 2>&1; then
        ready=true
        break
    fi
    sleep 2
done
$ready && ok "Kafka prêt" || fail "Kafka n'a pas répondu à temps. Vérifie : docker logs kafka"

# =====================================
# 5. Attente du dashboard (Streamlit)
# =====================================
step "Attente du dashboard Streamlit"
ready=false
for i in $(seq 1 40); do
    if curl -sf http://localhost:8501/_stcore/health > /dev/null 2>&1; then
        ready=true
        break
    fi
    sleep 2
done
if $ready; then
    ok "Dashboard prêt"
else
    echo -e "${YELLOW}Le dashboard met plus de temps que prévu à répondre.${NC}"
    echo -e "${YELLOW}Vérifie : docker logs dashboard${NC}"
fi

# =====================================
# Résumé
# =====================================
step "Plateforme démarrée"
cat << URLS

  Dashboard (Streamlit)   -> http://localhost:8501
  Spark Master UI         -> http://localhost:8080
  MinIO Console           -> http://localhost:9001  (minioadmin / minioadmin)
  PostgreSQL              -> localhost:5433  (postgres / postgres, base : elections)

Logs utiles :
  docker logs -f producer       # votes générés
  docker logs -f spark-master   # traitement Spark + écritures Gold
  docker logs -f dashboard      # dashboard Streamlit

Vérifier les données dans PostgreSQL :
  docker exec -it postgres psql -U postgres -d elections -c "SELECT * FROM votes_par_candidat;"

Arrêter :
  docker compose down          # garde les données (volumes conservés)
  docker compose down -v       # supprime aussi les volumes (repart de zéro)

URLS
