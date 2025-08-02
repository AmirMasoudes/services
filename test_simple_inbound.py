#!/usr/bin/env python3
import os
import sys
import django
import requests
import json
import random
import string

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from xui_servers.models import XUIServer
from xui_servers.services import XUIService
from xui_servers import settings as xui_settings

def test_simple_inbound():
    """تست ساده ایجاد inbound"""
    print("🔧 تست ساده ایجاد inbound...")
    
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
    
    # ایجاد داده inbound ساده
    port = random.randint(10000, 65000)
    fake_domain = random.choice(xui_settings.FAKE_DOMAINS)
    public_key = random.choice(xui_settings.REALITY_PUBLIC_KEYS)
    short_id = ''.join(random.choices(string.hexdigits.lower(), k=8))
    
    inbound_data = {
        "up": [],
        "down": [],
        "total": 0,
        "remark": f"Test-Inbound-{port}",
        "enable": True,
        "expiryTime": 0,
        "listen": "",
        "port": port,
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
                "serverNames": [fake_domain],
                "privateKey": "YFgo8YQUJmqhu2yXL8rd8D9gDgJ1H1XgfbYqMB6LmoM",
                "shortIds": [short_id]
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
    
    print(f"\n📊 داده inbound:")
    print(f"  - پورت: {port}")
    print(f"  - دامنه: {fake_domain}")
    print(f"  - کلید عمومی: {public_key[:20]}...")
    print(f"  - Short ID: {short_id}")
    
    # تست endpoint های مختلف برای ایجاد inbound
    print("\n📊 تست endpoint های ایجاد inbound...")
    
    add_endpoints = [
        "/api/inbounds/add",
        "/inbounds/add",
        "/api/inbound/add", 
        "/inbound/add",
        "/panel/api/inbounds/add",
        "/panel/inbounds/add"
    ]
    
    working_endpoint = None
    for endpoint in add_endpoints:
        try:
            print(f"\n🔧 تست {endpoint}...")
            response = session.post(
                f"http://{server.host}:{server.port}{endpoint}",
                json=inbound_data,
                timeout=10
            )
            
            print(f" کد پاسخ: {response.status_code}")
            print(f"📋 محتوای پاسخ: {response.text[:200]}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ Endpoint صحیح برای ایجاد: {endpoint}")
                    working_endpoint = endpoint
                    inbound_id = data.get('obj', {}).get('id')
                    print(f"✅ Inbound ایجاد شد (ID: {inbound_id})")
                    break
                else:
                    print(f"❌ خطا در ایجاد: {data.get('msg', 'خطای نامشخص')}")
            else:
                print(f"❌ خطا در اتصال: {response.status_code}")
                
        except Exception as e:
            print(f"❌ خطا در {endpoint}: {e}")
    
    if working_endpoint:
        print(f"\n🎯 Endpoint صحیح برای ایجاد: {working_endpoint}")
        print(f"✅ Inbound با موفقیت ایجاد شد!")
    else:
        print("\n❌ هیچ endpoint صحیحی برای ایجاد پیدا نشد")
    
    print("\n🎉 تست ساده کامل شد!")

if __name__ == "__main__":
    test_simple_inbound() 