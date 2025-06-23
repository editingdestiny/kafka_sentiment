from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import datetime
import time
import sys

Base = declarative_base()

# Define the database table for sentiment results
class SentimentResult(Base):
    __tablename__ = 'sentiment_results'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    url = Column(String(1000))
    published_at = Column(DateTime)
    
    # --- ADD NEW COLUMNS FOR EACH MODEL'S RESULTS ---
    vader_score = Column(Float)
    vader_label = Column(String(50))
    textblob_score = Column(Float)
    textblob_label = Column(String(50))
    transformer_score = Column(Float)
    transformer_label = Column(String(50))
    # --- END NEW COLUMNS ---

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return (f"<SentimentResult(title='{self.title[:50]}...', "
                f"vader_label='{self.vader_label}', "
                f"transformer_label='{self.transformer_label}')>")

# Database connection setup (no change needed here)
DB_USER = os.getenv('POSTGRES_USER', 'sd22750')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'your_secure_password')
DB_HOST = os.getenv('POSTGRES_HOST', 'postgres')
DB_NAME = os.getenv('POSTGRES_DB', 'sentiment')
DB_PORT = os.getenv('POSTGRES_PORT', '5432')

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = None
Session = None

def initialize_db_engine():
    global engine, Session
    max_retries = 20
    retry_delay_seconds = 5
    print(f"Attempting to connect to PostgreSQL for DB Sink at {DB_HOST}:{DB_PORT}/{DB_NAME}...", flush=True)
    for i in range(max_retries):
        try:
            engine = create_engine(DATABASE_URL)
            conn = engine.connect()
            conn.close()
            Session = sessionmaker(bind=engine)
            print("Successfully connected to PostgreSQL for DB Sink!", flush=True)
            return
        except Exception as e:
            print(f"Attempt {i+1}/{max_retries}: PostgreSQL not yet available or connection error: {e}. Retrying in {retry_delay_seconds} seconds...", flush=True)
            time.sleep(retry_delay_seconds)
    print("Failed to connect to PostgreSQL for DB Sink after multiple retries. Exiting.", flush=True)
    sys.exit(1)

initialize_db_engine()

def create_table_if_not_exists():
    """Creates the sentiment_results table if it doesn't already exist."""
    print("Checking/creating 'sentiment_results' table...", flush=True)
    Base.metadata.create_all(engine) # This creates tables defined in Base
    print("Table 'sentiment_results' check/creation complete.", flush=True)

def insert_sentiment_result(data):
    """
    Inserts a sentiment result into the database.
    'data' should be a dictionary containing relevant fields from all models.
    """
    session = Session()
    try:
        new_result = SentimentResult(
            title=data.get('title'),
            description=data.get('description'),
            url=data.get('url'),
            published_at=datetime.datetime.strptime(data['publishedAt'], '%Y-%m-%dT%H:%M:%SZ') if data.get('publishedAt') and isinstance(data['publishedAt'], str) else None,
            
            # --- MAP DATA TO NEW COLUMNS ---
            vader_score=data.get('vader_score'),
            vader_label=data.get('vader_label'),
            textblob_score=data.get('textblob_score'),
            textblob_label=data.get('textblob_label'),
            transformer_score=data.get('transformer_score'),
            transformer_label=data.get('transformer_label')
            # --- END MAP DATA ---
        )
        session.add(new_result)
        session.commit()
        # print(f"Inserted sentiment for: {data.get('title')}", flush=True)
    except Exception as e:
        session.rollback()
        print(f"Error inserting sentiment result for '{data.get('title')}': {e}", flush=True)
        # Log full traceback for debugging during development
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == '__main__':
    print("Running DB Sink test...", flush=True)
    create_table_if_not_exists()
    
    # Sample data for testing insertion with multiple models
    sample_data = {
        'title': 'Test Article DB Multi-Model',
        'description': 'This is a great product and a fantastic service. I highly recommend it!',
        'url': 'http://test.com/multi',
        'publishedAt': '2024-06-14T10:00:00Z',
        'vader_score': 0.8, 'vader_label': 'Positive',
        'textblob_score': 0.7, 'textblob_label': 'Positive',
        'transformer_score': 0.95, 'transformer_label': 'Positive'
    }
    insert_sentiment_result(sample_data)
    print("DB Sink test complete. Check database.", flush=True)