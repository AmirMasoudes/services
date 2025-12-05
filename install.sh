#!/bin/bash
# ========================================
# Linux Installation Script
# ========================================

set -e

echo "========================================"
echo "Sales Panel - Installation Script"
echo "========================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed!"
    echo "Please install Python 3.11+ using your package manager"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "[OK] Python found: $(python3 --version)"
echo ""

# Create virtual environment
echo "[*] Creating virtual environment..."
if [ -d "venv" ]; then
    echo "[*] Virtual environment already exists, skipping..."
else
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to create virtual environment!"
        exit 1
    fi
    echo "[OK] Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "[*] Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to activate virtual environment!"
    exit 1
fi
echo "[OK] Virtual environment activated"
echo ""

# Upgrade pip
echo "[*] Upgrading pip..."
pip install --upgrade pip
echo ""

# Install Django dependencies
echo "[*] Installing Django dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install Django dependencies!"
    exit 1
fi
echo "[OK] Django dependencies installed"
echo ""

# Install FastAPI backend dependencies
echo "[*] Installing FastAPI backend dependencies..."
cd backend
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install FastAPI dependencies!"
    cd ..
    exit 1
fi
cd ..
echo "[OK] FastAPI dependencies installed"
echo ""

# Check for .env file
echo "[*] Checking for .env file..."
if [ ! -f ".env" ]; then
    echo "[WARNING] .env file not found!"
    if [ -f ".env.example" ]; then
        echo "[*] Copying .env.example to .env..."
        cp .env.example .env
        echo "[OK] .env file created from .env.example"
        echo "[IMPORTANT] Please edit .env file and configure your settings!"
    else
        echo "[ERROR] .env.example file not found!"
        echo "Please create .env file manually with required configuration."
    fi
else
    echo "[OK] .env file found"
fi
echo ""

# Create logs directory
echo "[*] Creating logs directory..."
mkdir -p logs
echo "[OK] Logs directory ready"
echo ""

# Run Django migrations
echo "[*] Running Django migrations..."
python manage.py migrate || echo "[WARNING] Django migrations failed, but continuing..."
echo ""

# Run FastAPI migrations (if needed)
echo "[*] Setting up FastAPI database..."
cd backend
if [ -f "alembic.ini" ]; then
    echo "[*] Running Alembic migrations..."
    alembic upgrade head || echo "[WARNING] Alembic migrations failed, but continuing..."
fi
cd ..
echo ""

echo "========================================"
echo "Installation completed!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Run './run.sh' to start all services"
echo ""

