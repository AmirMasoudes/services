@echo off
REM ========================================
REM Windows Installation Script
REM ========================================
echo ========================================
echo Sales Panel - Installation Script
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.11+ from https://www.python.org/
    pause
    exit /b 1
)

echo [OK] Python found
echo.

REM Create virtual environment
echo [*] Creating virtual environment...
if exist venv (
    echo [*] Virtual environment already exists, skipping...
) else (
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment!
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
)
echo.

REM Activate virtual environment
echo [*] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment!
    pause
    exit /b 1
)
echo [OK] Virtual environment activated
echo.

REM Upgrade pip
echo [*] Upgrading pip...
python -m pip install --upgrade pip
echo.

REM Install Django dependencies
echo [*] Installing Django dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install Django dependencies!
    pause
    exit /b 1
)
echo [OK] Django dependencies installed
echo.

REM Install FastAPI backend dependencies
echo [*] Installing FastAPI backend dependencies...
cd backend
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install FastAPI dependencies!
    cd ..
    pause
    exit /b 1
)
cd ..
echo [OK] FastAPI dependencies installed
echo.

REM Check for .env file
echo [*] Checking for .env file...
if not exist .env (
    echo [WARNING] .env file not found!
    if exist .env.example (
        echo [*] Copying .env.example to .env...
        copy .env.example .env
        echo [OK] .env file created from .env.example
        echo [IMPORTANT] Please edit .env file and configure your settings!
    ) else (
        echo [ERROR] .env.example file not found!
        echo Please create .env file manually with required configuration.
    )
) else (
    echo [OK] .env file found
)
echo.

REM Create logs directory
echo [*] Creating logs directory...
if not exist logs mkdir logs
echo [OK] Logs directory ready
echo.

REM Run Django migrations
echo [*] Running Django migrations...
python manage.py migrate
if errorlevel 1 (
    echo [WARNING] Django migrations failed, but continuing...
)
echo.

REM Run FastAPI migrations (if needed)
echo [*] Setting up FastAPI database...
cd backend
if exist alembic.ini (
    echo [*] Running Alembic migrations...
    alembic upgrade head
    if errorlevel 1 (
        echo [WARNING] Alembic migrations failed, but continuing...
    )
)
cd ..
echo.

echo ========================================
echo Installation completed!
echo ========================================
echo.
echo Next steps:
echo 1. Edit .env file with your configuration
echo 2. Run 'run.bat' to start all services
echo.
pause

