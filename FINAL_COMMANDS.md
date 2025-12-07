# Final Migration Commands

## Quick Start (Windows PowerShell)

```powershell
# 1. Update .env file with PostgreSQL credentials
# Edit .env and add:
# DB_ENGINE=django.db.backends.postgresql
# DB_NAME=vpnbot_db
# DB_USER=postgres
# DB_PASSWORD=your_password
# DB_HOST=localhost
# DB_PORT=5432

# 2. Create PostgreSQL database and user
psql -U postgres -c "CREATE DATABASE vpnbot_db;"
psql -U postgres -c "CREATE USER postgres WITH PASSWORD 'your_password';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE vpnbot_db TO postgres;"
psql -U postgres -c "ALTER USER postgres CREATEDB;"

# 3. Run migrations
.\RUN_MIGRATIONS.ps1
```

## Step-by-Step Commands

### Step 1: Configure .env
```powershell
# Add to .env file:
DB_ENGINE=django.db.backends.postgresql
DB_NAME=vpnbot_db
DB_USER=postgres
DB_PASSWORD=your_actual_password_here
DB_HOST=localhost
DB_PORT=5432
```

### Step 2: Create PostgreSQL Database
```powershell
# Connect to PostgreSQL
psql -U postgres

# Run these SQL commands:
CREATE DATABASE vpnbot_db;
CREATE USER postgres WITH PASSWORD 'your_actual_password_here';
GRANT ALL PRIVILEGES ON DATABASE vpnbot_db TO postgres;
ALTER USER postgres CREATEDB;
\q
```

### Step 3: Test Database Connection
```powershell
python manage.py check --database default
```

### Step 4: Make Migrations
```powershell
python manage.py makemigrations
```

### Step 5: Apply Migrations
```powershell
python manage.py migrate
```

### Step 6: Verify
```powershell
python manage.py check
python manage.py showmigrations
```

## Alternative: Use SQL File

```powershell
# Edit create_postgres_user.sql with your password
# Then run:
psql -U postgres -f create_postgres_user.sql
```

## Files Updated

1. **config/settings.py** - Now reads both DB_* and DATABASE_* env vars
2. **order/models.py** - Plan field is now ForeignKey (not OneToOne)
3. **order/migrations/0002_*.py** - Migrates plans → plan field
4. **order/migrations/0003_*.py** - Makes plan field required

## Troubleshooting

### Password Authentication Failed
```powershell
# Check PostgreSQL is running
pg_isready

# Check pg_hba.conf allows password auth
# Location: C:\Program Files\PostgreSQL\<version>\data\pg_hba.conf
# Should have: host all all 127.0.0.1/32 md5
```

### Migration Errors
```powershell
# If migration fails, check:
python manage.py dbshell
# Then: \dt to see tables
# Then: \q to exit
```

### Reset Migrations (if needed)
```powershell
# WARNING: This deletes data!
python manage.py migrate order zero
python manage.py migrate
```

