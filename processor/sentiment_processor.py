from kafka import KafkaConsumer, KafkaProducer
import json
from utils.sentiment import analyze_sentiment

consumer = KafkaConsumer(
    'raw-news',
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest',
    enable_auto_commit=True
)

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

for msg in consumer:
    data = msg.value
    sentiment = analyze_sentiment(data["headline"])
    producer.send('sentiment-news', sentiment)
    print(f"Processed: {data['headline']}")
