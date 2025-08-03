#!/usr/bin/env python3
"""
تست اتصال ربات تلگرام
"""

import os
import sys
import django
import requests
import asyncio
from telegram import Bot
from telegram.error import NetworkError, InvalidToken

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings

def test_internet_connection():
    """تست اتصال اینترنت"""
    print("🌐 تست اتصال اینترنت...")
    
    try:
        # تست اتصال به Google
        response = requests.get("https://www.google.com", timeout=10)
        print("   ✅ اتصال به Google موفق")
        
        # تست اتصال به Telegram
        response = requests.get("https://api.telegram.org", timeout=10)
        print("   ✅ اتصال به Telegram API موفق")
        
        return True
    except Exception as e:
        print(f"   ❌ خطا در اتصال: {e}")
        return False

def test_bot_token():
    """تست TOKEN ربات"""
    print("\n🤖 تست TOKEN ربات...")
    
    token = getattr(settings, 'ADMIN_BOT_TOKEN', None)
    if not token or token == 'YOUR_ADMIN_BOT_TOKEN':
        print("   ❌ TOKEN تنظیم نشده")
        return False
    
    print(f"   📝 TOKEN: {token[:10]}...")
    
    try:
        # تست اتصال به ربات
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                bot_info = data.get('result', {})
                print(f"   ✅ ربات یافت شد: {bot_info.get('first_name', 'Unknown')}")
                print(f"   📱 نام کاربری: @{bot_info.get('username', 'Unknown')}")
                return True
            else:
                print(f"   ❌ خطا در پاسخ API: {data.get('description', 'Unknown error')}")
                return False
        else:
            print(f"   ❌ خطا در HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ خطا در تست TOKEN: {e}")
        return False

async def test_bot_async():
    """تست ربات به صورت async"""
    print("\n🔄 تست ربات (Async)...")
    
    token = getattr(settings, 'ADMIN_BOT_TOKEN', None)
    if not token or token == 'YOUR_ADMIN_BOT_TOKEN':
        print("   ❌ TOKEN تنظیم نشده")
        return False
    
    try:
        bot = Bot(token=token)
        
        # تست getMe
        me = await bot.get_me()
        print(f"   ✅ ربات فعال: {me.first_name} (@{me.username})")
        
        # تست اتصال
        await bot.get_updates()
        print("   ✅ اتصال موفق")
        
        return True
        
    except InvalidToken as e:
        print(f"   ❌ TOKEN نامعتبر: {e}")
        return False
    except NetworkError as e:
        print(f"   ❌ خطای شبکه: {e}")
        return False
    except Exception as e:
        print(f"   ❌ خطای نامشخص: {e}")
        return False

def test_admin_settings():
    """تست تنظیمات ادمین"""
    print("\n👤 تست تنظیمات ادمین...")
    
    password = getattr(settings, 'ADMIN_PASSWORD', 'admin123')
    user_ids = getattr(settings, 'ADMIN_USER_IDS', [])
    
    print(f"   🔑 رمز ادمین: {password}")
    print(f"   👥 تعداد ادمین‌ها: {len(user_ids)}")
    
    if user_ids:
        print(f"   📋 ID های ادمین: {user_ids}")
        return True
    else:
        print("   ❌ هیچ ادمینی تنظیم نشده")
        return False

def main():
    """تابع اصلی"""
    print("🚀 شروع تست اتصال ربات...")
    
    # تست 1: اتصال اینترنت
    internet_ok = test_internet_connection()
    
    # تست 2: TOKEN ربات
    token_ok = test_bot_token()
    
    # تست 3: ربات async
    bot_ok = asyncio.run(test_bot_async())
    
    # تست 4: تنظیمات ادمین
    admin_ok = test_admin_settings()
    
    # نتیجه کلی
    print("\n📊 نتیجه تست‌ها:")
    print(f"   🌐 اتصال اینترنت: {'✅' if internet_ok else '❌'}")
    print(f"   🤖 TOKEN ربات: {'✅' if token_ok else '❌'}")
    print(f"   🔄 ربات Async: {'✅' if bot_ok else '❌'}")
    print(f"   👤 تنظیمات ادمین: {'✅' if admin_ok else '❌'}")
    
    if all([internet_ok, token_ok, bot_ok, admin_ok]):
        print("\n🎉 تمام تست‌ها موفق بودند!")
        print("✅ ربات آماده اجرا است!")
        
        print("\n📋 راه‌اندازی:")
        print("1. python start_admin_bot.py")
        print("2. systemctl start admin-bot")
        
    else:
        print("\n❌ برخی تست‌ها ناموفق بودند!")
        
        if not internet_ok:
            print("🔧 مشکل: اتصال اینترنت")
            print("   راه‌حل: بررسی فایروال و DNS")
            
        if not token_ok:
            print("🔧 مشکل: TOKEN نامعتبر")
            print("   راه‌حل: دریافت TOKEN جدید از @BotFather")
            
        if not bot_ok:
            print("🔧 مشکل: اتصال ربات")
            print("   راه‌حل: بررسی تنظیمات شبکه")
            
        if not admin_ok:
            print("🔧 مشکل: تنظیمات ادمین")
            print("   راه‌حل: تنظیم ADMIN_USER_IDS")

if __name__ == "__main__":
    main() 