#!/usr/bin/env python3
"""
دیباگ جامع API X-UI
"""

import os
import sys
import django
import requests
import json
import time

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from xui_servers.models import XUIServer

def test_basic_connection():
    """تست اتصال پایه"""
    print("🔍 تست اتصال پایه...")
    
    try:
        server = XUIServer.objects.filter(is_active=True).first()
        if not server:
            print("❌ هیچ سرور فعالی یافت نشد")
            return None
        
        print(f"🌐 سرور: {server.name}")
        print(f"🔗 آدرس: {server.host}:{server.port}")
        print(f"👤 نام کاربری: {server.username}")
        print(f"🔑 رمز عبور: {server.password}")
        print(f"🌐 مسیر وب: {server.web_base_path}")
        
        # تست اتصال HTTP
        base_url = f"http://{server.host}:{server.port}"
        if server.web_base_path:
            base_url += server.web_base_path
        
        print(f"🌐 URL کامل: {base_url}")
        
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # تست اتصال اولیه
        try:
            response = session.get(f"{base_url}/", timeout=10)
            print(f"✅ اتصال HTTP: {response.status_code}")
            print(f"📄 محتوای پاسخ: {response.text[:200]}...")
        except Exception as e:
            print(f"❌ خطا در اتصال HTTP: {e}")
            return None
        
        return server, session, base_url
        
    except Exception as e:
        print(f"❌ خطا در تست اتصال: {e}")
        return None

def test_login_methods(server, session, base_url):
    """تست روش‌های مختلف لاگین"""
    print("\n🔐 تست روش‌های مختلف لاگین...")
    
    login_methods = [
        {
            "name": "JSON POST",
            "url": f"{base_url}/login",
            "data": {"username": server.username, "password": server.password},
            "headers": {"Content-Type": "application/json"}
        },
        {
            "name": "Form POST",
            "url": f"{base_url}/login",
            "data": {"username": server.username, "password": server.password},
            "headers": {"Content-Type": "application/x-www-form-urlencoded"}
        },
        {
            "name": "GET with params",
            "url": f"{base_url}/login?username={server.username}&password={server.password}",
            "data": None,
            "headers": {}
        }
    ]
    
    for method in login_methods:
        try:
            print(f"\n🔍 تست: {method['name']}")
            print(f"📡 URL: {method['url']}")
            
            if method['data']:
                response = session.post(
                    method['url'],
                    json=method['data'] if method['headers'].get('Content-Type') == 'application/json' else method['data'],
                    headers=method['headers'],
                    timeout=10
                )
            else:
                response = session.get(method['url'], timeout=10)
            
            print(f"📡 وضعیت: {response.status_code}")
            print(f"📄 محتوا: {response.text[:200]}...")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ JSON معتبر: {data}")
                    if data.get('success'):
                        print("✅ لاگین موفق!")
                        return True
                except:
                    print("❌ JSON نامعتبر")
            
        except Exception as e:
            print(f"❌ خطا: {e}")
    
    return False

def test_api_endpoints(server, session, base_url):
    """تست endpoint های مختلف API"""
    print("\n🧪 تست endpoint های مختلف API...")
    
    endpoints = [
        "/panel/api/inbounds/list",
        "/panel/api/inbounds",
        "/api/inbounds/list",
        "/api/inbounds",
        "/panel/inbounds/list",
        "/inbounds/list",
        "/api/inbound/list",
        "/inbound/list",
        "/panel/api/inbounds/get",
        "/api/inbound/get"
    ]
    
    for endpoint in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            print(f"\n🔍 تست: {url}")
            
            response = session.get(url, timeout=10)
            print(f"📡 وضعیت: {response.status_code}")
            print(f"📄 محتوا: {response.text[:300]}...")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ JSON معتبر: {len(data) if isinstance(data, list) else 'object'}")
                    if isinstance(data, list) and len(data) > 0:
                        print(f"📊 تعداد inbound ها: {len(data)}")
                        for i, inbound in enumerate(data[:2]):
                            print(f"  - Inbound {i+1}: {inbound.get('remark', 'Unknown')}")
                except Exception as e:
                    print(f"❌ خطا در پارس JSON: {e}")
            
        except Exception as e:
            print(f"❌ خطا: {e}")

def test_manual_requests():
    """تست درخواست‌های دستی"""
    print("\n🔧 تست درخواست‌های دستی...")
    
    try:
        server = XUIServer.objects.filter(is_active=True).first()
        if not server:
            print("❌ هیچ سرور فعالی یافت نشد")
            return
        
        base_url = f"http://{server.host}:{server.port}"
        if server.web_base_path:
            base_url += server.web_base_path
        
        # تست با requests ساده
        print(f"🌐 تست اتصال مستقیم به: {base_url}")
        
        # تست 1: اتصال ساده
        try:
            response = requests.get(f"{base_url}/", timeout=5)
            print(f"✅ اتصال ساده: {response.status_code}")
        except Exception as e:
            print(f"❌ خطا در اتصال ساده: {e}")
        
        # تست 2: لاگین با requests
        try:
            login_data = {
                "username": server.username,
                "password": server.password
            }
            
            response = requests.post(
                f"{base_url}/login",
                json=login_data,
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )
            print(f"📡 لاگین مستقیم: {response.status_code}")
            print(f"📄 محتوای لاگین: {response.text[:200]}...")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ لاگین JSON: {data}")
                except:
                    print("❌ لاگین JSON نامعتبر")
            
        except Exception as e:
            print(f"❌ خطا در لاگین مستقیم: {e}")
        
        # تست 3: درخواست API با session
        try:
            session = requests.Session()
            session.headers.update({
                'Content-Type': 'application/json',
                'User-Agent': 'Django-XUI-Bot/2.0'
            })
            
            # لاگین
            login_response = session.post(
                f"{base_url}/login",
                json=login_data,
                timeout=10
            )
            
            if login_response.status_code == 200:
                print("✅ لاگین موفق")
                
                # تست API
                api_response = session.get(f"{base_url}/panel/api/inbounds/list", timeout=10)
                print(f"📡 API وضعیت: {api_response.status_code}")
                print(f"📄 API محتوا: {api_response.text[:300]}...")
                
                if api_response.status_code == 200:
                    try:
                        data = api_response.json()
                        print(f"✅ API JSON: {len(data) if isinstance(data, list) else 'object'}")
                    except Exception as e:
                        print(f"❌ خطا در پارس API JSON: {e}")
            else:
                print(f"❌ لاگین ناموفق: {login_response.status_code}")
                
        except Exception as e:
            print(f"❌ خطا در تست API: {e}")
            
    except Exception as e:
        print(f"❌ خطا در تست دستی: {e}")

def main():
    """تابع اصلی"""
    print("🎉 دیباگ جامع API X-UI")
    print("=" * 50)
    
    # تست اتصال پایه
    result = test_basic_connection()
    if not result:
        print("❌ خطا در اتصال پایه")
        return
    
    server, session, base_url = result
    
    # تست روش‌های لاگین
    login_success = test_login_methods(server, session, base_url)
    
    if login_success:
        # تست endpoint های API
        test_api_endpoints(server, session, base_url)
    else:
        print("❌ لاگین ناموفق - تست endpoint ها متوقف شد")
    
    # تست درخواست‌های دستی
    test_manual_requests()
    
    print("\n🎉 عملیات کامل شد!")

if __name__ == "__main__":
    main() 