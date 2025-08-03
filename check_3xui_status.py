#!/usr/bin/env python3
"""
بررسی وضعیت سرور 3XUI
"""

import os
import sys
import django
import requests
import json
import subprocess

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from xui_servers.models import XUIServer

def check_server_status():
    """بررسی وضعیت سرور"""
    print("🔍 بررسی وضعیت سرور 3XUI...")
    
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
        
        # تست اتصال شبکه
        print(f"\n🌐 تست اتصال شبکه به {server.host}...")
        try:
            result = subprocess.run(
                f"ping -c 3 {server.host}",
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                print("✅ اتصال شبکه برقرار است")
            else:
                print("❌ اتصال شبکه برقرار نیست")
                print(result.stderr)
        except Exception as e:
            print(f"❌ خطا در تست اتصال شبکه: {e}")
        
        # تست اتصال HTTP
        base_url = f"http://{server.host}:{server.port}"
        if server.web_base_path:
            base_url += server.web_base_path
        
        print(f"\n🌐 تست اتصال HTTP به {base_url}...")
        try:
            response = requests.get(f"{base_url}/", timeout=10)
            print(f"✅ اتصال HTTP: {response.status_code}")
            print(f"📄 محتوای پاسخ: {response.text[:200]}...")
        except Exception as e:
            print(f"❌ خطا در اتصال HTTP: {e}")
            return None
        
        return server, base_url
        
    except Exception as e:
        print(f"❌ خطا در بررسی وضعیت: {e}")
        return None

def test_xui_api(server, base_url):
    """تست API 3XUI"""
    print(f"\n🧪 تست API 3XUI...")
    
    try:
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Content-Type': 'application/json'
        })
        
        # لاگین
        login_data = {
            "username": server.username,
            "password": server.password
        }
        
        print(f"🔐 تلاش برای لاگین...")
        login_response = session.post(f"{base_url}/login", json=login_data, timeout=10)
        print(f"📡 وضعیت لاگین: {login_response.status_code}")
        print(f"📄 محتوای لاگین: {login_response.text[:200]}...")
        
        if login_response.status_code == 200:
            try:
                login_data = login_response.json()
                print(f"✅ لاگین JSON: {login_data}")
                
                if login_data.get('success'):
                    print("✅ لاگین موفق!")
                    
                    # تست API endpoints
                    endpoints = [
                        "/panel/api/inbounds/list",
                        "/panel/api/inbounds",
                        "/api/inbounds/list",
                        "/api/inbounds"
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
                                except Exception as e:
                                    print(f"❌ خطا در پارس JSON: {e}")
                            
                        except Exception as e:
                            print(f"❌ خطا: {e}")
                else:
                    print("❌ لاگین ناموفق")
                    
            except Exception as e:
                print(f"❌ خطا در پارس JSON لاگین: {e}")
        else:
            print("❌ خطا در لاگین")
            
    except Exception as e:
        print(f"❌ خطا در تست API: {e}")

def check_xui_process():
    """بررسی فرآیندهای 3XUI"""
    print(f"\n🔍 بررسی فرآیندهای 3XUI...")
    
    try:
        # بررسی فرآیندهای x-ui
        result = subprocess.run(
            "ps aux | grep -i x-ui",
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("📋 فرآیندهای x-ui:")
            print(result.stdout)
        else:
            print("❌ خطا در بررسی فرآیندها")
            
    except Exception as e:
        print(f"❌ خطا در بررسی فرآیندها: {e}")

def check_xui_logs():
    """بررسی لاگ‌های 3XUI"""
    print(f"\n📋 بررسی لاگ‌های 3XUI...")
    
    log_paths = [
        "/usr/local/x-ui/x-ui.log",
        "/var/log/x-ui.log",
        "/opt/x-ui/x-ui.log"
    ]
    
    for log_path in log_paths:
        try:
            result = subprocess.run(
                f"tail -n 10 {log_path}",
                shell=True,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"📄 لاگ {log_path}:")
                print(result.stdout)
                break
            else:
                print(f"❌ فایل لاگ {log_path} یافت نشد")
                
        except Exception as e:
            print(f"❌ خطا در خواندن لاگ {log_path}: {e}")

def main():
    """تابع اصلی"""
    print("🎉 بررسی وضعیت سرور 3XUI")
    print("=" * 50)
    
    # بررسی وضعیت سرور
    result = check_server_status()
    if not result:
        print("❌ خطا در بررسی وضعیت سرور")
        return
    
    server, base_url = result
    
    # تست API
    test_xui_api(server, base_url)
    
    # بررسی فرآیندها
    check_xui_process()
    
    # بررسی لاگ‌ها
    check_xui_logs()
    
    print("\n🎉 عملیات کامل شد!")

if __name__ == "__main__":
    main() 