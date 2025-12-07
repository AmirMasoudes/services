# Complete Setup Commands

## Step 1: Verify PostgreSQL is Running

```powershell
# Check PostgreSQL service status
Get-Service postgresql*

# If not running, start it:
Start-Service postgresql-x64-17
# OR for other versions:
# Start-Service postgresql-x64-16
# Start-Service postgresql-x64-15
```

## Step 2: Create PostgreSQL Database and User

```powershell
# Connect to PostgreSQL (you'll be prompted for postgres user password)
psql -U postgres

# Then run these SQL commands:
CREATE DATABASE vpnbot_db;
CREATE USER postgres WITH PASSWORD 'EMe4sBbcVmWJ6lH7P64jJkgYzovgvEmEzGngLFnUrHYArf8D2aTFI1dtFsA0AlyFforuKZtPAOdCsLG2LQ';
ALTER USER postgres CREATEDB;
GRANT ALL PRIVILEGES ON DATABASE vpnbot_db TO postgres;
\q
```

**OR** if the user already exists, just update the password:

```powershell
psql -U postgres -c "ALTER USER postgres WITH PASSWORD 'EMe4sBbcVmWJ6lH7P64jJkgYzovgvEmEzGngLFnUrHYArf8D2aTFI1dtFsA0AlyFforuKZtPAOdCsLG2LQ';"
psql -U postgres -c "CREATE DATABASE vpnbot_db;" 2>$null
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE vpnbot_db TO postgres;"
```

## Step 3: Test Database Connection

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Test connection
python manage.py check --database default
```

## Step 4: Run Migrations

```powershell
# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

## Step 5: Create Superuser

```powershell
python manage.py createsuperuser
# Follow prompts:
# id_tel: admin
# username_tel: admin
# full_name: Admin User
# Password: (enter your password)
```

## Step 6: Run Development Server

```powershell
python manage.py runserver
```

## Troubleshooting

### If PostgreSQL password authentication fails:

1. **Check pg_hba.conf** (usually at `C:\Program Files\PostgreSQL\17\data\pg_hba.conf`):
   - Find line: `host    all             all             127.0.0.1/32            scram-sha-256`
   - If it says `ident` or `peer`, change to `scram-sha-256` or `md5`
   - Restart PostgreSQL: `Restart-Service postgresql-x64-17`

2. **Reset PostgreSQL password**:
   ```powershell
   # Connect as postgres user
   psql -U postgres
   # Then:
   ALTER USER postgres WITH PASSWORD 'EMe4sBbcVmWJ6lH7P64jJkgYzovgvEmEzGngLFnUrHYArf8D2aTFI1dtFsA0AlyFforuKZtPAOdCsLG2LQ';
   \q
   ```

3. **Test connection manually**:
   ```powershell
   psql -U postgres -d vpnbot_db -h localhost
   # Enter password when prompted
   ```

### If migrations fail:

```powershell
# Check for pending migrations
python manage.py showmigrations

# If needed, reset migrations (WARNING: deletes data)
python manage.py migrate order zero
python manage.py migrate
```

## Quick All-in-One Script

Save this as `setup.ps1`:

```powershell
# Setup script
Write-Host "Step 1: Creating database..." -ForegroundColor Cyan
$env:PGPASSWORD = "your_postgres_superuser_password"
psql -U postgres -c "CREATE DATABASE vpnbot_db;" 2>$null
psql -U postgres -c "ALTER USER postgres WITH PASSWORD 'EMe4sBbcVmWJ6lH7P64jJkgYzovgvEmEzGngLFnUrHYArf8D2aTFI1dtFsA0AlyFforuKZtPAOdCsLG2LQ';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE vpnbot_db TO postgres;"

Write-Host "Step 2: Activating virtual environment..." -ForegroundColor Cyan
.\venv\Scripts\Activate.ps1

Write-Host "Step 3: Running migrations..." -ForegroundColor Cyan
python manage.py makemigrations
python manage.py migrate

Write-Host "Step 4: Creating superuser..." -ForegroundColor Cyan
python manage.py createsuperuser

Write-Host "Setup complete!" -ForegroundColor Green
```

