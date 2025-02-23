from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StringType, StructType, StructField, IntegerType
import requests
import re

# Fonction pour parser les logs Apache
def parse_apache_log(log):
    pattern = r'^(\S+) - - \[(.*?)\] "(.*?)" (\d{3}) (\d+) "(.*?)" "(.*?)" (\d+)$'
    match = re.match(pattern, log)
    if match:
        return (
            match.group(1),  # ip
            match.group(2),  # timestamp
            match.group(3),  # request
            int(match.group(4)),  # status
            int(match.group(5)),  # size
            match.group(6),  # referrer
            match.group(7),  # user_agent
            int(match.group(8))  # duration
        )
    return None

# Fonction pour obtenir le pays à partir d'une IP
def generat_contry(ip_address):
    api_token = "3c6521274af1bf"
    url = f"https://ipinfo.io/{ip_address}?token={api_token}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('country', 'Unknown')
        else:
            return 'Unknown'
    except Exception as e:
        print(f"Erreur lors de l'appel API pour l'IP {ip_address}: {e}")
        return 'Unknown'

# Schéma pour les logs Apache
apache_log_schema = StructType([
    StructField("ip", StringType(), True),
    StructField("timestamp", StringType(), True),
    StructField("request", StringType(), True),
    StructField("status", IntegerType(), True),
    StructField("size", IntegerType(), True),
    StructField("referrer", StringType(), True),
    StructField("user_agent", StringType(), True),
    StructField("duration", IntegerType(), True)
])

# Initialisation de Spark
spark = SparkSession.builder \
    .appName("KafkaSparkStreaming") \
    .config("spark.sql.streaming.microBatchDuration", "10s") \
    .getOrCreate()

# Paramètres Kafka
kafka_params = {
    "kafka.bootstrap.servers": "172.17.0.1:9092", 
    "subscribe": "test",                          
    "startingOffsets": "latest"                   
}

try:
    # Lecture du flux Kafka
    stream = spark \
        .readStream \
        .format("kafka") \
        .options(**kafka_params) \
        .load()

    # Conversion des messages en chaînes de caractères
    messages = stream.selectExpr("CAST(value AS STRING)")

    # Parsing des logs Apache
    parsed_logs = messages.select(
        F.udf(parse_apache_log, apache_log_schema)(F.col("value")).alias("parsed_log")
    ).select("parsed_log.*")

    # Extraction de l'API à partir de la requête
    logs_df = parsed_logs.withColumn("api", F.regexp_extract(F.col("request"), r'^(.*) HTTP/\d\.\d$', 1))

    # Statistiques des API
    api_stats = logs_df.groupBy("api").agg(
        F.avg("duration").alias("avg"),
        F.min("duration").alias("min"),
        F.max("duration").alias("max")
    )

    # Démarrage de la requête de streaming pour les statistiques des API
    api_query = api_stats.writeStream \
        .outputMode("complete") \
        .format("console") \
        .start()

    # Ajout de la colonne "country" en utilisant une UDF
    generat_contry_udf = F.udf(generat_contry, StringType())
    logs_df = logs_df.withColumn("country", generat_contry_udf(F.col("ip")))

    # Statistiques par pays
    country_stats = logs_df.groupBy("country").agg(
        F.count("*").alias("number_of_requests")
    )

    # Démarrage de la requête de streaming pour les statistiques par pays
    country_query = country_stats.writeStream \
        .outputMode("complete") \
        .format("console") \
        .start()

    # Attendre que l'une des requêtes se termine
    spark.streams.awaitAnyTermination()

except Exception as e:
    print(f"Erreur lors de la lecture depuis Kafka : {e}")