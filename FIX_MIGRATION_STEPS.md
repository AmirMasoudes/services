# Migration Fix Steps

## Step 1: Update .env file

Add or update these variables in your `.env` file:

```env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=vpnbot_db
DB_USER=postgres
DB_PASSWORD=your_actual_password
DB_HOST=localhost
DB_PORT=5432
```

## Step 2: Create PostgreSQL User and Database

### Option A: Using psql (recommended)

```bash
# Connect as postgres superuser
psql -U postgres

# Then run:
CREATE DATABASE vpnbot_db;
CREATE USER postgres WITH PASSWORD 'your_actual_password';
GRANT ALL PRIVILEGES ON DATABASE vpnbot_db TO postgres;
ALTER USER postgres CREATEDB;
\q
```

### Option B: Using SQL file

```bash
# Edit create_postgres_user.sql with your actual password
# Then run:
psql -U postgres -f create_postgres_user.sql
```

## Step 3: Test Database Connection

```bash
python manage.py dbshell
# If connection works, type \q to exit
```

## Step 4: Delete Old Migrations (if needed)

If you have existing migrations that conflict:

```bash
# Backup first!
# Then delete migration files (keep __init__.py):
rm order/migrations/0001_initial.py
```

## Step 5: Create Fresh Migrations

```bash
python manage.py makemigrations
```

## Step 6: Apply Migrations

```bash
python manage.py migrate
```

## Step 7: Verify

```bash
python manage.py check
python manage.py showmigrations
```

## Troubleshooting

### If password authentication fails:
1. Check PostgreSQL is running: `pg_isready`
2. Check pg_hba.conf allows password authentication
3. Restart PostgreSQL: `sudo systemctl restart postgresql`

### If migration fails:
1. Check database connection: `python manage.py dbshell`
2. Check .env file has correct values
3. Verify settings.py reads from .env correctly

