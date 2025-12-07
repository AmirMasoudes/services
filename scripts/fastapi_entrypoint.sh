#!/bin/bash
# Entrypoint script for FastAPI container

set -e

echo "Waiting for PostgreSQL..."
while ! nc -z postgres 5432; do
  sleep 0.1
done
echo "PostgreSQL is ready"

echo "Waiting for Redis..."
while ! nc -z redis 6379; do
  sleep 0.1
done
echo "Redis is ready"

echo "Running Alembic migrations..."
cd backend
alembic upgrade head || echo "Alembic migrations skipped or failed"
cd ..

echo "Starting FastAPI application..."
exec "$@"

