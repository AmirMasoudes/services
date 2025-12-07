#!/bin/bash
# Entrypoint script for Bot containers

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

echo "Waiting for Django..."
while ! nc -z django 8000; do
  sleep 0.1
done
echo "Django is ready"

echo "Starting bot..."
exec "$@"

