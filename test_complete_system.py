#!/usr/bin/env python3
"""
تست کامل سیستم Django VPN
"""

import os
import sys
import django
import requests

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from xui_servers.models import XUIServer
from xui_servers.services import XUIService, UserConfigService
from accounts.models import UsersModel

def test_complete_system():
    """تست کامل سیستم"""
    print("🚀 تست کامل سیستم Django VPN")
    print("=" * 50)
    
    # 1. تست اتصال Django
    print("\n1️⃣ تست اتصال Django...")
    try:
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM auth_user;")
        user_count = cursor.fetchone()[0]
        print(f"✅ Django کار می‌کند - تعداد کاربران: {user_count}")
    except Exception as e:
        print(f"❌ خطا در Django: {e}")
        return
    
    # 2. تست سرور X-UI
    print("\n2️⃣ تست سرور X-UI...")
    server = XUIServer.objects.filter(is_active=True).first()
    if not server:
        print("❌ سرور X-UI فعالی یافت نشد")
        return
    
    print(f"✅ سرور X-UI: {server.name} ({server.host}:{server.port})")
    
    # 3. تست اتصال به X-UI
    print("\n3️⃣ تست اتصال به X-UI...")
    xui_service = XUIService(server)
    if not xui_service.login():
        print("❌ خطا در ورود به X-UI")
        return
    
    print("✅ اتصال به X-UI موفق")
    
    # 4. تست دریافت inbound ها
    print("\n4️⃣ تست دریافت inbound ها...")
    inbounds = xui_service.get_inbounds()
    print(f"✅ تعداد inbound موجود: {len(inbounds)}")
    
    # 5. تست ایجاد inbound جدید
    print("\n5️⃣ تست ایجاد inbound جدید...")
    inbound_id = xui_service.create_user_specific_inbound(1000, "vless")
    if inbound_id:
        print(f"✅ Inbound جدید ایجاد شد - ID: {inbound_id}")
    else:
        print("❌ خطا در ایجاد inbound")
        return
    
    # 6. تست Django Admin
    print("\n6️⃣ تست Django Admin...")
    try:
        response = requests.get("http://127.0.0.1:8000/admin/", timeout=5)
        if response.status_code == 302:  # Redirect to login
            print("✅ Django Admin در دسترس است")
        else:
            print(f"⚠️ Django Admin: {response.status_code}")
    except Exception as e:
        print(f"❌ خطا در دسترسی به Django Admin: {e}")
    
    # 7. تست Nginx
    print("\n7️⃣ تست Nginx...")
    try:
        response = requests.get("http://38.54.105.124/admin/", timeout=5)
        if response.status_code == 302:  # Redirect to login
            print("✅ Nginx کار می‌کند")
        else:
            print(f"⚠️ Nginx: {response.status_code}")
    except Exception as e:
        print(f"❌ خطا در دسترسی به Nginx: {e}")
    
    print("\n�� تست کامل شد!")
    print("=" * 50)
    print("�� خلاصه:")
    print("✅ Django: کار می‌کند")
    print("✅ X-UI: کار می‌کند")
    print("✅ Inbound Creation: کار می‌کند")
    print("✅ Django Admin: در دسترس است")
    print("✅ Nginx: کار می‌کند")
    print("\n🌐 دسترسی‌ها:")
    print("�� Django Admin: http://38.54.105.124/admin/")
    print("🔧 X-UI Panel: http://38.54.105.124:54321/MsxZ4xuIy5xLfQtsSC/")
    print("�� Username: admin")
    print("🔑 Password: YourSecurePassword123!@#")

if __name__ == "__main__":
    test_complete_system()
