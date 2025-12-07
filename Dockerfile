# Multi-stage Dockerfile for VPN Bot Management System
# Supports both Django and FastAPI services

FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements files
COPY requirements.txt .
COPY backend/requirements.txt backend/requirements.txt

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install -r backend/requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs staticfiles media

# Note: Static files collection happens at runtime in docker-compose

# Expose ports
EXPOSE 8000 8001

# Default command (can be overridden in docker-compose)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

