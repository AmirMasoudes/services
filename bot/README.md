# Telegram Bots Documentation

## Overview

This project includes two Telegram bots:
1. **Admin Bot** - For system administrators
2. **User Bot** - For end users

---

## Admin Bot

### Purpose
- Manage servers (X-UI/S-UI)
- Manage plans and pricing
- Manage users and subscriptions
- Process payments
- Monitor system health

### Setup

1. **Get Bot Token**
   ```bash
   # Contact @BotFather on Telegram
   # Create new bot or use existing
   # Copy the token
   ```

2. **Configure Environment**
   ```env
   ADMIN_BOT_TOKEN=your_admin_bot_token
   ADMIN_USER_IDS=123456789,987654321
   ADMIN_PASSWORD=secure_password
   ```

3. **Run Bot**
   ```bash
   python bot/admin_bot.py
   ```

### Commands

- `/start` - Start bot, show main menu
- `/dashboard` - View system statistics
- `/servers` - List all servers
- `/add_server` - Add new server
- `/plans` - List all plans
- `/add_plan` - Add new plan
- `/users` - List all users
- `/payments` - View pending payments
- `/sync_xui` - Sync with X-UI/S-UI
- `/cleanup` - Clean up expired configs

### Permissions

Only users with:
- Telegram ID in `ADMIN_USER_IDS`
- OR `is_admin=True` in database
- OR `is_staff=True` in database

Can use admin bot commands.

---

## User Bot

### Purpose
- View available plans
- Purchase subscriptions
- Get subscription links
- View usage statistics
- Renew/upgrade subscriptions

### Setup

1. **Get Bot Token**
   ```bash
   # Contact @BotFather on Telegram
   # Create new bot or use existing
   # Copy the token
   ```

2. **Configure Environment**
   ```env
   USER_BOT_TOKEN=your_user_bot_token
   ```

3. **Run Bot**
   ```bash
   python bot/user_bot.py
   ```

### Commands

- `/start` - Start bot, register user
- `/help` - Show help message
- Menu buttons:
  - 🎁 پلن تستی - Get trial plan
  - 🛒 خرید پلن - Purchase plan
  - 📦 پلن‌های من - My subscriptions
  - ℹ️ اطلاعات من - My information
  - 💬 ارتباط با ما - Contact us
  - 🆘 پشتیبانی - Support

### Features

- **Trial Plan:** Free 24-hour trial (one-time)
- **Paid Plans:** Purchase with payment receipt
- **Subscription Links:** Get shareable subscription URLs
- **Usage Tracking:** View data usage
- **Renewal:** Renew expired subscriptions
- **Upgrade:** Upgrade to better plans

---

## Bot Architecture

### Current Structure
```
bot/
├── admin_bot.py      # Admin bot (2260 lines - needs modularization)
├── user_bot.py       # User bot (2616 lines - needs modularization)
└── README.md         # This file
```

### Target Structure (Future)
```
bot/
├── admin/
│   ├── __init__.py
│   ├── commands.py   # Command handlers
│   ├── handlers.py   # Message/callback handlers
│   ├── keyboards.py  # Inline keyboards
│   ├── services.py   # Business logic
│   └── permissions.py # Permission checks
├── user/
│   ├── __init__.py
│   ├── commands.py
│   ├── handlers.py
│   ├── keyboards.py
│   ├── services.py
│   └── subscriptions.py
├── shared/
│   ├── __init__.py
│   ├── utils.py      # Shared utilities
│   ├── errors.py     # Error handling
│   └── logging.py    # Logging setup
└── README.md
```

---

## Environment Variables

### Required
```env
# Admin Bot
ADMIN_BOT_TOKEN=your_admin_bot_token
ADMIN_USER_IDS=123456789,987654321

# User Bot
USER_BOT_TOKEN=your_user_bot_token

# Django
SECRET_KEY=your_secret_key
DATABASE_URL=postgresql://user:pass@localhost/dbname

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Optional
```env
ADMIN_PASSWORD=secure_password
DEBUG=False
ALLOWED_HOSTS=your-domain.com
```

---

## Running Bots

### Development

```bash
# Terminal 1: Django
python manage.py runserver

# Terminal 2: Celery Worker
celery -A config worker -l info

# Terminal 3: Celery Beat
celery -A config beat -l info

# Terminal 4: Admin Bot
python bot/admin_bot.py

# Terminal 5: User Bot
python bot/user_bot.py
```

### Production

Use systemd services (see `services/` directory):

```bash
# Install services
sudo ./services/install-services.sh

# Start services
sudo systemctl start admin-bot
sudo systemctl start user-bot
sudo systemctl start celery-worker
sudo systemctl start celery-beat

# Enable on boot
sudo systemctl enable admin-bot
sudo systemctl enable user-bot
sudo systemctl enable celery-worker
sudo systemctl enable celery-beat
```

---

## Troubleshooting

### Bot Not Responding

1. Check bot token is correct
2. Check bot is running
3. Check logs for errors
4. Verify database connection
5. Check Celery is running (for provisioning)

### Commands Not Working

1. Verify user has permissions (admin bot)
2. Check command handlers are registered
3. Review logs for errors
4. Check database for user record

### Provisioning Fails

1. Check S-UI/X-UI connection
2. Verify API credentials
3. Check Celery worker logs
4. Review task queue status
5. Check database for errors

---

## Testing

### Manual Testing

1. Start all services
2. Send `/start` to admin bot
3. Verify menu appears
4. Test each command
5. Check database for changes

### Automated Testing

```bash
# Run bot tests (when created)
pytest tests/test_bots.py -v
```

---

## Security

### Bot Tokens
- Never commit tokens to repository
- Use environment variables
- Rotate tokens regularly
- Use different tokens for dev/prod

### Permissions
- Verify admin permissions on each command
- Don't trust user input
- Validate all data
- Log all admin actions

### Rate Limiting
- Implement rate limiting (pending)
- Prevent abuse
- Monitor for suspicious activity

---

## Monitoring

### Logs
- Bot logs: `logs/bot.log`
- Error logs: `logs/error.log`
- Celery logs: `logs/celery.log`

### Metrics
- Commands per minute
- Active users
- Provisioning success rate
- Error rate

---

## Future Improvements

1. **Modularization** - Split into separate modules
2. **State Machine** - Proper FSM for multi-step flows
3. **Error Handling** - Comprehensive error handling
4. **Rate Limiting** - Prevent abuse
5. **Analytics** - User behavior tracking
6. **Notifications** - Event-based notifications
7. **Internationalization** - Multi-language support

---

## Support

For issues:
- Check logs first
- Review `AUDIT_REPORT.md` for known issues
- See `IMPLEMENTATION_GUIDE.md` for setup
- Contact development team

