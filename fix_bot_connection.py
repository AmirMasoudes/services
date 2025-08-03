#!/usr/bin/env python3
"""
رفع مشکل اتصال ربات تلگرام
"""

import os
import sys
import django
import requests
import asyncio
import time
from datetime import datetime

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings

def test_basic_connection():
    """تست اتصال پایه"""
    print("🔍 تست اتصال پایه...")
    
    try:
        # تست DNS
        import socket
        socket.gethostbyname("api.telegram.org")
        print("   ✅ DNS کار می‌کند")
        
        # تست اتصال HTTP
        response = requests.get("http://api.telegram.org", timeout=5)
        print(f"   ✅ HTTP اتصال: {response.status_code}")
        
        # تست اتصال HTTPS
        response = requests.get("https://api.telegram.org", timeout=5)
        print(f"   ✅ HTTPS اتصال: {response.status_code}")
        
        return True
    except Exception as e:
        print(f"   ❌ خطا در اتصال پایه: {e}")
        return False

def test_proxy_settings():
    """تست تنظیمات پروکسی"""
    print("\n🌐 تست تنظیمات پروکسی...")
    
    # بررسی متغیرهای محیطی پروکسی
    proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']
    for var in proxy_vars:
        value = os.environ.get(var)
        if value:
            print(f"   ⚠️ {var}: {value}")
    
    # تست بدون پروکسی
    try:
        session = requests.Session()
        session.trust_env = False  # نادیده گرفتن تنظیمات پروکسی
        
        response = session.get("https://api.telegram.org", timeout=10)
        print(f"   ✅ اتصال بدون پروکسی: {response.status_code}")
        return True
    except Exception as e:
        print(f"   ❌ خطا در اتصال بدون پروکسی: {e}")
        return False

def test_bot_token_simple():
    """تست ساده TOKEN ربات"""
    print("\n🤖 تست ساده TOKEN ربات...")
    
    token = getattr(settings, 'ADMIN_BOT_TOKEN', None)
    if not token or token == 'YOUR_ADMIN_BOT_TOKEN':
        print("   ❌ TOKEN تنظیم نشده")
        return False
    
    try:
        # تست با requests ساده
        url = f"https://api.telegram.org/bot{token}/getMe"
        
        session = requests.Session()
        session.trust_env = False
        
        response = session.get(url, timeout=10)
        print(f"   📊 پاسخ HTTP: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                bot_info = data.get('result', {})
                print(f"   ✅ ربات فعال: {bot_info.get('first_name')} (@{bot_info.get('username')})")
                return True
            else:
                print(f"   ❌ خطا در API: {data.get('description')}")
                return False
        else:
            print(f"   ❌ خطای HTTP: {response.status_code}")
            print(f"   📄 پاسخ: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"   ❌ خطا در تست TOKEN: {e}")
        return False

def create_simple_bot():
    """ایجاد ربات ساده بدون async"""
    print("\n🔧 ایجاد ربات ساده...")
    
    token = getattr(settings, 'ADMIN_BOT_TOKEN', None)
    if not token or token == 'YOUR_ADMIN_BOT_TOKEN':
        print("   ❌ TOKEN تنظیم نشده")
        return False
    
    try:
        from telegram import Bot
        from telegram.error import NetworkError, InvalidToken
        
        # تنظیم timeout طولانی‌تر
        bot = Bot(token=token, request=telegram.request.HTTPXRequest(
            connection_pool_size=1,
            connect_timeout=30.0,
            read_timeout=30.0,
            write_timeout=30.0,
            pool_timeout=30.0
        ))
        
        print("   ✅ ربات ایجاد شد")
        return True
        
    except Exception as e:
        print(f"   ❌ خطا در ایجاد ربات: {e}")
        return False

def test_alternative_methods():
    """تست روش‌های جایگزین"""
    print("\n🔄 تست روش‌های جایگزین...")
    
    token = getattr(settings, 'ADMIN_BOT_TOKEN', None)
    if not token or token == 'YOUR_ADMIN_BOT_TOKEN':
        print("   ❌ TOKEN تنظیم نشده")
        return False
    
    # روش 1: استفاده از urllib
    try:
        import urllib.request
        import urllib.parse
        import json
        
        url = f"https://api.telegram.org/bot{token}/getMe"
        
        # تنظیم User-Agent
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            if data.get('ok'):
                bot_info = data.get('result', {})
                print(f"   ✅ روش urllib: {bot_info.get('first_name')}")
                return True
            else:
                print(f"   ❌ خطا در urllib: {data.get('description')}")
                
    except Exception as e:
        print(f"   ❌ خطا در urllib: {e}")
    
    # روش 2: استفاده از curl
    try:
        import subprocess
        
        cmd = f"curl -s -m 10 'https://api.telegram.org/bot{token}/getMe'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            import json
            data = json.loads(result.stdout)
            if data.get('ok'):
                bot_info = data.get('result', {})
                print(f"   ✅ روش curl: {bot_info.get('first_name')}")
                return True
            else:
                print(f"   ❌ خطا در curl: {data.get('description')}")
        else:
            print(f"   ❌ خطا در curl: {result.stderr}")
            
    except Exception as e:
        print(f"   ❌ خطا در curl: {e}")
    
    return False

def create_fixed_bot():
    """ایجاد ربات با تنظیمات اصلاح شده"""
    print("\n🔧 ایجاد ربات اصلاح شده...")
    
    token = getattr(settings, 'ADMIN_BOT_TOKEN', None)
    if not token or token == 'YOUR_ADMIN_BOT_TOKEN':
        print("   ❌ TOKEN تنظیم نشده")
        return False
    
    try:
        from telegram import Bot
        from telegram.request import HTTPXRequest
        
        # تنظیمات اصلاح شده
        request = HTTPXRequest(
            connection_pool_size=1,
            connect_timeout=60.0,
            read_timeout=60.0,
            write_timeout=60.0,
            pool_timeout=60.0
        )
        
        bot = Bot(token=token, request=request)
        
        # تست اتصال
        me = asyncio.run(bot.get_me())
        print(f"   ✅ ربات اصلاح شده: {me.first_name} (@{me.username})")
        return True
        
    except Exception as e:
        print(f"   ❌ خطا در ربات اصلاح شده: {e}")
        return False

def main():
    """تابع اصلی"""
    print("🚀 شروع رفع مشکل اتصال ربات...")
    print(f"⏰ زمان: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # تست 1: اتصال پایه
    basic_ok = test_basic_connection()
    
    # تست 2: تنظیمات پروکسی
    proxy_ok = test_proxy_settings()
    
    # تست 3: TOKEN ساده
    token_ok = test_bot_token_simple()
    
    # تست 4: ربات ساده
    bot_ok = create_simple_bot()
    
    # تست 5: روش‌های جایگزین
    alt_ok = test_alternative_methods()
    
    # تست 6: ربات اصلاح شده
    fixed_ok = create_fixed_bot()
    
    # نتیجه کلی
    print("\n📊 نتیجه تست‌ها:")
    print(f"   🔍 اتصال پایه: {'✅' if basic_ok else '❌'}")
    print(f"   🌐 تنظیمات پروکسی: {'✅' if proxy_ok else '❌'}")
    print(f"   🤖 TOKEN ساده: {'✅' if token_ok else '❌'}")
    print(f"   🔧 ربات ساده: {'✅' if bot_ok else '❌'}")
    print(f"   🔄 روش‌های جایگزین: {'✅' if alt_ok else '❌'}")
    print(f"   🔧 ربات اصلاح شده: {'✅' if fixed_ok else '❌'}")
    
    if any([basic_ok, token_ok, alt_ok, fixed_ok]):
        print("\n🎉 حداقل یک روش کار می‌کند!")
        
        if fixed_ok:
            print("✅ ربات اصلاح شده آماده است!")
            print("\n📋 راه‌اندازی:")
            print("python start_admin_bot_fixed.py")
        elif alt_ok:
            print("✅ روش جایگزین کار می‌کند!")
        elif token_ok:
            print("✅ TOKEN معتبر است!")
            
    else:
        print("\n❌ هیچ روشی کار نمی‌کند!")
        print("🔧 مشکلات احتمالی:")
        print("   1. مشکل فایروال")
        print("   2. مشکل DNS")
        print("   3. مشکل پروکسی")
        print("   4. TOKEN نامعتبر")
        print("   5. مشکل شبکه")

if __name__ == "__main__":
    main() 