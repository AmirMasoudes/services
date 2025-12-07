# VPN Bot Management System - Docker Deployment Guide

## Complete Docker Setup

This project is fully dockerized and production-ready. All services run in Docker containers with proper orchestration.

## Quick Start

### 1. Generate .env File

```powershell
powershell -ExecutionPolicy Bypass -File .\run.ps1
```

This will:
- Ask for all required configuration values
- Generate a complete `.env` file
- Create virtual environment
- Install dependencies
- Run Django migrations

### 2. Start All Services

```bash
docker compose up -d --build
```

This single command will:
- Build all Docker images
- Start PostgreSQL database
- Start Redis cache
- Run auto-migrations
- Start Django backend
- Start FastAPI service
- Start Celery worker
- Start Celery beat scheduler
- Start Admin bot
- Start User bot
- Start NGINX reverse proxy

### 3. Verify Services

```bash
docker compose ps
```

All services should show "Up" status.

## Services

### Core Services

1. **postgres** - PostgreSQL 15 database
   - Port: 5432
   - Data persisted in `postgres_data` volume

2. **redis** - Redis 7 cache and message broker
   - Port: 6379
   - Data persisted in `redis_data` volume

3. **auto_migrate** - Runs migrations once on startup
   - Runs Django migrations
   - Collects static files
   - Exits after completion

### Application Services

4. **django** - Django backend (Gunicorn)
   - Port: 8000
   - URL: http://localhost:8000
   - Admin: http://localhost:8000/admin/

5. **fastapi** - FastAPI service (Uvicorn)
   - Port: 8001
   - URL: http://localhost:8001
   - Docs: http://localhost:8001/docs

6. **celery_worker** - Celery background worker
   - Processes async tasks
   - 4 concurrent workers

7. **celery_beat** - Celery scheduler
   - Runs periodic tasks
   - Scheduled jobs

### Bot Services

8. **admin_bot** - Telegram Admin Bot
   - Connects to Telegram API
   - Manages X-UI servers
   - Handles admin commands

9. **user_bot** - Telegram User Bot
   - Connects to Telegram API
   - User-facing bot
   - Handles user requests

### Proxy Service

10. **nginx** - NGINX reverse proxy
    - Port: 80 (HTTP), 443 (HTTPS)
    - Routes to Django and FastAPI
    - Serves static files
    - Production-ready configuration

## Access Points

After starting services:

- **Django Admin**: http://localhost/admin/
- **Django API**: http://localhost/api/
- **FastAPI Docs**: http://localhost/docs
- **FastAPI ReDoc**: http://localhost/redoc
- **Health Check**: http://localhost/health

## Environment Variables

All services read from `.env` file. Key variables:

```env
# Server
SERVER_IP=127.0.0.1

# Panel
PANEL_USERNAME=admin
PANEL_PASSWORD=your_password
PANEL_PORT=2053
PANEL_URL=http://127.0.0.1:2053

# Telegram Bots
ADMIN_BOT_TOKEN=your_token
USER_BOT_TOKEN=your_token
ADMIN_USER_IDS=123456789

# Database
DB_NAME=vpnbot_db
DB_USER=postgres
DB_PASSWORD=your_password
DATABASE_HOST=postgres
DATABASE_PORT=5432

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# Celery
CELERY_BROKER=redis://redis:6379/0
CELERY_BACKEND=redis://redis:6379/1
```

## Common Commands

### Start Services
```bash
docker compose up -d
```

### Stop Services
```bash
docker compose down
```

### Stop and Remove Volumes (⚠️ Deletes Data)
```bash
docker compose down -v
```

### Rebuild After Code Changes
```bash
docker compose up -d --build
```

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f django
docker compose logs -f fastapi
docker compose logs -f admin_bot
docker compose logs -f user_bot
```

### Execute Commands

**Django shell:**
```bash
docker compose exec django python manage.py shell
```

**Create superuser:**
```bash
docker compose exec django python manage.py createsuperuser
```

**Run migrations manually:**
```bash
docker compose exec django python manage.py migrate
```

**Access PostgreSQL:**
```bash
docker compose exec postgres psql -U postgres -d vpnbot_db
```

**Access Redis CLI:**
```bash
docker compose exec redis redis-cli
```

## Service Dependencies

Services start in this order:

1. **postgres** and **redis** (health checks)
2. **auto_migrate** (waits for postgres/redis)
3. **django** (waits for postgres/redis/auto_migrate)
4. **fastapi** (waits for postgres/redis)
5. **celery_worker** and **celery_beat** (wait for postgres/redis/django)
6. **admin_bot** and **user_bot** (wait for postgres/redis/django)
7. **nginx** (waits for django/fastapi)

## Troubleshooting

### Services Won't Start

1. Check logs:
   ```bash
   docker compose logs
   ```

2. Verify `.env` file exists and is properly formatted

3. Check port availability:
   ```bash
   netstat -an | grep -E "8000|8001|5432|6379|80"
   ```

### Database Connection Issues

1. Verify PostgreSQL is healthy:
   ```bash
   docker compose exec postgres pg_isready -U postgres
   ```

2. Check database credentials in `.env`

3. Verify network connectivity:
   ```bash
   docker compose exec django ping postgres
   ```

### Redis Connection Issues

1. Verify Redis is healthy:
   ```bash
   docker compose exec redis redis-cli ping
   ```

2. Check Redis URL in `.env`

### Bot Not Starting

1. Check bot logs:
   ```bash
   docker compose logs admin_bot
   docker compose logs user_bot
   ```

2. Verify bot tokens in `.env`:
   - `ADMIN_BOT_TOKEN`
   - `USER_BOT_TOKEN`

3. Check bot can reach Django:
   ```bash
   docker compose exec admin_bot ping django
   ```

### Static Files Not Loading

1. Collect static files:
   ```bash
   docker compose exec django python manage.py collectstatic --noinput
   ```

2. Verify nginx volume mounts

### Celery Not Processing Tasks

1. Check Celery worker logs:
   ```bash
   docker compose logs celery_worker
   ```

2. Verify Redis connection

3. Check task registration:
   ```bash
   docker compose exec celery_worker celery -A config.celery inspect active
   ```

## Production Deployment

### 1. Configure TLS/SSL

1. Place SSL certificates in `nginx/ssl/`:
   - `cert.pem` - SSL certificate
   - `key.pem` - Private key

2. Uncomment HTTPS server block in `nginx/conf.d/default.conf`

3. Update `server_name` with your domain

4. Restart nginx:
   ```bash
   docker compose restart nginx
   ```

### 2. Set Production Environment Variables

Update `.env`:

```env
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
SECRET_KEY=your-very-secure-secret-key
```

### 3. Resource Limits

Add to `docker-compose.yml`:

```yaml
services:
  django:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

## Backup and Restore

### Backup Database

```bash
docker compose exec postgres pg_dump -U postgres vpnbot_db > backup.sql
```

### Restore Database

```bash
docker compose exec -T postgres psql -U postgres vpnbot_db < backup.sql
```

## Monitoring

### Health Checks

All services have health checks. View status:

```bash
docker compose ps
```

### Resource Usage

```bash
docker stats
```

## Architecture

```
┌─────────────────────────────────────────┐
│           NGINX (Port 80/443)          │
└──────────────┬──────────────────────────┘
               │
    ┌──────────┴──────────┐
    │                     │
┌───▼────┐          ┌─────▼────┐
│ Django │          │  FastAPI  │
│ :8000  │          │  :8001    │
└───┬────┘          └─────┬─────┘
    │                     │
    ├──────────┬──────────┤
    │          │          │
┌───▼────┐ ┌───▼────┐ ┌───▼────┐
│ Celery │ │ Celery │ │  Bots  │
│ Worker │ │  Beat  │ │        │
└───┬────┘ └───┬────┘ └───┬────┘
    │          │          │
    └──────────┴──────────┘
         │          │
    ┌────▼────┐ ┌──▼────┐
    │ Postgres│ │ Redis │
    │  :5432  │ │ :6379 │
    └─────────┘ └───────┘
```

## Support

For issues:
1. Check service logs: `docker compose logs`
2. Verify `.env` configuration
3. Review this README
4. Check Docker and Docker Compose versions

## Notes

- All services use `restart: unless-stopped` policy
- Network isolation via `vpnbot_network`
- Data persistence via Docker volumes
- Health checks ensure service availability
- Production-ready NGINX configuration included
- Auto-migration runs on startup
- All services wait for dependencies before starting

