"""
Celery Beat schedule configuration
"""
from celery.schedules import crontab

# Celery Beat schedule
beat_schedule = {
    # Check expired configs every hour
    "check-expired-configs": {
        "task": "app.tasks.config_expiry.check_expired_configs",
        "schedule": crontab(minute=0),  # Every hour at minute 0
    },
    # Check over-limit configs every hour
    "check-over-limit-configs": {
        "task": "app.tasks.config_expiry.check_over_limit_configs",
        "schedule": crontab(minute=30),  # Every hour at minute 30
    },
    # Sync usage from S-UI panels every 6 hours
    "sync-usage-from-sui": {
        "task": "app.tasks.usage_sync.sync_usage_from_sui",
        "schedule": crontab(hour="*/6", minute=0),  # Every 6 hours
    },
}

