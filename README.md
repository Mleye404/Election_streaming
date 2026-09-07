# Election Streaming — Suivi des résultats électoraux en temps réel

Pipeline de Data Engineering en streaming : des votes sont générés en continu,
envoyés dans Kafka, traités par Spark Structured Streaming (Bronze → Silver →
Gold), agrégés puis poussés dans PostgreSQL. Un dashboard Streamlit affiche
ces résultats et se rafraîchit automatiquement toutes les 3 secondes.

```
Producer (votes) → Kafka → Spark Structured Streaming
                              ├─ Bronze  (MinIO, brut)
                              ├─ Silver  (MinIO, nettoyé)
                              └─ Gold    (MinIO snapshot + PostgreSQL, ~toutes les 5s)
                                              ↓
                                   Dashboard Streamlit (auto-refresh)
```

## Démarrage

```bash
./run.sh
```

Ce script construit les images, démarre tous les services (`kafka`,
`producer`, `spark-master`, `spark-worker`, `postgres`, `minio`, `dashboard`),
attend que PostgreSQL, Kafka et le dashboard soient réellement prêts, puis
affiche les URLs d'accès.

Équivalent manuel, sans les vérifications :

```bash
docker compose up --build
```

## Accès

| Service              | URL                                      |
|-----------------------|-------------------------------------------|
| **Dashboard**         | http://localhost:8501                    |
| Spark Master UI       | http://localhost:8080                    |
| Spark Job UI          | http://localhost:4040 (pendant l'exécution du job) |
| MinIO Console         | http://localhost:9001 (`minioadmin` / `minioadmin`) |
| PostgreSQL            | `localhost:5433` (`postgres` / `postgres`, base `elections`) |

## Vérifier que la chaîne fonctionne de bout en bout

```bash
# 1. Le producer génère des votes
docker logs -f producer

# 2. Spark tourne et traite le flux
docker logs -f spark-master

# 3. Les tables PostgreSQL se remplissent
docker exec -it postgres psql -U postgres -d elections -c "SELECT * FROM votes_par_candidat;"

# 4. Le dashboard affiche les vraies données et se met à jour
# -> http://localhost:8501, regarder les chiffres évoluer toutes les ~5-10s
```

Arrêter la plateforme :

```bash
docker compose down        # garde les données (volumes conservés)
docker compose down -v     # supprime aussi les volumes (repart de zéro)
```

## Ce qui a été corrigé dans le pipeline existant

Le pipeline Bronze/Silver fonctionnait, mais la chaîne s'arrêtait avant
PostgreSQL. Les correctifs apportés :

- **`spark/sinks/minio_writer.py`** contenait par erreur une copie du contenu
  de `app.py` (y compris un import circulaire de lui-même) au lieu de la
  fonction `write_minio`. C'était le premier point de blocage : plus rien
  n'était écrit dans MinIO. Le fichier contient maintenant la vraie fonction.
- **Imports incohérents** : certains fichiers (`kafka_reader.py`, `parser.py`,
  `gold.py`) utilisaient des imports absolus `from spark.xxx import ...`, qui
  échouent (`ModuleNotFoundError`) car `/app` n'est pas sur le `PYTHONPATH` du
  conteneur Spark. `app.py` utilisait déjà des imports relatifs qui, eux,
  fonctionnent (spark-submit ajoute automatiquement `/app/spark` au path).
  Tous les imports ont été harmonisés sur ce style relatif.
- **La couche Gold n'était jamais exécutée** : `spark/jobs/gold.py` est un
  script batch autonome avec un `if __name__ == "__main__"`, mais rien ne
  l'appelait — ni `app.py`, ni le `docker-compose.yml`, ni de cron. Résultat :
  les tables PostgreSQL restaient vides. `app.py` calcule maintenant les
  agrégations Gold directement en streaming (`outputMode("complete")` +
  `foreachBatch`) et les pousse vers MinIO et PostgreSQL toutes les
  `AGGREGATION_TRIGGER_INTERVAL` (5 secondes par défaut, configurable dans
  `spark/config.py`). `jobs/gold.py` reste disponible comme script de
  backfill manuel si besoin, mais n'est plus requis pour le fonctionnement
  temps réel.
- **`postgres_writer.py`** écrit maintenant avec `.option("truncate", "true")`
  en mode overwrite, pour vider/réinsérer sans supprimer la table (et donc
  garder la clé primaire définie dans `postgres/init.sql`) à chaque
  rafraîchissement.

## Le dashboard (`dashboard/`)

- Se connecte directement à PostgreSQL (`votes_par_candidat`,
  `votes_par_region`, `votes_par_parti`, `participation_diaspora`) — aucune
  donnée fictive.
- Auto-refresh toutes les 3 secondes (`streamlit-autorefresh`).
- Affiche : total des votes, nombre de candidats, nombre de régions,
  candidat en tête et son nombre de votes, classement, votes par candidat
  (graphique), votes par région, votes par parti, participation
  nationale/diaspora, badge `LIVE`.
- Si les tables sont vides ou PostgreSQL n'est pas encore prêt, un message
  clair l'indique au lieu d'afficher une erreur ou des données inventées —
  la page se remet à jour automatiquement dès que les données arrivent.

## Notes

- Le dossier `backend/` (API FastAPI) du projet original a été retiré : le
  dashboard lit PostgreSQL directement, ce qui est plus simple et plus
  stable pour ce cas d'usage et évite une couche intermédiaire inutile.
- Pour changer la fréquence de rafraîchissement des agrégations Spark :
  `AGGREGATION_TRIGGER_INTERVAL` dans `spark/config.py`.
- Pour changer la fréquence de rafraîchissement du dashboard :
  `REFRESH_MS` dans `dashboard/app.py`.
