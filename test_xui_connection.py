#!/usr/bin/env python3
"""
تست اتصال XUI
"""

import os
import sys
import django
import requests
import json

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from xui_servers.models import XUIServer

def test_xui_connection():
    """تست اتصال XUI"""
    print("🔍 تست اتصال XUI...")
    
    try:
        server = XUIServer.objects.filter(is_active=True).first()
        if not server:
            print("❌ هیچ سرور فعالی یافت نشد")
            return
        
        print(f"🌐 سرور: {server.name}")
        print(f"🔗 آدرس: {server.host}:{server.port}")
        print(f"👤 نام کاربری: {server.username}")
        print(f"🔑 رمز عبور: {server.password}")
        print(f"🌐 مسیر وب: {server.web_base_path}")
        
        # ساخت URL
        base_url = f"http://{server.host}:{server.port}"
        if server.web_base_path:
            base_url += server.web_base_path
        
        print(f"🌐 URL کامل: {base_url}")
        
        # تست اتصال اولیه
        try:
            response = requests.get(f"{base_url}/", timeout=10)
            print(f"✅ اتصال HTTP: {response.status_code}")
            print(f"📄 محتوای پاسخ: {response.text[:200]}...")
        except Exception as e:
            print(f"❌ خطا در اتصال HTTP: {e}")
            return
        
        # تست لاگین
        session = requests.Session()
        session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Django-XUI-Bot/2.0'
        })
        
        login_data = {
            "username": server.username,
            "password": server.password
        }
        
        try:
            login_response = session.post(f"{base_url}/login", json=login_data, timeout=10)
            print(f"📡 وضعیت لاگین: {login_response.status_code}")
            print(f"📄 محتوای لاگین: {login_response.text[:200]}...")
            
            if login_response.status_code == 200:
                try:
                    data = login_response.json()
                    print(f"✅ لاگین JSON: {data}")
                    
                    if data.get('success'):
                        print("✅ لاگین موفق!")
                        
                        # تست API
                        api_response = session.get(f"{base_url}/panel/api/inbounds/list", timeout=10)
                        print(f"📡 API وضعیت: {api_response.status_code}")
                        print(f"📄 API محتوا: {api_response.text[:300]}...")
                        
                        if api_response.status_code == 200:
                            try:
                                api_data = api_response.json()
                                print(f"✅ API JSON: {len(api_data) if isinstance(api_data, list) else 'object'}")
                            except Exception as e:
                                print(f"❌ خطا در پارس API JSON: {e}")
                        else:
                            print("❌ خطا در API")
                    else:
                        print("❌ لاگین ناموفق")
                        
                except Exception as e:
                    print(f"❌ خطا در پارس JSON لاگین: {e}")
            else:
                print("❌ خطا در لاگین")
                
        except Exception as e:
            print(f"❌ خطا در لاگین: {e}")
            
    except Exception as e:
        print(f"❌ خطا در تست اتصال: {e}")

if __name__ == "__main__":
    test_xui_connection() 