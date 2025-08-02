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

def check_xui_version():
    """بررسی نسخه x-ui"""
    print("🔍 بررسی نسخه x-ui...")
    
    # دریافت سرور X-UI
    server = XUIServer.objects.filter(is_active=True).first()
    if not server:
        print("❌ سرور X-UI فعالی یافت نشد")
        return
    
    print(f"🖥️ سرور: {server.name}")
    print(f" آدرس: {server.host}:{server.port}")
    
    # تست endpoint های مختلف برای دریافت اطلاعات
    print("\n📊 تست endpoint های مختلف...")
    
    # endpoint های احتمالی برای دریافت اطلاعات
    info_endpoints = [
        "/",
        "/login",
        "/api/",
        "/api/inbounds",
        "/api/inbounds/list",
        "/inbounds",
        "/inbounds/list",
        "/panel/",
        "/panel/api/",
        "/panel/api/inbounds",
        "/panel/api/inbounds/list",
        "/panel/inbounds",
        "/panel/inbounds/list",
        "/xui/",
        "/xui/api/",
        "/xui/api/inbounds",
        "/xui/api/inbounds/list",
        "/v2-ui/",
        "/v2-ui/api/",
        "/v2-ui/api/inbounds",
        "/v2-ui/api/inbounds/list"
    ]
    
    working_endpoints = []
    
    for endpoint in info_endpoints:
        try:
            response = requests.get(f"http://{server.host}:{server.port}{endpoint}")
            print(f"✅ {endpoint}: {response.status_code}")
            
            if response.status_code == 200:
                print(f"📋 محتوای پاسخ: {response.text[:200]}")
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
    
    # تست ورود و دریافت اطلاعات
    print("\n📊 تست ورود و دریافت اطلاعات...")
    
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
                
                # تست دریافت inbound ها بعد از ورود
                print("\n📊 تست دریافت inbound ها بعد از ورود...")
                
                list_endpoints = [
                    "/api/inbounds/list",
                    "/inbounds/list",
                    "/panel/api/inbounds/list",
                    "/panel/inbounds/list",
                    "/xui/api/inbounds/list",
                    "/v2-ui/api/inbounds/list"
                ]
                
                for endpoint in list_endpoints:
                    try:
                        response = session.get(f"http://{server.host}:{server.port}{endpoint}")
                        print(f"✅ {endpoint}: {response.status_code}")
                        
                        if response.status_code == 200:
                            data = response.json()
                            print(f"📋 محتوای پاسخ: {json.dumps(data, indent=2)[:300]}")
                            print(f"🎯 این endpoint کار می‌کند!")
                            break
                        else:
                            print(f"❌ {endpoint}: {response.status_code}")
                            
                    except Exception as e:
                        print(f"❌ {endpoint}: {e}")
                
            else:
                print("❌ خطا در ورود به X-UI")
        else:
            print(f"❌ خطا در اتصال: {response.status_code}")
            
    except Exception as e:
        print(f"❌ خطا در ورود: {e}")
    
    print("\n🎉 بررسی نسخه x-ui کامل شد!")

if __name__ == "__main__":
    check_xui_version() 