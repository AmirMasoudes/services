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

def create_initial_inbound():
    """ایجاد inbound اولیه در X-UI"""
    print("🔧 ایجاد inbound اولیه در X-UI...")
    
    # دریافت سرور X-UI
    server = XUIServer.objects.filter(is_active=True).first()
    if not server:
        print("❌ سرور X-UI فعالی یافت نشد")
        return
    
    print(f"🖥️ سرور: {server.name}")
    print(f"   آدرس: {server.host}:{server.port}")
    
    # ایجاد سرویس X-UI
    xui_service = XUIService(server)
    
    # ورود به X-UI
    if not xui_service.login():
        print("❌ خطا در ورود به X-UI")
        return
    
    print("✅ ورود به X-UI موفق")
    
    # دریافت inbound های موجود
    inbounds = xui_service.get_inbounds()
    print(f"📊 تعداد inbound های موجود: {len(inbounds)}")
    
    if len(inbounds) == 0:
        print("🔄 ایجاد inbound اولیه...")
        
        # ایجاد inbound برای VLESS
        inbound_id = xui_service.create_auto_inbound("vless", 443)
        if inbound_id:
            print(f"✅ inbound VLESS ایجاد شد (ID: {inbound_id})")
        else:
            print("❌ خطا در ایجاد inbound VLESS")
    else:
        print("ℹ️ inbound های موجود:")
        for inbound in inbounds:
            print(f"  - ID: {inbound.get('id')}, نام: {inbound.get('remark', 'بدون نام')}")

if __name__ == "__main__":
    create_initial_inbound()
