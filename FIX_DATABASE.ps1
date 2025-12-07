# Complete Database Fix Script
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Database Configuration Fix" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Detect PostgreSQL setup
Write-Host "[1/5] Detecting PostgreSQL setup..." -ForegroundColor Yellow
$dockerRunning = docker ps --filter "name=postgres" --format "{{.Names}}" 2>&1 | Where-Object { $_ -notmatch "error|Cannot" }
$localPgRunning = Get-Service postgresql* -ErrorAction SilentlyContinue | Where-Object { $_.Status -eq 'Running' }

if ($dockerRunning) {
    Write-Host "  ✓ Docker PostgreSQL detected: $dockerRunning" -ForegroundColor Green
    $useDocker = $true
    $dbHost = "postgres"
} elseif ($localPgRunning) {
    Write-Host "  ✓ Local PostgreSQL detected: $($localPgRunning.Name)" -ForegroundColor Green
    $useDocker = $false
    $dbHost = "localhost"
} else {
    Write-Host "  ⚠ No PostgreSQL detected. Will configure for local PostgreSQL." -ForegroundColor Yellow
    $useDocker = $false
    $dbHost = "localhost"
}
Write-Host ""

# Step 2: Extract clean password from corrupted .env
Write-Host "[2/5] Fixing corrupted passwords in .env..." -ForegroundColor Yellow
$cleanPassword = "wpUfRbPwphJ4SWtfbYxJPEQptVhjCHQmCLjJOWsHP7bJjO7EtdAYDmqaHJlPxL993FPZXTnBY3Z2w4kuetHQ"

if (Test-Path .env) {
    Copy-Item .env .env.backup.$(Get-Date -Format 'yyyyMMdd_HHmmss') -Force
    Write-Host "  ✓ Backup created" -ForegroundColor Green
    
    $envContent = Get-Content .env -Raw
    
    # Remove PowerShell code from passwords
    $envContent = $envContent -replace ' param\(\$c\) if \(\$c -eq ''\+''\) \{ ''-'' \} elseif \(\$c -eq ''/''\) \{ ''_'' \} else \{ '''' \}', ''
    $envContent = $envContent -replace ' param\(\$c\) if \(\$c -eq ''\+''\) \{ ''-'' \} elseif \(\$c -eq ''/''\) \{ ''_'' \} else \{ '''' \} ', ''
    
    # Fix DB_PASSWORD
    $envContent = $envContent -replace '(?m)^DB_PASSWORD=.*$', "DB_PASSWORD=$cleanPassword"
    
    # Fix DATABASE_PASSWORD
    $envContent = $envContent -replace '(?m)^DATABASE_PASSWORD=.*$', "DATABASE_PASSWORD=$cleanPassword"
    
    # Fix DATABASE_URL
    $envContent = $envContent -replace 'DATABASE_URL=postgresql\+asyncpg://postgres:.*?@localhost:5432/vpnbot_db', "DATABASE_URL=postgresql+asyncpg://postgres:$cleanPassword@$dbHost:5432/vpnbot_db"
    
    # Fix DB_HOST based on detection
    $envContent = $envContent -replace '(?m)^DB_HOST=.*$', "DB_HOST=$dbHost"
    $envContent = $envContent -replace '(?m)^DATABASE_HOST=.*$', "DATABASE_HOST=$dbHost"
    
    # Ensure DB_NAME is correct
    $envContent = $envContent -replace '(?m)^DB_NAME=.*$', "DB_NAME=vpnbot_db"
    $envContent = $envContent -replace '(?m)^DATABASE_NAME=.*$', "DATABASE_NAME=vpnbot_db"
    
    # Write fixed content
    [System.IO.File]::WriteAllText((Resolve-Path .env), $envContent, [System.Text.Encoding]::UTF8)
    Write-Host "  ✓ .env file fixed" -ForegroundColor Green
} else {
    Write-Host "  ⚠ .env file not found" -ForegroundColor Yellow
}
Write-Host ""

# Step 3: Create/Update PostgreSQL database
Write-Host "[3/5] Setting up PostgreSQL database..." -ForegroundColor Yellow
if (-not $useDocker) {
    Write-Host "  Creating local database..." -ForegroundColor Gray
    Write-Host "  (You may be prompted for PostgreSQL superuser password)" -ForegroundColor Gray
    
    # Try to create database
    $createDb = psql -U postgres -c "CREATE DATABASE vpnbot_db;" 2>&1
    if ($LASTEXITCODE -eq 0 -or $createDb -match "already exists") {
        Write-Host "  ✓ Database vpnbot_db exists or created" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ Database creation had issues: $createDb" -ForegroundColor Yellow
    }
    
    # Update password
    $updatePwd = psql -U postgres -c "ALTER USER postgres WITH PASSWORD '$cleanPassword';" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ PostgreSQL user password updated" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ Password update had issues" -ForegroundColor Yellow
    }
    
    # Grant privileges
    $grant = psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE vpnbot_db TO postgres;" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Privileges granted" -ForegroundColor Green
    }
} else {
    Write-Host "  Using Docker PostgreSQL - no local setup needed" -ForegroundColor Gray
}
Write-Host ""

# Step 4: Test connection
Write-Host "[4/5] Testing database connection..." -ForegroundColor Yellow
if (Test-Path "venv\Scripts\Activate.ps1") {
    & "venv\Scripts\Activate.ps1" | Out-Null
    $testResult = python manage.py check --database default 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Database connection successful!" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Database connection failed" -ForegroundColor Red
        Write-Host "  Error: $testResult" -ForegroundColor Red
    }
} else {
    Write-Host "  ⚠ Virtual environment not found - skipping connection test" -ForegroundColor Yellow
}
Write-Host ""

# Step 5: Summary
Write-Host "[5/5] Summary" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Configuration:" -ForegroundColor Cyan
Write-Host "  Database Type: $(if ($useDocker) { 'Docker' } else { 'Local PostgreSQL 17' })" -ForegroundColor White
Write-Host "  DB_HOST: $dbHost" -ForegroundColor White
Write-Host "  DB_NAME: vpnbot_db" -ForegroundColor White
Write-Host "  DB_USER: postgres" -ForegroundColor White
Write-Host "  Password: [FIXED - cleaned from corrupted text]" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Run migrations: python manage.py makemigrations && python manage.py migrate" -ForegroundColor White
Write-Host "2. Create superuser: python manage.py createsuperuser" -ForegroundColor White
Write-Host "3. Start server: python manage.py runserver" -ForegroundColor White
if ($useDocker) {
    Write-Host ""
    Write-Host "OR use Docker:" -ForegroundColor Yellow
    Write-Host "  docker compose up -d" -ForegroundColor White
}
Write-Host ""

