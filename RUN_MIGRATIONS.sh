#!/bin/bash
# Run migrations safely

echo "Step 1: Checking database connection..."
python manage.py check --database default

if [ $? -ne 0 ]; then
    echo "ERROR: Database connection failed. Check your .env file."
    exit 1
fi

echo "Step 2: Making migrations..."
python manage.py makemigrations

if [ $? -ne 0 ]; then
    echo "ERROR: makemigrations failed."
    exit 1
fi

echo "Step 3: Applying migrations..."
python manage.py migrate

if [ $? -ne 0 ]; then
    echo "ERROR: migrate failed."
    exit 1
fi

echo "Step 4: Running system checks..."
python manage.py check

echo "SUCCESS: All migrations completed!"

