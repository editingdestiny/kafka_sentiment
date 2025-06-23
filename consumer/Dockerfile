FROM python:3.10-slim-buster

WORKDIR /app

COPY requirements.txt .
# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# --- ADD THIS LINE ---
# Download NLTK data required by VADER directly into the NLTK data path
RUN python -c "import nltk; nltk.download('vader_lexicon', download_dir='/usr/local/share/nltk_data')"
# You can also omit download_dir, NLTK will use default paths, but being explicit helps sometimes.
# --- END ADD THIS LINE ---

# Copy utils folder and its content
COPY utils/ /app/utils/
COPY sentiment_db_sink.py /app/sentiment_db_sink.py
COPY consumer.py /app/consumer.py

CMD ["python", "consumer.py"]