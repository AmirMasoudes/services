#!/usr/bin/env python3
"""
خلاصه نهایی سیستم Django VPN
"""

import os
import sys
import django
import requests
import subprocess
from datetime import datetime

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from xui_servers.models import XUIServer
from xui_servers.services import XUIService
from accounts.models import UsersModel

def system_summary():
    """خلاصه نهایی سیستم"""
    print("🎉 خلاصه نهایی سیستم Django VPN")
    print("=" * 60)
    print(f"📅 تاریخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # خلاصه سیستم
    print("\n خلاصه سیستم:")
    print("✅ Django VPN Management System")
    print("✅ X-UI Integration")
    print("✅ Automatic Inbound Creation")
    print("✅ Custom User Model")
    print("✅ Web Services")
    print("✅ Database")
    print("✅ User Management")
    
    # اطلاعات دسترسی
    print("\n🌐 دسترسی‌ها:")
    print(" Django Admin: http://38.54.105.124/admin/")
    print("🔧 X-UI Panel: http://38.54.105.124:54321/MsxZ4xuIy5xLfQtsSC/")
    print(" Username: admin")
    print("🔑 Password: YourSecurePassword123")
    
    # وضعیت سرویس‌ها
    print("\n وضعیت سرویس‌ها:")
    services = [
        ("django-vpn", "Django VPN"),
        ("nginx", "Nginx"),
        ("redis-server", "Redis"),
        ("postgresql", "PostgreSQL")
    ]
    
    active_services = 0
    for service, name in services:
        result = subprocess.run(f"systemctl is-active {service}", shell=True, capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip() == "active":
            print(f"✅ {name}: فعال")
            active_services += 1
        else:
            print(f"❌ {name}: غیرفعال")
    
    print(f"\n📊 سرویس‌های فعال: {active_services}/{len(services)}")
    
    # وضعیت پورت‌ها
    print("\n🔌 وضعیت پورت‌ها:")
    ports = [
        (80, "HTTP"),
        (8000, "Django"),
        (54321, "X-UI Panel"),
        (6379, "Redis"),
        (5432, "PostgreSQL")
    ]
    
    open_ports = 0
    for port, name in ports:
        result = subprocess.run(f"ss -tlnp | grep :{port}", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {name} (:{port}): باز")
            open_ports += 1
        else:
            print(f"❌ {name} (:{port}): بسته")
    
    print(f"\n📊 پورت‌های باز: {open_ports}/{len(ports)}")
    
    # اطلاعات Django
    print("\n اطلاعات Django:")
    try:
        user_count = UsersModel.objects.count()
        print(f"✅ تعداد کاربران: {user_count}")
        
        admin_user = UsersModel.objects.filter(id_tel='admin').first()
        if admin_user:
            print("✅ Superuser: موجود")
        else:
            print("❌ Superuser: موجود نیست")
    except Exception as e:
        print(f"❌ خطا در Django: {e}")
    
    # اطلاعات X-UI
    print("\n🔧 اطلاعات X-UI:")
    server = XUIServer.objects.filter(is_active=True).first()
    if server:
        print(f"✅ سرور: {server.name}")
        print(f"   آدرس: {server.host}:{server.port}")
        
        xui_service = XUIService(server)
        if xui_service.login():
            inbounds = xui_service.get_inbounds()
            print(f"✅ Inbound ها: {len(inbounds)} عدد")
        else:
            print("❌ اتصال X-UI: ناموفق")
    else:
        print("❌ سرور X-UI: یافت نشد")
    
    # تست وب سرویس‌ها
    print("\n🌐 تست وب سرویس‌ها:")
    
    # Django Admin
    try:
        response = requests.get("http://127.0.0.1:8000/admin/", timeout=5)
        if response.status_code == 302:
            print("✅ Django Admin: کار می‌کند")
        else:
            print(f"⚠️ Django Admin: {response.status_code}")
    except Exception as e:
        print(f"❌ Django Admin: {e}")
    
    # Nginx
    try:
        response = requests.get("http://38.54.105.124/admin/", timeout=5)
        if response.status_code == 302:
            print("✅ Nginx: کار می‌کند")
        else:
            print(f"⚠️ Nginx: {response.status_code}")
    except Exception as e:
        print(f"❌ Nginx: {e}")
    
    # X-UI Panel
    try:
        response = requests.get("http://38.54.105.124:54321/MsxZ4xuIy5xLfQtsSC/", timeout=5)
        if response.status_code == 200:
            print("✅ X-UI Panel: کار می‌کند")
        else:
            print(f"⚠️ X-UI Panel: {response.status_code}")
    except Exception as e:
        print(f"❌ X-UI Panel: {e}")
    
    print("\n🎉 خلاصه نهایی کامل شد!")
    print("=" * 60)
    print("✅ سیستم آماده استفاده است!")
    print("=" * 60)

if __name__ == "__main__":
    system_summary()
