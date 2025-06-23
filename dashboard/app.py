# app.py
import dash
from sqlalchemy import create_engine
import os
import time
import sys
import dash_bootstrap_components as dbc

# Import modularized components
from layout import create_layout
from callbacks import register_callbacks

# --- Database Connection Configuration ---
DB_USER = os.getenv('POSTGRES_USER', 'sd22750')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'your_secure_password')
DB_HOST = os.getenv('POSTGRES_HOST', 'postgres')
DB_NAME = os.getenv('POSTGRES_DB', 'sentiment')
DB_PORT = os.getenv('POSTGRES_PORT', '5432')

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# --- Database Engine Initialization with Retry Logic ---
engine = None
max_db_retries = 20
db_retry_delay_seconds = 5

print(f"Attempting to connect to PostgreSQL for Dash app at {DB_HOST}:{DB_PORT}/{DB_NAME}...", flush=True)
for i in range(max_db_retries):
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            pass # Simple connection test
        print("Successfully connected to PostgreSQL for Dash app!", flush=True)
        break
    except Exception as e:
        print(f"Attempt {i+1}/{max_db_retries}: PostgreSQL not yet available for Dash app or connection error: {e}. Retrying in {db_retry_delay_seconds} seconds...", flush=True)
        time.sleep(db_retry_delay_seconds)

if engine is None:
    print("Failed to connect to PostgreSQL for Dash app after multiple retries. Exiting.", flush=True)
    sys.exit(1)

# --- Dash App Initialization ---
app = dash.Dash(__name__,
                url_base_pathname='/sentimentdashboard/',  # <-- This must match the PathPrefix
                external_stylesheets=[dbc.themes.CYBORG], update_title='Updating...',
                meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}])

# --- Set the layout ---

# --- Set the layout ---
app.layout = create_layout()

# --- Register callbacks ---
register_callbacks(app, engine) # Pass the engine to callbacks

# --- Run the Dash App ---
if __name__ == '__main__':
    print("Starting Dash app...", flush=True)
    app.run(debug=True, host='0.0.0.0', port=8050)