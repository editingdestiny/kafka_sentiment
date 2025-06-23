import os
from dotenv import load_dotenv

# Load environment variables from the .env file in the project root
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..', '.env')
load_dotenv(dotenv_path=env_path)

# Kafka Configuration
KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'kafka:9092')  # Kafka broker URL (use container DNS for internal communication)
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'sentiment-test')  # Topic where sentiment messages will be published
KAFKA_GROUP_ID = os.getenv('KAFKA_GROUP_ID', 'sentiment-group')  # Kafka consumer group ID

# Sentiment Analysis Model Configuration (Replace with your model's path or API URL)
SENTIMENT_MODEL_PATH = os.getenv('SENTIMENT_MODEL_PATH', '/path/to/your/sentiment/model')  # Update this path as needed

# PostgreSQL Database Configuration
DB_HOST = os.getenv('DB_HOST', 'sentiment-postgres')  # PostgreSQL container name
DB_PORT = os.getenv('DB_PORT', 5432)  # Default PostgreSQL port
DB_NAME = os.getenv('DB_NAME', 'sentiment')  # Database name
DB_USER = os.getenv('DB_USER', 'sd22750')  # Username for the database
DB_PASSWORD = os.getenv('DB_PASSWORD', 'your_secure_password')  # Set this securely in your environment

# Log Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')  # Can be 'DEBUG', 'INFO', 'ERROR', etc.

# Dashboard Configuration (Optional)
DASHBOARD_ENABLED = os.getenv('DASHBOARD_ENABLED', 'True')  # Set to True to enable the dashboard
DASHBOARD_HOST = os.getenv('DASHBOARD_HOST', 'localhost')  # Dashboard host, if different
DASHBOARD_PORT = os.getenv('DASHBOARD_PORT', 8050)  # Dashboard port (default for Dash)

# Sentiment API URL (if using an external API for sentiment analysis)
SENTIMENT_API_URL = os.getenv('SENTIMENT_API_URL', 'http://localhost:8000/analyze')  # Change if you use an external API for sentiment analysis

# Producer Settings (How frequently the producer pushes messages)
PRODUCER_INTERVAL = int(os.getenv('PRODUCER_INTERVAL', 5))  # Interval in seconds for producing messages

# Health Check URL for monitoring purposes
HEALTH_CHECK_URL = os.getenv('HEALTH_CHECK_URL', '/health')  # Optional: Used for health monitoring of the services

# Miscellaneous
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')  # 'production' or 'development' based on the deployment
DEBUG = os.getenv('DEBUG', 'False')  # Set to True for debugging purposes

# Adminer Configuration (For accessing Adminer, if needed)
ADMINER_HOST = os.getenv('ADMINER_HOST', 'sd-pta.duckdns.org')  # Your Adminer URL (used with Traefik)

# Function to print out the configuration for debugging purposes
def print_config():
    print(f"KAFKA_BROKER: {KAFKA_BROKER}")
    print(f"KAFKA_TOPIC: {KAFKA_TOPIC}")
    print(f"SENTIMENT_MODEL_PATH: {SENTIMENT_MODEL_PATH}")
    print(f"DB_HOST: {DB_HOST}")
    print(f"LOG_LEVEL: {LOG_LEVEL}")
    print(f"DASHBOARD_ENABLED: {DASHBOARD_ENABLED}")

if __name__ == "__main__":
    print_config()
