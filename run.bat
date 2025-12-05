@echo off
REM ========================================
REM Windows Run Script
REM ========================================

echo ========================================
echo Sales Panel - Starting Services
echo ========================================
echo.

REM Check if .env exists
if not exist .env (
    echo [ERROR] .env file not found!
    echo Please copy .env.example to .env and configure it.
    pause
    exit /b 1
)

REM Check if venv exists
if not exist venv (
    echo [ERROR] Virtual environment not found!
    echo Please run install.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
echo [*] Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if Redis is running (optional)
echo [*] Checking Redis connection...
python -c "import redis; r=redis.Redis(host='localhost', port=6379, db=0); r.ping()" 2>nul
if errorlevel 1 (
    echo [WARNING] Redis is not running. Some features may not work.
    echo [INFO] You can start Redis manually or skip this warning.
) else (
    echo [OK] Redis is running
)
echo.

REM Start Django migrations (if needed)
echo [*] Running Django migrations...
python manage.py migrate --noinput
echo.

REM Start FastAPI backend in background
echo [*] Starting FastAPI backend...
cd backend
start "FastAPI Backend" cmd /k "venv\Scripts\activate.bat && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
cd ..
timeout /t 3 /nobreak >nul
echo [OK] FastAPI backend started on http://localhost:8000
echo.

REM Start Celery worker in background
echo [*] Starting Celery worker...
cd backend
start "Celery Worker" cmd /k "venv\Scripts\activate.bat && celery -A app.core.celery_app worker --loglevel=info"
cd ..
timeout /t 2 /nobreak >nul
echo [OK] Celery worker started
echo.

REM Start Celery beat in background
echo [*] Starting Celery beat...
cd backend
start "Celery Beat" cmd /k "venv\Scripts\activate.bat && celery -A app.core.celery_app beat --loglevel=info"
cd ..
timeout /t 2 /nobreak >nul
echo [OK] Celery beat started
echo.

REM Start Admin Bot
echo [*] Starting Admin Bot...
start "Admin Bot" cmd /k "venv\Scripts\activate.bat && python bot\admin_bot.py"
timeout /t 2 /nobreak >nul
echo [OK] Admin bot started
echo.

REM Start User Bot
echo [*] Starting User Bot...
start "User Bot" cmd /k "venv\Scripts\activate.bat && python bot\user_bot.py"
timeout /t 2 /nobreak >nul
echo [OK] User bot started
echo.

echo ========================================
echo All services started!
echo ========================================
echo.
echo Services running:
echo - FastAPI Backend: http://localhost:8000
echo - API Docs: http://localhost:8000/api/docs
echo - Admin Bot: Running
echo - User Bot: Running
echo.
echo Press any key to stop all services...
pause >nul

REM Kill all started processes
echo.
echo [*] Stopping all services...
taskkill /FI "WINDOWTITLE eq FastAPI Backend*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Celery Worker*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Celery Beat*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Admin Bot*" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq User Bot*" /T /F >nul 2>&1
echo [OK] All services stopped

