#!/usr/bin/env python3
"""
رفع مشکلات API XUI
"""

import os
import sys
import django
import requests
import json
import subprocess

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from xui_servers.models import XUIServer

def check_xui_server():
    """بررسی سرور XUI"""
    print("🔍 بررسی سرور XUI...")
    
    try:
        server = XUIServer.objects.filter(is_active=True).first()
        if not server:
            print("❌ هیچ سرور فعالی یافت نشد")
            return None
        
        print(f"🌐 سرور: {server.name}")
        print(f"🔗 آدرس: {server.host}:{server.port}")
        print(f"👤 نام کاربری: {server.username}")
        print(f"🔑 رمز عبور: {server.password}")
        print(f"🌐 مسیر وب: {server.web_base_path}")
        
        return server
        
    except Exception as e:
        print(f"❌ خطا در بررسی سرور: {e}")
        return None

def test_xui_connection(server):
    """تست اتصال XUI"""
    print(f"\n🌐 تست اتصال به {server.host}:{server.port}...")
    
    try:
        # تست اتصال شبکه
        result = subprocess.run(
            f"ping -c 3 {server.host}",
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✅ اتصال شبکه برقرار است")
        else:
            print("❌ اتصال شبکه برقرار نیست")
            return False
        
        # تست اتصال HTTP
        base_url = f"http://{server.host}:{server.port}"
        if server.web_base_path:
            base_url += server.web_base_path
        
        print(f"🌐 تست اتصال HTTP به {base_url}...")
        
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"📡 وضعیت HTTP: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ اتصال HTTP موفق")
            return True
        else:
            print(f"❌ خطا در اتصال HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ خطا در تست اتصال: {e}")
        return False

def test_xui_api(server):
    """تست API XUI با استفاده از XUIService"""
    print(f"\n🧪 تست API XUI با XUIService...")
    
    try:
        from xui_servers.services import XUIService
        
        # ایجاد سرویس XUI
        xui_service = XUIService(server)
        
        # تست لاگین
        print("🔐 تست لاگین...")
        if not xui_service.login():
            print("❌ لاگین ناموفق")
            return False
        
        print("✅ لاگین موفق!")
        
        # تست دریافت inbound ها
        print("📋 تست دریافت inbound ها...")
        inbounds = xui_service.get_inbounds()
        
        if inbounds and len(inbounds) > 0:
            print(f"✅ دریافت {len(inbounds)} inbound")
            for i, inbound in enumerate(inbounds[:3]):  # نمایش 3 inbound اول
                print(f"  - Inbound {i+1}: {inbound.get('remark', 'Unknown')} (پورت: {inbound.get('port', 'نامشخص')})")
            return True
        else:
            print("❌ هیچ inbound یافت نشد")
            return False
            
    except Exception as e:
        print(f"❌ خطا در تست API: {e}")
        return False

def fix_xui_settings():
    """رفع تنظیمات XUI"""
    print(f"\n🔧 رفع تنظیمات XUI...")
    
    try:
        # بررسی فایل تنظیمات
        settings_file = "xui_servers/settings.py"
        if os.path.exists(settings_file):
            print(f"📄 فایل تنظیمات موجود: {settings_file}")
            
            # خواندن محتوای فایل
            with open(settings_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # بررسی تنظیمات اتصال
            if 'XUI_CONNECTION_SETTINGS' in content:
                print("✅ تنظیمات اتصال موجود")
            else:
                print("⚠️ تنظیمات اتصال یافت نشد")
                
            if 'PORT_SETTINGS' in content:
                print("✅ تنظیمات پورت موجود")
            else:
                print("⚠️ تنظیمات پورت یافت نشد")
                
        else:
            print(f"❌ فایل تنظیمات یافت نشد: {settings_file}")
            
    except Exception as e:
        print(f"❌ خطا در بررسی تنظیمات: {e}")

def restart_services():
    """راه‌اندازی مجدد سرویس‌ها"""
    print(f"\n🔄 راه‌اندازی مجدد سرویس‌ها...")
    
    try:
        # راه‌اندازی مجدد user-bot
        result = subprocess.run(
            "systemctl restart user-bot",
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ user-bot راه‌اندازی مجدد شد")
        else:
            print(f"❌ خطا در راه‌اندازی مجدد user-bot: {result.stderr}")
        
        # بررسی وضعیت
        result = subprocess.run(
            "systemctl status user-bot",
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("📊 وضعیت user-bot:")
            print(result.stdout)
        else:
            print(f"❌ خطا در بررسی وضعیت: {result.stderr}")
            
    except Exception as e:
        print(f"❌ خطا در راه‌اندازی مجدد: {e}")

def main():
    """تابع اصلی"""
    print("🎉 رفع مشکلات API XUI")
    print("=" * 50)
    
    # بررسی سرور
    server = check_xui_server()
    if not server:
        print("❌ سرور یافت نشد")
        return
    
    # تست اتصال
    connection_ok = test_xui_connection(server)
    if not connection_ok:
        print("❌ اتصال ناموفق")
        return
    
    # تست API
    api_ok = test_xui_api(server)
    if not api_ok:
        print("❌ API ناموفق")
        print("🔧 تلاش برای رفع مشکلات...")
        
        # رفع تنظیمات
        fix_xui_settings()
        
        # راه‌اندازی مجدد سرویس‌ها
        restart_services()
    else:
        print("✅ API موفق")
        
        # راه‌اندازی مجدد سرویس‌ها
        restart_services()
    
    print("\n🎉 عملیات کامل شد!")

if __name__ == "__main__":
    main() 