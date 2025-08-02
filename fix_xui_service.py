#!/usr/bin/env python3
"""
اصلاح سرویس X-UI برای استفاده از endpoint صحیح
"""

import os
import sys
import django

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from xui_servers.models import XUIServer
from xui_servers.services import XUIService

def fix_xui_service():
    """اصلاح سرویس X-UI"""
    print("🔧 اصلاح سرویس X-UI...")
    
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
    
    # تست ایجاد inbound جدید
    print("\n🔧 تست ایجاد inbound جدید...")
    inbound_id = xui_service.create_user_specific_inbound(999, "vless")
    
    if inbound_id:
        print(f"✅ Inbound با موفقیت ایجاد شد - ID: {inbound_id}")
        print("🎉 سرویس X-UI آماده است!")
    else:
        print("❌ خطا در ایجاد inbound")

if __name__ == "__main__":
    fix_xui_service()
