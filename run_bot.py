#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
اسکریپت ساده و کارآمد برای استارت بات (Python 3.14 Compatible)
"""

import os
import sys

# تنظیم encoding برای Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# اضافه کردن مسیر پروژه
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.conf import settings
import asyncio

def run_user_bot():
    """اجرای ربات کاربر"""
    print("=" * 60)
    print("[*] استارت ربات کاربر...")
    print("=" * 60)
    
    # بررسی توکن
    token = getattr(settings, 'USER_BOT_TOKEN', None)
    if not token or token == 'YOUR_BOT_TOKEN_HERE':
        print("[ERROR] توکن ربات کاربر تنظیم نشده است!")
        return False
    
    print(f"[OK] توکن پیدا شد: {token[:20]}...")
    print("[*] ربات در حال اجرا است...")
    print("[*] برای توقف Ctrl+C را فشار دهید\n")
    
    try:
        # Import و اجرای ربات
        from bot.user_bot import main
        
        # استفاده از asyncio.run که خودش event loop را مدیریت می‌کند
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[*] ربات متوقف شد")
    except Exception as e:
        print(f"\n[ERROR] خطا: {e}")
        import traceback
        traceback.print_exc()
    
    return True

def run_admin_bot():
    """اجرای ربات ادمین"""
    print("=" * 60)
    print("[*] استارت ربات ادمین...")
    print("=" * 60)
    
    # بررسی توکن
    token = getattr(settings, 'ADMIN_BOT_TOKEN', None)
    if not token or token == 'YOUR_ADMIN_BOT_TOKEN':
        print("[ERROR] توکن ربات ادمین تنظیم نشده است!")
        return False
    
    print(f"[OK] توکن پیدا شد: {token[:20]}...")
    print("[*] ربات در حال اجرا است...")
    print("[*] برای توقف Ctrl+C را فشار دهید\n")
    
    try:
        from bot.admin_bot import main
        main()
    except KeyboardInterrupt:
        print("\n[*] ربات متوقف شد")
    except Exception as e:
        print(f"\n[ERROR] خطا: {e}")
        import traceback
        traceback.print_exc()
    
    return True

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='استارت ربات تلگرام')
    parser.add_argument('--user', action='store_true', help='ربات کاربر')
    parser.add_argument('--admin', action='store_true', help='ربات ادمین')
    
    args = parser.parse_args()
    
    if args.user:
        run_user_bot()
    elif args.admin:
        run_admin_bot()
    else:
        print("=" * 60)
        print("[*] استارت ربات تلگرام")
        print("=" * 60)
        print("\nاستفاده:")
        print("  python run_bot.py --user    # ربات کاربر")
        print("  python run_bot.py --admin   # ربات ادمین")
        print()

