#!/usr/bin/env python3
"""
دیباگ API X-UI
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

def debug_xui_api():
    """دیباگ API X-UI"""
    print("🔍 دیباگ API X-UI...")
    
    try:
        server = XUIServer.objects.filter(is_active=True).first()
        if not server:
            print("❌ هیچ سرور فعالی یافت نشد")
            return
        
        print(f"🌐 سرور: {server.name}")
        print(f"🔗 آدرس: {server.host}:{server.port}")
        print(f"👤 نام کاربری: {server.username}")
        print(f"🔑 رمز عبور: {server.password}")
        
        # اتصال به X-UI
        base_url = f"http://{server.host}:{server.port}"
        if hasattr(server, 'web_base_path') and server.web_base_path:
            base_url += server.web_base_path
        
        print(f"🌐 URL پایه: {base_url}")
        
        session = requests.Session()
        
        # تست اتصال اولیه
        try:
            response = session.get(f"{base_url}/login", timeout=5)
            print(f"✅ اتصال به X-UI: {response.status_code}")
            print(f"📄 محتوای پاسخ: {response.text[:200]}...")
        except Exception as e:
            print(f"❌ خطا در اتصال: {e}")
            return
        
        # لاگین
        login_data = {
            "username": server.username,
            "password": server.password
        }
        
        print(f"🔐 داده‌های لاگین: {login_data}")
        
        try:
            login_response = session.post(f"{base_url}/login", json=login_data, timeout=10)
            print(f"🔐 پاسخ لاگین: {login_response.status_code}")
            print(f"📄 محتوای پاسخ لاگین: {login_response.text[:200]}...")
            
            if login_response.status_code != 200:
                print(f"❌ خطا در لاگین: {login_response.status_code}")
                return
            
            print("✅ لاگین موفق")
            
        except Exception as e:
            print(f"❌ خطا در لاگین: {e}")
            return
        
        # تست دریافت inbound ها
        try:
            print(f"📡 درخواست inbound ها: {base_url}/panel/api/inbounds")
            inbounds_response = session.get(f"{base_url}/panel/api/inbounds", timeout=10)
            print(f"📡 پاسخ inbound ها: {inbounds_response.status_code}")
            print(f"📄 محتوای پاسخ inbound ها: {inbounds_response.text[:500]}...")
            
            if inbounds_response.status_code != 200:
                print(f"❌ خطا در دریافت inbound ها: {inbounds_response.status_code}")
                return
            
            # تست پارس JSON
            try:
                inbounds = inbounds_response.json()
                print(f"✅ JSON پارس شد: {len(inbounds)} inbound")
                
                for i, inbound in enumerate(inbounds[:3]):  # فقط 3 تا اول
                    print(f"\n🔧 Inbound {i+1}:")
                    print(f"  - ID: {inbound.get('id')}")
                    print(f"  - نام: {inbound.get('remark')}")
                    print(f"  - پورت: {inbound.get('port')}")
                    print(f"  - پروتکل: {inbound.get('protocol')}")
                
            except json.JSONDecodeError as e:
                print(f"❌ خطا در پارس JSON: {e}")
                print(f"📄 محتوای کامل: {inbounds_response.text}")
                return
            
        except Exception as e:
            print(f"❌ خطا در دریافت inbound ها: {e}")
            return
        
    except Exception as e:
        print(f"❌ خطا در دیباگ: {e}")

def test_different_endpoints():
    """تست endpoint های مختلف"""
    print("\n🧪 تست endpoint های مختلف...")
    
    try:
        server = XUIServer.objects.filter(is_active=True).first()
        if not server:
            print("❌ هیچ سرور فعالی یافت نشد")
            return
        
        base_url = f"http://{server.host}:{server.port}"
        if hasattr(server, 'web_base_path') and server.web_base_path:
            base_url += server.web_base_path
        
        session = requests.Session()
        
        # لاگین
        login_data = {
            "username": server.username,
            "password": server.password
        }
        
        login_response = session.post(f"{base_url}/login", json=login_data, timeout=10)
        if login_response.status_code != 200:
            print(f"❌ خطا در لاگین: {login_response.status_code}")
            return
        
        print("✅ لاگین موفق")
        
        # تست endpoint های مختلف
        endpoints = [
            "/panel/api/inbounds",
            "/panel/api/inbounds/list",
            "/panel/api/inbounds/get",
            "/api/inbounds",
            "/api/inbounds/list"
        ]
        
        for endpoint in endpoints:
            try:
                url = f"{base_url}{endpoint}"
                print(f"\n🔍 تست: {url}")
                
                response = session.get(url, timeout=5)
                print(f"📡 وضعیت: {response.status_code}")
                print(f"📄 محتوا: {response.text[:100]}...")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"✅ JSON معتبر: {len(data) if isinstance(data, list) else 'object'}")
                    except:
                        print(f"❌ JSON نامعتبر")
                
            except Exception as e:
                print(f"❌ خطا: {e}")
        
    except Exception as e:
        print(f"❌ خطا در تست endpoint ها: {e}")

def main():
    """تابع اصلی"""
    print("🎉 دیباگ API X-UI")
    print("=" * 50)
    
    # دیباگ API
    debug_xui_api()
    
    # تست endpoint های مختلف
    test_different_endpoints()
    
    print("\n🎉 عملیات کامل شد!")

if __name__ == "__main__":
    main() 