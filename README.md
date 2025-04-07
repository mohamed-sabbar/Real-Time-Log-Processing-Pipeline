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
```batch 
Big-Data-Project:.
|   README.md
|
+---images
|       architecture.png
|       dashboard_phone.png
|       run_web_app.png
|       spring_boot_web_app.png
|
\---Main
    |   commands.sh
    |   Dashboard.pbix
    |
    +---.idea
    |       workspace.xml
    |
    +---Lambda
    |   |   docker-compose.yaml
    |   |   producer.py
    |   |   transform.py
    |   |
    |   +---.idea
    |   |   |   .gitignore
    |   |   |   .name
    |   |   |   misc.xml
    |   |   |   modules.xml
    |   |   |   price prediction (big data envirnment).iml
    |   |   |   vcs.xml
    |   |   |   workspace.xml
    |   |   |
    |   |   \---inspectionProfiles
    |   |           profiles_settings.xml
    |   |
    |   +---Batch_layer
    |   |   |   batch_layer.py
    |   |   |   batch_pipeline.py
    |   |   |   HDFS_consumer.py
    |   |   |   put_data_hdfs.py
    |   |   |   save_data_postgresql.py
    |   |   |   spark_tranformation.py
    |   |   |   __init__.py
    |   |   |
    |   |   +---dags
    |   |   |       syc_with_Airflow.py
    |   |   |       __init__.py
    |   |   |
    |   |   \---__pycache__
    |   |           batch_layer.cpython-310.pyc
    |   |           HDFS_consumer.cpython-310.pyc
    |   |           put_data_hdfs.cpython-310.pyc
    |   |           save_data_postgresql.cpython-310.pyc
    |   |           spark_tranformation.cpython-310.pyc
    |   |           __init__.cpython-310.pyc
    |   |
    |   +---ML_operations
    |   |   |   xgb_model.pkl
    |   |   |
    |   |   \---__pycache__
    |   +---real_time_web_app(Flask)
    |   |   |   app.py
    |   |   |   get_Data_from_hbase.py
    |   |   |
    |   |   +---static
    |   |   |   +---css
    |   |   |   |       style.css
    |   |   |   |
    |   |   |   \---js
    |   |   |           script.js
    |   |   |
    |   |   +---templates
    |   |   |       index.html
    |   |   |
    |   |   \---__pycache__
    |   |           get_Data_from_hbase.cpython-310.pyc
    |   |
    |   +---Stream_data
    |   |   |   stream_data.csv
    |   |   |   stream_data.py
    |   |   |
    |   |   \---__pycache__
    |   +---Stream_layer
    |   |       insert_data_hbase.py
    |   |       ML_consumer.py
    |   |       stream_pipeline.py
    |   |       __init__.py
    |   |
    |   \---__pycache__
    |           producer.cpython-310.pyc
    |           transform.cpython-310.pyc
    |
    \---real_time_app(Spring boot)
        |   .classpath
        |   .gitignore
        |   .project
        |   HELP.md
        |   mvnw
        |   mvnw.cmd
        |   pom.xml
        |
        +---.mvn
        |   \---wrapper
        |           maven-wrapper.jar
        |           maven-wrapper.properties
        |
        +---.settings
        |       org.eclipse.core.resources.prefs
        |       org.eclipse.jdt.core.prefs
        |       org.eclipse.m2e.core.prefs
        |
        +---src
        |   +---main
        |   |   +---java
        |   |   |   \---com
        |   |   |       \---example
        |   |   |           \---demo
        |   |   |               |   RealTimeAppApplication.java
        |   |   |               |
        |   |   |               +---controller
        |   |   |               |       IndexController.java
        |   |   |               |
        |   |   |               \---service
        |   |   |                       HbaseService.java
        |   |   |
        |   |   \---resources
        |   |       |   application.properties
        |   |       |
        |   |       +---static
        |   |       |   +---css
        |   |       |   |       style.css
        |   |       |   |
        |   |       |   \---js
        |   |       |           script.js
        |   |       |
        |   |       \---templates
        |   |               index.html
        |   |
        |   \---test
        |       \---java
        |           \---com
        |               \---example
        |                   \---demo
        |                           RealTimeAppApplicationTests.java
        |
        \---target
            +---classes
            |   |   application.properties
            |   |
            |   +---com
            |   |   \---example
            |   |       \---demo
            |   |           |   RealTimeAppApplication.class
            |   |           |
            |   |           +---controller
            |   |           |       IndexController.class
            |   |           |
            |   |           \---service
            |   |                   HbaseService.class
            |   |
            |   +---META-INF
            |   |   |   MANIFEST.MF
            |   |   |
            |   |   \---maven
            |   |       \---com.example
            |   |           \---real_time_app
            |   |                   pom.properties
            |   |                   pom.xml
            |   |
            |   +---static
            |   |   +---css
            |   |   |       style.css
            |   |   |
            |   |   \---js
            |   |           script.js
            |   |
            |   \---templates
            |           index.html
            |
            \---test-classes
                \---com
                    \---example
                        \---demo
                                RealTimeAppApplicationTests.class


```


