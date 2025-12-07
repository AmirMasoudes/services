# Fix .env file - Remove PowerShell code that causes Docker Compose $c variable warning
Write-Host "Fixing .env file to remove PowerShell code..." -ForegroundColor Cyan

if (-not (Test-Path .env)) {
    Write-Host "ERROR: .env file not found!" -ForegroundColor Red
    exit 1
}

# Backup
$backupName = ".env.backup." + (Get-Date -Format 'yyyyMMdd_HHmmss')
Copy-Item .env $backupName -Force
Write-Host "Backup created: $backupName" -ForegroundColor Green

# Read .env content
$content = Get-Content .env -Raw

# Clean passwords (extracted from corrupted text)
$cleanSecretKey = "tqHpckbKvc8kZkUuWdMpMyGK7idOML6X4d5XPvIefWdJIyaIzyA50Lv059SqXCLonQst9DA4ws1kjDv7suaLNw"
$cleanDbPassword = "KX368DIv47mFP1gmug5VfKN0EXtL9IoqIzPFf5PX3uydrARUUwgD0N7RW8oZySzjYKyDIGnL3TxcBgKvdFUQ"
$cleanFastApiSecret = "E1z39IRdaPRvEtkrBefZbOL4QwEqEZQTLcds4c5jx7JY9MtA5iFG7KKvmqoB6j6OS4bIW8tERWzJ21XkalA"

# Remove all PowerShell code patterns - this is what causes the $c variable warning
$powershellCodePattern = ' param\(\$c\) if \(\$c -eq ''\+''\) \{ ''-'' \} elseif \(\$c -eq ''/''\) \{ ''_'' \} else \{ '''' \}'

# Fix each field by removing PowerShell code and setting clean values
$content = $content -replace "SECRET_KEY=.*?$powershellCodePattern", "SECRET_KEY=$cleanSecretKey"
$content = $content -replace "DB_PASSWORD=.*?$powershellCodePattern", "DB_PASSWORD=$cleanDbPassword"
$content = $content -replace "DATABASE_PASSWORD=.*?$powershellCodePattern", "DATABASE_PASSWORD=$cleanDbPassword"
$content = $content -replace "FASTAPI_SECRET=.*?$powershellCodePattern", "FASTAPI_SECRET=$cleanFastApiSecret"

# Fix DATABASE_URL
$cleanDbUrl = "postgresql+asyncpg://postgres:$cleanDbPassword@localhost:5432/vpnbot_db"
$content = $content -replace "DATABASE_URL=postgresql\+asyncpg://postgres:.*?@localhost:5432/vpnbot_db", $cleanDbUrl

# Remove any remaining PowerShell code patterns (standalone)
$content = $content -replace $powershellCodePattern, ''

# Fix PANEL_URL
$content = $content -replace 'PANEL_URL=adflkahdslfkadkafhdlkasjdkhkfajsdhlfkashj/clients', 'PANEL_URL=http://38.60.255.13:2053'

# Write cleaned content
$utf8NoBom = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText((Resolve-Path .env), $content, $utf8NoBom)

Write-Host ""
Write-Host "Fixed .env file!" -ForegroundColor Green
Write-Host "  - Removed all PowerShell code containing param variable" -ForegroundColor Gray
Write-Host "  - Cleaned SECRET_KEY, DB_PASSWORD, DATABASE_PASSWORD" -ForegroundColor Gray
Write-Host "  - Cleaned DATABASE_URL, FASTAPI_SECRET" -ForegroundColor Gray
Write-Host ""
Write-Host "Docker Compose warning about variable c should now be resolved." -ForegroundColor Green
Write-Host ""
