#!/usr/bin/env python3
"""
اسکریپت راه‌اندازی ربات ادمین
"""

import os
import sys
import django
import logging
from datetime import datetime

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from bot.admin_bot import AdminBot

# تنظیم لاگینگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """تابع اصلی"""
    print("🚀 راه‌اندازی ربات ادمین X-UI...")
    
    try:
        # بررسی تنظیمات
        from django.conf import settings
        
        if not hasattr(settings, 'ADMIN_BOT_TOKEN') or settings.ADMIN_BOT_TOKEN == 'YOUR_ADMIN_BOT_TOKEN':
            print("❌ لطفاً ADMIN_BOT_TOKEN را در تنظیمات تنظیم کنید!")
            return
        
        if not hasattr(settings, 'ADMIN_USER_IDS') or not settings.ADMIN_USER_IDS:
            print("❌ لطفاً ADMIN_USER_IDS را در تنظیمات تنظیم کنید!")
            return
        
        print(f"✅ تنظیمات ربات ادمین بررسی شد")
        print(f"🔑 رمز ادمین: {getattr(settings, 'ADMIN_PASSWORD', 'admin123')}")
        print(f"👥 تعداد ادمین‌ها: {len(settings.ADMIN_USER_IDS)}")
        
        # راه‌اندازی ربات
        bot = AdminBot()
        print("✅ ربات ادمین آماده اجرا است!")
        print("📱 برای استفاده:")
        print("   1. ربات را در تلگرام پیدا کنید")
        print("   2. دستور /start را ارسال کنید")
        print("   3. با رمز ادمین وارد شوید")
        print("   4. از دستورات مدیریت استفاده کنید")
        
        bot.run()
        
    except KeyboardInterrupt:
        print("\n🛑 ربات ادمین متوقف شد")
    except Exception as e:
        print(f"❌ خطا در راه‌اندازی ربات ادمین: {e}")
        logger.error(f"خطا در راه‌اندازی ربات ادمین: {e}")

if __name__ == "__main__":
    main() 