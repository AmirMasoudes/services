# Docker Deployment Guide

This guide explains how to deploy the VPN Bot Management System using Docker and Docker Compose.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- At least 2GB RAM available
- Ports 80, 443, 5432, 6379, 8000, 8001 available (or configure different ports)

## Quick Start

### 1. Generate .env File

First, run the setup script to generate your `.env` file:

```powershell
powershell -ExecutionPolicy Bypass -File .\run.ps1
```

This will ask for all required configuration values and generate a complete `.env` file.

### 2. Build and Start All Services

```bash
docker compose up -d --build
```

This command will:
- Build all Docker images
- Create and start all containers
- Set up networking
- Initialize volumes
- Run health checks

### 3. Verify Services

Check that all services are running:

```bash
docker compose ps
```

All services should show "Up" status.

### 4. View Logs

View logs from all services:

```bash
docker compose logs -f
```

View logs from a specific service:

```bash
docker compose logs -f django_backend
docker compose logs -f fastapi_service
docker compose logs -f celery_worker
```

## Services

The Docker Compose setup includes the following services:

### 1. **postgres** - PostgreSQL Database
- Port: 5432 (configurable via `DB_PORT` in `.env`)
- Data persisted in `postgres_data` volume
- Health checks enabled

### 2. **redis** - Redis Cache & Message Broker
- Port: 6379 (configurable via `REDIS_PORT` in `.env`)
- Data persisted in `redis_data` volume
- Health checks enabled

### 3. **django_backend** - Django Application
- Port: 8000
- Automatically runs migrations on startup
- Collects static files
- Serves via Gunicorn with 4 workers

### 4. **fastapi_service** - FastAPI Application
- Port: 8001
- Runs with 4 Uvicorn workers
- Health check endpoint at `/health`

### 5. **celery_worker** - Celery Worker
- Processes background tasks
- 4 concurrent workers
- Connects to Redis for task queue

### 6. **celery_beat** - Celery Beat Scheduler
- Runs periodic tasks
- Connects to Redis for scheduling

### 7. **nginx** - Reverse Proxy
- Ports: 80 (HTTP), 443 (HTTPS - ready for TLS)
- Routes requests to Django and FastAPI
- Serves static and media files
- Production-ready configuration

## Access Points

After starting the services:

- **Django Admin**: http://localhost/admin/
- **Django API**: http://localhost/api/
- **FastAPI Docs**: http://localhost/docs
- **FastAPI ReDoc**: http://localhost/redoc
- **Health Check**: http://localhost/health

## Environment Variables

All services read from the `.env` file. Key variables:

```env
# Database
DB_NAME=vpnbot_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=postgres
DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0
REDIS_PORT=6379

# Celery
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2

# Django
SECRET_KEY=your_secret_key
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1

# FastAPI
DATABASE_URL=postgresql+asyncpg://postgres:password@postgres:5432/vpnbot_db
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

### View Service Status
```bash
docker compose ps
```

### Execute Commands in Containers

**Django shell:**
```bash
docker compose exec django_backend python manage.py shell
```

**Create Django superuser:**
```bash
docker compose exec django_backend python manage.py createsuperuser
```

**Run Django migrations manually:**
```bash
docker compose exec django_backend python manage.py migrate
```

**Access PostgreSQL:**
```bash
docker compose exec postgres psql -U postgres -d vpnbot_db
```

**Access Redis CLI:**
```bash
docker compose exec redis redis-cli
```

## Production Deployment

### 1. Configure TLS/SSL

1. Place your SSL certificates in `nginx/ssl/`:
   - `cert.pem` - SSL certificate
   - `key.pem` - Private key

2. Uncomment the HTTPS server block in `nginx/conf.d/default.conf`

3. Update `server_name` with your domain

4. Restart nginx:
   ```bash
   docker compose restart nginx
   ```

### 2. Set Production Environment Variables

Update `.env` with production values:

```env
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
SECRET_KEY=your-very-secure-secret-key
```

### 3. Configure Resource Limits

Add resource limits to `docker-compose.yml`:

```yaml
services:
  django_backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

### 4. Enable Logging

Logs are stored in Docker volumes. To persist logs:

```yaml
volumes:
  logs_volume:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /path/to/logs
```

## Troubleshooting

### Services Won't Start

1. Check logs:
   ```bash
   docker compose logs
   ```

2. Verify `.env` file exists and is properly formatted

3. Check port availability:
   ```bash
   netstat -an | findstr "8000 8001 5432 6379"
   ```

### Database Connection Issues

1. Verify PostgreSQL is healthy:
   ```bash
   docker compose exec postgres pg_isready -U postgres
   ```

2. Check database credentials in `.env`

3. Verify network connectivity:
   ```bash
   docker compose exec django_backend ping postgres
   ```

### Redis Connection Issues

1. Verify Redis is healthy:
   ```bash
   docker compose exec redis redis-cli ping
   ```

2. Check Redis URL in `.env`

### Static Files Not Loading

1. Collect static files:
   ```bash
   docker compose exec django_backend python manage.py collectstatic --noinput
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

## Backup and Restore

### Backup Database

```bash
docker compose exec postgres pg_dump -U postgres vpnbot_db > backup.sql
```

### Restore Database

```bash
docker compose exec -T postgres psql -U postgres vpnbot_db < backup.sql
```

### Backup Volumes

```bash
docker run --rm -v vpnbot_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz /data
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

### Log Aggregation

For production, consider using:
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Grafana + Prometheus
- Docker logging drivers

## Support

For issues or questions:
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

