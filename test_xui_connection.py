#!/usr/bin/env python3
"""
اسکریپت تست اتصال به X-UI
"""

import os
import sys
import django

# اضافه کردن مسیر پروژه
sys.path.append('/opt/configvpn')

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from xui_servers.models import XUIServer
from xui_servers.services import XUIService

def test_xui_connection():
    """تست اتصال به X-UI"""
    print("🔍 تست اتصال به X-UI...")
    
    # ایجاد سرور X-UI با تنظیمات فعلی
    server, created = XUIServer.objects.get_or_create(
        host="38.54.105.124",
        defaults={
            "name": "سرور اصلی",
            "port": 54321,
            "username": "admin",
            "password": "YourSecurePassword123!@#",
            "web_base_path": "/MsxZ4xuIy5xLfQtsSC/",
            "is_active": True
        }
    )
    
    if created:
        print(f"✅ سرور جدید ایجاد شد: {server}")
    else:
        print(f"📋 سرور موجود: {server}")
    
    print(f"🌐 URL کامل: {server.get_full_url()}")
    
    # تست اتصال
    xui_service = XUIService(server)
    
    print("🔐 تلاش برای ورود به X-UI...")
    if xui_service.login():
        print("✅ ورود به X-UI موفقیت‌آمیز بود!")
        
        # دریافت inbound ها
        print("📋 دریافت لیست inbound ها...")
        inbounds = xui_service.get_inbounds()
        
        if inbounds:
            print(f"✅ {len(inbounds)} inbound یافت شد:")
            for i, inbound in enumerate(inbounds, 1):
                remark = inbound.get('remark', 'بدون نام')
                port = inbound.get('port', 'نامشخص')
                protocol = inbound.get('protocol', 'نامشخص')
                print(f"  {i}. {remark} - پورت: {port} - پروتکل: {protocol}")
        else:
            print("⚠️ هیچ inbound یافت نشد")
            
    else:
        print("❌ خطا در ورود به X-UI")
        print("🔍 بررسی کنید:")
        print("1. نام کاربری و رمز عبور صحیح باشد")
        print("2. پورت 54321 باز باشد")
        print("3. X-UI در حال اجرا باشد")
        print("4. مسیر وب صحیح باشد: /MsxZ4xuIy5xLfQtsSC/")

def test_inbound_creation():
    """تست ایجاد inbound"""
    print("\n🔧 تست ایجاد inbound...")
    
    server = XUIServer.objects.filter(host="38.54.105.124").first()
    if not server:
        print("❌ سرور یافت نشد")
        return
    
    xui_service = XUIService(server)
    if not xui_service.login():
        print("❌ خطا در ورود به X-UI")
        return
    
    # تست ایجاد inbound برای کاربر
    user_id = 12345  # تست
    inbound_id = xui_service.get_or_create_inbound_for_user(user_id, "vless")
    
    if inbound_id:
        print(f"✅ Inbound با موفقیت ایجاد شد - ID: {inbound_id}")
    else:
        print("❌ خطا در ایجاد inbound")

if __name__ == "__main__":
    print("🚀 شروع تست اتصال X-UI")
    print("=" * 50)
    
    test_xui_connection()
    test_inbound_creation()
    
    print("\n" + "=" * 50)
    print("🏁 تست کامل شد") 