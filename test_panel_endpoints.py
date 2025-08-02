#!/usr/bin/env python3
"""
تست endpoint های /panel/ برای X-UI
"""

import requests
import json
import sys
import os

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# اضافه کردن مسیر پروژه
sys.path.append('/opt/vpn-service/services')

import django
django.setup()

from xui_servers.models import XUIServer
from xui_servers.services import XUIService

def test_panel_endpoints():
    """تست endpoint های /panel/"""
    
    print("🔍 تست endpoint های /panel/ برای X-UI")
    print("=" * 50)
    
    # تنظیمات سرور
    server = XUIServer.objects.first()
    if not server:
        print("❌ سرور X-UI یافت نشد")
        return
    
    print(f"🌐 سرور: {server.host}:{server.port}")
    print(f"📁 مسیر: {server.web_base_path}")
    
    # تست اتصال
    xui_service = XUIService(server)
    
    # ورود
    print("\n🔐 تست ورود...")
    if not xui_service.login():
        print("❌ خطا در ورود")
        return
    
    print("✅ ورود موفق")
    
    # تست دریافت inbound ها
    print("\n📋 تست دریافت inbound ها...")
    inbounds = xui_service.get_inbounds()
    print(f"📊 تعداد inbound: {len(inbounds)}")
    
    # تست ایجاد inbound
    print("\n🔧 تست ایجاد inbound...")
    
    test_inbound = {
        "remark": "Panel-Test-Inbound",
        "port": 8448,
        "protocol": "vmess",
        "settings": json.dumps({"clients": []}),
        "streamSettings": json.dumps({"network": "tcp", "security": "none"}),
        "sniffing": "{\"enabled\":true,\"destOverride\":[\"http\",\"tls\"]}",
        "enable": True,
        "expiryTime": 0,
        "listen": "",
        "up": 0,
        "down": 0,
        "total": 0
    }
    
    # تست endpoint های مختلف
    endpoints = [
        "/panel/api/inbounds/add",
        "/panel/inbounds/add"
    ]
    
    for endpoint in endpoints:
        print(f"\n🔗 تست {endpoint}...")
        try:
            response = xui_service.session.post(
                f"{xui_service.base_url}{endpoint}",
                json=test_inbound,
                timeout=10
            )
            
            print(f"📊 وضعیت: {response.status_code}")
            print(f"📄 پاسخ: {response.text}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('success'):
                        print(f"✅ موفق با {endpoint}")
                        break
                    else:
                        print(f"❌ خطا: {data.get('msg')}")
                except:
                    print("❌ پاسخ JSON نامعتبر")
            else:
                print(f"❌ خطای HTTP: {response.status_code}")
                
        except Exception as e:
            print(f"❌ خطا: {e}")
    
    print("\n🏁 تست کامل شد")

if __name__ == "__main__":
    test_panel_endpoints() 