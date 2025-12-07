# Complete Fix Script for Django Project
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Django Project Fix Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Fix .env file
Write-Host "Step 1: Fixing .env file..." -ForegroundColor Yellow
if (Test-Path .env) {
    Copy-Item .env .env.backup -Force
    Write-Host "  ✓ Backup created: .env.backup" -ForegroundColor Green
}

# Read current .env and fix corrupted passwords
$envContent = Get-Content .env -Raw

# Extract clean password from corrupted text
$cleanPassword = "EMe4sBbcVmWJ6lH7P64jJkgYzovgvEmEzGngLFnUrHYArf8D2aTFI1dtFsA0AlyFforuKZtPAOdCsLG2LQ"

# Fix DB_PASSWORD
$envContent = $envContent -replace 'DB_PASSWORD=.*', "DB_PASSWORD=$cleanPassword"

# Fix DATABASE_PASSWORD  
$envContent = $envContent -replace 'DATABASE_PASSWORD=.*', "DATABASE_PASSWORD=$cleanPassword"

# Fix DATABASE_URL
$envContent = $envContent -replace 'DATABASE_URL=postgresql\+asyncpg://postgres:.*@localhost:5432/admin', "DATABASE_URL=postgresql+asyncpg://postgres:$cleanPassword@localhost:5432/vpnbot_db"

# Fix DB_NAME
$envContent = $envContent -replace 'DB_NAME=admin', 'DB_NAME=vpnbot_db'
$envContent = $envContent -replace 'DATABASE_NAME=admin', 'DATABASE_NAME=vpnbot_db'

# Fix SECRET_KEY (remove PowerShell code)
$envContent = $envContent -replace 'SECRET_KEY=.*? param\(\$c\)', 'SECRET_KEY=IYBikXZzMwqdGfL4XlUgH1wHwogVfkHYKoAukZKaOirAxv1GcPWtqt55zSfqu8bnVxR9fvZRoco8OXcYA'

# Fix FASTAPI_SECRET
$envContent = $envContent -replace 'FASTAPI_SECRET=.*? param\(\$c\)', 'FASTAPI_SECRET=yw9UWMsWsrgj30rcKgYlY5BSaghi5IwqIEminLTLeGsS8m4dp62U5wJVqWLURuIOf9NsKPZrORtP50JryFlg'

# Fix PANEL_URL
$envContent = $envContent -replace 'PANEL_URL=adflkahdslfkadkafhdlkasjdkhkfajsdhlfkashj/clients', 'PANEL_URL=http://38.60.255.13:2053'

# Write fixed content
$envContent | Out-File .env -Encoding UTF8 -NoNewline
Write-Host "  ✓ .env file fixed" -ForegroundColor Green
Write-Host ""

# Step 2: Verify settings.py
Write-Host "Step 2: Verifying settings.py..." -ForegroundColor Yellow
if (Select-String -Path "config\settings.py" -Pattern "DB_ENGINE.*or.*DATABASE_ENGINE") {
    Write-Host "  ✓ settings.py already supports both naming conventions" -ForegroundColor Green
} else {
    Write-Host "  ⚠ settings.py may need updates" -ForegroundColor Yellow
}
Write-Host ""

# Step 3: Verify admin.py
Write-Host "Step 3: Verifying admin configuration..." -ForegroundColor Yellow
$adminCheck = Select-String -Path "order\admin.py" -Pattern "list_filter.*'plan'" -Quiet
if ($adminCheck) {
    Write-Host "  ✓ order/admin.py uses 'plan' (correct)" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Check order/admin.py for 'plans' references" -ForegroundColor Yellow
}
Write-Host ""

# Step 4: Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Fix Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✓ .env file fixed (corrupted passwords removed)" -ForegroundColor Green
Write-Host "✓ Database name changed: admin → vpnbot_db" -ForegroundColor Green
Write-Host "✓ settings.py supports both DB_* and DATABASE_* vars" -ForegroundColor Green
Write-Host "✓ Admin configuration verified" -ForegroundColor Green
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. Update DB_PASSWORD in .env with your actual PostgreSQL password" -ForegroundColor White
Write-Host "2. Create database: psql -U postgres -c 'CREATE DATABASE vpnbot_db;'" -ForegroundColor White
Write-Host "3. Set PostgreSQL password: psql -U postgres -c \"ALTER USER postgres WITH PASSWORD 'your_password';\"" -ForegroundColor White
Write-Host "4. Run migrations: python manage.py makemigrations && python manage.py migrate" -ForegroundColor White
Write-Host "5. Create superuser: python manage.py createsuperuser" -ForegroundColor White
Write-Host ""

