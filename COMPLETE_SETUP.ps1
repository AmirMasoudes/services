# Complete Setup Script - Fixes everything and runs migrations
Write-Host ""
Write-Host "========================================" -ForegroundColor Magenta
Write-Host "  Complete Django Setup & Migration" -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Magenta
Write-Host ""

# Step 1: Fix database configuration
Write-Host "[1/6] Fixing database configuration..." -ForegroundColor Cyan
.\FIX_DATABASE.ps1
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ⚠ Database fix script had issues, continuing..." -ForegroundColor Yellow
}
Write-Host ""

# Step 2: Activate virtual environment
Write-Host "[2/6] Activating virtual environment..." -ForegroundColor Cyan
if (Test-Path "venv\Scripts\Activate.ps1") {
    & "venv\Scripts\Activate.ps1"
    Write-Host "  ✓ Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "  ✗ Virtual environment not found!" -ForegroundColor Red
    Write-Host "  Please create venv first: python -m venv venv" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# Step 3: Check Django system
Write-Host "[3/6] Running Django system check..." -ForegroundColor Cyan
$checkResult = python manage.py check 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ System check passed" -ForegroundColor Green
} else {
    Write-Host "  ⚠ System check found issues:" -ForegroundColor Yellow
    Write-Host $checkResult -ForegroundColor Gray
    Write-Host ""
    Write-Host "  Continuing anyway..." -ForegroundColor Yellow
}
Write-Host ""

# Step 4: Test database connection
Write-Host "[4/6] Testing database connection..." -ForegroundColor Cyan
$dbCheck = python manage.py check --database default 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Database connection successful" -ForegroundColor Green
} else {
    Write-Host "  ✗ Database connection failed!" -ForegroundColor Red
    Write-Host "  Error: $dbCheck" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Please:" -ForegroundColor Yellow
    Write-Host "  1. Ensure PostgreSQL is running" -ForegroundColor White
    Write-Host "  2. Check .env file has correct DB_PASSWORD" -ForegroundColor White
    Write-Host "  3. Verify database 'vpnbot_db' exists" -ForegroundColor White
    Write-Host ""
    exit 1
}
Write-Host ""

# Step 5: Create migrations
Write-Host "[5/6] Creating migrations..." -ForegroundColor Cyan
$makemigrations = python manage.py makemigrations 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Migrations created successfully" -ForegroundColor Green
    if ($makemigrations -match "No changes") {
        Write-Host "  (No new migrations needed)" -ForegroundColor Gray
    }
} else {
    Write-Host "  ✗ makemigrations failed!" -ForegroundColor Red
    Write-Host "  Error: $makemigrations" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 6: Apply migrations
Write-Host "[6/6] Applying migrations..." -ForegroundColor Cyan
$migrate = python manage.py migrate --noinput 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Migrations applied successfully" -ForegroundColor Green
} else {
    Write-Host "  ✗ migrate failed!" -ForegroundColor Red
    Write-Host "  Error: $migrate" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Final summary
Write-Host "========================================" -ForegroundColor Magenta
Write-Host "  Setup Complete!" -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Magenta
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Create superuser:" -ForegroundColor White
Write-Host "   python manage.py createsuperuser" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Start development server:" -ForegroundColor White
Write-Host "   python manage.py runserver" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Access admin panel:" -ForegroundColor White
Write-Host "   http://localhost:8000/admin" -ForegroundColor Gray
Write-Host ""

