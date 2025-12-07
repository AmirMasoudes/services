-- PostgreSQL User Creation Script
-- Run this as postgres superuser: psql -U postgres -f create_postgres_user.sql

-- Create database if it doesn't exist
-- Replace 'vpnbot_db' with your actual database name from .env
SELECT 'CREATE DATABASE vpnbot_db'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'vpnbot_db')\gexec

-- Create user if it doesn't exist
-- Replace 'postgres' and 'your_password' with actual values from .env
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = 'postgres') THEN
        CREATE USER postgres WITH PASSWORD 'your_password';
    ELSE
        ALTER USER postgres WITH PASSWORD 'your_password';
    END IF;
END
$$;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE vpnbot_db TO postgres;
ALTER USER postgres CREATEDB;

-- Connect to the database and grant schema privileges
\c vpnbot_db
GRANT ALL ON SCHEMA public TO postgres;

