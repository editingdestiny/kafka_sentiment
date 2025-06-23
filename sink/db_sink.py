from kafka import KafkaConsumer
import psycopg2
import json

conn = psycopg2.connect(
    dbname="sentiment",
    user="sd22750",
    password="VarshaI2me",
    host="localhost"
)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS news_sentiment (
    id SERIAL PRIMARY KEY,
    text TEXT,
    sentiment TEXT,
    compound FLOAT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

consumer = KafkaConsumer(
    'sentiment-news',
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest',
    enable_auto_commit=True
)

for msg in consumer:
    data = msg.value
    cur.execute(
        "INSERT INTO news_sentiment (text, sentiment, compound) VALUES (%s, %s, %s)",
        (data["text"], data["label"], data["compound"])
    )
    conn.commit()
    print(f"Stored sentiment for: {data['text']}")
