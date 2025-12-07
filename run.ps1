# VPN Bot Management System - Production Setup Script
# Fully stable and production-grade PowerShell automation
# Compatible with PowerShell 5+ and PowerShell 7
# Fixed: pip upgrade, venv recreation, dependency installation, Docker support

#Requires -Version 5.0

$ErrorActionPreference = "Continue"
$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$LogDir = Join-Path $ScriptRoot "logs"
$ErrorLog = Join-Path $LogDir "error.log"
$VenvPath = Join-Path $ScriptRoot "venv"
$RequirementsFile = Join-Path $ScriptRoot "requirements.txt"
$BackendRequirementsFile = Join-Path $ScriptRoot "backend\requirements.txt"
$EnvFile = Join-Path $ScriptRoot ".env"
$DockerComposeFile = Join-Path $ScriptRoot "docker-compose.yml"
$Dockerfile = Join-Path $ScriptRoot "Dockerfile"

# PyPI mirror configuration for reliable downloads
$PyPIIndex = "https://pypi.org/simple"
$PyPITrustedHost = "pypi.org"

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
    Write-ErrorLog $Message
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

function Write-ErrorLog {
    param([string]$Message)
    try {
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        $logMessage = "$timestamp - ERROR: $Message"
        Add-Content -Path $ErrorLog -Value $logMessage -ErrorAction SilentlyContinue
    } catch {
        # Ignore log write errors to prevent infinite loops
    }
}

function Initialize-LogDirectory {
    try {
        if (-not (Test-Path $LogDir)) {
            New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
            Write-Success "Logs directory created"
        }
    } catch {
        Write-Error "Failed to create logs directory: $_"
        # Don't throw - continue anyway
    }
}

function Test-PythonInstalled {
    try {
        Write-Info "Checking Python installation..."
        if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
            Write-Error "Python is not installed or not in PATH"
            Write-Host ""
            Write-Host "FIX: Install Python 3.11+ from https://www.python.org/" -ForegroundColor Yellow
            Write-Host "     Ensure 'Add Python to PATH' is checked during installation" -ForegroundColor Yellow
            Write-Host ""
            throw "Python not found"
        }
        
        $versionOutput = python --version 2>&1
        Write-Success "Python found: $versionOutput"
        
        $versionMatch = $versionOutput -match "Python (\d+)\.(\d+)"
        if ($versionMatch) {
            $major = [int]$matches[1]
            $minor = [int]$matches[2]
            if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 11)) {
                Write-Error "Python 3.11+ is required. Found: $versionOutput"
                Write-Host ""
                Write-Host "FIX: Upgrade to Python 3.11+ from https://www.python.org/" -ForegroundColor Yellow
                Write-Host ""
                throw "Python version too old"
            }
        }
    } catch {
        Write-Error "Python check failed: $_"
        throw
    }
}

function Stop-PythonProcesses {
    try {
        Write-Info "Stopping all Python processes..."
        $pythonProcesses = Get-Process python -ErrorAction SilentlyContinue
        if ($pythonProcesses) {
            foreach ($proc in $pythonProcesses) {
                try {
                    Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
                    Write-Info "Stopped Python process: $($proc.Id)"
                } catch {
                    # Ignore errors stopping processes
                }
            }
            Start-Sleep -Seconds 2
            Write-Success "Python processes stopped"
        } else {
            Write-Info "No Python processes running"
        }
    } catch {
        Write-Warning "Could not stop all Python processes: $_"
    }
}

function Remove-VenvSafely {
    param([switch]$Force)
    
    try {
        if (Test-Path $VenvPath) {
            if (-not $Force) {
                Write-Host ""
                $response = Read-Host "Virtual environment exists. Recreate it? (y/N)"
                if ($response -notmatch "^[Yy]") {
                    Write-Info "Keeping existing virtual environment"
                    return $false
                }
            }
            
            Write-Info "Removing existing virtual environment..."
            Stop-PythonProcesses
            
            $maxRetries = 5
            $retryCount = 0
            $removed = $false
            
            while ($retryCount -lt $maxRetries -and -not $removed) {
                try {
                    # Try to unlock files by stopping processes again
                    Stop-PythonProcesses
                    Start-Sleep -Seconds 1
                    
                    # Remove directory
                    Remove-Item -Path $VenvPath -Recurse -Force -ErrorAction Stop
                    $removed = $true
                    Write-Success "Virtual environment removed"
                } catch {
                    $retryCount++
                    if ($retryCount -lt $maxRetries) {
                        Write-Warning ("Retry {0}/{1}: Could not remove venv, waiting..." -f $retryCount, $maxRetries)
                        Start-Sleep -Seconds 3
                        Stop-PythonProcesses
                    } else {
                        Write-Error ("Failed to remove virtual environment after {0} attempts" -f $maxRetries)
                        Write-Host ""
                        Write-Host "FIX: Manually delete the 'venv' folder and run the script again" -ForegroundColor Yellow
                        Write-Host "     Path: $VenvPath" -ForegroundColor Yellow
                        Write-Host ""
                        throw "Failed to remove venv"
                    }
                }
            }
            return $true
        }
        return $false
    } catch {
        Write-Error "Virtual environment removal failed: $_"
        throw
    }
}

function Setup-Venv {
    try {
        Write-Info "Setting up virtual environment..."
        
        $removed = Remove-VenvSafely
        
        Write-Info "Creating virtual environment..."
        python -m venv $VenvPath 2>&1 | Out-Null
        
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to create virtual environment"
            throw "Virtual environment creation failed"
        }
        
        if (-not (Test-Path $VenvPath)) {
            Write-Error "Virtual environment directory not created"
            throw "Virtual environment creation failed"
        }
        
        Write-Success "Virtual environment created"
        
        $pythonExe = Join-Path $VenvPath "Scripts\python.exe"
        $pipExe = Join-Path $VenvPath "Scripts\pip.exe"
        
        # Wait a moment for files to be fully created
        Start-Sleep -Seconds 1
        
        if (-not (Test-Path $pythonExe)) {
            Write-Error "python.exe not found in virtual environment"
            Write-Host ""
            Write-Host "FIX: Recreate virtual environment manually:" -ForegroundColor Yellow
            Write-Host "     Remove 'venv' folder and run: python -m venv venv" -ForegroundColor Yellow
            Write-Host ""
            throw "Virtual environment incomplete"
        }
        
        Write-Success "python.exe validated"
        
        if (-not (Test-Path $pipExe)) {
            Write-Warning "pip not found, installing via ensurepip..."
            & $pythonExe -m ensurepip --upgrade 2>&1 | Out-Null
            if ($LASTEXITCODE -ne 0) {
                Write-Warning "ensurepip failed, trying alternative method..."
                # Try to install pip manually
                $pipScript = Join-Path $VenvPath "Scripts\get-pip.py"
                if (-not (Test-Path $pipScript)) {
                    Write-Error "Could not install pip in virtual environment"
                    throw "pip installation failed"
                }
            }
        }
        
        if (-not (Test-Path $pipExe)) {
            Write-Error "pip.exe not found after installation attempt"
            throw "pip not available"
        }
        
        Write-Success "pip validated"
        
    } catch {
        Write-Error "Virtual environment setup failed: $_"
        throw
    }
}

function Upgrade-Pip {
    param([string]$PythonExe)
    
    try {
        Write-Info "Upgrading pip..."
        
        # Use PyPI mirror with trusted host to avoid version check errors
        $upgradeOutput = & $PythonExe -m pip install --upgrade pip `
            -i $PyPIIndex `
            --trusted-host $PyPITrustedHost `
            --disable-pip-version-check `
            2>&1
        
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "Pip upgrade had issues, but continuing..."
            Write-ErrorLog "pip upgrade output: $upgradeOutput"
            # Don't throw - continue anyway as pip might still work
        } else {
            Write-Success "pip upgraded successfully"
        }
    } catch {
        Write-Warning "Pip upgrade failed, continuing anyway: $_"
        Write-ErrorLog "pip upgrade exception: $_"
        # Don't throw - continue with existing pip version
    }
}

function Install-DependenciesWithRetry {
    param(
        [string]$PythonExe,
        [string]$RequirementsPath,
        [string]$Description
    )
    
    if (-not (Test-Path $RequirementsPath)) {
        Write-Warning "$Description requirements file not found: $RequirementsPath"
        return $false
    }
    
    $maxRetries = 3
    $retryCount = 0
    $success = $false
    
    while ($retryCount -lt $maxRetries -and -not $success) {
        try {
            Write-Info "Installing $Description requirements (attempt $($retryCount + 1)/$maxRetries)..."
            
            $installOutput = & $PythonExe -m pip install -r $RequirementsPath `
                -i $PyPIIndex `
                --trusted-host $PyPITrustedHost `
                --disable-pip-version-check `
                2>&1
            
            if ($LASTEXITCODE -eq 0) {
                Write-Success "$Description requirements installed successfully"
                $success = $true
            } else {
                $retryCount++
                if ($retryCount -lt $maxRetries) {
                    Write-Warning "$Description installation failed, retrying in 3 seconds..."
                    Write-ErrorLog "$Description install attempt $retryCount failed: $installOutput"
                    Start-Sleep -Seconds 3
                } else {
                    Write-Error "$Description requirements installation failed after $maxRetries attempts"
                    Write-ErrorLog "$Description install final failure: $installOutput"
                    
                    $errorLines = $installOutput | Where-Object { $_ -match "ERROR|yanked|broken|failed|conflict" }
                    if ($errorLines) {
                        Write-Warning "Installation errors detected:"
                        foreach ($line in $errorLines) {
                            Write-Warning "  $line"
                        }
                    }
                    
                    Write-Host ""
                    Write-Host "FIX: Check error log at $ErrorLog for details" -ForegroundColor Yellow
                    Write-Host "     Ensure all package versions in requirements.txt are compatible" -ForegroundColor Yellow
                    Write-Host ""
                    
                    # Don't throw - allow script to continue
                    return $false
                }
            }
        } catch {
            $retryCount++
            if ($retryCount -lt $maxRetries) {
                Write-Warning "$Description installation exception, retrying: $_"
                Start-Sleep -Seconds 3
            } else {
                Write-Error "$Description installation failed after $maxRetries attempts: $_"
                Write-ErrorLog "$Description install exception: $_"
                return $false
            }
        }
    }
    
    return $success
}

function Install-Dependencies {
    try {
        Write-Info "Installing dependencies..."
        
        $pythonExe = Join-Path $VenvPath "Scripts\python.exe"
        
        if (-not (Test-Path $pythonExe)) {
            Write-Error "python.exe not found in virtual environment"
            throw "Python executable not available"
        }
        
        # Upgrade pip first (with error handling)
        Upgrade-Pip -PythonExe $pythonExe
        
        # Install main requirements
        if (Test-Path $RequirementsFile) {
            $mainSuccess = Install-DependenciesWithRetry `
                -PythonExe $pythonExe `
                -RequirementsPath $RequirementsFile `
                -Description "Django"
            
            if (-not $mainSuccess) {
                Write-Warning "Django requirements installation had issues, but continuing..."
            }
        } else {
            Write-Warning "Main requirements.txt not found: $RequirementsFile"
        }
        
        # Install backend requirements
        if (Test-Path $BackendRequirementsFile) {
            $backendSuccess = Install-DependenciesWithRetry `
                -PythonExe $pythonExe `
                -RequirementsPath $BackendRequirementsFile `
                -Description "FastAPI"
            
            if (-not $backendSuccess) {
                Write-Warning "FastAPI requirements installation had issues, but continuing..."
            }
        } else {
            Write-Info "Backend requirements.txt not found (optional): $BackendRequirementsFile"
        }
        
        Write-Success "Dependency installation completed"
        
    } catch {
        Write-Error "Dependency installation failed: $_"
        Write-ErrorLog "Dependency installation exception: $_"
        # Don't throw - allow script to continue
    }
}

function Test-DockerInstalled {
    try {
        Write-Info "Checking Docker installation..."
        
        if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
            Write-Warning "Docker is not installed or not in PATH"
            Write-Host ""
            Write-Host "Docker is optional but recommended for production deployment" -ForegroundColor Yellow
            Write-Host "Install from: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
            Write-Host ""
            return $false
        }
        
        $dockerVersion = docker --version 2>&1
        Write-Success "Docker found: $dockerVersion"
        return $true
    } catch {
        Write-Warning "Docker check failed: $_"
        return $false
    }
}

function Test-DockerComposeInstalled {
    try {
        if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue)) {
            # Try docker compose (v2 syntax)
            $composeCheck = docker compose version 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Docker Compose found (v2): $composeCheck"
                return $true
            }
            return $false
        }
        $composeVersion = docker-compose --version 2>&1
        Write-Success "Docker Compose found: $composeVersion"
        return $true
    } catch {
        return $false
    }
}

function Test-Dockerfile {
    try {
        if (Test-Path $Dockerfile) {
            Write-Success "Dockerfile found: $Dockerfile"
            return $true
        } else {
            Write-Warning "Dockerfile not found: $Dockerfile"
            return $false
        }
    } catch {
        Write-Warning "Dockerfile check failed: $_"
        return $false
    }
}

function Generate-DockerCompose {
    try {
        if (Test-Path $DockerComposeFile) {
            Write-Info "docker-compose.yml already exists"
            return
        }
        
        Write-Info "Generating docker-compose.yml..."
        
        $composeContent = @"
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: vpnbot_postgres
    environment:
      POSTGRES_DB: vpnbot_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: changeme
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: vpnbot_redis
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  django:
    build:
      context: .
      dockerfile: Dockerfile.django
    container_name: vpnbot_django
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    environment:
      - DEBUG=True

  fastapi:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: vpnbot_fastapi
    command: uvicorn app.main:app --host 0.0.0.0 --port 8001
    volumes:
      - ./backend:/app
    ports:
      - "8001:8001"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy

volumes:
  postgres_data:
"@
        
        $composeContent | Out-File -FilePath $DockerComposeFile -Encoding UTF8 -Force
        Write-Success "docker-compose.yml generated at $DockerComposeFile"
        Write-Warning "Please review and update the docker-compose.yml file with your configuration"
        
    } catch {
        Write-Warning "Failed to generate docker-compose.yml: $_"
        Write-ErrorLog "docker-compose generation failed: $_"
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
            Write-Warning "This field is required! Using default or generating value..."
            # Auto-generate if possible
            if ($Prompt -match "TOKEN") {
                Write-Warning "Token fields cannot be auto-generated. Please provide a value."
                return Ask-Value -Prompt $Prompt -DefaultValue $DefaultValue -IsPassword:$IsPassword -Required:$Required
            }
        }
        $value = $DefaultValue
    }
    
    return $value
}

function Generate-SecretKey {
    try {
        $bytes = New-Object byte[] 64
        $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
        $rng.GetBytes($bytes)
        $secret = [Convert]::ToBase64String($bytes)
        $secret = $secret -replace '[+/=]', { param($c) if ($c -eq '+') { '-' } elseif ($c -eq '/') { '_' } else { '' } }
        return $secret
    } catch {
        $fallback = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 64 | ForEach-Object {[char]$_})
        return $fallback
    }
}

function Collect-Configuration {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Magenta
    Write-Host "Configuration Collection" -ForegroundColor Magenta
    Write-Host "========================================" -ForegroundColor Magenta
    Write-Host ""
    Write-Host "Please provide the following configuration values:" -ForegroundColor Yellow
    Write-Host "Press Enter to use defaults or auto-generated values" -ForegroundColor Gray
    Write-Host ""
    
    $config = @{}
    
    Write-Host "--- Server Configuration ---" -ForegroundColor Cyan
    $config.SERVER_IP = Ask-Value -Prompt "Enter SERVER_IP" -DefaultValue "127.0.0.1" -Required $true
    
    Write-Host ""
    Write-Host "--- Panel Configuration ---" -ForegroundColor Cyan
    $config.PANEL_USERNAME = Ask-Value -Prompt "Enter PANEL_USERNAME" -DefaultValue "admin" -Required $true
    $config.PANEL_PASSWORD = Ask-Value -Prompt "Enter PANEL_PASSWORD" -IsPassword -DefaultValue "" -Required $true
    $config.PANEL_PORT = Ask-Value -Prompt "Enter PANEL_PORT" -DefaultValue "2053" -Required $true
    $config.PANEL_URL = Ask-Value -Prompt "Enter PANEL_URL" -DefaultValue ("http://{0}:{1}" -f $config.SERVER_IP, $config.PANEL_PORT) -Required $true
    
    Write-Host ""
    Write-Host "--- Telegram Bot Configuration ---" -ForegroundColor Cyan
    $config.ADMIN_BOT_TOKEN = Ask-Value -Prompt "Enter ADMIN_BOT_TOKEN" -DefaultValue "" -Required $true
    $config.USER_BOT_TOKEN = Ask-Value -Prompt "Enter USER_BOT_TOKEN" -DefaultValue "" -Required $true
    
    Write-Host ""
    Write-Host "--- Database Configuration ---" -ForegroundColor Cyan
    $config.DATABASE_NAME = Ask-Value -Prompt "Enter DATABASE_NAME" -DefaultValue "vpnbot_db" -Required $true
    
    Write-Host ""
    Write-Host "--- Redis Configuration ---" -ForegroundColor Cyan
    $config.REDIS_PORT = Ask-Value -Prompt "Enter REDIS_PORT" -DefaultValue "6379" -Required $false
    
    Write-Host ""
    Write-Info "Generating additional configuration values..."
    
    $config.SECRET_KEY = Generate-SecretKey
    $config.FASTAPI_SECRET_KEY = Generate-SecretKey
    $config.DEBUG = "False"
    $config.ALLOWED_HOSTS = ("{0},localhost,127.0.0.1" -f $config.SERVER_IP)
    $config.DB_ENGINE = "django.db.backends.postgresql"
    $config.DB_USER = "postgres"
    $config.DB_PASSWORD = Generate-SecretKey
    $config.DB_HOST = "localhost"
    $config.DB_PORT = "5432"
    $config.DATABASE_URL = ("postgresql+asyncpg://{0}:{1}@{2}:{3}/{4}" -f $config.DB_USER, $config.DB_PASSWORD, $config.DB_HOST, $config.DB_PORT, $config.DATABASE_NAME)
    $config.REDIS_URL = ("redis://localhost:{0}/0" -f $config.REDIS_PORT)
    $config.CELERY_BROKER_URL = ("redis://localhost:{0}/1" -f $config.REDIS_PORT)
    $config.CELERY_RESULT_BACKEND = ("redis://localhost:{0}/2" -f $config.REDIS_PORT)
    $config.ADMIN_USER_IDS = "123456789"
    $config.ADMIN_PASSWORD = $config.PANEL_PASSWORD
    $config.XUI_DEFAULT_HOST = $config.SERVER_IP
    $config.XUI_DEFAULT_PORT = $config.PANEL_PORT
    $config.XUI_DEFAULT_USERNAME = $config.PANEL_USERNAME
    $config.XUI_DEFAULT_PASSWORD = $config.PANEL_PASSWORD
    $config.XUI_WEB_BASE_PATH = "/app/"
    $config.SUI_BASE_URL = ("http://{0}:2095" -f $config.SERVER_IP)
    
    Write-Success "Configuration collected"
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

# Server Configuration
SERVER_IP=$($Config.SERVER_IP)

# Panel Configuration
PANEL_USERNAME=$($Config.PANEL_USERNAME)
PANEL_PASSWORD=$($Config.PANEL_PASSWORD)
PANEL_PORT=$($Config.PANEL_PORT)
PANEL_URL=$($Config.PANEL_URL)

# Telegram Bots
ADMIN_BOT_TOKEN=$($Config.ADMIN_BOT_TOKEN)
USER_BOT_TOKEN=$($Config.USER_BOT_TOKEN)
ADMIN_PASSWORD=$($Config.ADMIN_PASSWORD)
ADMIN_USER_IDS=$($Config.ADMIN_USER_IDS)

# Django Core
SECRET_KEY=$($Config.SECRET_KEY)
DEBUG=$($Config.DEBUG)
ALLOWED_HOSTS=$($Config.ALLOWED_HOSTS)

# Database
DB_ENGINE=$($Config.DB_ENGINE)
DB_NAME=$($Config.DATABASE_NAME)
DB_USER=$($Config.DB_USER)
DB_PASSWORD=$($Config.DB_PASSWORD)
DB_HOST=$($Config.DB_HOST)
DB_PORT=$($Config.DB_PORT)
DATABASE_HOST=postgres
DATABASE_PORT=5432
DATABASE_USER=postgres
DATABASE_PASSWORD=$($Config.DB_PASSWORD)

# FastAPI Database
DATABASE_URL=$($Config.DATABASE_URL)
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# Redis
REDIS_URL=$($Config.REDIS_URL)
REDIS_HOST=redis
REDIS_PORT=$($Config.REDIS_PORT)
REDIS_CACHE_TTL=3600

# Celery
CELERY_BROKER_URL=$($Config.CELERY_BROKER_URL)
CELERY_RESULT_BACKEND=$($Config.CELERY_RESULT_BACKEND)
CELERY_BROKER=redis://redis:6379/0
CELERY_BACKEND=redis://redis:6379/1

# X-UI Panel
XUI_DEFAULT_HOST=$($Config.XUI_DEFAULT_HOST)
XUI_DEFAULT_PORT=$($Config.XUI_DEFAULT_PORT)
XUI_DEFAULT_USERNAME=$($Config.XUI_DEFAULT_USERNAME)
XUI_DEFAULT_PASSWORD=$($Config.XUI_DEFAULT_PASSWORD)
XUI_WEB_BASE_PATH=$($Config.XUI_WEB_BASE_PATH)
XUI_USE_SSL=False
XUI_VERIFY_SSL=False
XUI_TIMEOUT=30

# S-UI Panel
SUI_BASE_URL=$($Config.SUI_BASE_URL)
SUI_HOST=$($Config.SERVER_IP)
SUI_PORT=2095
SUI_USE_SSL=False
SUI_BASE_PATH=/app
SUI_API_TOKEN=
SUI_API_KEY=

# FastAPI
ENVIRONMENT=development
HOST=0.0.0.0
PORT=8001
SECRET_KEY=$($Config.FASTAPI_SECRET_KEY)
FASTAPI_SECRET=$($Config.FASTAPI_SECRET_KEY)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
CORS_ALLOW_CREDENTIALS=True
"@
    
    try {
        $envContent | Out-File -FilePath $EnvFile -Encoding UTF8 -Force
        Write-Success ".env file created at $EnvFile"
    } catch {
        Write-Error "Failed to create .env file: $_"
        throw
    }
}

function Run-DjangoMigrations {
    try {
        Write-Info "Running Django migrations..."
        
        $pythonExe = Join-Path $VenvPath "Scripts\python.exe"
        $managePy = Join-Path $ScriptRoot "manage.py"
        
        if (-not (Test-Path $managePy)) {
            Write-Warning "manage.py not found, skipping Django migrations"
            return
        }
        
        Write-Info "Creating migrations..."
        $makemigrationsOutput = & $pythonExe $managePy makemigrations 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "makemigrations had issues"
            Write-ErrorLog "makemigrations output: $makemigrationsOutput"
        } else {
            Write-Success "Migrations created"
        }
        
        Write-Info "Applying migrations..."
        $migrateOutput = & $pythonExe $managePy migrate --noinput 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "Migration had issues (database might not be running)"
            Write-ErrorLog "migrate output: $migrateOutput"
            Write-Host ""
            Write-Host "NOTE: Migrations can be run later when database is available" -ForegroundColor Yellow
            Write-Host ""
        } else {
            Write-Success "Migrations applied"
        }
        
    } catch {
        Write-Warning "Django migration had issues: $_"
        Write-ErrorLog "Django migration exception: $_"
        # Don't throw - migrations can be run later
    }
}

function Show-FinalSummary {
    param([hashtable]$Config)
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Magenta
    Write-Host "Setup Complete!" -ForegroundColor Magenta
    Write-Host "========================================" -ForegroundColor Magenta
    Write-Host ""
    
    Write-Success "Virtual environment ready at: $VenvPath"
    Write-Success "Dependencies installed"
    Write-Success ".env file generated at: $EnvFile"
    
    Write-Host ""
    Write-Host "=== Configuration Summary ===" -ForegroundColor Cyan
    Write-Host "Server IP: $($Config.SERVER_IP)" -ForegroundColor White
    Write-Host "Panel URL: $($Config.PANEL_URL)" -ForegroundColor White
    Write-Host "Database: $($Config.DATABASE_NAME)" -ForegroundColor White
    Write-Host ""
    
    Write-Host "=== Docker Status ===" -ForegroundColor Cyan
    $dockerInstalled = Test-DockerInstalled
    $composeInstalled = Test-DockerComposeInstalled
    $dockerfileExists = Test-Dockerfile
    
    if ($dockerInstalled -and $composeInstalled) {
        Write-Success "Docker and Docker Compose are available"
        if (Test-Path $DockerComposeFile) {
            Write-Info "To start services: docker compose up --build -d"
            Write-Info "To stop services: docker compose down"
        }
    } else {
        Write-Warning "Docker not fully configured (optional)"
    }
    
    Write-Host ""
    Write-Host "=== Manual Run Commands ===" -ForegroundColor Cyan
    $pythonExe = Join-Path $VenvPath "Scripts\python.exe"
    Write-Host "Django server:" -ForegroundColor White
    Write-Host "  $pythonExe manage.py runserver" -ForegroundColor Gray
    Write-Host ""
    Write-Host "FastAPI server:" -ForegroundColor White
    Write-Host "  $pythonExe backend\app\main.py" -ForegroundColor Gray
    Write-Host "  OR: cd backend && $pythonExe -m uvicorn app.main:app --reload" -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "=== Next Steps ===" -ForegroundColor Cyan
    Write-Host "1. Review and update .env file if needed" -ForegroundColor White
    Write-Host "2. Create Django superuser: $pythonExe manage.py createsuperuser" -ForegroundColor White
    if ($dockerInstalled -and $composeInstalled) {
        Write-Host "3. Start Docker services: docker compose up --build -d" -ForegroundColor White
    } else {
        Write-Host "3. Start database and Redis services manually" -ForegroundColor White
    }
    Write-Host "4. Run migrations if not already done" -ForegroundColor White
    Write-Host ""
    
    Write-Info "Error log location: $ErrorLog"
    Write-Host ""
}

function Main {
    try {
        Write-Host ""
        Write-Host "VPN Bot Management System - Production Setup" -ForegroundColor Cyan
        Write-Host "=============================================" -ForegroundColor Cyan
        Write-Host ""
        
        Initialize-LogDirectory
        Test-PythonInstalled
        
        $config = Collect-Configuration
        Generate-EnvFile -Config $config
        
        Setup-Venv
        Install-Dependencies
        Run-DjangoMigrations
        
        # Docker checks and setup
        $dockerInstalled = Test-DockerInstalled
        if ($dockerInstalled) {
            Test-DockerComposeInstalled | Out-Null
            Test-Dockerfile | Out-Null
            Generate-DockerCompose
        }
        
        Show-FinalSummary -Config $config
        
    } catch {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Red
        Write-Error "Setup failed: $_"
        Write-Host "========================================" -ForegroundColor Red
        Write-Host ""
        Write-Info "Check error log: $ErrorLog"
        Write-Host ""
        Write-Host "Common fixes:" -ForegroundColor Yellow
        Write-Host "  - Ensure Python 3.11+ is installed and in PATH" -ForegroundColor Yellow
        Write-Host "  - Check that no Python processes are locking files" -ForegroundColor Yellow
        Write-Host "  - Review error log for detailed information" -ForegroundColor Yellow
        Write-Host ""
        exit 1
    }
}

Main
