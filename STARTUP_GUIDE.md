# 🚀 Sales Panel - Complete Startup Guide

## 📋 Table of Contents
1. [Quick Start](#quick-start)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Running the Project](#running-the-project)
6. [Troubleshooting](#troubleshooting)

---

## ⚡ Quick Start

### Windows:
```bash
# 1. Install dependencies
install.bat

# 2. Configure .env file
# Edit .env with your settings

# 3. Run all services
run.bat
```

### Linux:
```bash
# 1. Install dependencies
chmod +x install.sh run.sh
./install.sh

# 2. Configure .env file
# Edit .env with your settings

# 3. Run all services
./run.sh
```

---

## 📦 Prerequisites

### Required:
- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **PostgreSQL 15+** (optional, SQLite works for Django)
- **Redis 7+** (optional, but recommended)

### For Windows:
- Python 3.11+ installed
- Git Bash (optional, for better terminal experience)

### For Linux:
- Python 3.11+ and pip
- PostgreSQL client libraries (if using PostgreSQL)
- Redis server

---

## 🔧 Installation

### Step 1: Clone/Download the Project
```bash
cd services
```

### Step 2: Run Installation Script

**Windows:**
```bash
install.bat
```

**Linux:**
```bash
chmod +x install.sh
./install.sh
```

The installation script will:
- ✅ Create Python virtual environment
- ✅ Install all dependencies (Django + FastAPI)
- ✅ Create `.env` file from `.env.example` (if not exists)
- ✅ Create logs directory
- ✅ Run database migrations

---

## ⚙️ Configuration

### Step 1: Configure Environment Variables

Edit the `.env` file in the project root:

```bash
# Copy example file if needed
cp .env.example .env

# Edit with your favorite editor
nano .env        # Linux
notepad .env     # Windows
```

### Step 2: Required Configuration

**Minimum required settings:**

```env
# Security
SECRET_KEY=your-very-secure-secret-key-here
DEBUG=True

# Database (for FastAPI)
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/sales_panel

# Telegram Bots
ADMIN_BOT_TOKEN=your-admin-bot-token
USER_BOT_TOKEN=your-user-bot-token
ADMIN_USER_IDS=123456789,987654321

# S-UI Panel (for FastAPI backend)
SUI_BASE_URL=http://your-sui-panel:2095
SUI_API_KEY=your-sui-api-key

# X-UI Panel (for Django bots)
XUI_DEFAULT_HOST=your-xui-host
XUI_DEFAULT_PORT=2053
XUI_DEFAULT_USERNAME=admin
XUI_DEFAULT_PASSWORD=admin
```

### Step 3: Database Setup

**For SQLite (Django - Default):**
No additional setup needed. SQLite will be created automatically.

**For PostgreSQL (FastAPI):**
```bash
# Create database
createdb sales_panel

# Or using psql
psql -U postgres
CREATE DATABASE sales_panel;
```

---

## 🏃 Running the Project

### Option 1: Run All Services (Recommended)

**Windows:**
```bash
run.bat
```

**Linux:**
```bash
./run.sh
```

This will start:
- ✅ FastAPI Backend (http://localhost:8000)
- ✅ Celery Worker
- ✅ Celery Beat
- ✅ Admin Bot
- ✅ User Bot

### Option 2: Run Services Manually

**Terminal 1 - FastAPI Backend:**
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Celery Worker:**
```bash
cd backend
celery -A app.core.celery_app worker --loglevel=info
```

**Terminal 3 - Celery Beat:**
```bash
cd backend
celery -A app.core.celery_app beat --loglevel=info
```

**Terminal 4 - Admin Bot:**
```bash
python bot/admin_bot.py
```

**Terminal 5 - User Bot:**
```bash
python bot/user_bot.py
```

---

## 🔍 Verification

### Check if services are running:

1. **FastAPI Backend:**
   - Open: http://localhost:8000
   - API Docs: http://localhost:8000/api/docs
   - Health: http://localhost:8000/health

2. **Telegram Bots:**
   - Send `/start` to your bots
   - Check bot responses

3. **Database:**
   - Django: Check `db.sqlite3` file exists
   - FastAPI: Check PostgreSQL connection

---

## 🐛 Troubleshooting

### Problem: Python not found
**Solution:**
- Install Python 3.11+ from python.org
- Add Python to PATH during installation
- Restart terminal

### Problem: Virtual environment creation fails
**Solution:**
```bash
# Windows
python -m venv venv --clear

# Linux
python3 -m venv venv --clear
```

### Problem: Dependencies installation fails
**Solution:**
```bash
# Upgrade pip first
pip install --upgrade pip

# Install one by one
pip install -r requirements.txt
cd backend && pip install -r requirements.txt
```

### Problem: .env file not found
**Solution:**
```bash
# Copy example file
cp .env.example .env

# Or create manually
touch .env
# Then add required variables
```

### Problem: Database connection error
**Solution:**
- Check DATABASE_URL in .env
- Verify PostgreSQL is running
- Check database credentials
- For SQLite: Check file permissions

### Problem: Redis connection error
**Solution:**
```bash
# Start Redis
redis-server

# Or install Redis
# Windows: Download from redis.io
# Linux: sudo apt-get install redis-server
```

### Problem: Telegram bot not responding
**Solution:**
- Verify bot tokens in .env
- Check ADMIN_USER_IDS are correct
- Check bot logs in logs/ directory
- Verify internet connection

### Problem: S-UI/X-UI connection fails
**Solution:**
- Verify panel URL and credentials
- Check firewall settings
- Test API connection manually
- Check logs for detailed errors

### Problem: Port already in use
**Solution:**
```bash
# Windows: Find process using port
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux: Find and kill process
lsof -ti:8000 | xargs kill -9
```

---

## 📁 Project Structure

```
services/
├── .env                    # Unified environment configuration
├── .env.example            # Example environment file
├── install.bat             # Windows installation script
├── install.sh              # Linux installation script
├── run.bat                 # Windows run script
├── run.sh                  # Linux run script
├── requirements.txt        # Django dependencies
├── manage.py               # Django management
├── config/                 # Django settings
├── bot/                    # Telegram bots
│   ├── admin_bot.py
│   └── user_bot.py
├── backend/                # FastAPI backend
│   ├── app/
│   ├── alembic/
│   └── requirements.txt
└── logs/                   # Application logs
```

---

## 🔐 Security Notes

1. **Never commit .env file** - It contains sensitive information
2. **Change SECRET_KEY** - Generate a strong secret key
3. **Use strong passwords** - For database and admin accounts
4. **Enable HTTPS in production** - Set SECURE_SSL_REDIRECT=True
5. **Restrict ALLOWED_HOSTS** - Don't use '*' in production
6. **Set DEBUG=False** - In production environment

---

## 📞 Support

If you encounter issues:

1. Check logs in `logs/` directory
2. Verify all environment variables are set
3. Check service status (ports, processes)
4. Review error messages carefully
5. Check GitHub issues (if applicable)

---

## ✅ Post-Installation Checklist

- [ ] .env file configured
- [ ] Database connection working
- [ ] Redis running (if used)
- [ ] FastAPI backend accessible
- [ ] Telegram bots responding
- [ ] S-UI/X-UI panels connected
- [ ] All services running without errors

---

## 🎉 You're Ready!

Your Sales Panel is now set up and running. Access:
- **API Documentation:** http://localhost:8000/api/docs
- **Admin Panel:** Use Django admin or Telegram bot
- **User Interface:** Use Telegram user bot

Happy coding! 🚀

