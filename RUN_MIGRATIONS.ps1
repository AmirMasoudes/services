# PowerShell script to run migrations safely

Write-Host "Step 1: Checking database connection..." -ForegroundColor Cyan
python manage.py check --database default

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Database connection failed. Check your .env file." -ForegroundColor Red
    exit 1
}

Write-Host "Step 2: Making migrations..." -ForegroundColor Cyan
python manage.py makemigrations

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: makemigrations failed." -ForegroundColor Red
    exit 1
}

Write-Host "Step 3: Applying migrations..." -ForegroundColor Cyan
python manage.py migrate

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: migrate failed." -ForegroundColor Red
    exit 1
}

Write-Host "Step 4: Running system checks..." -ForegroundColor Cyan
python manage.py check

Write-Host "SUCCESS: All migrations completed!" -ForegroundColor Green

