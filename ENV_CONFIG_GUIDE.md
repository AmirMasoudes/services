# Environment Configuration Guide

## Overview

This project uses **two separate environment files** for clean separation between Django and FastAPI services:

1. **`config.env`** - Django backend + shared services (Telegram bots, X-UI, S-UI, Celery)
2. **`backend_fastapi.env`** - FastAPI backend only

## File Structure

```
services/
├── config.env              # Django + Shared Services
├── backend_fastapi.env     # FastAPI Backend
└── ENV_CONFIG_GUIDE.md     # This file
```

## Configuration Files

### 1. `config.env` (Django + Shared Services)

**Used by:**
- Django application (`config/settings.py`)
- Telegram bots (`bot/admin_bot.py`, `bot/user_bot.py`)
- X-UI integration (`xui_servers/`)
- S-UI integration (`xui_servers/sui_client.py`)
- Celery tasks (`xui_servers/tasks.py`)

**Key Variables:**
- `SECRET_KEY` - Django secret key
- `DB_ENGINE`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` - Database config
- `ADMIN_BOT_TOKEN`, `USER_BOT_TOKEN` - Telegram bot tokens
- `XUI_*` - X-UI panel configuration
- `SUI_*` - S-UI panel configuration
- `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND` - Celery configuration

### 2. `backend_fastapi.env` (FastAPI Backend)

**Used by:**
- FastAPI application (`backend/app/core/config.py`)

**Key Variables:**
- `SECRET_KEY` - FastAPI JWT secret key
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection
- `SUI_BASE_URL`, `SUI_API_KEY` - S-UI API configuration
- `CORS_ORIGINS` - CORS allowed origins

## Setup Instructions

### Option 1: Separate Files (Recommended)

1. **Configure Django:**
   ```bash
   cp config.env config.env.local
   # Edit config.env.local with your values
   ```

2. **Configure FastAPI:**
   ```bash
   cp backend_fastapi.env backend_fastapi.env.local
   # Edit backend_fastapi.env.local with your values
   ```

3. **Update code to load from separate files:**
   - Django already loads from `config.env`
   - FastAPI needs to be updated to load from `backend_fastapi.env`

### Option 2: Unified File (Alternative)

If you prefer a single file, you can combine both into `.env` at the project root. Both services will read from it.

## Variable Categories

### Django Core
- `SECRET_KEY` - **REQUIRED** - Django secret key
- `DEBUG` - Debug mode (False for production)
- `ALLOWED_HOSTS` - Comma-separated list of allowed hosts

### Database
- `DB_ENGINE` - Database engine (`django.db.backends.sqlite3` or `django.db.backends.postgresql`)
- `DB_NAME` - Database name
- `DB_USER` - Database user (PostgreSQL only)
- `DB_PASSWORD` - Database password (PostgreSQL only)
- `DB_HOST` - Database host (PostgreSQL only)
- `DB_PORT` - Database port (PostgreSQL only)
- `DATABASE_URL` - FastAPI database URL (PostgreSQL only)

### Telegram Bots
- `ADMIN_BOT_TOKEN` - **REQUIRED** - Admin bot token from @BotFather
- `USER_BOT_TOKEN` - **REQUIRED** - User bot token from @BotFather
- `ADMIN_PASSWORD` - **REQUIRED** - Admin password for bot authentication
- `ADMIN_USER_IDS` - **REQUIRED** - Comma-separated Telegram user IDs

### X-UI Panel
- `XUI_DEFAULT_HOST` - X-UI panel host
- `XUI_DEFAULT_PORT` - X-UI panel port
- `XUI_DEFAULT_USERNAME` - X-UI panel username
- `XUI_DEFAULT_PASSWORD` - X-UI panel password
- `XUI_WEB_BASE_PATH` - X-UI web base path
- `XUI_USE_SSL` - Use SSL (True/False)
- `XUI_VERIFY_SSL` - Verify SSL certificate (True/False)
- `XUI_TIMEOUT` - Request timeout in seconds

### S-UI Panel
- `SUI_HOST` - S-UI panel host
- `SUI_PORT` - S-UI panel port
- `SUI_USE_SSL` - Use SSL (True/False)
- `SUI_BASE_PATH` - S-UI base path
- `SUI_API_TOKEN` - S-UI API token
- `SUI_BASE_URL` - FastAPI S-UI base URL
- `SUI_API_KEY` - FastAPI S-UI API key
- `SUI_DEFAULT_TIMEOUT` - Request timeout
- `SUI_MAX_RETRIES` - Maximum retry attempts

### VPN Protocol
- `DEFAULT_PROTOCOL` - Default VPN protocol (vless/vmess/trojan)
- `MIN_PORT` - Minimum port number
- `MAX_PORT` - Maximum port number
- `TLS_ENABLED` - Enable TLS
- `REALITY_ENABLED` - Enable Reality protocol
- `REALITY_DEST` - Reality destination
- `REALITY_SERVER_NAMES` - Reality server names
- `REALITY_PRIVATE_KEY` - Reality private key
- `WS_PATH` - WebSocket path
- `WS_HOST` - WebSocket host

### Trial & Plans
- `TRIAL_HOURS` - Trial duration in hours
- `PAID_DAYS` - Paid plan duration in days
- `EXPIRY_WARNING_HOURS` - Hours before expiry to warn
- `EXPIRY_WARNING_MESSAGE` - Warning message template

### Naming
- `TRIAL_INBOUND_PREFIX` - Prefix for trial inbounds
- `PAID_INBOUND_PREFIX` - Prefix for paid inbounds
- `USER_INBOUND_PREFIX` - Prefix for user inbounds

### Connection
- `CONNECTION_TIMEOUT` - Connection timeout in seconds
- `RETRY_ATTEMPTS` - Number of retry attempts

### Celery
- `CELERY_BROKER_URL` - Celery broker URL (Redis)
- `CELERY_RESULT_BACKEND` - Celery result backend (Redis)

### FastAPI Security
- `SECRET_KEY` - JWT secret key
- `ALGORITHM` - JWT algorithm (HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Access token expiry
- `REFRESH_TOKEN_EXPIRE_DAYS` - Refresh token expiry

### FastAPI CORS
- `CORS_ORIGINS` - Comma-separated allowed origins
- `CORS_ALLOW_CREDENTIALS` - Allow credentials

## Removed Variables

The following variables were **removed** as they are not actually used in the codebase:

- ❌ `EMAIL_*` - Email settings (defined but never used)
- ❌ `PAYMENT_CARD_NUMBER` - Payment card (only used once with hardcoded default)
- ❌ `CURRENCY`, `CURRENCY_SYMBOL` - Currency settings (defined but never used)
- ❌ `TELEGRAM_NOTIFICATIONS_ENABLED`, `SYSTEM_MESSAGES_ENABLED` - Notification flags (defined but never used)
- ❌ `MESSAGE_LANGUAGE`, `MESSAGE_RTL` - Message settings (defined but never used)
- ❌ `DEFAULT_TRIAL_PLAN_*` - Trial plan defaults (defined but never used)
- ❌ `LIMIT_IP_PER_USER`, `MB_TO_GB_CONVERSION` - Advanced settings (defined but never used)
- ❌ `RATE_LIMIT_*` - Rate limiting (FastAPI default values, not configurable)
- ❌ `DEFAULT_PAGE_SIZE`, `MAX_PAGE_SIZE` - Pagination (FastAPI default values, not configurable)
- ❌ `TELEGRAM_BOT_TOKEN`, `TELEGRAM_ADMIN_ID` - FastAPI Telegram (not used, bots use Django settings)

## Production Checklist

- [ ] Set `DEBUG=False` in both files
- [ ] Generate strong `SECRET_KEY` values (different for Django and FastAPI)
- [ ] Configure PostgreSQL database
- [ ] Set proper `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS`
- [ ] Enable SSL settings (`SECURE_SSL_REDIRECT=True`, `SESSION_COOKIE_SECURE=True`)
- [ ] Configure production Redis URLs
- [ ] Set proper Telegram bot tokens
- [ ] Configure X-UI/S-UI panel credentials
- [ ] Set production server IP/domain

## Security Notes

1. **Never commit** `.env` or `config.env` files to version control
2. Use **different** `SECRET_KEY` values for Django and FastAPI
3. Use **strong passwords** for database and panel access
4. Enable **SSL/TLS** in production
5. Restrict `ALLOWED_HOSTS` to your actual domains
6. Use **environment-specific** files (`.env.production`, `.env.staging`)

