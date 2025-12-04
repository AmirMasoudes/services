# Sales Panel Backend API

Production-ready FastAPI backend for Sales Panel project.

## Features

- ✅ FastAPI with async/await support
- ✅ PostgreSQL database with SQLAlchemy
- ✅ JWT authentication with role-based access control
- ✅ Redis for caching and rate limiting
- ✅ Celery for background tasks
- ✅ S-UI panel integration
- ✅ Telegram notifications
- ✅ Full CRUD operations for all modules
- ✅ Comprehensive error handling
- ✅ Logging system
- ✅ Docker support

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/      # API endpoints
│   ├── core/
│   │   ├── config.py          # Configuration
│   │   ├── database.py        # Database setup
│   │   ├── security.py        # JWT & password hashing
│   │   └── celery_app.py     # Celery configuration
│   ├── crud/                  # CRUD operations
│   ├── models/                # SQLAlchemy models
│   ├── schemas/               # Pydantic schemas
│   ├── services/              # Business logic services
│   ├── tasks/                 # Celery tasks
│   ├── middleware/            # Custom middlewares
│   └── main.py                # FastAPI app
├── alembic/                   # Database migrations
├── scripts/                   # Utility scripts
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Quick Start

### Using Docker (Recommended)

1. Clone the repository
2. Copy `.env.example` to `.env` and configure it
3. Run with Docker Compose:

```bash
docker-compose up -d
```

4. Create admin user:

```bash
docker-compose exec backend python scripts/seed_admin.py
```

### Manual Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Set up environment variables:

```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Run database migrations:

```bash
alembic upgrade head
```

4. Create admin user:

```bash
python scripts/seed_admin.py
```

5. Start the server:

```bash
uvicorn app.main:app --reload
```

6. Start Celery worker (in another terminal):

```bash
celery -A app.core.celery_app worker --loglevel=info
```

7. Start Celery beat (in another terminal):

```bash
celery -A app.core.celery_app beat --loglevel=info
```

## API Documentation

Once the server is running, access the API documentation at:

- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## Environment Variables

See `.env.example` for all available environment variables.

### Required Variables

- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT secret key (generate with `openssl rand -hex 32`)
- `TELEGRAM_BOT_TOKEN`: Telegram bot token (optional)
- `TELEGRAM_ADMIN_ID`: Admin Telegram ID (optional)

## API Modules

### 1. Authentication (`/api/v1/auth`)
- `POST /login` - User login
- `POST /refresh` - Refresh access token
- `GET /me` - Get current user info

### 2. Users (`/api/v1/users`)
- `GET /` - List users (Admin)
- `POST /` - Create user (Admin)
- `GET /{id}` - Get user (Admin)
- `PUT /{id}` - Update user (Admin)
- `DELETE /{id}` - Delete user (Admin)
- `POST /{id}/balance` - Update balance (Admin)
- `GET /me` - Get own profile

### 3. Servers (`/api/v1/servers`)
- `GET /` - List servers (Admin)
- `POST /` - Create server (Admin)
- `GET /{id}` - Get server (Admin)
- `PUT /{id}` - Update server (Admin)
- `DELETE /{id}` - Delete server (Admin)
- `POST /{id}/check-health` - Check server health (Admin)
- `GET /{id}/capacity` - Get capacity info (Admin)

### 4. Configs (`/api/v1/configs`)
- `GET /` - List configs
- `POST /` - Create config
- `GET /{id}` - Get config
- `PUT /{id}` - Update config (Admin)
- `DELETE /{id}` - Delete config

### 5. Orders (`/api/v1/orders`)
- `GET /` - List orders
- `POST /` - Create order
- `GET /{id}` - Get order
- `PUT /{id}` - Update order (Admin)
- `GET /stats/summary` - Get statistics (Admin)

### 6. Tickets (`/api/v1/tickets`)
- `GET /` - List tickets
- `POST /` - Create ticket
- `GET /{id}` - Get ticket
- `PUT /{id}` - Answer ticket (Admin)
- `DELETE /{id}` - Delete ticket (Admin)

### 7. Finance (`/api/v1/finance`)
- `GET /expenses` - List expenses (Admin)
- `POST /expenses` - Create expense (Admin)
- `GET /expenses/{id}` - Get expense (Admin)
- `PUT /expenses/{id}` - Update expense (Admin)
- `DELETE /expenses/{id}` - Delete expense (Admin)
- `GET /summary` - Get finance summary (Admin)
- `GET /stats` - Get finance statistics (Admin)

## Background Tasks

Celery tasks run automatically:

- **Check Expired Configs**: Every hour
- **Check Over-Limit Configs**: Every hour
- **Sync Usage from S-UI**: Every 6 hours

## S-UI Integration

The backend integrates with S-UI panels for:

- Creating configs/clients
- Deleting configs/clients
- Updating limits and expiry
- Syncing usage data
- Health checks

## Testing

Run tests with pytest:

```bash
pytest
```

## Production Deployment

1. Set `DEBUG=False` in `.env`
2. Use a strong `SECRET_KEY`
3. Configure proper CORS origins
4. Use a production database
5. Set up proper logging
6. Use a reverse proxy (nginx)
7. Enable HTTPS

## License

MIT

