import sys
import os
import warnings
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, udf
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType

from src.utils.config_loader import config
KAFKA_BOOTSTRAP_SERVERS = config.get("kafka.bootstrap_servers")
TOPIC_INPUT = config.get("kafka.topic_input")
CHECKPOINT_LOCATION = config.get("spark.checkpoint_location")
os.environ['PYSPARK_PYTHON'] = sys.executable
os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable

predictor = None

def get_predictor():
    global predictor
    if predictor is None:
        from src.models.predictor import FlightPredictor
        predictor = FlightPredictor()
    return predictor


def predict_delay_udf(origin, dest, carrier, day_month, day_week, crs_minutes, dist, temp, rhum, prcp, wspd, coco):
    model = get_predictor()
    warnings.filterwarnings("ignore", category=UserWarning)
    flight_data = {
        'ORIGIN': origin,
        'DEST': dest,
        'OP_UNIQUE_CARRIER': carrier,
        'DAY_OF_MONTH': day_month,
        'DAY_OF_WEEK': day_week,
        'CRS_MINUTES': crs_minutes,
        'DISTANCE': dist,
        'temp': temp,
        'rhum': rhum,
        'prcp': prcp,
        'wspd': wspd,
        'coco': coco
    }
    
    prob = model.predict(flight_data)
    if prob is None:
        return -1.0
    return float(prob)

predict_spark_udf = udf(predict_delay_udf, FloatType())

def start_spark_streaming():
    
    spark = SparkSession.builder \
        .appName("FlightDelayPredictionSpark") \
        .config("spark.sql.streaming.checkpointLocation", CHECKPOINT_LOCATION) \
        .config("spark.driver.bindAddress", "127.0.0.1") \
        .config("spark.driver.host", "127.0.0.1") \
        .config("spark.ui.showConsoleProgress", "false") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1") \
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
        StructField("coco", FloatType())
    ])

    df_kafka = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
        .option("subscribe", TOPIC_INPUT) \
        .option("startingOffsets", "latest") \
        .load()

    df_parsed = df_kafka.select(from_json(col("value").cast("string"), schema).alias("data")).select("data.*")

    df_predicted = df_parsed.withColumn("prediction_prob", predict_spark_udf(
        col("ORIGIN"), col("DEST"), col("OP_UNIQUE_CARRIER"),
        col("DAY_OF_MONTH"), col("DAY_OF_WEEK"), col("CRS_MINUTES"),
        col("DISTANCE"), col("temp"), col("rhum"), col("prcp"), col("wspd"), col("coco")
    ))

    df_final = df_predicted.withColumn("status", 
        udf(lambda p: "DELAYED" if p > 0.5 else "ON TIME", StringType())(col("prediction_prob"))
    )

    query = df_final.select("OP_UNIQUE_CARRIER", "ORIGIN", "DEST", "status", "prediction_prob") \
        .writeStream \
        .outputMode("append") \
        .format("console") \
        .option("truncate", False) \
        .start()

    query.awaitTermination()

if __name__ == "__main__":
    start_spark_streaming()