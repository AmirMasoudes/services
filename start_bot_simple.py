#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
اسکریپت ساده برای استارت بات‌ها
"""

import os
import sys
import django

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings

def start_user_bot():
    """استارت ربات کاربر"""
    print("[*] در حال استارت ربات کاربر...")
    try:
        from bot import user_bot
        import asyncio
        
        # Fix for Windows
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
        # بررسی توکن
        token = getattr(settings, 'USER_BOT_TOKEN', None)
        if not token or token == 'YOUR_BOT_TOKEN_HERE':
            print("[ERROR] توکن ربات کاربر تنظیم نشده است!")
            print("لطفا USER_BOT_TOKEN را در config.env تنظیم کنید.")
            return False
        
        print(f"[OK] توکن ربات کاربر پیدا شد")
        print("[*] در حال اجرای ربات کاربر...")
        asyncio.run(user_bot.main())
        return True
    except Exception as e:
        print(f"[ERROR] خطا در استارت ربات کاربر: {e}")
        import traceback
        traceback.print_exc()
        return False

def start_admin_bot():
    """استارت ربات ادمین"""
    print("[*] در حال استارت ربات ادمین...")
    try:
        from bot.admin_bot import AdminBot
        
        # بررسی توکن
        token = getattr(settings, 'ADMIN_BOT_TOKEN', None)
        if not token or token == 'YOUR_ADMIN_BOT_TOKEN':
            print("[ERROR] توکن ربات ادمین تنظیم نشده است!")
            print("لطفا ADMIN_BOT_TOKEN را در config.env تنظیم کنید.")
            return False
        
        print(f"[OK] توکن ربات ادمین پیدا شد")
        print("[*] در حال اجرای ربات ادمین...")
        
        bot = AdminBot()
        bot.run()
        return True
    except Exception as e:
        print(f"[ERROR] خطا در استارت ربات ادمین: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """تابع اصلی"""
    import argparse
    
    parser = argparse.ArgumentParser(description='استارت ربات‌های تلگرام')
    parser.add_argument('--user', action='store_true', help='استارت ربات کاربر')
    parser.add_argument('--admin', action='store_true', help='استارت ربات ادمین')
    parser.add_argument('--both', action='store_true', help='استارت هر دو ربات')
    
    args = parser.parse_args()
    
    if not (args.user or args.admin or args.both):
        print("=" * 60)
        print("🤖 استارت ربات‌های تلگرام")
        print("=" * 60)
        print("\nاستفاده:")
        print("  python start_bot_simple.py --user    # فقط ربات کاربر")
        print("  python start_bot_simple.py --admin   # فقط ربات ادمین")
        print("  python start_bot_simple.py --both    # هر دو ربات")
        print()
        return
    
    if args.both:
        print("=" * 60)
        print("[*] در حال استارت هر دو ربات...")
        print("=" * 60)
        print("\n⚠️  توجه: برای اجرای همزمان هر دو ربات،")
        print("   از start_bots.py استفاده کنید یا هر کدام را در ترمینال جداگانه اجرا کنید.")
        print()
        return
    
    if args.user:
        start_user_bot()
    elif args.admin:
        start_admin_bot()

if __name__ == "__main__":
    main()

