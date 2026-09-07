Oui mec, exactement 👌🔥

**`installation.md`** = comment installer et lancer le projet, commandes détaillées.

**`README.md`** = la vitrine du projet sur GitHub. Il doit expliquer rapidement :

* 🎯 le problème / objectif ;
* 🏗️ l'architecture ;
* 🔄 le pipeline ;
* 🛠️ les technologies ;
* 📊 les fonctionnalités ;
* 🔒 éventuellement les aspects de fiabilité/sécurité ;
* 🚀 comment démarrer rapidement ;
* 📁 la structure du projet.

Je te conseille de ne pas faire un README trop long, parce que tu as déjà `installation.md` pour les détails d'installation.

Voici une version propre que tu peux **copier-coller directement dans GitHub** 👇

---

# 🗳️ Election Streaming — Real-Time Data Pipeline

## 📌 Présentation

**Election Streaming** est une plateforme de traitement et de visualisation de données électorales en temps réel.

Le projet simule un flux continu de votes et met en place une architecture **Big Data Streaming** permettant de collecter, traiter, stocker et visualiser les résultats électoraux en temps réel.

L'objectif principal est de démontrer la mise en œuvre d'un pipeline complet basé sur des technologies de streaming et de traitement distribué.

---

## 🎯 Objectifs

Le projet permet de :

* 📥 Simuler un flux continu de votes électoraux ;
* 🚀 Transporter les événements en temps réel avec Kafka ;
* ⚡ Traiter les données avec Spark Structured Streaming ;
* 🗄️ Stocker les données selon une architecture Bronze / Silver / Gold ;
* ☁️ Utiliser MinIO comme Data Lake ;
* 🐘 Alimenter PostgreSQL avec les résultats agrégés ;
* 📊 Visualiser les résultats en temps réel à travers un dashboard Streamlit.

---

# 🏗️ Architecture

```text
                        ┌─────────────────┐
                        │    PRODUCER     │
                        │ Votes simulés   │
                        └────────┬────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │      KAFKA      │
                        │ Streaming Layer │
                        └────────┬────────┘
                                 │
                                 ▼
                  ┌─────────────────────────┐
                  │          SPARK          │
                  │  Structured Streaming   │
                  └────────────┬────────────┘
                               │
                 ┌─────────────┼─────────────┐
                 │             │             │
                 ▼             ▼             ▼
             🥉 BRONZE      🥈 SILVER      🥇 GOLD
              MinIO          MinIO          MinIO
                                              │
                                              ▼
                                      ┌───────────────┐
                                      │  PostgreSQL   │
                                      │  Aggregations │
                                      └───────┬───────┘
                                              │
                                              ▼
                                      ┌───────────────┐
                                      │   Streamlit   │
                                      │   Dashboard   │
                                      └───────────────┘
```

---

# 🔄 Pipeline de traitement

Le pipeline fonctionne selon les étapes suivantes :

### 1️⃣ Génération des votes

Un **Producer Python** simule en continu des événements électoraux.

Chaque vote contient des informations telles que :

* Candidat ;
* Parti politique ;
* Région ;
* Type de vote ;
* Horodatage.

Les événements sont envoyés vers Kafka.

---

### 2️⃣ Streaming avec Kafka

Kafka joue le rôle de plateforme de messagerie et transporte les événements entre les différentes composantes du pipeline.

```text
Producer → Kafka Topic → Spark
```

Kafka permet de gérer le flux continu des votes avant leur traitement.

---

### 3️⃣ Traitement avec Spark Structured Streaming

Spark Structured Streaming consomme les événements provenant de Kafka et réalise les différentes transformations.

Le pipeline permet notamment :

* la lecture des événements ;
* la transformation des données ;
* l'agrégation des votes ;
* le calcul des résultats par candidat ;
* le calcul des résultats par région ;
* le calcul des résultats par parti ;
* le calcul de la participation nationale et diaspora.

---

# 🗄️ Architecture Medallion

Les données sont organisées selon une architecture **Bronze / Silver / Gold**.

```text
Kafka
  │
  ▼
┌───────────────┐
│    BRONZE     │
│ Raw Data      │
│    MinIO      │
└───────┬───────┘
        │
        ▼
┌───────────────┐
│    SILVER     │
│ Clean Data    │
│    MinIO      │
└───────┬───────┘
        │
        ▼
┌───────────────┐
│     GOLD      │
│ Aggregations  │
│ MinIO + PostgreSQL │
└───────────────┘
```

### 🥉 Bronze

Stockage des données brutes provenant du flux Kafka.

### 🥈 Silver

Nettoyage et transformation des données.

### 🥇 Gold

Données agrégées et prêtes à être utilisées pour l'analyse et la visualisation.

Les résultats Gold sont également stockés dans **PostgreSQL** afin d'alimenter le dashboard.

---

# 📊 Dashboard temps réel

Le dashboard est développé avec **Streamlit**.

Il permet de visualiser en temps réel :

* 🗳️ Le nombre total de votes ;
* 👥 Le nombre de candidats ;
* 📍 Le nombre de régions ;
* 🏆 Le candidat actuellement en tête ;
* 📊 Les votes par candidat ;
* 🥇 Le classement des candidats ;
* 🗺️ Les votes par région ;
* 🏛️ Les votes par parti ;
* 🌍 La répartition entre votes nationaux et diaspora.

Le dashboard récupère directement les données réelles depuis PostgreSQL et se rafraîchit automatiquement.

---

# 🛠️ Technologies utilisées

| Technologie       | Rôle                                     |
| ----------------- | ---------------------------------------- |
| 🐍 Python         | Développement du Producer et du pipeline |
| 📨 Apache Kafka   | Streaming des événements                 |
| ⚡ Apache Spark    | Traitement des données en temps réel     |
| 🐘 PostgreSQL     | Stockage des résultats agrégés           |
| ☁️ MinIO          | Data Lake compatible S3                  |
| 📊 Streamlit      | Dashboard temps réel                     |
| 🐳 Docker         | Conteneurisation                         |
| 🐳 Docker Compose | Orchestration des services               |

---

# 📁 Structure du projet

```text
election-streaming/
│
├── dashboard/
│   └── app.py
│
├── kafka/
│
├── producer/
│
├── spark/
│
├── postgres/
│
├── docker-compose.yml
├── run.sh
├── README.md
└── installation.md
```

---

# 🚀 Démarrage rapide

Après avoir cloné le projet :

```bash
git clone https://github.com/Mleye404/Election_streaming.git
cd Election_streaming
```

Donnez les droits d'exécution au script :

```bash
chmod +x run.sh
```

Puis lancez la plateforme :

```bash
./run.sh
```

---

## 📖 Installation complète

Pour consulter toutes les instructions d'installation et les commandes détaillées :

👉 Consultez le fichier **[installation.md](installation.md)**.

---

# 🌐 Interfaces disponibles

Après le lancement de la plateforme :

| Service                | Adresse                 |
| ---------------------- | ----------------------- |
| 📊 Dashboard Streamlit | `http://localhost:8501` |
| ⚡ Spark Master         | `http://localhost:8080` |
| 🔥 Spark Job UI        | `http://localhost:4040` |
| ☁️ MinIO Console       | `http://localhost:9001` |

---

# 🔒 Fiabilité et bonnes pratiques

Le projet utilise plusieurs mécanismes permettant d'améliorer la fiabilité du pipeline :

* traitement continu des événements avec Kafka ;
* traitement structuré avec Spark Structured Streaming ;
* architecture Bronze / Silver / Gold ;
* stockage persistant des données ;
* séparation des responsabilités entre les différents services ;
* utilisation de conteneurs Docker pour garantir la reproductibilité de l'environnement ;
* vérification de la disponibilité des services au démarrage.

---

# 🔄 Flux complet

```text
Votes simulés
      │
      ▼
   Producer
      │
      ▼
    Kafka
      │
      ▼
Spark Structured Streaming
      │
      ├──────────────► Bronze ──────► MinIO
      │
      ├──────────────► Silver ──────► MinIO
      │
      └──────────────► Gold
                          │
                 ┌────────┴────────┐
                 ▼                 ▼
              MinIO          PostgreSQL
                                   │
                                   ▼
                             Streamlit
                             Dashboard
```

---

# 👨‍💻 Auteur

**Mouhamadou Leye**

🎓 Master 1 — Ingénierie Logicielle et Intelligence Artificielle
🏫 École Polytechnique de Thiès (EPT)

GitHub : [Mleye404](https://github.com/Mleye404?utm_source=chatgpt.com)

---

## ⭐ Conclusion

**Election Streaming** démontre la mise en œuvre d'une architecture complète de traitement de données en temps réel.

Le projet combine :

> **Kafka + Spark Structured Streaming + MinIO + PostgreSQL + Streamlit + Docker**

afin de construire une plateforme capable de traiter, stocker et visualiser des données électorales simulées en continu.
