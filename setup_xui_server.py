#!/usr/bin/env python3
"""
اسکریپت تنظیم سرور X-UI در Django
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

def setup_xui_server():
    """تنظیم سرور X-UI در Django"""
    print("🔧 تنظیم سرور X-UI...")
    
    # تنظیمات سرور فعلی
    server_config = {
        "name": "سرور اصلی",
        "host": "38.54.105.124",
        "port": 54321,
        "username": "admin",
        "password": "YourSecurePassword123!@#",
        "web_base_path": "/MsxZ4xuIy5xLfQtsSC/",
        "is_active": True
    }
    
    # ایجاد یا به‌روزرسانی سرور
    server, created = XUIServer.objects.get_or_create(
        host=server_config["host"],
        defaults=server_config
    )
    
    if created:
        print(f"✅ سرور جدید ایجاد شد: {server}")
    else:
        # به‌روزرسانی تنظیمات موجود
        for key, value in server_config.items():
            setattr(server, key, value)
        server.save()
        print(f"📝 سرور موجود به‌روزرسانی شد: {server}")
    
    print(f"🌐 URL کامل: {server.get_full_url()}")
    
    # تست اتصال
    print("🔐 تست اتصال به X-UI...")
    xui_service = XUIService(server)
    
    if xui_service.login():
        print("✅ اتصال به X-UI موفقیت‌آمیز بود!")
        
        # دریافت inbound ها
        inbounds = xui_service.get_inbounds()
        print(f"📋 تعداد inbound موجود: {len(inbounds)}")
        
        return server
    else:
        print("❌ خطا در اتصال به X-UI")
        print("🔍 لطفا تنظیمات زیر را بررسی کنید:")
        print(f"  - آدرس: {server.host}:{server.port}")
        print(f"  - مسیر وب: {server.web_base_path}")
        print(f"  - نام کاربری: {server.username}")
        print(f"  - رمز عبور: {server.password}")
        return None

def create_default_inbounds(server):
    """ایجاد inbound های پیش‌فرض"""
    print("\n🔧 ایجاد inbound های پیش‌فرض...")
    
    xui_service = XUIService(server)
    if not xui_service.login():
        print("❌ خطا در ورود به X-UI")
        return
    
    # دریافت inbound های موجود
    existing_inbounds = xui_service.get_inbounds()
    existing_remarks = [inbound.get('remark', '') for inbound in existing_inbounds]
    
    # تنظیمات inbound های پیش‌فرض
    default_inbounds = [
        {
            "name": "VLess-Reality-Main",
            "protocol": "vless",
            "port": 443,
            "description": "Inbound اصلی برای VLess Reality"
        },
        {
            "name": "VMess-Main", 
            "protocol": "vmess",
            "port": 8443,
            "description": "Inbound برای VMess"
        },
        {
            "name": "Trojan-Main",
            "protocol": "trojan", 
            "port": 9443,
            "description": "Inbound برای Trojan"
        }
    ]
    
    created_count = 0
    for inbound_config in default_inbounds:
        remark = inbound_config["name"]
        
        if remark not in existing_remarks:
            print(f"➕ ایجاد inbound: {remark}")
            
            # ایجاد inbound
            inbound_id = xui_service.create_auto_inbound(
                protocol=inbound_config["protocol"],
                port=inbound_config["port"]
            )
            
            if inbound_id:
                print(f"  ✅ ایجاد شد - ID: {inbound_id}")
                created_count += 1
            else:
                print(f"  ❌ خطا در ایجاد")
        else:
            print(f"📋 inbound موجود: {remark}")
    
    print(f"\n📊 خلاصه: {created_count} inbound جدید ایجاد شد")

def test_user_creation(server):
    """تست ایجاد کاربر"""
    print("\n👤 تست ایجاد کاربر...")
    
    xui_service = XUIService(server)
    if not xui_service.login():
        print("❌ خطا در ورود به X-UI")
        return
    
    # تست ایجاد inbound برای کاربر
    test_user_id = 12345
    inbound_id = xui_service.get_or_create_inbound_for_user(test_user_id, "vless")
    
    if inbound_id:
        print(f"✅ Inbound برای کاربر ایجاد شد - ID: {inbound_id}")
        
        # تست ایجاد کاربر در inbound
        user_data = {
            "id": "test-user-123",
            "email": "test@vpn.com",
            "totalGB": 10,
            "expiryTime": 0
        }
        
        if xui_service.create_user(inbound_id, user_data):
            print("✅ کاربر با موفقیت ایجاد شد")
        else:
            print("❌ خطا در ایجاد کاربر")
    else:
        print("❌ خطا در ایجاد inbound")

def main():
    """تابع اصلی"""
    print("🚀 شروع تنظیم سرور X-UI")
    print("=" * 50)
    
    # تنظیم سرور
    server = setup_xui_server()
    
    if server:
        # ایجاد inbound های پیش‌فرض
        create_default_inbounds(server)
        
        # تست ایجاد کاربر
        test_user_creation(server)
    
    print("\n" + "=" * 50)
    print("🏁 تنظیمات کامل شد")

if __name__ == "__main__":
    main() 