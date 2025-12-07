# Final fix for .env file - Remove all PowerShell code causing Docker Compose $c warning
Write-Host "Fixing .env file..." -ForegroundColor Cyan

if (-not (Test-Path .env)) {
    Write-Host "ERROR: .env file not found!" -ForegroundColor Red
    exit 1
}

# Backup
$backupName = ".env.backup." + (Get-Date -Format 'yyyyMMdd_HHmmss')
Copy-Item .env $backupName -Force
Write-Host "Backup created: $backupName" -ForegroundColor Green

# Read .env line by line
$lines = Get-Content .env
$fixedLines = @()

foreach ($line in $lines) {
    $fixedLine = $line
    
    # Clean SECRET_KEY (Django Core) - remove everything after the clean key
    if ($fixedLine -match '^SECRET_KEY=' -and $fixedLine -notmatch '^SECRET_KEY=tqHpckbKvc8kZkUuWdMpMyGK7idOML6X4d5XPvIefWdJIyaIzyA50Lv059SqXCLonQst9DA4ws1kjDv7suaLNw$') {
        $fixedLine = "SECRET_KEY=tqHpckbKvc8kZkUuWdMpMyGK7idOML6X4d5XPvIefWdJIyaIzyA50Lv059SqXCLonQst9DA4ws1kjDv7suaLNw"
    }
    
    # Clean DB_PASSWORD - extract clean password
    if ($fixedLine -match '^DB_PASSWORD=') {
        $fixedLine = "DB_PASSWORD=KX368DIv47mFP1gmug5VfKN0EXtL9IoqIzPFf5PX3uydrARUUwgD0N7RW8oZySzjYKyDIGnL3TxcBgKvdFUQ"
    }
    
    # Clean DATABASE_PASSWORD
    if ($fixedLine -match '^DATABASE_PASSWORD=') {
        $fixedLine = "DATABASE_PASSWORD=KX368DIv47mFP1gmug5VfKN0EXtL9IoqIzPFf5PX3uydrARUUwgD0N7RW8oZySzjYKyDIGnL3TxcBgKvdFUQ"
    }
    
    # Clean DATABASE_URL
    if ($fixedLine -match '^DATABASE_URL=') {
        $fixedLine = "DATABASE_URL=postgresql+asyncpg://postgres:KX368DIv47mFP1gmug5VfKN0EXtL9IoqIzPFf5PX3uydrARUUwgD0N7RW8oZySzjYKyDIGnL3TxcBgKvdFUQ@localhost:5432/vpnbot_db"
    }
    
    # Clean SECRET_KEY (FastAPI section) - different value
    if ($fixedLine -match '^SECRET_KEY=' -and $fixedLines -contains 'FASTAPI') {
        $fixedLine = "SECRET_KEY=E1z39IRdaPRvEtkrBefZbOL4QwEqEZQTLcds4c5jx7JY9MtA5iFG7KKvmqoB6j6OS4bIW8tERWzJ21XkalA"
    }
    
    # Clean FASTAPI_SECRET
    if ($fixedLine -match '^FASTAPI_SECRET=') {
        $fixedLine = "FASTAPI_SECRET=E1z39IRdaPRvEtkrBefZbOL4QwEqEZQTLcds4c5jx7JY9MtA5iFG7KKvmqoB6j6OS4bIW8tERWzJ21XkalA"
    }
    
    # Remove any lines that are just PowerShell code
    if ($fixedLine -match '^\s*param\(') {
        continue
    }
    
    # Remove PowerShell code from any line
    $fixedLine = $fixedLine -replace '\s*param\(\$c\).*', ''
    
    # Fix PANEL_URL
    if ($fixedLine -match 'PANEL_URL=adflkahdslfkadkafhdlkasjdkhkfajsdhlfkashj') {
        $fixedLine = "PANEL_URL=http://38.60.255.13:2053"
    }
    
    $fixedLines += $fixedLine
}

# Write fixed content
$utf8NoBom = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllLines((Resolve-Path .env), $fixedLines, $utf8NoBom)

Write-Host ""
Write-Host "Fixed .env file!" -ForegroundColor Green
Write-Host "  - Removed all PowerShell code" -ForegroundColor Gray
Write-Host "  - Cleaned all password fields" -ForegroundColor Gray
Write-Host ""
Write-Host "Docker Compose warning about variable c should now be resolved." -ForegroundColor Green
Write-Host ""

