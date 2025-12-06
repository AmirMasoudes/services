# VPN Bot Management System - Automated Setup Script
# Production-ready PowerShell automation
# Compatible with PowerShell 5+ and PowerShell 7
# ASCII-only, no special characters

#Requires -Version 5.0

$ErrorActionPreference = "Stop"
$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$LogDir = Join-Path $ScriptRoot "logs"
$EnvFile = Join-Path $ScriptRoot ".env"
$VenvPath = Join-Path $ScriptRoot ".venv"
$ErrorLog = Join-Path $LogDir "error.log"

function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "[OK] $Message" -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    try {
        Add-Content -Path $ErrorLog -Value "$timestamp - ERROR: $Message" -ErrorAction SilentlyContinue
    } catch {
        # Ignore log write errors
    }
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

function Initialize-LogDirectory {
    try {
        if (-not (Test-Path $LogDir)) {
            New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
            Write-Success "Logs directory created"
        }
    } catch {
        Write-Error "Failed to create logs directory: $_"
        throw
    }
}

function Test-PythonInstalled {
    try {
        Write-Info "Checking Python installation..."
        if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
            Write-Error "Python is not installed or not in PATH"
            Write-Info "Please install Python 3.10+ from https://www.python.org/"
            throw "Python not found"
        }
        
        $versionOutput = python --version 2>&1
        Write-Success "Python found: $versionOutput"
        
        $versionMatch = $versionOutput -match "Python (\d+)\.(\d+)"
        if ($versionMatch) {
            $major = [int]$matches[1]
            $minor = [int]$matches[2]
            if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 10)) {
                Write-Error "Python 3.10+ is required. Found: $versionOutput"
                throw "Python version too old"
            }
        }
    } catch {
        Write-Error "Python check failed: $_"
        throw
    }
}

function Ask-Value {
    param(
        [string]$Prompt,
        [string]$DefaultValue = "",
        [switch]$IsPassword = $false,
        [switch]$Required = $true
    )
    
    $fullPrompt = $Prompt
    if ($DefaultValue) {
        $fullPrompt += " (default: $DefaultValue)"
    }
    if ($Required) {
        $fullPrompt += " [REQUIRED]"
    }
    $fullPrompt += ": "
    
    if ($IsPassword) {
        $secureInput = Read-Host $fullPrompt -AsSecureString
        $value = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
            [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureInput)
        )
    } else {
        $value = Read-Host $fullPrompt
    }
    
    if ([string]::IsNullOrWhiteSpace($value)) {
        if ($Required -and [string]::IsNullOrWhiteSpace($DefaultValue)) {
            Write-Error "This field is required!"
            return Ask-Value -Prompt $Prompt -DefaultValue $DefaultValue -IsPassword:$IsPassword -Required:$Required
        }
        $value = $DefaultValue
    }
    
    return $value
}

function Generate-SecretKey {
    try {
        $bytes = New-Object byte[] 50
        $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
        $rng.GetBytes($bytes)
        $secret = [Convert]::ToBase64String($bytes)
        $secret = $secret -replace '[+/=]', { param($c) if ($c -eq '+') { '-' } elseif ($c -eq '/') { '_' } else { '' } }
        return $secret
    } catch {
        $fallback = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 50 | ForEach-Object {[char]$_})
        return $fallback
    }
}

function Collect-MinimalConfig {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Magenta
    Write-Host "Minimal Configuration (3 inputs only)" -ForegroundColor Magenta
    Write-Host "========================================" -ForegroundColor Magenta
    Write-Host ""
    Write-Host "Only 3 values required. Everything else will be auto-generated." -ForegroundColor Yellow
    Write-Host ""
    
    $config = @{}
    
    $config.SERVER_IP = Ask-Value -Prompt "Enter server IP" -DefaultValue "127.0.0.1" -Required $true
    $config.PANEL_USERNAME = Ask-Value -Prompt "Enter panel username" -DefaultValue "admin" -Required $true
    $config.PANEL_PASSWORD = Ask-Value -Prompt "Enter panel password" -IsPassword -Required $true
    
    Write-Host ""
    Write-Info "Auto-generating all other configuration values..."
    
    $config.SECRET_KEY = Generate-SecretKey
    $config.FASTAPI_SECRET_KEY = Generate-SecretKey
    $config.DEBUG = "False"
    $config.ALLOWED_HOSTS = "$($config.SERVER_IP),localhost,127.0.0.1"
    $config.DB_ENGINE = "django.db.backends.sqlite3"
    $config.DB_NAME = "db.sqlite3"
    $config.DB_USER = ""
    $config.DB_PASSWORD = ""
    $config.DB_HOST = ""
    $config.DB_PORT = ""
    $config.DATABASE_URL = ""
    $config.DATABASE_POOL_SIZE = "10"
    $config.DATABASE_MAX_OVERFLOW = "20"
    $config.CSRF_TRUSTED_ORIGINS = "http://$($config.SERVER_IP),https://$($config.SERVER_IP),http://localhost,https://localhost"
    $config.SECURE_HSTS_SECONDS = "0"
    $config.SECURE_SSL_REDIRECT = "False"
    $config.SESSION_COOKIE_SECURE = "False"
    $config.CSRF_COOKIE_SECURE = "False"
    $config.ADMIN_BOT_TOKEN = "YOUR_ADMIN_BOT_TOKEN_HERE"
    $config.USER_BOT_TOKEN = "YOUR_USER_BOT_TOKEN_HERE"
    $config.ADMIN_PASSWORD = $config.PANEL_PASSWORD
    $config.ADMIN_USER_IDS = "123456789"
    $config.XUI_DEFAULT_HOST = $config.SERVER_IP
    $config.XUI_DEFAULT_PORT = "2053"
    $config.XUI_DEFAULT_USERNAME = $config.PANEL_USERNAME
    $config.XUI_DEFAULT_PASSWORD = $config.PANEL_PASSWORD
    $config.XUI_WEB_BASE_PATH = "/app/"
    $config.XUI_USE_SSL = "False"
    $config.XUI_VERIFY_SSL = "False"
    $config.XUI_TIMEOUT = "30"
    $config.SUI_HOST = $config.SERVER_IP
    $config.SUI_PORT = "2095"
    $config.SUI_USE_SSL = "False"
    $config.SUI_BASE_PATH = "/app"
    $config.SUI_API_TOKEN = ""
    $config.SUI_BASE_URL = "http://$($config.SERVER_IP):2095"
    $config.SUI_API_KEY = ""
    $config.SERVER_DOMAIN = $config.SERVER_IP
    $config.SERVER_PORT = "8000"
    $config.SERVER_PROTOCOL = "http"
    $config.DEFAULT_PROTOCOL = "vless"
    $config.MIN_PORT = "10000"
    $config.MAX_PORT = "65000"
    $config.TLS_ENABLED = "True"
    $config.REALITY_ENABLED = "True"
    $config.REALITY_DEST = "www.aparat.com:443"
    $config.REALITY_SERVER_NAMES = "www.aparat.com"
    $config.REALITY_PRIVATE_KEY = Generate-SecretKey
    $config.WS_PATH = "/"
    $config.WS_HOST = ""
    $config.TRIAL_HOURS = "24"
    $config.PAID_DAYS = "30"
    $config.EXPIRY_WARNING_HOURS = "6"
    $config.EXPIRY_WARNING_MESSAGE = "Config expires in {hours} hours"
    $config.TRIAL_INBOUND_PREFIX = "TrialBot"
    $config.PAID_INBOUND_PREFIX = "PaidBot"
    $config.USER_INBOUND_PREFIX = "UserBot"
    $config.CONNECTION_TIMEOUT = "15"
    $config.RETRY_ATTEMPTS = "5"
    $config.REDIS_URL = "redis://localhost:6379/0"
    $config.REDIS_CACHE_TTL = "3600"
    $config.CELERY_BROKER_URL = "redis://localhost:6379/1"
    $config.CELERY_RESULT_BACKEND = "redis://localhost:6379/2"
    $config.ENVIRONMENT = "development"
    $config.FASTAPI_HOST = "0.0.0.0"
    $config.FASTAPI_PORT = "8001"
    $config.ALGORITHM = "HS256"
    $config.ACCESS_TOKEN_EXPIRE_MINUTES = "30"
    $config.REFRESH_TOKEN_EXPIRE_DAYS = "7"
    $config.CORS_ORIGINS = "http://localhost:3000,http://localhost:5173"
    $config.CORS_ALLOW_CREDENTIALS = "True"
    
    Write-Success "Configuration generated"
    return $config
}

function Generate-EnvFile {
    param([hashtable]$Config)
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Magenta
    Write-Host "Generating .env File" -ForegroundColor Magenta
    Write-Host "========================================" -ForegroundColor Magenta
    Write-Host ""
    
    $envContent = @"
# Auto-generated environment configuration
# Generated on: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
# Only 3 values were provided by user, rest auto-generated

# Django Core
SECRET_KEY=$($Config.SECRET_KEY)
DEBUG=$($Config.DEBUG)
ALLOWED_HOSTS=$($Config.ALLOWED_HOSTS)

# Database
DB_ENGINE=$($Config.DB_ENGINE)
DB_NAME=$($Config.DB_NAME)
DB_USER=$($Config.DB_USER)
DB_PASSWORD=$($Config.DB_PASSWORD)
DB_HOST=$($Config.DB_HOST)
DB_PORT=$($Config.DB_PORT)

# FastAPI Database (optional - uses SQLite fallback if empty)
DATABASE_URL=$($Config.DATABASE_URL)
DATABASE_POOL_SIZE=$($Config.DATABASE_POOL_SIZE)
DATABASE_MAX_OVERFLOW=$($Config.DATABASE_MAX_OVERFLOW)

# Security
CSRF_TRUSTED_ORIGINS=$($Config.CSRF_TRUSTED_ORIGINS)
SECURE_HSTS_SECONDS=$($Config.SECURE_HSTS_SECONDS)
SECURE_SSL_REDIRECT=$($Config.SECURE_SSL_REDIRECT)
SESSION_COOKIE_SECURE=$($Config.SESSION_COOKIE_SECURE)
CSRF_COOKIE_SECURE=$($Config.CSRF_COOKIE_SECURE)

# Telegram Bots
ADMIN_BOT_TOKEN=$($Config.ADMIN_BOT_TOKEN)
USER_BOT_TOKEN=$($Config.USER_BOT_TOKEN)
ADMIN_PASSWORD=$($Config.ADMIN_PASSWORD)
ADMIN_USER_IDS=$($Config.ADMIN_USER_IDS)

# X-UI Panel
XUI_DEFAULT_HOST=$($Config.XUI_DEFAULT_HOST)
XUI_DEFAULT_PORT=$($Config.XUI_DEFAULT_PORT)
XUI_DEFAULT_USERNAME=$($Config.XUI_DEFAULT_USERNAME)
XUI_DEFAULT_PASSWORD=$($Config.XUI_DEFAULT_PASSWORD)
XUI_WEB_BASE_PATH=$($Config.XUI_WEB_BASE_PATH)
XUI_USE_SSL=$($Config.XUI_USE_SSL)
XUI_VERIFY_SSL=$($Config.XUI_VERIFY_SSL)
XUI_TIMEOUT=$($Config.XUI_TIMEOUT)

# S-UI Panel
SUI_HOST=$($Config.SUI_HOST)
SUI_PORT=$($Config.SUI_PORT)
SUI_USE_SSL=$($Config.SUI_USE_SSL)
SUI_BASE_PATH=$($Config.SUI_BASE_PATH)
SUI_API_TOKEN=$($Config.SUI_API_TOKEN)
SUI_BASE_URL=$($Config.SUI_BASE_URL)
SUI_API_KEY=$($Config.SUI_API_KEY)
SUI_DEFAULT_TIMEOUT=30
SUI_MAX_RETRIES=3

# Server Configuration
SERVER_IP=$($Config.SERVER_IP)
SERVER_DOMAIN=$($Config.SERVER_DOMAIN)
SERVER_PORT=$($Config.SERVER_PORT)
SERVER_PROTOCOL=$($Config.SERVER_PROTOCOL)

# VPN Protocol
DEFAULT_PROTOCOL=$($Config.DEFAULT_PROTOCOL)
MIN_PORT=$($Config.MIN_PORT)
MAX_PORT=$($Config.MAX_PORT)
TLS_ENABLED=$($Config.TLS_ENABLED)
REALITY_ENABLED=$($Config.REALITY_ENABLED)
REALITY_DEST=$($Config.REALITY_DEST)
REALITY_SERVER_NAMES=$($Config.REALITY_SERVER_NAMES)
REALITY_PRIVATE_KEY=$($Config.REALITY_PRIVATE_KEY)
WS_PATH=$($Config.WS_PATH)
WS_HOST=$($Config.WS_HOST)

# Trial and Plan
TRIAL_HOURS=$($Config.TRIAL_HOURS)
PAID_DAYS=$($Config.PAID_DAYS)
EXPIRY_WARNING_HOURS=$($Config.EXPIRY_WARNING_HOURS)
EXPIRY_WARNING_MESSAGE=$($Config.EXPIRY_WARNING_MESSAGE)

# Naming Prefixes
TRIAL_INBOUND_PREFIX=$($Config.TRIAL_INBOUND_PREFIX)
PAID_INBOUND_PREFIX=$($Config.PAID_INBOUND_PREFIX)
USER_INBOUND_PREFIX=$($Config.USER_INBOUND_PREFIX)

# Connection Settings
CONNECTION_TIMEOUT=$($Config.CONNECTION_TIMEOUT)
RETRY_ATTEMPTS=$($Config.RETRY_ATTEMPTS)

# Redis
REDIS_URL=$($Config.REDIS_URL)
REDIS_CACHE_TTL=$($Config.REDIS_CACHE_TTL)

# Celery
CELERY_BROKER_URL=$($Config.CELERY_BROKER_URL)
CELERY_RESULT_BACKEND=$($Config.CELERY_RESULT_BACKEND)

# FastAPI
ENVIRONMENT=$($Config.ENVIRONMENT)
HOST=$($Config.FASTAPI_HOST)
PORT=$($Config.FASTAPI_PORT)
SECRET_KEY=$($Config.FASTAPI_SECRET_KEY)
ALGORITHM=$($Config.ALGORITHM)
ACCESS_TOKEN_EXPIRE_MINUTES=$($Config.ACCESS_TOKEN_EXPIRE_MINUTES)
REFRESH_TOKEN_EXPIRE_DAYS=$($Config.REFRESH_TOKEN_EXPIRE_DAYS)
CORS_ORIGINS=$($Config.CORS_ORIGINS)
CORS_ALLOW_CREDENTIALS=$($Config.CORS_ALLOW_CREDENTIALS)
"@
    
    try {
        $envContent | Out-File -FilePath $EnvFile -Encoding UTF8 -Force
        Write-Success ".env file created at $EnvFile"
    } catch {
        Write-Error "Failed to create .env file: $_"
        throw
    }
}

function Setup-Venv {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Magenta
    Write-Host "Setting Up Virtual Environment" -ForegroundColor Magenta
    Write-Host "========================================" -ForegroundColor Magenta
    Write-Host ""
    
    try {
        if (Test-Path $VenvPath) {
            Write-Warning "Virtual environment already exists"
            $recreate = Ask-Value -Prompt "Recreate virtual environment? (yes/no)" -DefaultValue "no" -Required $false
            if ($recreate -eq "yes" -or $recreate -eq "y") {
                Remove-Item -Path $VenvPath -Recurse -Force
                Write-Success "Old virtual environment removed"
            } else {
                Write-Info "Using existing virtual environment"
                return
            }
        }
        
        Write-Info "Creating virtual environment..."
        python -m venv $VenvPath
        
        if (-not (Test-Path $VenvPath)) {
            Write-Error "Failed to create virtual environment"
            throw "Virtual environment creation failed"
        }
        
        Write-Success "Virtual environment created"
    } catch {
        Write-Error "Virtual environment setup failed: $_"
        throw
    }
}

function Install-Dependencies {
    param([hashtable]$Config)
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Magenta
    Write-Host "Installing Dependencies" -ForegroundColor Magenta
    Write-Host "========================================" -ForegroundColor Magenta
    Write-Host ""
    
    try {
        $pythonExe = Join-Path $VenvPath "Scripts\python.exe"
        $pipExe = Join-Path $VenvPath "Scripts\pip.exe"
        
        if (-not (Test-Path $pythonExe)) {
            Write-Error "Python executable not found in virtual environment"
            throw "Virtual environment incomplete"
        }
        
        Write-Info "Upgrading pip..."
        & $pythonExe -m pip install --upgrade pip --quiet 2>&1 | Out-Null
        
        $requirementsFile = Join-Path $ScriptRoot "requirements.txt"
        if (Test-Path $requirementsFile) {
            Write-Info "Installing Django requirements..."
            & $pipExe install -r $requirementsFile 2>&1 | Out-Null
            if ($LASTEXITCODE -ne 0) {
                Write-Error "Failed to install Django requirements"
                throw "Requirements installation failed"
            }
            Write-Success "Django requirements installed"
        } else {
            Write-Warning "requirements.txt not found"
        }
        
        $backendRequirements = Join-Path $ScriptRoot "backend\requirements.txt"
        if (Test-Path $backendRequirements) {
            Write-Info "Installing FastAPI requirements..."
            & $pipExe install -r $backendRequirements 2>&1 | Out-Null
            if ($LASTEXITCODE -ne 0) {
                Write-Warning "FastAPI requirements installation had issues, continuing..."
            } else {
                Write-Success "FastAPI requirements installed"
            }
        }
        
        Write-Info "Installing additional dependencies..."
        & $pipExe install aiosqlite --quiet 2>&1 | Out-Null
        
    } catch {
        Write-Error "Dependency installation failed: $_"
        throw
    }
}

function Init-Django {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Magenta
    Write-Host "Initializing Django" -ForegroundColor Magenta
    Write-Host "========================================" -ForegroundColor Magenta
    Write-Host ""
    
    try {
        $pythonExe = Join-Path $VenvPath "Scripts\python.exe"
        $managePy = Join-Path $ScriptRoot "manage.py"
        
        if (-not (Test-Path $managePy)) {
            Write-Warning "manage.py not found, skipping Django setup"
            return
        }
        
        Write-Info "Creating migrations..."
        $makemigrationsLog = Join-Path $LogDir "django_makemigrations.log"
        & $pythonExe $managePy makemigrations 2>&1 | Out-File -FilePath $makemigrationsLog
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "makemigrations had issues, check log: $makemigrationsLog"
        } else {
            Write-Success "Migrations created"
        }
        
        Write-Info "Applying migrations..."
        $migrateLog = Join-Path $LogDir "django_migrate.log"
        & $pythonExe $managePy migrate 2>&1 | Out-File -FilePath $migrateLog
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Migration failed, check log: $migrateLog"
            throw "Django migration failed"
        }
        Write-Success "Migrations applied"
        
        $createSuperuser = Ask-Value -Prompt "Create Django superuser? (yes/no)" -DefaultValue "no" -Required $false
        if ($createSuperuser -eq "yes" -or $createSuperuser -eq "y") {
            Write-Info "Creating superuser..."
            & $pythonExe $managePy createsuperuser
            Write-Success "Superuser creation completed"
        }
    } catch {
        Write-Error "Django initialization failed: $_"
        throw
    }
}

function Init-FastAPI {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Magenta
    Write-Host "Initializing FastAPI" -ForegroundColor Magenta
    Write-Host "========================================" -ForegroundColor Magenta
    Write-Host ""
    
    try {
        $pythonExe = Join-Path $VenvPath "Scripts\python.exe"
        $alembicIni = Join-Path $ScriptRoot "backend\alembic.ini"
        
        if (-not (Test-Path $alembicIni)) {
            Write-Warning "alembic.ini not found, skipping FastAPI database setup"
            return
        }
        
        Write-Info "Running Alembic migrations..."
        Push-Location (Join-Path $ScriptRoot "backend")
        try {
            $alembicLog = Join-Path $LogDir "alembic_upgrade.log"
            & $pythonExe -m alembic upgrade head 2>&1 | Out-File -FilePath $alembicLog
            if ($LASTEXITCODE -ne 0) {
                Write-Warning "Alembic migration had issues, check log: $alembicLog"
                Write-Info "FastAPI will use SQLite fallback if DATABASE_URL is not set"
            } else {
                Write-Success "Alembic migrations applied"
            }
        } finally {
            Pop-Location
        }
    } catch {
        Write-Warning "FastAPI initialization had issues: $_"
        Write-Info "FastAPI will continue with fallback configuration"
    }
}

function Start-Services {
    param([hashtable]$Config)
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Magenta
    Write-Host "Starting Services" -ForegroundColor Magenta
    Write-Host "========================================" -ForegroundColor Magenta
    Write-Host ""
    
    try {
        $pythonExe = Join-Path $VenvPath "Scripts\python.exe"
        $managePy = Join-Path $ScriptRoot "manage.py"
        $fastApiMain = Join-Path $ScriptRoot "backend\app\main.py"
        
        if (Test-Path $managePy) {
            Write-Info "Starting Django server in new window..."
            $djangoLog = Join-Path $LogDir "django.log"
            $djangoCmd = "cd `"$ScriptRoot`"; `"$pythonExe`" `"$managePy`" runserver 0.0.0.0:8000 2>&1 | Tee-Object -FilePath `"$djangoLog`""
            Start-Process powershell -ArgumentList "-NoExit", "-Command", $djangoCmd
            Start-Sleep -Seconds 2
            Write-Success "Django server started (Terminal 1)"
        }
        
        if (Test-Path $fastApiMain) {
            Write-Info "Starting FastAPI server in new window..."
            $apiLog = Join-Path $LogDir "api.log"
            $fastApiCmd = "cd `"$ScriptRoot`"; `"$pythonExe`" -m uvicorn backend.app.main:app --host $($Config.FASTAPI_HOST) --port $($Config.FASTAPI_PORT) --reload 2>&1 | Tee-Object -FilePath `"$apiLog`""
            Start-Process powershell -ArgumentList "-NoExit", "-Command", $fastApiCmd
            Start-Sleep -Seconds 2
            Write-Success "FastAPI server started (Terminal 2)"
        }
        
        $userBot = Join-Path $ScriptRoot "bot\user_bot.py"
        $adminBot = Join-Path $ScriptRoot "bot\admin_bot.py"
        $botFiles = @()
        if (Test-Path $userBot) { $botFiles += $userBot }
        if (Test-Path $adminBot) { $botFiles += $adminBot }
        
        if ($botFiles.Count -gt 0) {
            Write-Info "Starting bot services in new window..."
            $botLog = Join-Path $LogDir "bots.log"
            $botCommands = @()
            foreach ($botFile in $botFiles) {
                $botName = Split-Path $botFile -Leaf
                $botCommands += "Write-Host 'Starting $botName' -ForegroundColor Cyan; `"$pythonExe`" `"$botFile`" 2>&1 | Tee-Object -FilePath `"$botLog`" -Append"
            }
            if ($botCommands.Count -gt 0) {
                $botCmd = "cd `"$ScriptRoot`"; " + ($botCommands -join "; ")
                Start-Process powershell -ArgumentList "-NoExit", "-Command", $botCmd
                Start-Sleep -Seconds 2
                Write-Success "Bot services started (Terminal 3)"
            }
        } else {
            Write-Warning "No bot files found (user_bot.py or admin_bot.py)"
        }
    } catch {
        Write-Error "Service startup failed: $_"
        throw
    }
}

function Main {
    try {
        Write-Host ""
        Write-Host "VPN Bot Management System - Setup Script" -ForegroundColor Cyan
        Write-Host "Production-ready PowerShell automation" -ForegroundColor Cyan
        Write-Host ""
        
        Initialize-LogDirectory
        Test-PythonInstalled
        
        $config = Collect-MinimalConfig
        Generate-EnvFile -Config $config
        
        Setup-Venv
        Install-Dependencies -Config $config
        
        Init-Django
        Init-FastAPI
        Start-Services -Config $config
        
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Magenta
        Write-Host "Setup Complete!" -ForegroundColor Magenta
        Write-Host "========================================" -ForegroundColor Magenta
        Write-Host ""
        Write-Success "All services have been started in separate terminals"
        Write-Info "Check logs in: $LogDir"
        Write-Info "Django: http://localhost:8000"
        Write-Info "FastAPI: http://$($config.FASTAPI_HOST):$($config.FASTAPI_PORT)"
        Write-Host ""
        
    } catch {
        Write-Error "Setup failed: $_"
        Write-Error "Check error log: $ErrorLog"
        exit 1
    }
}

Main
