#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
اسکریپت اصلاح شده برای استارت بات تلگرام (Python 3.14 Compatible)
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

def start_user_bot():
    """استارت ربات کاربر - نسخه اصلاح شده برای Python 3.14"""
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
        
        # Import asyncio
        import asyncio
        
        # برای Python 3.14+ از روش مستقیم استفاده می‌کنیم
        # ایجاد event loop جدید
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        print("[OK] ربات کاربر در حال اجرا...")
        print("[*] برای توقف Ctrl+C را فشار دهید")
        print()
        
        try:
            # Import bot module
            from bot.user_bot import main as user_bot_main
            
            # اجرای main function
            loop.run_until_complete(user_bot_main())
        finally:
            # بستن event loop
            try:
                pending = asyncio.all_tasks(loop)
                if pending:
                    loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            except:
                pass
            finally:
                loop.close()
        
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
    
    args = parser.parse_args()
    
    if args.user:
        start_user_bot()
    elif args.admin:
        start_admin_bot()
    else:
        print("=" * 60)
        print("[*] استارت ربات‌های تلگرام")
        print("=" * 60)
        print("\nاستفاده:")
        print("  python start_bot_fixed.py --user    # استارت ربات کاربر")
        print("  python start_bot_fixed.py --admin   # استارت ربات ادمین")
        print()

if __name__ == "__main__":
    main()

