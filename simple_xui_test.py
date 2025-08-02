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

def simple_xui_test():
    """تست ساده x-ui"""
    print("🔧 تست ساده x-ui...")
    
    # دریافت سرور X-UI
    server = XUIServer.objects.filter(is_active=True).first()
    if not server:
        print("❌ سرور X-UI فعالی یافت نشد")
        return
    
    print(f"🖥️ سرور: {server.name}")
    print(f" آدرس: {server.host}:{server.port}")
    
    # تست اتصال ساده
    print("\n📊 تست اتصال ساده...")
    try:
        response = requests.get(f"http://{server.host}:{server.port}/", timeout=5)
        print(f"✅ اتصال موفق: {response.status_code}")
        print(f"📋 محتوای پاسخ: {response.text[:200]}")
    except Exception as e:
        print(f"❌ خطا در اتصال: {e}")
        return
    
    # تست ورود
    print("\n📊 تست ورود...")
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'User-Agent': 'Django-XUI-Bot/1.0'
    })
    
    login_data = {
        "username": server.username,
        "password": server.password
    }
    
    try:
        response = session.post(
            f"http://{server.host}:{server.port}/login",
            json=login_data,
            timeout=10
        )
        
        print(f"کد پاسخ: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ ورود موفق")
                session.cookies.update(response.cookies)
                
                # تست دریافت inbound ها
                print("\n📊 تست دریافت inbound ها...")
                
                # تست endpoint های مختلف
                test_endpoints = [
                    "/api/inbounds/list",
                    "/inbounds/list",
                    "/panel/api/inbounds/list",
                    "/panel/inbounds/list"
                ]
                
                for endpoint in test_endpoints:
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
                print("❌ خطا در ورود")
        else:
            print(f"❌ خطا در اتصال: {response.status_code}")
            
    except Exception as e:
        print(f"❌ خطا در ورود: {e}")
    
    print("\n🎉 تست ساده x-ui کامل شد!")

if __name__ == "__main__":
    simple_xui_test() 