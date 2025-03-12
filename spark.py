from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StringType, StructType, StructField, IntegerType
import requests
import re
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
    api_token = "3c6521274af1bf"
    url = f"https://ipinfo.io/{ip_address}?token={api_token}"
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data['country']
    except Exception as e:
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

   
    api_stats = logs_df.groupBy("api").agg(
        F.avg("duration").alias("avg"),
        F.min("duration").alias("min"),
        F.max("duration").alias("max")
    )

    
    api_query = api_stats.writeStream \
        .outputMode("complete") \
        .format("console") \
        .start()

    
    generat_contry_udf = F.udf(generate_country, StringType())
    logs_df = logs_df.withColumn("country", generat_contry_udf(F.col("ip")))

    
    country_stats = logs_df.groupBy("country").agg(
        F.count("*").alias("number_of_requests")
    )

    
    country_query = country_stats.writeStream \
        .outputMode("complete") \
        .format("console") \
        .start()

    
    spark.streams.awaitAnyTermination()

except Exception as e:
    print(f"Erreur lors de la lecture depuis Kafka : {e}")