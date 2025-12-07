# ========================================
# COMPLETE SETUP SCRIPT
# Run this script to fix and setup everything
# ========================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Magenta
Write-Host "  Django Project Complete Setup" -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Magenta
Write-Host ""

# Step 1: Apply fixes
Write-Host "[1/6] Applying fixes to .env and configuration..." -ForegroundColor Cyan
.\APPLY_FIXES.ps1
Write-Host ""

# Step 2: Check PostgreSQL service
Write-Host "[2/6] Checking PostgreSQL service..." -ForegroundColor Cyan
$pgService = Get-Service postgresql* -ErrorAction SilentlyContinue | Where-Object {$_.Status -eq 'Running'}
if ($pgService) {
    Write-Host "  ✓ PostgreSQL is running: $($pgService.Name)" -ForegroundColor Green
} else {
    Write-Host "  ⚠ PostgreSQL service not found or not running" -ForegroundColor Yellow
    Write-Host "  Please start PostgreSQL manually:" -ForegroundColor Yellow
    Write-Host "    Start-Service postgresql-x64-17" -ForegroundColor Gray
    Write-Host ""
    $continue = Read-Host "Continue anyway? (y/N)"
    if ($continue -ne 'y') { exit }
}
Write-Host ""

# Step 3: Create database
Write-Host "[3/6] Creating PostgreSQL database..." -ForegroundColor Cyan
Write-Host "  Please enter PostgreSQL superuser password when prompted" -ForegroundColor Yellow
$dbResult = psql -U postgres -c "CREATE DATABASE vpnbot_db;" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Database created or already exists" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Database creation had issues (may already exist)" -ForegroundColor Yellow
}
Write-Host ""

# Step 4: Set PostgreSQL password
Write-Host "[4/6] Setting PostgreSQL user password..." -ForegroundColor Cyan
$newPassword = "EMe4sBbcVmWJ6lH7P64jJkgYzovgvEmEzGngLFnUrHYArf8D2aTFI1dtFsA0AlyFforuKZtPAOdCsLG2LQ"
Write-Host "  Setting password for user 'postgres'..." -ForegroundColor Yellow
$pwdResult = psql -U postgres -c "ALTER USER postgres WITH PASSWORD '$newPassword';" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Password updated" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Password update had issues" -ForegroundColor Yellow
}
Write-Host ""

# Step 5: Grant privileges
Write-Host "[5/6] Granting database privileges..." -ForegroundColor Cyan
$grantResult = psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE vpnbot_db TO postgres;" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Privileges granted" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Privilege grant had issues" -ForegroundColor Yellow
}
Write-Host ""

# Step 6: Test connection and run migrations
Write-Host "[6/6] Testing connection and running migrations..." -ForegroundColor Cyan
if (Test-Path "venv\Scripts\Activate.ps1") {
    & "venv\Scripts\Activate.ps1"
    Write-Host "  ✓ Virtual environment activated" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "  Testing database connection..." -ForegroundColor Yellow
    python manage.py check --database default 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Database connection successful" -ForegroundColor Green
        
        Write-Host ""
        Write-Host "  Running makemigrations..." -ForegroundColor Yellow
        python manage.py makemigrations 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ Migrations created" -ForegroundColor Green
        } else {
            Write-Host "  ⚠ makemigrations had issues" -ForegroundColor Yellow
        }
        
        Write-Host ""
        Write-Host "  Running migrate..." -ForegroundColor Yellow
        python manage.py migrate 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ Migrations applied" -ForegroundColor Green
        } else {
            Write-Host "  ⚠ migrate had issues" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  ✗ Database connection failed" -ForegroundColor Red
        Write-Host "  Check your .env file and PostgreSQL password" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ⚠ Virtual environment not found" -ForegroundColor Yellow
    Write-Host "  Please activate venv manually and run:" -ForegroundColor Yellow
    Write-Host "    python manage.py makemigrations" -ForegroundColor Gray
    Write-Host "    python manage.py migrate" -ForegroundColor Gray
}
Write-Host ""

# Final summary
Write-Host "========================================" -ForegroundColor Magenta
Write-Host "  Setup Complete!" -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Magenta
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Create superuser: python manage.py createsuperuser" -ForegroundColor White
Write-Host "2. Run server: python manage.py runserver" -ForegroundColor White
Write-Host "3. Access admin: http://localhost:8000/admin" -ForegroundColor White
Write-Host ""

