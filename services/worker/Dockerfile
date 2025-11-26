FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY pyproject.toml .

# Install Python dependencies
RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi

# Copy worker code
COPY services/worker/ /app/worker/

# Set Python path
ENV PYTHONPATH=/app

# Run Celery worker
CMD ["celery", "-A", "worker.tasks", "worker", "--loglevel=info", "--concurrency=4"]
