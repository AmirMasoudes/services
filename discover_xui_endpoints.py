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

def discover_xui_endpoints():
    """کشف endpoint های x-ui"""
    print("🔍 کشف endpoint های x-ui...")
    
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
    
    # تست endpoint های مختلف
    print("\n📊 تست endpoint های مختلف...")
    
    # endpoint های احتمالی
    test_endpoints = [
        # اصلی
        "/",
        "/login",
        "/logout",
        "/api/",
        "/api/inbounds",
        "/api/inbounds/list",
        "/api/inbounds/add",
        "/api/inbounds/update",
        "/api/inbounds/del",
        "/api/inbounds/get",
        "/api/inbounds/updateClient",
        "/api/inbounds/addClient",
        "/api/inbounds/delClient",
        
        # بدون api
        "/inbounds",
        "/inbounds/list",
        "/inbounds/add",
        "/inbounds/update",
        "/inbounds/del",
        "/inbounds/get",
        "/inbounds/updateClient",
        "/inbounds/addClient",
        "/inbounds/delClient",
        
        # با panel
        "/panel/",
        "/panel/api/",
        "/panel/api/inbounds",
        "/panel/api/inbounds/list",
        "/panel/api/inbounds/add",
        "/panel/api/inbounds/update",
        "/panel/api/inbounds/del",
        "/panel/api/inbounds/get",
        "/panel/api/inbounds/updateClient",
        "/panel/api/inbounds/addClient",
        "/panel/api/inbounds/delClient",
        
        # بدون api در panel
        "/panel/inbounds",
        "/panel/inbounds/list",
        "/panel/inbounds/add",
        "/panel/inbounds/update",
        "/panel/inbounds/del",
        "/panel/inbounds/get",
        "/panel/inbounds/updateClient",
        "/panel/inbounds/addClient",
        "/panel/inbounds/delClient",
        
        # سایر
        "/xui/",
        "/xui/api/",
        "/xui/api/inbounds",
        "/xui/api/inbounds/list",
        "/xui/api/inbounds/add",
        
        # v2-ui
        "/v2-ui/",
        "/v2-ui/api/",
        "/v2-ui/api/inbounds",
        "/v2-ui/api/inbounds/list",
        "/v2-ui/api/inbounds/add",
    ]
    
    working_endpoints = []
    
    for endpoint in test_endpoints:
        try:
            response = session.get(f"http://{server.host}:{server.port}{endpoint}")
            print(f"✅ {endpoint}: {response.status_code}")
            
            if response.status_code == 200:
                print(f"📋 محتوای پاسخ: {response.text[:100]}")
                working_endpoints.append(endpoint)
            elif response.status_code == 404:
                print(f"❌ {endpoint}: 404 Not Found")
            else:
                print(f"⚠️ {endpoint}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {endpoint}: {e}")
    
    print(f"\n🎯 endpoint های کارآمد ({len(working_endpoints)} عدد):")
    for endpoint in working_endpoints:
        print(f"  - {endpoint}")
    
    # تست POST برای endpoint های کارآمد
    print("\n📊 تست POST برای endpoint های کارآمد...")
    
    test_data = {
        "remark": "Test-Inbound",
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
    
    post_endpoints = [
        "/api/inbounds/add",
        "/inbounds/add",
        "/panel/api/inbounds/add",
        "/panel/inbounds/add",
        "/xui/api/inbounds/add",
        "/v2-ui/api/inbounds/add"
    ]
    
    working_post_endpoints = []
    
    for endpoint in post_endpoints:
        try:
            print(f"\n🔧 تست POST {endpoint}...")
            response = session.post(
                f"http://{server.host}:{server.port}{endpoint}",
                json=test_data,
                timeout=10
            )
            
            print(f" کد پاسخ: {response.status_code}")
            print(f"📋 محتوای پاسخ: {response.text[:200]}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ POST {endpoint} موفق")
                    working_post_endpoints.append(endpoint)
                else:
                    print(f"❌ خطا در POST: {data.get('msg', 'خطای نامشخص')}")
            else:
                print(f"❌ خطا در اتصال: {response.status_code}")
                
        except Exception as e:
            print(f"❌ خطا در POST {endpoint}: {e}")
    
    print(f"\n🎯 POST endpoint های کارآمد ({len(working_post_endpoints)} عدد):")
    for endpoint in working_post_endpoints:
        print(f"  - {endpoint}")
    
    print("\n🎉 کشف endpoint ها کامل شد!")

if __name__ == "__main__":
    discover_xui_endpoints() 