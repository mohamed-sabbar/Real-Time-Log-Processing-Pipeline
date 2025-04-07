# 🚀 Real-Time Log Processing Pipeline

Un pipeline de traitement de logs en temps réel construit avec **Filebeat**, **Kafka**, **Spark Streaming**, **Flask** et une **interface React** — le tout orchestré avec **Docker**.

---

## 🧭 Aperçu de l'architecture

Voici le schéma du pipeline :

![Architecture](./assets/architecture.png)

### 🔄 Fonctionnement

1. **Filebeat** collecte les logs depuis des fichiers systèmes ou applicatifs.
2. Les logs sont envoyés à **Kafka**, qui gère les flux de données en temps réel via des topics.
3. **Spark Streaming** consomme les données Kafka et les traite en temps réel.
4. Les données traitées sont renvoyées à Kafka ou directement exposées via une **API Flask**.
5. Une **interface React** consomme l’API pour afficher les logs et métriques en temps réel.

---

## 🛠️ Technologies utilisées

| Outil         | Rôle                                    |
|---------------|-----------------------------------------|
| 📝 Filebeat    | Collecte des fichiers de logs           |
| 🛰️ Kafka       | Broker de messages pour les données      |
| ⚡ Spark       | Traitement de flux en temps réel        |
| 🐍 Flask       | Exposition des données via une API REST |
| ⚛️ React       | Dashboard pour visualiser les données    |
| 🐳 Docker      | Conteneurisation et orchestration       |

---

## 📂 Structure du projet
├── README.md # Documentation du projet
│
├── images/ # Captures d'écran et diagrammes
│ ├── architecture.png # Diagramme d'architecture
│ ├── dashboard_phone.png # Vue mobile du dashboard
│ ├── run_web_app.png # Capture de l'application web
│ └── spring_boot_web_app.png # Interface Spring Boot
│
├── Main/
│ ├── commands.sh # Scripts utilitaires
│ └── Dashboard.pbix # Fichier Power BI
│
├── Lambda/
│ ├── docker-compose.yaml # Configuration Docker
│ ├── producer.py # Producteur de données
│ └── transform.py # Scripts de transformation
│
└── .idea/ # Configuration IDE
├── .gitignore
├── .name
├── misc.xml
└── modules.xml



