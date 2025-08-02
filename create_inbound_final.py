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

def create_inbound_final():
    """ایجاد inbound با API صحیح"""
    print("🔧 ایجاد inbound با API صحیح...")
    
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
                # ذخیره cookie
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
    
    # بررسی inbound های موجود
    print("\n📊 بررسی inbound های موجود...")
    try:
        response = session.get(f"http://{server.host}:{server.port}/panel/api/inbounds/list")
        print(f" کد پاسخ: {response.status_code}")
        print(f"📋 محتوای پاسخ: {response.text[:200]}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                inbounds = data.get('obj', [])
                print(f"✅ تعداد inbound های موجود: {len(inbounds)}")
                
                if len(inbounds) > 0:
                    print("ℹ️ inbound های موجود:")
                    for inbound in inbounds:
                        print(f"  - ID: {inbound.get('id')}, نام: {inbound.get('remark', 'بدون نام')}")
                    return inbounds[0].get('id')
                else:
                    print("🔄 هیچ inbound موجود نیست. در حال ایجاد...")
            else:
                print(f"❌ خطا در دریافت inbound ها: {data.get('msg', 'خطای نامشخص')}")
        else:
            print(f"❌ خطا در اتصال: {response.status_code}")
            
    except Exception as e:
        print(f"❌ خطا در بررسی inbound ها: {e}")
    
    # ایجاد inbound جدید
    print("\n   ایجاد inbound جدید...")
    
    inbound_data = {
        "up": [],
        "down": [],
        "total": 0,
        "remark": "AutoBot-VLESS-443",
        "enable": True,
        "expiryTime": 0,
        "listen": "",
        "port": 443,
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
    
    try:
        response = session.post(
            f"http://{server.host}:{server.port}/panel/api/inbounds/add",
            json=inbound_data,
            timeout=10
        )
        
        print(f" کد پاسخ: {response.status_code}")
        print(f"📋 محتوای پاسخ: {response.text[:200]}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                inbound_id = data.get('obj', {}).get('id')
                print(f"✅ inbound ایجاد شد (ID: {inbound_id})")
                return inbound_id
            else:
                print(f"❌ خطا در ایجاد inbound: {data.get('msg', 'خطای نامشخص')}")
        else:
            print(f"❌ خطا در اتصال: {response.status_code}")
            
    except Exception as e:
        print(f"❌ خطا در ایجاد inbound: {e}")
    
    return None

if __name__ == "__main__":
    create_inbound_final()
