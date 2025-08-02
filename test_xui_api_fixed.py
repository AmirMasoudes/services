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
from xui_servers.services import XUIService

def test_xui_api_fixed():
    """تست X-UI API با endpoint های جدید"""
    print("🔧 تست X-UI API با endpoint های جدید...")
    
    # دریافت سرور X-UI
    server = XUIServer.objects.filter(is_active=True).first()
    if not server:
        print("❌ سرور X-UI فعالی یافت نشد")
        return
    
    print(f"🖥️ سرور: {server.name}")
    print(f" آدرس: {server.host}:{server.port}")
    
    # ایجاد سرویس X-UI
    xui_service = XUIService(server)
    
    # ورود به X-UI
    if not xui_service.login():
        print("❌ خطا در ورود به X-UI")
        return
    
    print("✅ ورود به X-UI موفق")
    
    # تست دریافت inbound ها
    print("\n📊 تست دریافت inbound ها...")
    inbounds = xui_service.get_inbounds()
    print(f"تعداد inbound های موجود: {len(inbounds)}")
    
    if inbounds:
        print("📋 inbound های موجود:")
        for inbound in inbounds:
            print(f"  - ID: {inbound.get('id')}, نام: {inbound.get('remark', 'بدون نام')}, پورت: {inbound.get('port')}")
    else:
        print("ℹ️ هیچ inbound موجود نیست")
    
    # تست ایجاد inbound جدید
    print("\n🔧 تست ایجاد inbound جدید...")
    inbound_id = xui_service.create_user_specific_inbound(999, "vless", 8443)
    
    if inbound_id:
        print(f"✅ inbound جدید ایجاد شد (ID: {inbound_id})")
        
        # بررسی inbound های جدید
        inbounds_after = xui_service.get_inbounds()
        print(f"تعداد inbound های موجود بعد از ایجاد: {len(inbounds_after)}")
        
        # پیدا کردن inbound جدید
        new_inbound = None
        for inbound in inbounds_after:
            if inbound.get('id') == inbound_id:
                new_inbound = inbound
                break
        
        if new_inbound:
            print(f"✅ inbound جدید پیدا شد:")
            print(f"  - نام: {new_inbound.get('remark')}")
            print(f"  - پورت: {new_inbound.get('port')}")
            print(f"  - پروتکل: {new_inbound.get('protocol')}")
        else:
            print("❌ inbound جدید پیدا نشد!")
    else:
        print("❌ خطا در ایجاد inbound جدید")
    
    print("\n🎉 تست X-UI API کامل شد!")

if __name__ == "__main__":
    test_xui_api_fixed() 