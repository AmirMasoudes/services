# Fix .env file by replacing corrupted passwords
Write-Host "Fixing .env file..." -ForegroundColor Cyan

# Backup original
Copy-Item .env .env.backup -Force
Write-Host "Backup created: .env.backup" -ForegroundColor Green

# Copy fixed version
Copy-Item .env.fixed .env -Force
Write-Host ".env file fixed!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Update DB_PASSWORD in .env with your actual PostgreSQL password" -ForegroundColor Yellow
Write-Host "2. Create PostgreSQL database: psql -U postgres -c 'CREATE DATABASE vpnbot_db;'" -ForegroundColor Yellow
Write-Host "3. Run: python manage.py migrate" -ForegroundColor Yellow

