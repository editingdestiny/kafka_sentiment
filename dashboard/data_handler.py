# data_handler.py
import pandas as pd
from sqlalchemy import text # Import text for SQLAlchemy 2.0 compatibility

def fetch_sentiment_data(engine, start_date=None, end_date=None, sentiment_labels=None, limit=1000):
    """
    Fetches sentiment data from the PostgreSQL database.
    
    Args:
        engine: SQLAlchemy database engine.
        start_date (str): Start date for filtering (YYYY-MM-DD).
        end_date (str): End date for filtering (YYYY-MM-DD).
        sentiment_labels (list): List of VADER sentiment labels to filter by.
        limit (int): Maximum number of records to retrieve.
        
    Returns:
        pd.DataFrame: DataFrame containing sentiment results.
    """
    try:
        query_parts = []
        params = {}

        sql_query = """
        SELECT
            id,
            title,
            description,
            url,
            vader_score,
            vader_label,
            textblob_score,
            textblob_label,
            transformer_score,
            transformer_label,
            created_at
        FROM
            sentiment_results
        """

        if start_date:
            query_parts.append("created_at >= :start_date")
            params['start_date'] = start_date
        if end_date:
            query_parts.append("created_at <= :end_date")
            params['end_date'] = end_date

        if sentiment_labels and len(sentiment_labels) > 0:
            sentiment_placeholders = ','.join([f":sentiment_{i}" for i in range(len(sentiment_labels))])
            query_parts.append(f"vader_label IN ({sentiment_placeholders})")
            for i, label in enumerate(sentiment_labels):
                params[f'sentiment_{i}'] = label

        if query_parts:
            sql_query += " WHERE " + " AND ".join(query_parts)

        sql_query += " ORDER BY created_at DESC LIMIT :limit;"
        params['limit'] = limit
        
        df = pd.read_sql(text(sql_query), engine, params=params)
        df['created_at'] = pd.to_datetime(df['created_at'])
        print(f"Fetched {len(df)} records from database with filters.", flush=True)
        return df
    except Exception as e:
        print(f"Error fetching data from database: {e}", flush=True)
        return pd.DataFrame()