# Setup Instructions for run.ps1

## Quick Start

### 1. Run the Script

Open PowerShell as Administrator (recommended) or regular user, navigate to the project directory, and run:

```powershell
powershell -ExecutionPolicy Bypass -File .\run.ps1
```

### 2. Alternative Execution Methods

If you get execution policy errors, try:

```powershell
# Method 1: Bypass for this session
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
.\run.ps1

# Method 2: Unrestricted (less secure)
Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Scope CurrentUser
.\run.ps1
```

## What the Script Does

1. **Checks Python Installation** - Verifies Python 3.10+ is installed
2. **Collects Configuration** - Interactively asks for all required values
3. **Generates .env File** - Creates production-ready environment file
4. **Creates Virtual Environment** - Sets up `.venv` directory
5. **Installs Dependencies** - Installs all required packages
6. **Sets Up Redis** - Configures Redis (Docker/Local/Skip)
7. **Initializes Databases** - Runs Django migrations and Alembic upgrades
8. **Starts Services** - Launches Django, FastAPI, and Bots in separate terminals

## Example .env Output

After running the script, you'll get a `.env` file like this:

```env
# ========================================
# Auto-generated environment configuration
# Generated on: 2024-12-05 10:30:45
# ========================================

# Django Core
SECRET_KEY=django-insecure-your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=vpnbot_db
DB_USER=postgres
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432

# FastAPI Database
DATABASE_URL=postgresql+asyncpg://postgres:your_secure_password@localhost:5432/vpnbot_db
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# Security
CSRF_TRUSTED_ORIGINS=http://localhost,https://localhost,https://yourdomain.com
SECURE_HSTS_SECONDS=31536000
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Telegram Bots
ADMIN_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
USER_BOT_TOKEN=9876543210:XYZwvuTSRqpoNMLkjihGFE
ADMIN_PASSWORD=your_secure_admin_password
ADMIN_USER_IDS=123456789,987654321

# X-UI Panel
XUI_DEFAULT_HOST=xui.yourdomain.com
XUI_DEFAULT_PORT=2053
XUI_DEFAULT_USERNAME=admin
XUI_DEFAULT_PASSWORD=your_xui_password
XUI_WEB_BASE_PATH=/admin/
XUI_USE_SSL=True
XUI_VERIFY_SSL=True
XUI_TIMEOUT=30

# S-UI Panel
SUI_HOST=sui.yourdomain.com
SUI_PORT=2095
SUI_USE_SSL=True
SUI_BASE_PATH=/app
SUI_API_TOKEN=your_sui_api_token
SUI_BASE_URL=https://sui.yourdomain.com:2095
SUI_API_KEY=your_sui_api_key
SUI_DEFAULT_TIMEOUT=30
SUI_MAX_RETRIES=3

# Server Configuration
SERVER_IP=192.168.1.100
SERVER_DOMAIN=yourdomain.com
SERVER_PORT=8000
SERVER_PROTOCOL=https

# VPN Protocol
DEFAULT_PROTOCOL=vless
MIN_PORT=10000
MAX_PORT=65000
TLS_ENABLED=True
REALITY_ENABLED=True
REALITY_DEST=www.aparat.com:443
REALITY_SERVER_NAMES=www.aparat.com
REALITY_PRIVATE_KEY=your_reality_private_key_here
WS_PATH=/
WS_HOST=

# Trial & Plan
TRIAL_HOURS=24
PAID_DAYS=30
EXPIRY_WARNING_HOURS=6
EXPIRY_WARNING_MESSAGE=کانفیگ شما تا {hours} ساعت دیگر منقضی می‌شود ⏰

# Naming Prefixes
TRIAL_INBOUND_PREFIX=TrialBot
PAID_INBOUND_PREFIX=PaidBot
USER_INBOUND_PREFIX=UserBot

# Connection Settings
CONNECTION_TIMEOUT=15
RETRY_ATTEMPTS=5

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_CACHE_TTL=3600

# Celery
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# FastAPI
ENVIRONMENT=production
HOST=0.0.0.0
PORT=8001
SECRET_KEY=your_fastapi_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
CORS_ALLOW_CREDENTIALS=True
```

## Interactive Prompts

The script will ask you for:

### Required Fields (marked with *)
- Django SECRET_KEY *
- Admin bot token *
- User bot token *
- Admin password *
- Admin user IDs *
- X-UI username *
- X-UI password *
- Reality private key *
- Database credentials (if PostgreSQL) *

### Optional Fields (have defaults)
- DEBUG (default: False)
- ALLOWED_HOSTS (default: localhost,127.0.0.1)
- Server IP/Domain
- Redis mode (docker/local/skip)
- And many more with sensible defaults

## Service Terminals

After setup, the script opens **3 separate PowerShell windows**:

1. **Terminal 1** - Django server (`python manage.py runserver`)
2. **Terminal 2** - FastAPI server (`uvicorn backend.app.main:app`)
3. **Terminal 3** - Telegram bots (user_bot.py, admin_bot.py)

Each terminal shows real-time logs and can be closed independently.

## Log Files

All logs are saved in the `logs/` directory:

- `logs/backend.log` - Django server output
- `logs/api.log` - FastAPI server output
- `logs/bots.log` - Bot services output
- `logs/error.log` - Error messages
- `logs/django_makemigrations.log` - Migration creation logs
- `logs/django_migrate.log` - Migration application logs
- `logs/alembic_upgrade.log` - Alembic migration logs

## Troubleshooting

### Python Not Found
- Install Python 3.10-3.12 from https://www.python.org/
- Make sure to check "Add Python to PATH" during installation
- Restart PowerShell after installation

### Execution Policy Error
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Redis Issues
- **Docker mode**: Make sure Docker Desktop is running
- **Local mode**: Install Redis for Windows from GitHub releases
- **Skip mode**: Services will run but Celery won't work

### Database Connection Errors
- For PostgreSQL: Make sure PostgreSQL is running and credentials are correct
- For SQLite: Make sure the directory is writable

### Port Already in Use
- Change ports in the configuration
- Django: `SERVER_PORT` (default: 8000)
- FastAPI: `FASTAPI_PORT` (default: 8001)

## Requirements

- **Windows 10+**
- **PowerShell 5.0+**
- **Python 3.10 - 3.12**
- **Docker Desktop** (optional, for Redis Docker mode)
- **PostgreSQL** (optional, if using PostgreSQL instead of SQLite)

## Security Notes

1. The `.env` file contains sensitive information - **never commit it to version control**
2. Use strong passwords for all services
3. In production, set `DEBUG=False`
4. Enable SSL/TLS settings for production
5. Restrict `ALLOWED_HOSTS` to your actual domains

## Next Steps

After successful setup:

1. Verify all services are running in their terminals
2. Check logs for any errors
3. Test Django admin at: http://localhost:8000/admin
4. Test FastAPI docs at: http://localhost:8001/api/docs
5. Test Telegram bots by sending `/start` command

## Support

If you encounter issues:

1. Check the `logs/error.log` file
2. Verify all requirements are met
3. Check that ports are not in use
4. Ensure all credentials are correct
5. Review the service terminal outputs

