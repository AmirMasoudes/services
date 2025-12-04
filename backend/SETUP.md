# Setup Instructions

## Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker and Docker Compose (optional)

## Quick Start with Docker

1. **Clone and navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Copy environment file:**
   ```bash
   cp .env.example .env
   ```

3. **Edit `.env` file with your configuration:**
   - Set `SECRET_KEY` (generate with: `openssl rand -hex 32`)
   - Set `DATABASE_URL` if using external database
   - Set `TELEGRAM_BOT_TOKEN` and `TELEGRAM_ADMIN_ID` (optional)

4. **Start services:**
   ```bash
   docker-compose up -d
   ```

5. **Create database tables:**
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

6. **Create admin user:**
   ```bash
   docker-compose exec backend python scripts/seed_admin.py
   ```

7. **Access the API:**
   - API: http://localhost:8000
   - Docs: http://localhost:8000/api/docs
   - Health: http://localhost:8000/health

## Manual Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up PostgreSQL database:**
   ```sql
   CREATE DATABASE sales_panel;
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Run migrations:**
   ```bash
   alembic upgrade head
   ```

5. **Create admin user:**
   ```bash
   python scripts/seed_admin.py
   ```

6. **Start Redis:**
   ```bash
   redis-server
   ```

7. **Start the application:**
   ```bash
   uvicorn app.main:app --reload
   ```

8. **Start Celery worker (new terminal):**
   ```bash
   celery -A app.core.celery_app worker --loglevel=info
   ```

9. **Start Celery beat (new terminal):**
   ```bash
   celery -A app.core.celery_app beat --loglevel=info
   ```

## Creating Initial Migration

If you need to create the initial migration:

```bash
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## Default Admin Credentials

After running the seed script:
- Username: `admin`
- Password: `admin123`

**⚠️ IMPORTANT: Change the password immediately after first login!**

## Testing the API

1. **Login to get access token:**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "admin123"}'
   ```

2. **Use the access token in subsequent requests:**
   ```bash
   curl -X GET "http://localhost:8000/api/v1/users" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
   ```

## Import Postman Collection

1. Open Postman
2. Click Import
3. Select `postman_collection.json`
4. Set environment variable `base_url` to `http://localhost:8000`
5. Login first to get tokens, then set `access_token` variable

## Troubleshooting

### Database Connection Issues
- Check PostgreSQL is running
- Verify DATABASE_URL in .env
- Ensure database exists

### Redis Connection Issues
- Check Redis is running: `redis-cli ping`
- Verify REDIS_URL in .env

### Celery Issues
- Ensure Redis is running
- Check CELERY_BROKER_URL and CELERY_RESULT_BACKEND

### S-UI Integration Issues
- Verify panel URL and API key
- Check server health endpoint
- Review logs for detailed errors

## Production Deployment

1. Set `DEBUG=False`
2. Use strong `SECRET_KEY`
3. Configure proper CORS origins
4. Use production database
5. Enable HTTPS
6. Set up proper logging
7. Use reverse proxy (nginx)
8. Configure firewall rules
9. Set up monitoring
10. Regular backups

