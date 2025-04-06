from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StringType, StructType, StructField, IntegerType
import requests
import re
import json
def parse_apache_log(log):
    pattern = r'^(\S+) - - \[(.*?)\] "(.*?)" (\d{3}) (\d+) "(.*?)" "(.*?)" (\d+)$'
    match = re.match(pattern, log)
    if match:
        return (
            match.group(1),  
            match.group(2),  
            match.group(3),  
            int(match.group(4)),  
            int(match.group(5)),  
            match.group(6),  
            match.group(7),  
            int(match.group(8))  
        )
    return None
def generate_country(ip_address):
    api_token = "2dfcd789e725a3"
    url = f"https://ipinfo.io/{ip_address}?token={api_token}"

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # Lève une exception pour les erreurs HTTP (4xx, 5xx)
        data = response.json()
        return data.get('country', "Unknown")  # Utilisation de `.get()` pour éviter une KeyError
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la requête : {e}")  # Afficher l'erreur pour debug
        return "Unknown"
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
spark = SparkSession.builder \
    .appName("KafkaSparkStreaming") \
    .config("spark.sql.streaming.microBatchDuration", "10s") \
    .getOrCreate()
kafka_params = {
    "kafka.bootstrap.servers": "172.17.0.1:9092",  
    "subscribe": "test",  
    "startingOffsets": "latest"
}
try:
    
    stream = spark \
        .readStream \
        .format("kafka") \
        .options(**kafka_params) \
        .load()

    
    messages = stream.selectExpr("CAST(value AS STRING)")

    
    messages = messages.withColumn("message", F.get_json_object(F.col("value"), "$.message"))

    
    parsed_logs = messages.select(
        F.udf(parse_apache_log, apache_log_schema)(F.col("message")).alias("parsed_log")
    ).select("parsed_log.*")

    
    logs_df = parsed_logs.withColumn("api", F.regexp_extract(F.col("request"), r'^(.*) HTTP/\d\.\d$', 1))

    # Calculer les statistiques des API
    api_stats = logs_df.groupBy("api").agg(
        F.avg("duration").alias("avg"),
        F.min("duration").alias("min"),
        F.max("duration").alias("max")
    )

    
    api_stats_json = api_stats.withColumn("value", F.to_json(F.struct("*")))

    
    api_stats_query = api_stats_json \
        .selectExpr("CAST(value AS STRING)") \
        .writeStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "172.17.0.1:9092") \
        .option("topic", "api_stats") \
        .option("checkpointLocation", "/tmp/checkpoints/api_stats") \
        .outputMode("update") \
        .start()

    
    generat_contry_udf = F.udf(generate_country, StringType())
    logs_df = logs_df.withColumn("country", generat_contry_udf(F.col("ip")))

    
    country_stats = logs_df.groupBy("country").agg(
        F.count("*").alias("number_of_requests")
    )

    
    country_stats_json = country_stats.withColumn("value", F.to_json(F.struct("*")))

    
    country_stats_query = country_stats_json \
        .selectExpr("CAST(value AS STRING)") \
        .writeStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "172.17.0.1:9092") \
        .option("topic", "country_stats") \
        .option("checkpointLocation", "/tmp/checkpoints/country_stats") \
        .outputMode("update") \
        .start()

    
    spark.streams.awaitAnyTermination()

except Exception as e:
    print(f"Erreur lors de la lecture depuis Kafka : {e}")