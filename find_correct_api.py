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

def find_correct_api():
    """پیدا کردن API صحیح X-UI"""
    print("🔍 پیدا کردن API صحیح X-UI...")
    
    # دریافت سرور X-UI
    server = XUIServer.objects.filter(is_active=True).first()
    if not server:
        print("❌ سرور X-UI فعالی یافت نشد")
        return
    
    print(f"🖥️ سرور: {server.name}")
    print(f" آدرس: {server.host}:{server.port}")
    
    # ایجاد session
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'User-Agent': 'Django-XUI-Bot/1.0'
    })
    
    # ورود به X-UI
    login_data = {
        "username": server.username,
        "password": server.password
    }
    
    try:
        print("🔐 در حال ورود به X-UI...")
        response = session.post(
            f"http://{server.host}:{server.port}/login",
            json=login_data,
            timeout=10
        )
        
        print(f" کد پاسخ: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ ورود به X-UI موفق")
                session.cookies.update(response.cookies)
            else:
                print("❌ خطا در ورود به X-UI")
                return
        else:
            print(f"❌ خطا در اتصال: {response.status_code}")
            return
            
    except Exception as e:
        print(f"❌ خطا در ورود: {e}")
        return
    
    # تست endpoint های مختلف برای دریافت inbound ها
    print("\n📊 تست endpoint های دریافت inbound...")
    
    list_endpoints = [
        "/api/inbounds/list",
        "/inbounds/list", 
        "/api/inbound/list",
        "/inbound/list",
        "/panel/inbounds/list",
        "/panel/inbound/list",
        "/api/inbounds",
        "/inbounds",
        "/api/inbound",
        "/inbound",
        "/panel/api/inbounds",
        "/panel/inbounds",
        "/panel/api/inbound", 
        "/panel/inbound"
    ]
    
    working_endpoint = None
    for endpoint in list_endpoints:
        try:
            response = session.get(f"http://{server.host}:{server.port}{endpoint}")
            print(f"✅ {endpoint}: {response.status_code}")
            if response.status_code == 200:
                print(f"📋 محتوای پاسخ: {response.text[:200]}")
                working_endpoint = endpoint
                break
        except Exception as e:
            print(f"❌ {endpoint}: {e}")
    
    if working_endpoint:
        print(f"\n🎯 Endpoint صحیح برای دریافت: {working_endpoint}")
    else:
        print("\n❌ هیچ endpoint صحیحی برای دریافت پیدا نشد")
    
    # تست endpoint های مختلف برای ایجاد inbound
    print("\n📊 تست endpoint های ایجاد inbound...")
    
    add_endpoints = [
        "/api/inbounds/add",
        "/inbounds/add",
        "/api/inbound/add", 
        "/inbound/add",
        "/panel/inbounds/add",
        "/panel/inbound/add",
        "/api/inbounds",
        "/inbounds",
        "/api/inbound",
        "/inbound",
        "/panel/api/inbounds",
        "/panel/inbounds",
        "/panel/api/inbound",
        "/panel/inbound"
    ]
    
    # داده تست برای ایجاد inbound
    test_inbound_data = {
        "up": [],
        "down": [],
        "total": 0,
        "remark": "Test-Inbound",
        "enable": True,
        "expiryTime": 0,
        "listen": "",
        "port": 8443,
        "protocol": "vless",
        "settings": {
            "clients": [],
            "decryption": "none",
            "fallbacks": []
        },
        "streamSettings": {
            "network": "tcp",
            "security": "reality",
            "realitySettings": {
                "show": False,
                "dest": "www.aparat.com:443",
                "xver": 0,
                "serverNames": ["www.aparat.com"],
                "privateKey": "YFgo8YQUJmqhu2yXL8rd8D9gDgJ1H1XgfbYqMB6LmoM",
                "shortIds": [""]
            },
            "tcpSettings": {
                "header": {
                    "type": "none"
                }
            }
        },
        "sniffing": {
            "enabled": True,
            "destOverride": ["http", "tls"]
        }
    }
    
    working_add_endpoint = None
    for endpoint in add_endpoints:
        try:
            print(f"\n🔄 تست {endpoint}...")
            response = session.post(
                f"http://{server.host}:{server.port}{endpoint}",
                json=test_inbound_data,
                timeout=10
            )
            
            print(f" کد پاسخ: {response.status_code}")
            print(f"📋 محتوای پاسخ: {response.text[:200]}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ Endpoint صحیح برای ایجاد: {endpoint}")
                    working_add_endpoint = endpoint
                    break
                else:
                    print(f"❌ خطا در ایجاد: {data.get('msg', 'خطای نامشخص')}")
            else:
                print(f"❌ خطا در اتصال: {response.status_code}")
                
        except Exception as e:
            print(f"❌ خطا در {endpoint}: {e}")
    
    if working_add_endpoint:
        print(f"\n🎯 Endpoint صحیح برای ایجاد: {working_add_endpoint}")
    else:
        print("\n❌ هیچ endpoint صحیحی برای ایجاد پیدا نشد")
    
    # خلاصه نتایج
    print("\n" + "="*50)
    print("📋 خلاصه نتایج:")
    if working_endpoint:
        print(f"✅ دریافت inbound: {working_endpoint}")
    else:
        print("❌ دریافت inbound: پیدا نشد")
        
    if working_add_endpoint:
        print(f"✅ ایجاد inbound: {working_add_endpoint}")
    else:
        print("❌ ایجاد inbound: پیدا نشد")
    
    print("="*50)

if __name__ == "__main__":
    find_correct_api() 