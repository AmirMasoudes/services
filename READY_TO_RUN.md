# Ready to Run - Final Instructions

## Quick Start

Run this single command:

```powershell
powershell -ExecutionPolicy Bypass -File .\run.ps1
```

## What You'll Be Asked

The script will ask for only **3 values**:

1. **Enter server IP:** (e.g., `127.0.0.1` or your server IP)
2. **Enter panel username:** (e.g., `admin`)
3. **Enter panel password:** (your password)

Everything else is **automatically generated**.

## What Happens Automatically

1. ✅ Python version check (requires 3.10+)
2. ✅ Virtual environment creation (`.venv`)
3. ✅ Dependency installation (Django + FastAPI)
4. ✅ Configuration generation (`.env` file)
5. ✅ Django migrations
6. ✅ FastAPI database setup
7. ✅ Service startup (3 separate terminals)

## Services Started

After setup completes, you'll have:

- **Terminal 1:** Django server at http://localhost:8000
- **Terminal 2:** FastAPI server at http://localhost:8001
- **Terminal 3:** Telegram bots (user_bot.py and admin_bot.py)

## Logs

All logs are saved in `logs/` directory:

- `logs/django.log` - Django server output
- `logs/api.log` - FastAPI server output
- `logs/bots.log` - Bot services output
- `logs/error.log` - Error messages
- `logs/django_makemigrations.log` - Migration creation
- `logs/django_migrate.log` - Migration application
- `logs/alembic_upgrade.log` - FastAPI migrations

## Post-Setup Configuration

After the initial setup, you may want to:

1. **Configure Telegram Bots:**
   - Edit `.env` file
   - Set `ADMIN_BOT_TOKEN` and `USER_BOT_TOKEN`
   - Set `ADMIN_USER_IDS` to your Telegram user ID(s)
   - Restart bot services

2. **Optional: Configure PostgreSQL:**
   - Edit `.env` file
   - Set `DATABASE_URL` with your PostgreSQL connection string
   - Run migrations again

## Troubleshooting

### Python Not Found
- Install Python 3.10+ from https://www.python.org/
- Make sure to check "Add Python to PATH" during installation

### Port Already in Use
- Change `SERVER_PORT` (Django) or `PORT` (FastAPI) in `.env`
- Or stop the service using the port

### Migration Errors
- Check `logs/django_makemigrations.log` and `logs/django_migrate.log`
- Fix any model issues and run migrations again

### Import Errors
- Make sure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

## Files Generated

After running the script:

- `.venv/` - Virtual environment
- `.env` - Environment configuration (auto-generated)
- `logs/` - Log files directory
- `db.sqlite3` - Django database (if using SQLite)

## Verification

To verify everything is working:

1. **Check Django:** http://localhost:8000/admin
2. **Check FastAPI:** http://localhost:8001/api/docs
3. **Check Bots:** Send `/start` to your Telegram bots
4. **Check Logs:** Review files in `logs/` directory

## Support

If you encounter issues:

1. Check `logs/error.log` for error details
2. Review service terminal outputs
3. Verify all 3 input values were provided correctly
4. Ensure Python 3.10+ is installed and in PATH

## Success Criteria

The setup is successful when:

- ✅ All 3 services start without errors
- ✅ Django is accessible at http://localhost:8000
- ✅ FastAPI is accessible at http://localhost:8001/api/docs
- ✅ Bots respond to Telegram commands
- ✅ No errors in `logs/error.log`

## Next Steps

1. Configure Telegram bot tokens in `.env`
2. Set your Telegram user ID in `ADMIN_USER_IDS`
3. Create Django superuser (if prompted)
4. Start using the system!

---

**The project is now ready to run with a single command!**

