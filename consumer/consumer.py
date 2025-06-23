import json
import time
import sys
import datetime # Ensure datetime is imported for consistent timestamps
from kafka import KafkaConsumer # <--- THIS LINE IS MISSING IN YOUR CONTAINER'S CODE
from kafka.errors import NoBrokersAvailable # This one is also critical for the KafkaProducer equivalent, make sure it's there too
# Import your sentiment analysis and database sink modules
# These paths are relative to the consumer/ directory in your Dockerfile
from utils.sentiment import analyze_sentiment
from sentiment_db_sink import create_table_if_not_exists, insert_sentiment_result

# Kafka Consumer setup
KAFKA_BROKER = 'kafka:9092' # Matches Kafka service name in docker-compose
KAFKA_TOPIC = 'raw-news'
KAFKA_GROUP_ID = 'news-sentiment-consumer-group-v2' # The updated group ID

consumer = None
max_kafka_retries = 20
kafka_retry_delay_seconds = 5

print(f"Attempting to connect to Kafka consumer...", flush=True)
for i in range(max_kafka_retries):
    try:
        consumer = KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=KAFKA_BROKER,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest', # Start from the beginning of the topic if no committed offset
            group_id=KAFKA_GROUP_ID, # Use the new group ID
            enable_auto_commit=True, # Automatically commit offsets
            # Configure to quickly detect broker availability for initial connection
            # request_timeout_ms=10000,
            # retry_backoff_ms=500
        )
        print("Successfully connected to Kafka consumer!", flush=True)
        break
    except Exception as e:
        print(f"Attempt {i+1}/{max_kafka_retries}: Kafka consumer not ready yet or connection error: {e}. Retrying in {kafka_retry_delay_seconds} seconds...", flush=True)
        time.sleep(kafka_retry_delay_seconds)

if consumer is None:
    print("Failed to connect to Kafka consumer after multiple retries. Exiting.", flush=True)
    sys.exit(1)

# Database table creation (only once at startup)
print("Initializing database connection and creating table if needed...", flush=True)
try:
    create_table_if_not_exists()
    print("Database table 'sentiment_results' check/creation complete.", flush=True)
except Exception as e:
    print(f"CRITICAL ERROR: Failed to create database table: {e}", flush=True)
    sys.exit(1) # Exit if table creation fails, as we can't store results

print(f"Listening for messages on '{KAFKA_TOPIC}'...", flush=True)

# Main message processing loop
for message in consumer:
    try:
        news_article = message.value
        # Check if the required 'title' key exists
        if not news_article or 'title' not in news_article:
            print(f"Skipping malformed message (no title): {news_article}", flush=True)
            continue

        print(f"Received: {news_article.get('title')}", flush=True)

        # Use 'description' for richer sentiment if available, otherwise 'title'
        text_for_sentiment = news_article.get('description', news_article.get('title', ''))

        if text_for_sentiment:
            # Perform Sentiment Analysis using all configured models
            # analyze_sentiment now returns results from multiple models
            sentiment_analysis_results = analyze_sentiment(text_for_sentiment)

            # Add all sentiment results to the article dictionary
            # These keys must match the column names in sentiment_db_sink.py
            news_article['vader_score'] = sentiment_analysis_results.get('vader_score')
            news_article['vader_label'] = sentiment_analysis_results.get('vader_label')
            news_article['textblob_score'] = sentiment_analysis_results.get('textblob_score')
            news_article['textblob_label'] = sentiment_analysis_results.get('textblob_label')
            news_article['transformer_score'] = sentiment_analysis_results.get('transformer_score')
            news_article['transformer_label'] = sentiment_analysis_results.get('transformer_label')

            print(f"Analyzed sentiment for '{news_article['title']}': "
                  f"VADER={news_article.get('vader_label')}, "
                  f"TextBlob={news_article.get('textblob_label')}, "
                  f"Transformer={news_article.get('transformer_label')}", flush=True)

            # Store the processed article with all sentiment data in the database
            insert_sentiment_result(news_article)
            print(f"Successfully stored sentiment for '{news_article['title']}' in DB.", flush=True)
        else:
            print(f"Skipping sentiment analysis for '{news_article['title']}': No description or title text available.", flush=True)

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON message: {e}. Raw message: {message.value}", flush=True)
    except KeyError as e:
        print(f"Missing expected key in message: {e}. Message: {message.value}", flush=True)
    except Exception as e:
        print(f"An unhandled error occurred during message processing or DB insertion for message: {news_article}. Error: {e}", flush=True)
        # Log full traceback for better debugging in development
        import traceback
        traceback.print_exc()