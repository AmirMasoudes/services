#!/usr/bin/env python3
"""
اسکریپت دیباگ برای بررسی مشکل ایجاد inbound در X-UI
"""

import os
import sys
import django
import json
import requests

# اضافه کردن مسیر پروژه
sys.path.append('/opt/vpn-service/services')

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from xui_servers.models import XUIServer
from xui_servers.services import XUIService
from xui_servers import settings as xui_settings

def debug_xui_endpoints():
    """دیباگ endpoint های X-UI"""
    print("🔍 دیباگ endpoint های X-UI...")
    
    server = XUIServer.objects.filter(host="38.54.105.124").first()
    if not server:
        print("❌ سرور یافت نشد")
        return
    
    print(f"🌐 URL سرور: {server.get_full_url()}")
    
    # تست اتصال
    xui_service = XUIService(server)
    if not xui_service.login():
        print("❌ خطا در ورود به X-UI")
        return
    
    print("✅ ورود موفق")
    
    # تست endpoint های مختلف
    endpoints = [
        "/api/inbounds/list",
        "/inbounds/list", 
        "/api/inbound/list",
        "/inbound/list",
        "/panel/api/inbounds/list",
        "/panel/inbounds/list"
    ]
    
    print("\n📋 تست endpoint های دریافت inbound:")
    for endpoint in endpoints:
        try:
            response = xui_service.session.get(
                f"{xui_service.base_url}{endpoint}",
                timeout=10
            )
            print(f"  {endpoint}: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"    پاسخ: {json.dumps(data, indent=2)}")
        except Exception as e:
            print(f"  {endpoint}: خطا - {e}")

def debug_inbound_creation():
    """دیباگ ایجاد inbound"""
    print("\n🔧 دیباگ ایجاد inbound...")
    
    server = XUIServer.objects.filter(host="38.54.105.124").first()
    xui_service = XUIService(server)
    
    if not xui_service.login():
        print("❌ خطا در ورود به X-UI")
        return
    
    # تست endpoint های ایجاد inbound
    add_endpoints = [
        "/api/inbounds/add",
        "/inbounds/add",
        "/api/inbound/add", 
        "/inbound/add",
        "/panel/api/inbounds/add",
        "/panel/inbounds/add"
    ]
    
    # ایجاد داده تست inbound
    test_inbound_data = {
        "remark": "Test-Inbound",
        "port": 8443,
        "protocol": "vmess",
        "settings": {
            "clients": []
        },
        "streamSettings": {
            "network": "ws",
            "security": "none",
            "wsSettings": {
                "acceptProxyProtocol": False,
                "path": "/",
                "headers": {}
            }
        },
        "sniffing": {
            "enabled": True,
            "destOverride": ["http", "tls"]
        },
        "enable": True,
        "expiryTime": 0,
        "listen": "",
        "up": [],
        "down": [],
        "total": 0
    }
    
    print(f"📤 داده ارسالی: {json.dumps(test_inbound_data, indent=2)}")
    
    print("\n📤 تست endpoint های ایجاد inbound:")
    for endpoint in add_endpoints:
        try:
            response = xui_service.session.post(
                f"{xui_service.base_url}{endpoint}",
                json=test_inbound_data,
                timeout=10
            )
            print(f"  {endpoint}: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"    پاسخ: {json.dumps(data, indent=2)}")
            else:
                print(f"    خطا: {response.text}")
        except Exception as e:
            print(f"  {endpoint}: خطا - {e}")

def test_simple_inbound():
    """تست ایجاد inbound ساده"""
    print("\n🧪 تست ایجاد inbound ساده...")
    
    server = XUIServer.objects.filter(host="38.54.105.124").first()
    xui_service = XUIService(server)
    
    if not xui_service.login():
        print("❌ خطا در ورود به X-UI")
        return
    
    # تست با داده ساده‌تر
    simple_inbound = {
        "remark": "Simple-Test",
        "port": 8444,
        "protocol": "vmess",
        "settings": {
            "clients": []
        },
        "streamSettings": {
            "network": "tcp",
            "security": "none"
        },
        "sniffing": {
            "enabled": True,
            "destOverride": ["http", "tls"]
        }
    }
    
    print("📤 ارسال درخواست ایجاد inbound ساده...")
    
    # تست endpoint اصلی
    try:
        response = xui_service.session.post(
            f"{xui_service.base_url}/api/inbounds/add",
            json=simple_inbound,
            timeout=10
        )
        
        print(f"📊 وضعیت پاسخ: {response.status_code}")
        print(f"📄 محتوای پاسخ: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ پاسخ JSON: {json.dumps(data, indent=2)}")
        else:
            print("❌ خطا در ایجاد inbound")
            
    except Exception as e:
        print(f"❌ خطا در ارسال درخواست: {e}")

def check_xui_version():
    """بررسی نسخه X-UI"""
    print("\n📋 بررسی نسخه X-UI...")
    
    server = XUIServer.objects.filter(host="38.54.105.124").first()
    xui_service = XUIService(server)
    
    if not xui_service.login():
        print("❌ خطا در ورود به X-UI")
        return
    
    # تست endpoint های مختلف برای دریافت اطلاعات
    info_endpoints = [
        "/api/panel/info",
        "/panel/info",
        "/api/info",
        "/info"
    ]
    
    for endpoint in info_endpoints:
        try:
            response = xui_service.session.get(
                f"{xui_service.base_url}{endpoint}",
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                print(f"✅ اطلاعات X-UI از {endpoint}:")
                print(f"   {json.dumps(data, indent=2)}")
                break
        except Exception as e:
            print(f"  {endpoint}: خطا - {e}")

def main():
    """تابع اصلی"""
    print("🚀 شروع دیباگ X-UI")
    print("=" * 50)
    
    debug_xui_endpoints()
    debug_inbound_creation()
    test_simple_inbound()
    check_xui_version()
    
    print("\n" + "=" * 50)
    print("🏁 دیباگ کامل شد")

if __name__ == "__main__":
    main() 