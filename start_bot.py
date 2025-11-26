#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
اسکریپت ساده برای استارت بات تلگرام
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

def check_tokens():
    """بررسی توکن‌ها"""
    print("=" * 60)
    print("[*] بررسی توکن‌ها...")
    print("=" * 60)
    
    admin_token = getattr(settings, 'ADMIN_BOT_TOKEN', None)
    user_token = getattr(settings, 'USER_BOT_TOKEN', None)
    
    if admin_token and admin_token != 'YOUR_ADMIN_BOT_TOKEN':
        print(f"[OK] توکن ربات ادمین: {admin_token[:20]}...")
    else:
        print("[ERROR] توکن ربات ادمین تنظیم نشده است!")
    
    if user_token and user_token != 'YOUR_BOT_TOKEN_HERE':
        print(f"[OK] توکن ربات کاربر: {user_token[:20]}...")
    else:
        print("[ERROR] توکن ربات کاربر تنظیم نشده است!")
    
    print()
    return admin_token, user_token

def start_user_bot():
    """استارت ربات کاربر"""
    print("=" * 60)
    print("[*] استارت ربات کاربر...")
    print("=" * 60)
    
    try:
        # بررسی توکن
        token = getattr(settings, 'USER_BOT_TOKEN', None)
        if not token or token == 'YOUR_BOT_TOKEN_HERE':
            print("[ERROR] توکن ربات کاربر تنظیم نشده است!")
            print("لطفا USER_BOT_TOKEN را در config.env تنظیم کنید.")
            return False
        
        # Import و اجرای ربات
        import asyncio
        import nest_asyncio
        
        # Fix for Windows and Python 3.14
        if sys.platform == 'win32':
            try:
                asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            except:
                pass  # Ignore deprecation warning
        
        # Apply nest_asyncio to allow nested event loops
        nest_asyncio.apply()
        
        print("[OK] ربات کاربر در حال اجرا...")
        print("[*] برای توقف Ctrl+C را فشار دهید")
        print()
        
        # Import after nest_asyncio is applied
        from bot.user_bot import main as user_bot_main
        
        # Use asyncio.run with nest_asyncio
        asyncio.run(user_bot_main())
        return True
        
    except KeyboardInterrupt:
        print("\n[*] ربات کاربر متوقف شد")
        return True
    except Exception as e:
        print(f"[ERROR] خطا در استارت ربات کاربر: {e}")
        import traceback
        traceback.print_exc()
        return False

def start_admin_bot():
    """استارت ربات ادمین"""
    print("=" * 60)
    print("[*] استارت ربات ادمین...")
    print("=" * 60)
    
    try:
        # بررسی توکن
        token = getattr(settings, 'ADMIN_BOT_TOKEN', None)
        if not token or token == 'YOUR_ADMIN_BOT_TOKEN':
            print("[ERROR] توکن ربات ادمین تنظیم نشده است!")
            print("لطفا ADMIN_BOT_TOKEN را در config.env تنظیم کنید.")
            return False
        
        # Import و اجرای ربات
        from bot.admin_bot import main as admin_bot_main
        
        print("[OK] ربات ادمین در حال اجرا...")
        print("[*] برای توقف Ctrl+C را فشار دهید")
        print()
        
        admin_bot_main()
        return True
        
    except KeyboardInterrupt:
        print("\n[*] ربات ادمین متوقف شد")
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
    parser.add_argument('--check', action='store_true', help='بررسی توکن‌ها')
    
    args = parser.parse_args()
    
    # بررسی توکن‌ها
    if args.check:
        check_tokens()
        return
    
    if args.user:
        check_tokens()
        start_user_bot()
    elif args.admin:
        check_tokens()
        start_admin_bot()
    else:
        print("=" * 60)
        print("🤖 استارت ربات‌های تلگرام")
        print("=" * 60)
        print("\nاستفاده:")
        print("  python start_bot.py --user    # استارت ربات کاربر")
        print("  python start_bot.py --admin   # استارت ربات ادمین")
        print("  python start_bot.py --check   # بررسی توکن‌ها")
        print()
        print("برای استارت هر دو ربات همزمان:")
        print("  - یک ترمینال: python start_bot.py --user")
        print("  - ترمینال دیگر: python start_bot.py --admin")
        print()

if __name__ == "__main__":
    main()

