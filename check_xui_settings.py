#!/usr/bin/env python3
import os
import sys
import django
import requests
import json

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from xui_servers.models import XUIServer
from xui_servers import settings as xui_settings

def check_xui_settings():
    """بررسی تنظیمات X-UI"""
    print("🔧 بررسی تنظیمات X-UI...")
    
    # بررسی تنظیمات پورت
    print("\n📊 تنظیمات پورت:")
    print(f"  - حداقل پورت: {xui_settings.PORT_SETTINGS['min_port']}")
    print(f"  - حداکثر پورت: {xui_settings.PORT_SETTINGS['max_port']}")
    
    # بررسی تنظیمات پروتکل
    print("\n📊 تنظیمات پروتکل:")
    for protocol, config in xui_settings.PROTOCOL_SETTINGS.items():
        print(f"  - {protocol.upper()}: {config.get('name', 'بدون نام')}")
    
    # بررسی دامنه‌های فیک
    print(f"\n📊 دامنه‌های فیک ({len(xui_settings.FAKE_DOMAINS)} عدد):")
    for domain in xui_settings.FAKE_DOMAINS[:5]:  # فقط 5 تا اول
        print(f"  - {domain}")
    if len(xui_settings.FAKE_DOMAINS) > 5:
        print(f"  ... و {len(xui_settings.FAKE_DOMAINS) - 5} عدد دیگر")
    
    # بررسی کلیدهای عمومی
    print(f"\n📊 کلیدهای عمومی ({len(xui_settings.REALITY_PUBLIC_KEYS)} عدد):")
    for key in xui_settings.REALITY_PUBLIC_KEYS[:3]:  # فقط 3 تا اول
        print(f"  - {key[:20]}...")
    if len(xui_settings.REALITY_PUBLIC_KEYS) > 3:
        print(f"  ... و {len(xui_settings.REALITY_PUBLIC_KEYS) - 3} عدد دیگر")
    
    # بررسی تنظیمات inbound
    print("\n📊 تنظیمات inbound:")
    print(f"  - نام پیشوند: {xui_settings.INBOUND_NAMING['prefix']}")
    print(f"  - تنظیمات پایه: {list(xui_settings.INBOUND_SETTINGS.keys())}")
    
    # بررسی تنظیمات کاربر
    print("\n📊 تنظیمات کاربر:")
    print(f"  - تنظیمات پیش‌فرض: {list(xui_settings.USER_DEFAULT_SETTINGS.keys())}")
    print(f"  - فرمت ایمیل تستی: {xui_settings.EMAIL_SETTINGS['trial_format']}")
    print(f"  - فرمت ایمیل پولی: {xui_settings.EMAIL_SETTINGS['paid_format']}")
    
    # بررسی تنظیمات کانفیگ
    print("\n📊 تنظیمات کانفیگ:")
    print(f"  - فرمت نام تستی: {xui_settings.CONFIG_NAMING['trial_format']}")
    print(f"  - فرمت نام پولی: {xui_settings.CONFIG_NAMING['paid_format']}")
    
    # بررسی تنظیمات انقضا
    print("\n📊 تنظیمات انقضا:")
    print(f"  - ساعت تستی: {xui_settings.EXPIRY_SETTINGS['trial_hours']}")
    print(f"  - روز پولی: {xui_settings.EXPIRY_SETTINGS['paid_days']}")
    
    # بررسی تنظیمات ترافیک
    print("\n📊 تنظیمات ترافیک:")
    print(f"  - تبدیل MB به GB: {xui_settings.TRAFFIC_SETTINGS['mb_to_gb_conversion']}")
    
    print("\n✅ بررسی تنظیمات X-UI کامل شد!")

def test_xui_connection():
    """تست اتصال به X-UI"""
    print("\n🔧 تست اتصال به X-UI...")
    
    # دریافت سرور X-UI
    server = XUIServer.objects.filter(is_active=True).first()
    if not server:
        print("❌ سرور X-UI فعالی یافت نشد")
        return
    
    print(f"🖥️ سرور: {server.name}")
    print(f" آدرس: {server.host}:{server.port}")
    print(f"👤 نام کاربری: {server.username}")
    
    # تست اتصال
    try:
        response = requests.get(f"http://{server.host}:{server.port}", timeout=5)
        print(f"✅ اتصال به سرور موفق (کد: {response.status_code})")
    except Exception as e:
        print(f"❌ خطا در اتصال به سرور: {e}")
        return
    
    # تست ورود
    try:
        login_data = {
            "username": server.username,
            "password": server.password
        }
        
        response = requests.post(
            f"http://{server.host}:{server.port}/login",
            json=login_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ ورود به X-UI موفق")
            else:
                print(f"❌ خطا در ورود: {data.get('msg', 'خطای نامشخص')}")
        else:
            print(f"❌ خطا در اتصال: {response.status_code}")
            
    except Exception as e:
        print(f"❌ خطا در ورود: {e}")

if __name__ == "__main__":
    check_xui_settings()
    test_xui_connection() 