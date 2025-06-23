FROM python:3.10-slim-buster

WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- CHANGE IS HERE ---
# Copy all the Dash application code (including app.py and all modularized files)
# This assumes that your app.py, layout.py, callbacks.py, data_handler.py,
# and constants.py are all in the same directory as this Dockerfile.
COPY . .
# --------------------

# Expose the port Dash runs on (default is 8050)
EXPOSE 8050

# Command to run the Dash application
CMD ["python", "app.py"]