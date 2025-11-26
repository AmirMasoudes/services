from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.utils import timezone

from accounts.models import UsersModel
from .models import UserConfig, XUIServer
from .enhanced_api_models import XUIAutoManager


@shared_task
def send_expiry_warnings() -> int:
    """
    ارسال پیام هشدار انقضای کانفیگ برای کاربرها در تلگرام.

    از تنظیمات زیر استفاده می‌شود:
      - EXPIRY_WARNING_HOURS
      - EXPIRY_WARNING_MESSAGE
      - USER_BOT_TOKEN
    """
    from telegram import Bot

    hours = getattr(settings, "EXPIRY_WARNING_HOURS", 6)
    message_template = getattr(
        settings,
        "EXPIRY_WARNING_MESSAGE",
        "کانفیگ شما تا {hours} ساعت دیگر منقضی می‌شود ⏰",
    )

    now = timezone.now()
    window_end = now + timedelta(hours=hours)

    # پیدا کردن کانفیگ‌هایی که فعال‌اند و تا N ساعت آینده منقضی می‌شوند
    configs = (
        UserConfig.objects.filter(
            is_active=True,
            expires_at__gt=now,
            expires_at__lte=window_end,
        )
        .select_related("user")
        .all()
    )

    token = getattr(settings, "USER_BOT_TOKEN", None)
    if not token:
        return 0

    bot = Bot(token=token)
    sent = 0

    for config in configs:
        user: UsersModel = config.user
        chat_id = getattr(user, "telegram_id", None)
        if not chat_id:
            continue

        remaining_seconds = max(
            0, int((config.expires_at - now).total_seconds())
        )
        remaining_hours = max(1, remaining_seconds // 3600)

        text = message_template.format(hours=remaining_hours)

        try:
            bot.send_message(chat_id=chat_id, text=text)
            sent += 1
        except Exception:
            # در صورت خطا برای یک کاربر، بقیه را ادامه می‌دهیم
            continue

    return sent


@shared_task
def cleanup_expired_and_overused() -> dict:
    """
    پاکسازی خودکار کاربران/کانفیگ‌هایی که:
      - زمان انقضای آن‌ها گذشته است
      - یا حجم/ترافیک‌شان تمام شده است

    این تسک روی تمام سرورهای X-UI فعال اجرا می‌شود و از
    XUIAutoManager برای ارتباط با پنل و حذف از X-UI استفاده می‌کند.
    """
    total_results = {
        "expired_users": 0,
        "traffic_exceeded": 0,
        "total_cleaned": 0,
    }

    for server in XUIServer.objects.filter(is_active=True):
        manager = XUIAutoManager(server)
        res = manager.run_cleanup()

        total_results["expired_users"] += res.get("expired_users", 0)
        total_results["traffic_exceeded"] += res.get("traffic_exceeded", 0)
        total_results["total_cleaned"] += res.get("total_cleaned", 0)

    return total_results

