#!/usr/bin/env python3
import os
import sys
import django

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from xui_servers.models import XUIServer
from xui_servers.services import XUIService

def setup_xui_server():
    """تنظیم سرور X-UI در دیتابیس"""
    print("   تنظیم سرور X-UI...")
    
    # حذف سرورهای قبلی
    XUIServer.objects.all().delete()
    
    # ایجاد سرور جدید
    server = XUIServer.objects.create(
        name="سرور اصلی",
        host="127.0.0.1",
        port=44,
        username="ames",
        password="FJam@1610",
        is_active=True
    )
    
    print(f"✅ سرور X-UI ایجاد شد: {server.name}")
    print(f"🖥️ آدرس: {server.host}:{server.port}")
    print(f"👤 نام کاربری: {server.username}")
    
    # تست اتصال
    try:
        xui_service = XUIService(server)
        if xui_service.login():
            print("✅ اتصال به X-UI موفق")
            inbounds = xui_service.get_inbounds()
            print(f"📊 تعداد inbound ها: {len(inbounds)}")
        else:
            print("❌ خطا در اتصال به X-UI")
    except Exception as e:
        print(f"❌ خطا در تست اتصال: {e}")

if __name__ == "__main__":
    setup_xui_server()
