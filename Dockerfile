# Multi-stage Dockerfile for Color Correction System

# Base Python image
FROM python:3.11-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry

WORKDIR /app

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Install dependencies
RUN poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi

# Stage for libraries
FROM base as libs

# Copy library source code
COPY libs/ /app/libs/

# Install libraries in development mode
RUN cd /app/libs/cv && pip install -e . && \
    cd /app/libs/ml && pip install -e .

# Final stage for production
FROM libs as production

# Copy services
COPY services/ /app/services/

# Set Python path
ENV PYTHONPATH=/app

# Expose ports
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command (can be overridden)
CMD ["uvicorn", "services.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
