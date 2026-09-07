# Guide d'installation et d'exécution

# Election Streaming --- Suivi des résultats électoraux en temps réel

Ce document explique comment installer et lancer le projet **de bout en
bout**.

Le projet met en place une plateforme de traitement de données
électorales en temps réel :

``` text
Producer → Kafka → Spark Structured Streaming
                         │
                         ├── Bronze → MinIO
                         ├── Silver → MinIO
                         └── Gold → MinIO + PostgreSQL
                                           │
                                           ▼
                                   Dashboard Streamlit
```

Le lancement principal du projet se fait avec le script **`run.sh`**,
qui automatise le démarrage de toute la plateforme.

------------------------------------------------------------------------

## 1. Prérequis

Avant de commencer, il faut avoir installé :

-   Git
-   Docker
-   Docker Compose

Vérifiez l'installation avec :

``` bash
git --version
docker --version
docker compose version
```

Docker doit également être démarré avant de lancer le projet.

Vous pouvez vérifier cela avec :

``` bash
docker info
```

Si cette commande retourne une erreur, démarrez Docker Desktop ou le
service Docker avant de continuer.

------------------------------------------------------------------------

## 2. Récupérer le projet

Clonez le dépôt GitHub :

``` bash
git clone <URL_DU_REPOSITORY>
```

Placez-vous ensuite dans le dossier du projet :

``` bash
cd election-streaming
```

> Remplacez `election-streaming` par le nom réel du dossier créé par
> Git.

------------------------------------------------------------------------

## 3. Vérifier la présence des fichiers

Le dossier principal doit notamment contenir :

``` text
election-streaming/
│
├── docker-compose.yml
├── run.sh
├── README.md
├── installation.md
│
├── dashboard/
├── kafka/
├── postgres/
├── producer/
└── spark/
```

------------------------------------------------------------------------

# 4. Donner les droits d'exécution au script

Sous Linux ou macOS, rendez le script exécutable :

``` bash
chmod +x run.sh
```

Cette commande n'est généralement nécessaire qu'une seule fois.

------------------------------------------------------------------------

# 5. Lancer toute la plateforme

Le moyen recommandé pour démarrer le projet est :

``` bash
./run.sh
```

Le script effectue automatiquement les opérations suivantes :

1.  Vérifie que Docker est démarré.
2.  Construit les images Docker nécessaires.
3.  Démarre tous les services.
4.  Attend que PostgreSQL soit prêt.
5.  Attend que Kafka soit prêt.
6.  Attend que le dashboard Streamlit soit disponible.
7.  Affiche les différentes URLs d'accès.

Les services démarrés sont :

-   Kafka
-   Producer
-   Spark Master
-   Spark Worker
-   PostgreSQL
-   MinIO
-   Dashboard Streamlit

------------------------------------------------------------------------

## 6. Ce que fait exactement `run.sh`

Le script utilise principalement la commande :

``` bash
docker compose up --build -d
```

Cette commande :

-   construit les images nécessaires ;
-   télécharge les images Docker manquantes ;
-   crée les conteneurs ;
-   démarre toute la plateforme en arrière-plan.

Le script attend ensuite que les principaux services soient disponibles
avant de terminer.

------------------------------------------------------------------------

# 7. Vérifier que les conteneurs fonctionnent

Une fois le script terminé, vérifiez l'état de tous les services :

``` bash
docker compose ps
```

ou :

``` bash
docker ps
```

Les services principaux doivent être en état de fonctionnement.

------------------------------------------------------------------------

# 8. Accéder aux interfaces

Après le démarrage, les interfaces suivantes sont disponibles.

  Service               Adresse
  --------------------- -----------------------
  Dashboard Streamlit   http://localhost:8501
  Spark Master UI       http://localhost:8080
  Spark Job UI          http://localhost:4040
  MinIO Console         http://localhost:9001
  PostgreSQL            localhost:5433

### MinIO

Identifiants par défaut :

``` text
Utilisateur : minioadmin
Mot de passe : minioadmin
```

### PostgreSQL

``` text
Host : localhost
Port : 5433
Utilisateur : postgres
Mot de passe : postgres
Base de données : elections
```

> L'interface Spark Job sur le port `4040` est disponible pendant
> l'exécution du job Spark.

------------------------------------------------------------------------

# 9. Vérifier le pipeline de bout en bout

Après le lancement, il est recommandé de vérifier chaque étape de la
chaîne.

## Étape 1 --- Vérifier le Producer

Le Producer génère continuellement des votes et les envoie vers Kafka.

Exécutez :

``` bash
docker logs -f producer
```

Vous devez voir des messages indiquant la génération et l'envoi des
votes.

Pour arrêter l'affichage des logs :

``` text
Ctrl + C
```

------------------------------------------------------------------------

## Étape 2 --- Vérifier Spark Structured Streaming

Spark lit les données depuis Kafka, les transforme et alimente les
différentes couches Bronze, Silver et Gold.

Exécutez :

``` bash
docker logs -f spark-master
```

Vous devez voir le traitement des micro-batchs et les écritures des
données.

------------------------------------------------------------------------

## Étape 3 --- Vérifier PostgreSQL

Les résultats agrégés doivent être enregistrés dans PostgreSQL.

Pour vérifier les votes par candidat :

``` bash
docker exec -it postgres psql -U postgres -d elections -c "SELECT * FROM votes_par_candidat;"
```

Vous pouvez également consulter les autres tables :

### Votes par région

``` bash
docker exec -it postgres psql -U postgres -d elections -c "SELECT * FROM votes_par_region;"
```

### Votes par parti

``` bash
docker exec -it postgres psql -U postgres -d elections -c "SELECT * FROM votes_par_parti;"
```

### Participation nationale et diaspora

``` bash
docker exec -it postgres psql -U postgres -d elections -c "SELECT * FROM participation_diaspora;"
```

Les résultats doivent évoluer au fur et à mesure que Spark traite les
nouveaux votes.

------------------------------------------------------------------------

## Étape 4 --- Vérifier le Dashboard

Ouvrez dans votre navigateur :

``` text
http://localhost:8501
```

Le dashboard affiche uniquement les données réelles provenant de
PostgreSQL.

Il présente notamment :

-   le nombre total de votes ;
-   le nombre de candidats ;
-   le nombre de régions ;
-   le candidat en tête ;
-   le nombre de votes du leader ;
-   les votes par candidat ;
-   le classement des candidats ;
-   les votes par région ;
-   les votes par parti ;
-   la participation nationale et diaspora.

Le dashboard se rafraîchit automatiquement toutes les 3 secondes.

------------------------------------------------------------------------

# 10. Consulter les logs

Voici les principales commandes utiles pour consulter les logs.

### Producer

``` bash
docker logs -f producer
```

### Kafka

``` bash
docker logs -f kafka
```

### Spark

``` bash
docker logs -f spark-master
```

### PostgreSQL

``` bash
docker logs -f postgres
```

### Dashboard

``` bash
docker logs -f dashboard
```

### MinIO

``` bash
docker logs -f minio
```

------------------------------------------------------------------------

# 11. Commandes utiles

## Voir tous les conteneurs

``` bash
docker ps
```

## Voir tous les services du projet

``` bash
docker compose ps
```

## Arrêter temporairement la plateforme

``` bash
docker compose down
```

Cette commande arrête les conteneurs mais conserve les volumes et donc
les données persistantes.

------------------------------------------------------------------------

## Repartir complètement de zéro

``` bash
docker compose down -v
```

Cette commande :

-   arrête les conteneurs ;
-   supprime les volumes ;
-   supprime les données persistantes du projet.

Ensuite, relancez :

``` bash
./run.sh
```

------------------------------------------------------------------------

# 12. Redémarrer la plateforme

Après un arrêt classique :

``` bash
docker compose down
```

Vous pouvez relancer le projet avec :

``` bash
./run.sh
```

------------------------------------------------------------------------

# 13. Démarrage manuel sans `run.sh`

Le script `run.sh` est recommandé car il vérifie automatiquement
plusieurs services.

Cependant, il est également possible de démarrer manuellement avec :

``` bash
docker compose up --build -d
```

Pour suivre les logs de tous les services :

``` bash
docker compose logs -f
```

Pour arrêter :

``` bash
docker compose down
```

------------------------------------------------------------------------

# 14. Dépannage

## Docker n'est pas démarré

Si vous obtenez une erreur liée à Docker :

``` text
Docker n'est pas démarré
```

Démarrez Docker Desktop ou le service Docker.

Puis vérifiez :

``` bash
docker info
```

------------------------------------------------------------------------

## Un service ne démarre pas

Vérifiez l'état des services :

``` bash
docker compose ps
```

Puis consultez les logs du service concerné.

Exemple :

``` bash
docker logs postgres
```

ou :

``` bash
docker logs kafka
```

------------------------------------------------------------------------

## Le dashboard ne s'affiche pas

Vérifiez les logs :

``` bash
docker logs dashboard
```

Puis vérifiez que le port `8501` est accessible :

``` text
http://localhost:8501
```

------------------------------------------------------------------------

## PostgreSQL ne contient pas encore de données

Au démarrage du projet, il faut attendre que :

1.  Kafka soit prêt ;
2.  le Producer envoie les premiers votes ;
3.  Spark traite les micro-batchs ;
4.  les agrégations Gold soient écrites dans PostgreSQL.

Patientez quelques secondes puis relancez la vérification :

``` bash
docker exec -it postgres psql -U postgres -d elections -c "SELECT * FROM votes_par_candidat;"
```

------------------------------------------------------------------------

# 15. Résumé --- Installation rapide

Pour un utilisateur qui possède déjà Docker et Git :

``` bash
# 1. Cloner le projet
git clone <URL_DU_REPOSITORY>

# 2. Entrer dans le projet
cd election-streaming

# 3. Donner les droits d'exécution
chmod +x run.sh

# 4. Lancer toute la plateforme
./run.sh

# 5. Vérifier les services
docker compose ps
```

Puis ouvrir :

``` text
Dashboard : http://localhost:8501
Spark UI : http://localhost:8080
MinIO : http://localhost:9001
```

------------------------------------------------------------------------

# Architecture finale

``` text
                    ┌───────────────┐
                    │   Producer    │
                    │    Votes      │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │     Kafka     │
                    └───────┬───────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │ Spark Structured   │
                 │     Streaming      │
                 └──────────┬──────────┘
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
           Bronze         Silver         Gold
           MinIO          MinIO      MinIO + PostgreSQL
                                               │
                                               ▼
                                      ┌────────────────┐
                                      │   Streamlit    │
                                      │   Dashboard    │
                                      └────────────────┘
```

------------------------------------------------------------------------

**Commande principale du projet :**

``` bash
./run.sh
```

C'est la commande recommandée pour lancer toute la plateforme de
traitement électoral en temps réel.
