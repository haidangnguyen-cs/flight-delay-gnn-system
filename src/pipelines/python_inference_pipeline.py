import json
import warnings
from kafka import KafkaConsumer
from src.utils.config_loader import config
from src.models.predictor import FlightPredictor

BOOTSTRAP_SERVERS = config.get("kafka.bootstrap_servers")
TOPIC_INPUT = config.get("kafka.topic_input")
TOPIC_OUTPUT = config.get("kafka.topic_output")
THRESHOLD = config.get("model.threshold", 0.5)
warnings.filterwarnings("ignore", category=UserWarning)

def start_inference():
    predictor = FlightPredictor()
    consumer = KafkaConsumer(
        TOPIC_INPUT,
        bootstrap_servers=BOOTSTRAP_SERVERS,
        auto_offset_reset='latest',
        group_id=config.get("kafka.consumer_group"),
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    try:
        for message in consumer:
            flight_data = message.value
            
            probability = predictor.predict(flight_data)
            
            airline = flight_data.get('OP_UNIQUE_CARRIER', 'Unknown')
            origin = flight_data.get('ORIGIN', '???')
            dest = flight_data.get('DEST', '???')
            
            if probability is None:
                continue

            is_delayed = probability > THRESHOLD
            
            if is_delayed:
                status_text = "DELAYED"
            else:
                status_text = "ON TIME"

            print(f" [{status_text}] {airline} | {origin} -> {dest} | Delay probability: {probability:.2%}")

    except KeyboardInterrupt:
        print("\nSystem stopped.")
    finally:
        consumer.close()

if __name__ == "__main__":
    start_inference()