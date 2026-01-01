import json
import pandas as pd
import os
from kafka import KafkaProducer
from src.utils.config_loader import config

BOOTSTRAP_SERVERS = config.get("kafka.bootstrap_servers")[0]
TOPIC_NAME = config.get("kafka.topic_input")

def json_serializer(data):
    return json.dumps(data).encode("utf-8")

def start_ingestion():

    producer = KafkaProducer(
        bootstrap_servers=BOOTSTRAP_SERVERS,
        value_serializer=json_serializer,
        linger_ms=10,
        batch_size=16384
    )

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    csv_path = os.path.join(base_dir, "data/processed/flights_final_dataset.csv")

    df = pd.read_csv(csv_path)
    df = df.sample(frac=1).reset_index(drop=True)
    
    try:
        for index, row in df.iterrows():
            flight_dict = row.to_dict()
            producer.send(TOPIC_NAME, flight_dict)
            
            print(f" [Sent] {flight_dict['OP_UNIQUE_CARRIER']} | {flight_dict['ORIGIN']} -> {flight_dict['DEST']}")

        producer.flush() 
        print(f"DONE")
            
    except KeyboardInterrupt:
        print("\nStopped sending data.")
    finally:
        producer.close()

if __name__ == "__main__":
    start_ingestion()