# Implementation Guide - Complete System Refactoring

## Overview

This guide provides step-by-step instructions for implementing all fixes and improvements identified in the audit.

---

## Prerequisites

- Python 3.11+
- Django 5.2+
- PostgreSQL (recommended) or SQLite (development)
- Redis (for Celery)
- Git

---

## Step 1: Environment Setup

### 1.1 Clone Repository

```bash
git clone https://github.com/AmirMasoudes/services.git
cd services
```

### 1.2 Create Branch

```bash
git checkout -b cursor/sui-bots-refactor
```

### 1.3 Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 1.4 Install Dependencies

```bash
pip install -r requirements.txt
pip install pytest pytest-django pytest-cov requests-mock black ruff isort mypy
```

### 1.5 Create Environment File

```bash
cp .env.example .env
# Edit .env with your actual values
```

**CRITICAL:** Never commit `.env` file. It's already in `.gitignore`.

---

## Step 2: Database Migrations

### 2.1 Review Model Changes

The following models have been updated:
- `order/models.py` - Added status, order_number, payment fields, fixed OneToOne → ForeignKey
- `xui_servers/models.py` - Added health checks, sync fields, status, subscription_url, indexes
- New `AuditLog` model added

### 2.2 Create Migrations

```bash
python manage.py makemigrations
```

This will create migrations for:
- `order` app (OrderUserModel, PayMentModel changes)
- `xui_servers` app (XUIServer, XUIInbound, XUIClient, UserConfig, AuditLog changes)

### 2.3 Review Migrations

```bash
python manage.py showmigrations
```

### 2.4 Apply Migrations

```bash
python manage.py migrate
```

**Note:** If you have existing data, the migrations include data migrations to:
- Generate order numbers for existing orders
- Set default status values
- Create indexes

### 2.5 Verify Migrations

```bash
python manage.py dbshell
# Check tables
\dt
# Check indexes
\d+ order_orderusermodel
\d+ xui_servers_userconfig
```

---

## Step 3: S-UI Integration

### 3.1 Verify S-UI Client

The S-UI client is already created in `xui_servers/sui_client.py` with:
- Retry logic with exponential backoff
- Idempotency support
- Health checks
- Proper error handling

### 3.2 Configure S-UI Settings

In your `.env` file:

```env
SUI_HOST=your-sui-server-host
SUI_PORT=2095
SUI_USE_SSL=False
SUI_BASE_PATH=/app
SUI_API_TOKEN=your-api-token
```

### 3.3 Test S-UI Connection

```python
python manage.py shell
```

```python
from xui_servers.sui_client import SUIClient

client = SUIClient(
    host='your-host',
    port=2095,
    api_token='your-token'
)

# Test connection
if client.login():
    print("✅ S-UI connection successful")
    inbounds = client.get_inbounds()
    print(f"Found {len(inbounds)} inbounds")
else:
    print("❌ S-UI connection failed")
```

---

## Step 4: Celery Setup

### 4.1 Start Redis

```bash
# Using Docker
docker run -d -p 6379:6379 redis:7

# Or install locally
# Ubuntu/Debian: sudo apt-get install redis-server
# macOS: brew install redis
```

### 4.2 Verify Celery Configuration

Check `config/celery.py` and `config/settings.py` for Celery settings.

### 4.3 Start Celery Worker

```bash
celery -A config worker -l info
```

### 4.4 Start Celery Beat (for scheduled tasks)

```bash
celery -A config beat -l info
```

### 4.5 Test Celery Tasks

```python
python manage.py shell
```

```python
from xui_servers.provisioning_tasks import provision_subscription

# Test task (will fail if no real config, but tests the queue)
result = provision_subscription.delay('test-id')
print(result.get(timeout=10))
```

---

## Step 5: Update Bot Handlers

### 5.1 Admin Bot

The admin bot needs modularization. For now, ensure it uses the new provisioning tasks:

**In `bot/admin_bot.py`, update provisioning calls to use:**

```python
from xui_servers.provisioning_tasks import provision_subscription

# Instead of direct provisioning:
provision_subscription.delay(str(user_config.id), idempotency_key=f"admin_{user_id}")
```

### 5.2 User Bot

Update user bot to:
1. Use provisioning tasks for subscription creation
2. Generate subscription links properly
3. Check sync status before showing configs

**Example update in `bot/user_bot.py`:**

```python
from xui_servers.provisioning_tasks import provision_subscription

# When user purchases plan:
user_config = UserConfig.objects.create(...)
provision_subscription.delay(str(user_config.id))
```

---

## Step 6: Security Hardening

### 6.1 Remove Secrets from Repository

```bash
# Check for secrets
git log --all --full-history -- config.env
git log --all --full-history -- db.sqlite3

# If found, remove from history (use git-filter-repo or BFG)
# See SECURITY_FIXES.md for details
```

### 6.2 Verify .gitignore

Ensure `.gitignore` includes:
- `.env`
- `config.env`
- `db.sqlite3`
- `*.log`
- `secrets/`

### 6.3 Rotate Secrets

If any secrets were exposed:
1. Generate new bot tokens from @BotFather
2. Generate new API tokens for S-UI
3. Update `.env` file
4. Update production environment

### 6.4 Enable Security Settings

In `config/settings.py` (for production):

```python
DEBUG = False
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
```

---

## Step 7: Testing

### 7.1 Run Unit Tests

```bash
pytest tests/test_sui_client.py -v
```

### 7.2 Run Integration Tests

```bash
pytest tests/test_provisioning.py -v
```

### 7.3 Run All Tests

```bash
pytest tests/ -v --cov=. --cov-report=html
```

### 7.4 Check Coverage

Open `htmlcov/index.html` in browser to see coverage report.

---

## Step 8: Code Quality

### 8.1 Format Code

```bash
black .
isort .
```

### 8.2 Lint Code

```bash
ruff check .
```

### 8.3 Type Check

```bash
mypy . --ignore-missing-imports
```

---

## Step 9: Deployment

### 9.1 Production Checklist

- [ ] All migrations applied
- [ ] Environment variables set
- [ ] Secrets rotated
- [ ] Database backed up
- [ ] Celery workers running
- [ ] Redis running
- [ ] Tests passing
- [ ] Security settings enabled
- [ ] Monitoring configured

### 9.2 Start Services

```bash
# Django
gunicorn config.wsgi:application --bind 0.0.0.0:8000

# Celery Worker
celery -A config worker -l info

# Celery Beat
celery -A config beat -l info

# Admin Bot
python bot/admin_bot.py

# User Bot
python bot/user_bot.py
```

### 9.3 Health Checks

```bash
# Django
curl http://localhost:8000/admin/

# Celery
celery -A config inspect active

# Redis
redis-cli ping
```

---

## Step 10: Monitoring

### 10.1 Set Up Logging

Configure logging in `config/settings.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'xui_servers': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

### 10.2 Monitor Tasks

```bash
# View active tasks
celery -A config inspect active

# View scheduled tasks
celery -A config inspect scheduled

# View stats
celery -A config inspect stats
```

---

## Troubleshooting

### Migration Issues

If migrations fail:

```bash
# Show migration status
python manage.py showmigrations

# Fake migration (if needed)
python manage.py migrate --fake

# Rollback (if needed)
python manage.py migrate app_name previous_migration
```

### Celery Issues

```bash
# Check Celery status
celery -A config inspect ping

# Purge queue (if needed)
celery -A config purge

# Check logs
tail -f logs/celery.log
```

### S-UI Connection Issues

1. Verify API token is correct
2. Check network connectivity
3. Verify SSL settings
4. Check S-UI panel is accessible
5. Review logs for detailed errors

---

## Next Steps

After completing this guide:

1. **Modularize Bots:** Split `admin_bot.py` and `user_bot.py` into modules
2. **Add More Tests:** Increase test coverage
3. **Performance Optimization:** Add caching, optimize queries
4. **Monitoring:** Set up proper monitoring and alerting
5. **Documentation:** Complete API documentation

---

## Support

For issues or questions:
- Review `AUDIT_REPORT.md` for problem details
- Check `SECURITY_FIXES.md` for security improvements
- See code comments for implementation details
