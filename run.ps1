# ========================================
# VPN Bot Management System - Setup Script
# ========================================
# Production-ready PowerShell automation
# Compatible with PowerShell 5+ and PowerShell 7

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
    Add-Content -Path $ErrorLog -Value "$timestamp - ERROR: $Message" -ErrorAction SilentlyContinue
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
        [switch]$IsBoolean = $false,
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
            return Ask-Value -Prompt $Prompt -DefaultValue $DefaultValue -IsPassword:$IsPassword -IsBoolean:$IsBoolean -Required:$Required
        }
        $value = $DefaultValue
    }
    
    if ($IsBoolean) {
        $lowerValue = $value.ToLower()
        return ($lowerValue -eq "true" -or $lowerValue -eq "1" -or $lowerValue -eq "yes" -or $lowerValue -eq "y")
    }
    
    return $value
}

function Collect-Configuration {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Magenta
    Write-Host "Configuration Collection" -ForegroundColor Magenta
    Write-Host "========================================" -ForegroundColor Magenta
    Write-Host ""
    
    $config = @{}
    
    Write-Host "Django Configuration:" -ForegroundColor Yellow
    $config.SECRET_KEY = Ask-Value -Prompt "Django SECRET_KEY" -Required $true
    $debugInput = Ask-Value -Prompt "DEBUG (True/False)" -DefaultValue "False" -IsBoolean
    $config.DEBUG = if ($debugInput) { "True" } else { "False" }
    $config.ALLOWED_HOSTS = Ask-Value -Prompt "ALLOWED_HOSTS (comma-separated)" -DefaultValue "localhost,127.0.0.1"
    
    Write-Host ""
    Write-Host "Telegram Bot Configuration:" -ForegroundColor Yellow
    $config.ADMIN_BOT_TOKEN = Ask-Value -Prompt "Admin bot token" -Required $true
    $config.USER_BOT_TOKEN = Ask-Value -Prompt "User bot token" -Required $true
    $config.ADMIN_PASSWORD = Ask-Value -Prompt "Admin password" -IsPassword -Required $true
    $config.ADMIN_USER_IDS = Ask-Value -Prompt "Admin user IDs (comma-separated)" -Required $true
    
    Write-Host ""
    Write-Host "X-UI Panel Configuration:" -ForegroundColor Yellow
    $config.XUI_DEFAULT_HOST = Ask-Value -Prompt "X-UI host" -DefaultValue "localhost"
    $config.XUI_DEFAULT_PORT = Ask-Value -Prompt "X-UI port" -DefaultValue "2053"
    $config.XUI_DEFAULT_USERNAME = Ask-Value -Prompt "X-UI username" -Required $true
    $config.XUI_DEFAULT_PASSWORD = Ask-Value -Prompt "X-UI password" -IsPassword -Required $true
    $config.XUI_WEB_BASE_PATH = Ask-Value -Prompt "X-UI web base path" -DefaultValue "/app/"
    $xuiSsl = Ask-Value -Prompt "X-UI use SSL (True/False)" -DefaultValue "True" -IsBoolean
    $config.XUI_USE_SSL = if ($xuiSsl) { "True" } else { "False" }
    $xuiVerify = Ask-Value -Prompt "X-UI verify SSL (True/False)" -DefaultValue "False" -IsBoolean
    $config.XUI_VERIFY_SSL = if ($xuiVerify) { "True" } else { "False" }
    $config.XUI_TIMEOUT = Ask-Value -Prompt "X-UI timeout (seconds)" -DefaultValue "30"
    
    Write-Host ""
    Write-Host "S-UI Panel Configuration:" -ForegroundColor Yellow
    $config.SUI_HOST = Ask-Value -Prompt "S-UI host" -DefaultValue "localhost"
    $config.SUI_PORT = Ask-Value -Prompt "S-UI port" -DefaultValue "2095"
    $suiSsl = Ask-Value -Prompt "S-UI use SSL (True/False)" -DefaultValue "False" -IsBoolean
    $config.SUI_USE_SSL = if ($suiSsl) { "True" } else { "False" }
    $config.SUI_BASE_PATH = Ask-Value -Prompt "S-UI base path" -DefaultValue "/app"
    $config.SUI_API_TOKEN = Ask-Value -Prompt "S-UI API token" -DefaultValue ""
    $config.SUI_BASE_URL = Ask-Value -Prompt "S-UI base URL" -DefaultValue "http://localhost:2095"
    $config.SUI_API_KEY = Ask-Value -Prompt "S-UI API key" -DefaultValue ""
    
    Write-Host ""
    Write-Host "Server Configuration:" -ForegroundColor Yellow
    $config.SERVER_IP = Ask-Value -Prompt "Server IP" -DefaultValue "127.0.0.1"
    $config.SERVER_DOMAIN = Ask-Value -Prompt "Domain" -DefaultValue "localhost"
    $config.SERVER_PORT = Ask-Value -Prompt "Server port" -DefaultValue "8000"
    $config.SERVER_PROTOCOL = Ask-Value -Prompt "Server protocol (http/https)" -DefaultValue "http"
    
    Write-Host ""
    Write-Host "VPN Protocol Configuration:" -ForegroundColor Yellow
    $config.DEFAULT_PROTOCOL = Ask-Value -Prompt "Default protocol (vless/vmess/trojan)" -DefaultValue "vless"
    $config.MIN_PORT = Ask-Value -Prompt "Minimum port" -DefaultValue "10000"
    $config.MAX_PORT = Ask-Value -Prompt "Maximum port" -DefaultValue "65000"
    $tlsEnabled = Ask-Value -Prompt "TLS enabled (True/False)" -DefaultValue "True" -IsBoolean
    $config.TLS_ENABLED = if ($tlsEnabled) { "True" } else { "False" }
    $realityEnabled = Ask-Value -Prompt "Reality enabled (True/False)" -DefaultValue "True" -IsBoolean
    $config.REALITY_ENABLED = if ($realityEnabled) { "True" } else { "False" }
    $config.REALITY_DEST = Ask-Value -Prompt "Reality destination" -DefaultValue "www.aparat.com:443"
    $config.REALITY_SERVER_NAMES = Ask-Value -Prompt "Reality server names" -DefaultValue "www.aparat.com"
    $config.REALITY_PRIVATE_KEY = Ask-Value -Prompt "Reality private key" -Required $true
    $config.WS_PATH = Ask-Value -Prompt "WebSocket path" -DefaultValue "/"
    $config.WS_HOST = Ask-Value -Prompt "WebSocket host" -DefaultValue ""
    
    Write-Host ""
    Write-Host "Trial and Plan Configuration:" -ForegroundColor Yellow
    $config.TRIAL_HOURS = Ask-Value -Prompt "Trial hours" -DefaultValue "24"
    $config.PAID_DAYS = Ask-Value -Prompt "Paid days" -DefaultValue "30"
    $config.EXPIRY_WARNING_HOURS = Ask-Value -Prompt "Expiry warning hours" -DefaultValue "6"
    $config.EXPIRY_WARNING_MESSAGE = Ask-Value -Prompt "Expiry warning message" -DefaultValue "Config expires in {hours} hours"
    
    Write-Host ""
    Write-Host "Naming Prefixes:" -ForegroundColor Yellow
    $config.TRIAL_INBOUND_PREFIX = Ask-Value -Prompt "Trial inbound prefix" -DefaultValue "TrialBot"
    $config.PAID_INBOUND_PREFIX = Ask-Value -Prompt "Paid inbound prefix" -DefaultValue "PaidBot"
    $config.USER_INBOUND_PREFIX = Ask-Value -Prompt "User inbound prefix" -DefaultValue "UserBot"
    
    Write-Host ""
    Write-Host "Connection Settings:" -ForegroundColor Yellow
    $config.CONNECTION_TIMEOUT = Ask-Value -Prompt "Connection timeout (seconds)" -DefaultValue "15"
    $config.RETRY_ATTEMPTS = Ask-Value -Prompt "Retry attempts" -DefaultValue "5"
    
    Write-Host ""
    Write-Host "Database Configuration:" -ForegroundColor Yellow
    $dbEngine = Ask-Value -Prompt "Database engine (sqlite/postgresql)" -DefaultValue "sqlite"
    if ($dbEngine -eq "postgresql") {
        $config.DB_ENGINE = "django.db.backends.postgresql"
        $config.DB_NAME = Ask-Value -Prompt "Database name" -Required $true
        $config.DB_USER = Ask-Value -Prompt "Database user" -Required $true
        $config.DB_PASSWORD = Ask-Value -Prompt "Database password" -IsPassword -Required $true
        $config.DB_HOST = Ask-Value -Prompt "Database host" -DefaultValue "localhost"
        $config.DB_PORT = Ask-Value -Prompt "Database port" -DefaultValue "5432"
        $config.DATABASE_URL = "postgresql+asyncpg://$($config.DB_USER):$($config.DB_PASSWORD)@$($config.DB_HOST):$($config.DB_PORT)/$($config.DB_NAME)"
        $config.DATABASE_POOL_SIZE = Ask-Value -Prompt "Database pool size" -DefaultValue "10"
        $config.DATABASE_MAX_OVERFLOW = Ask-Value -Prompt "Database max overflow" -DefaultValue "20"
    } else {
        $config.DB_ENGINE = "django.db.backends.sqlite3"
        $config.DB_NAME = "db.sqlite3"
        $config.DB_USER = ""
        $config.DB_PASSWORD = ""
        $config.DB_HOST = ""
        $config.DB_PORT = ""
        $config.DATABASE_URL = ""
        $config.DATABASE_POOL_SIZE = ""
        $config.DATABASE_MAX_OVERFLOW = ""
    }
    
    Write-Host ""
    Write-Host "Redis Configuration:" -ForegroundColor Yellow
    $config.REDIS_URL = Ask-Value -Prompt "Redis URL" -DefaultValue "redis://localhost:6379/0"
    $config.REDIS_CACHE_TTL = Ask-Value -Prompt "Redis cache TTL (seconds)" -DefaultValue "3600"
    $config.CELERY_BROKER_URL = Ask-Value -Prompt "Celery broker URL" -DefaultValue "redis://localhost:6379/1"
    $config.CELERY_RESULT_BACKEND = Ask-Value -Prompt "Celery result backend URL" -DefaultValue "redis://localhost:6379/2"
    
    Write-Host ""
    Write-Host "FastAPI Configuration:" -ForegroundColor Yellow
    $config.ENVIRONMENT = Ask-Value -Prompt "Environment (development/production)" -DefaultValue "development"
    $config.FASTAPI_HOST = Ask-Value -Prompt "FastAPI host" -DefaultValue "0.0.0.0"
    $config.FASTAPI_PORT = Ask-Value -Prompt "FastAPI port" -DefaultValue "8001"
    $config.FASTAPI_SECRET_KEY = Ask-Value -Prompt "FastAPI SECRET_KEY" -DefaultValue $config.SECRET_KEY
    $config.ALGORITHM = Ask-Value -Prompt "JWT algorithm" -DefaultValue "HS256"
    $config.ACCESS_TOKEN_EXPIRE_MINUTES = Ask-Value -Prompt "Access token expire minutes" -DefaultValue "30"
    $config.REFRESH_TOKEN_EXPIRE_DAYS = Ask-Value -Prompt "Refresh token expire days" -DefaultValue "7"
    $config.CORS_ORIGINS = Ask-Value -Prompt "CORS origins (comma-separated)" -DefaultValue "http://localhost:3000,http://localhost:5173"
    $corsCreds = Ask-Value -Prompt "CORS allow credentials (True/False)" -DefaultValue "True" -IsBoolean
    $config.CORS_ALLOW_CREDENTIALS = if ($corsCreds) { "True" } else { "False" }
    
    Write-Host ""
    Write-Host "Security Settings:" -ForegroundColor Yellow
    $config.CSRF_TRUSTED_ORIGINS = Ask-Value -Prompt "CSRF trusted origins (comma-separated)" -DefaultValue "http://localhost,https://localhost"
    $config.SECURE_HSTS_SECONDS = Ask-Value -Prompt "Secure HSTS seconds" -DefaultValue "0"
    $secureSsl = Ask-Value -Prompt "Secure SSL redirect (True/False)" -DefaultValue "False" -IsBoolean
    $config.SECURE_SSL_REDIRECT = if ($secureSsl) { "True" } else { "False" }
    $sessionSecure = Ask-Value -Prompt "Session cookie secure (True/False)" -DefaultValue "False" -IsBoolean
    $config.SESSION_COOKIE_SECURE = if ($sessionSecure) { "True" } else { "False" }
    $csrfSecure = Ask-Value -Prompt "CSRF cookie secure (True/False)" -DefaultValue "False" -IsBoolean
    $config.CSRF_COOKIE_SECURE = if ($csrfSecure) { "True" } else { "False" }
    
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

# FastAPI Database
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
        & $pythonExe -m pip install --upgrade pip --quiet
        
        $requirementsFile = Join-Path $ScriptRoot "requirements.txt"
        if (Test-Path $requirementsFile) {
            Write-Info "Installing requirements from requirements.txt..."
            & $pipExe install -r $requirementsFile
            if ($LASTEXITCODE -ne 0) {
                Write-Error "Failed to install requirements"
                throw "Requirements installation failed"
            }
            Write-Success "Requirements installed"
        } else {
            Write-Warning "requirements.txt not found"
        }
        
        $backendRequirements = Join-Path $ScriptRoot "backend\requirements.txt"
        if (Test-Path $backendRequirements) {
            Write-Info "Installing FastAPI requirements..."
            & $pipExe install -r $backendRequirements
            if ($LASTEXITCODE -ne 0) {
                Write-Warning "FastAPI requirements installation had issues"
            } else {
                Write-Success "FastAPI requirements installed"
            }
        }
        
        if ($Config.DB_ENGINE -eq "django.db.backends.postgresql") {
            Write-Info "Installing PostgreSQL driver..."
            & $pipExe install psycopg2-binary --quiet
            if ($LASTEXITCODE -eq 0) {
                Write-Success "PostgreSQL driver installed"
            }
        }
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
        & $pythonExe $managePy makemigrations 2>&1 | Out-File -FilePath (Join-Path $LogDir "django_makemigrations.log")
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "makemigrations had issues"
        } else {
            Write-Success "Migrations created"
        }
        
        Write-Info "Applying migrations..."
        & $pythonExe $managePy migrate 2>&1 | Out-File -FilePath (Join-Path $LogDir "django_migrate.log")
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Migration failed"
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
        
        $botFiles = Get-ChildItem -Path $ScriptRoot -Filter "*bot*.py" -Recurse -ErrorAction SilentlyContinue | Where-Object { $_.FullName -notlike "*__pycache__*" }
        if ($botFiles) {
            Write-Info "Starting bot services in new window..."
            $botLog = Join-Path $LogDir "bots.log"
            $botCommands = @()
            foreach ($botFile in $botFiles) {
                $botCommands += "Write-Host 'Starting $($botFile.Name)' -ForegroundColor Cyan; `"$pythonExe`" `"$($botFile.FullName)`" 2>&1 | Tee-Object -FilePath `"$botLog`" -Append"
            }
            $botCmd = "cd `"$ScriptRoot`"; " + ($botCommands -join "; ")
            Start-Process powershell -ArgumentList "-NoExit", "-Command", $botCmd
            Start-Sleep -Seconds 2
            Write-Success "Bot services started (Terminal 3)"
        } else {
            Write-Warning "No bot files found"
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
        
        $config = Collect-Configuration
        Generate-EnvFile -Config $config
        
        Setup-Venv
        Install-Dependencies -Config $config
        
        Init-Django
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
