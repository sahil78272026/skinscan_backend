FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Create non-root user
RUN groupadd -r skinscan && useradd -r -g skinscan skinscan

WORKDIR /app

# Install system deps needed by psycopg2-binary and Pillow
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev libjpeg62-turbo-dev && \
    rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Switch to non-root user
RUN chown -R skinscan:skinscan /app
USER skinscan

EXPOSE 8000

# Entrypoint: run migrations, then start gunicorn with uvicorn workers
COPY entrypoint.sh /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
