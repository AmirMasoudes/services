#!/bin/bash
# ========================================
# Linux Run Script
# ========================================

set -e

echo "========================================"
echo "Sales Panel - Starting Services"
echo "========================================"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "[ERROR] .env file not found!"
    echo "Please copy .env.example to .env and configure it."
    exit 1
fi

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "[ERROR] Virtual environment not found!"
    echo "Please run ./install.sh first."
    exit 1
fi

# Activate virtual environment
echo "[*] Activating virtual environment..."
source venv/bin/activate

# Check if Redis is running (optional)
echo "[*] Checking Redis connection..."
python3 -c "import redis; r=redis.Redis(host='localhost', port=6379, db=0); r.ping()" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "[WARNING] Redis is not running. Some features may not work."
    echo "[INFO] You can start Redis with: redis-server"
else
    echo "[OK] Redis is running"
fi
echo ""

# Create logs directory
mkdir -p logs

# Run Django migrations
echo "[*] Running Django migrations..."
python manage.py migrate --noinput
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "[*] Stopping all services..."
    kill $FASTAPI_PID $CELERY_WORKER_PID $CELERY_BEAT_PID $ADMIN_BOT_PID $USER_BOT_PID 2>/dev/null || true
    echo "[OK] All services stopped"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start FastAPI backend in background
echo "[*] Starting FastAPI backend..."
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > ../logs/fastapi.log 2>&1 &
FASTAPI_PID=$!
cd ..
sleep 3
echo "[OK] FastAPI backend started on http://localhost:8000 (PID: $FASTAPI_PID)"
echo ""

# Start Celery worker in background
echo "[*] Starting Celery worker..."
cd backend
celery -A app.core.celery_app worker --loglevel=info > ../logs/celery_worker.log 2>&1 &
CELERY_WORKER_PID=$!
cd ..
sleep 2
echo "[OK] Celery worker started (PID: $CELERY_WORKER_PID)"
echo ""

# Start Celery beat in background
echo "[*] Starting Celery beat..."
cd backend
celery -A app.core.celery_app beat --loglevel=info > ../logs/celery_beat.log 2>&1 &
CELERY_BEAT_PID=$!
cd ..
sleep 2
echo "[OK] Celery beat started (PID: $CELERY_BEAT_PID)"
echo ""

# Start Admin Bot in background
echo "[*] Starting Admin Bot..."
python bot/admin_bot.py > logs/admin_bot.log 2>&1 &
ADMIN_BOT_PID=$!
sleep 2
echo "[OK] Admin bot started (PID: $ADMIN_BOT_PID)"
echo ""

# Start User Bot in background
echo "[*] Starting User Bot..."
python bot/user_bot.py > logs/user_bot.log 2>&1 &
USER_BOT_PID=$!
sleep 2
echo "[OK] User bot started (PID: $USER_BOT_PID)"
echo ""

echo "========================================"
echo "All services started!"
echo "========================================"
echo ""
echo "Services running:"
echo "- FastAPI Backend: http://localhost:8000 (PID: $FASTAPI_PID)"
echo "- API Docs: http://localhost:8000/api/docs"
echo "- Celery Worker: (PID: $CELERY_WORKER_PID)"
echo "- Celery Beat: (PID: $CELERY_BEAT_PID)"
echo "- Admin Bot: (PID: $ADMIN_BOT_PID)"
echo "- User Bot: (PID: $USER_BOT_PID)"
echo ""
echo "Logs are in the 'logs' directory"
echo ""
echo "Press Ctrl+C to stop all services..."
echo ""

# Wait for user interrupt
wait

