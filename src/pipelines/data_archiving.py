from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, current_timestamp, expr
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType

from src.utils.config_loader import config

KAFKA_SERVER = config.get("kafka.bootstrap_servers")[0]
TOPIC_INPUT = config.get("kafka.topic_input")
CASSANDRA_HOST = config.get("cassandra.hosts")[0] 
KEYSPACE = config.get("cassandra.keyspace")
TABLE = config.get("cassandra.table_training")
CHECKPOINT_LOCATION = config.get("spark.checkpoint_location")[1]

def start_archiving():

    spark = SparkSession.builder \
        .appName("FlightDataArchiving") \
        .config("spark.cassandra.connection.host", CASSANDRA_HOST) \
        .config("spark.sql.streaming.checkpointLocation", CHECKPOINT_LOCATION) \
        .config("spark.jars.packages", "com.datastax.spark:spark-cassandra-connector_2.12:3.5.1,org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("ERROR")

    schema = StructType([
        StructField("ORIGIN", StringType()),
        StructField("DEST", StringType()),
        StructField("OP_UNIQUE_CARRIER", StringType()),
        StructField("DAY_OF_MONTH", IntegerType()),
        StructField("DAY_OF_WEEK", IntegerType()),
        StructField("CRS_MINUTES", IntegerType()),
        StructField("DISTANCE", FloatType()),
        StructField("temp", FloatType()),
        StructField("rhum", FloatType()),
        StructField("prcp", FloatType()),
        StructField("wspd", FloatType()),
        StructField("coco", FloatType()),
        StructField("DEP_DEL15", FloatType())
    ])

    df_kafka = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_SERVER) \
        .option("subscribe", TOPIC_INPUT) \
        .option("startingOffsets", "latest") \
        .load()

    df_parsed = df_kafka \
        .select(from_json(col("value").cast("string"), schema).alias("data")) \
        .select("data.*") \
        .select([col(c).alias(c.lower()) for c in schema.fieldNames()])

    df_final = df_parsed \
        .withColumn("id", expr("uuid()")) \
        .withColumn("created_at", current_timestamp())

    query = df_final.writeStream \
        .outputMode("append") \
        .format("org.apache.spark.sql.cassandra") \
        .option("keyspace", KEYSPACE) \
        .option("table", TABLE) \
        .option("checkpointLocation", CHECKPOINT_LOCATION) \
        .start()

    query.awaitTermination()

if __name__ == "__main__":
    start_archiving()