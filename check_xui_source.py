#!/usr/bin/env python3
import os
import subprocess
import requests
import json

def check_xui_source():
    """بررسی x-ui source code"""
    print("🔍 بررسی x-ui source code...")
    
    # بررسی فایل‌های x-ui
    xui_paths = [
        '/tmp/x-ui-source',
        '/usr/local/x-ui',
        '/etc/x-ui'
    ]
    
    for path in xui_paths:
        if os.path.exists(path):
            print(f"✅ مسیر موجود: {path}")
            try:
                files = os.listdir(path)
                print(f"📁 فایل‌ها: {files[:10]}")
                
                # بررسی فایل‌های مهم
                important_files = ['main.go', 'router.go', 'api.go', 'config.json']
                for file in important_files:
                    file_path = os.path.join(path, file)
                    if os.path.exists(file_path):
                        print(f"📄 فایل مهم: {file}")
                        try:
                            with open(file_path, 'r') as f:
                                content = f.read()
                                # جستجوی endpoint ها
                                if 'inbounds' in content:
                                    print(f"🔍 در {file} کلمه 'inbounds' پیدا شد")
                                if '/api/' in content:
                                    print(f"🔍 در {file} کلمه '/api/' پیدا شد")
                        except Exception as e:
                            print(f"❌ خطا در خواندن {file}: {e}")
            except Exception as e:
                print(f"❌ خطا در خواندن مسیر: {e}")
        else:
            print(f"❌ مسیر موجود نیست: {path}")
    
    # تست endpoint های مختلف بر اساس x-ui source
    print("\n📊 تست endpoint های مختلف...")
    
    # endpoint های احتمالی بر اساس x-ui
    test_endpoints = [
        # اصلی
        "/",
        "/login",
        "/logout",
        
        # API endpoints
        "/api/inbounds",
        "/api/inbounds/list",
        "/api/inbounds/add",
        "/api/inbounds/update",
        "/api/inbounds/del",
        "/api/inbounds/get",
        "/api/inbounds/updateClient",
        "/api/inbounds/addClient",
        "/api/inbounds/delClient",
        
        # بدون /api/
        "/inbounds",
        "/inbounds/list",
        "/inbounds/add",
        "/inbounds/update",
        "/inbounds/del",
        "/inbounds/get",
        "/inbounds/updateClient",
        "/inbounds/addClient",
        "/inbounds/delClient",
        
        # با /xui/
        "/xui/",
        "/xui/api/",
        "/xui/api/inbounds",
        "/xui/api/inbounds/list",
        "/xui/api/inbounds/add",
        
        # سایر
        "/panel/",
        "/panel/api/",
        "/panel/api/inbounds",
        "/panel/api/inbounds/list",
        "/panel/api/inbounds/add",
    ]
    
    # تست اتصال
    try:
        response = requests.get('http://127.0.0.1:44/', timeout=5)
        print(f"✅ اتصال به x-ui موفق: {response.status_code}")
        
        # تست ورود
        session = requests.Session()
        login_data = {
            "username": "ames",
            "password": "FJam@1610"
        }
        
        response = session.post('http://127.0.0.1:44/login', json=login_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ ورود موفق")
                
                # تست endpoint های مختلف
                for endpoint in test_endpoints:
                    try:
                        response = session.get(f"http://127.0.0.1:44{endpoint}")
                        if response.status_code == 200:
                            print(f"✅ {endpoint}: {response.status_code}")
                            print(f"📋 محتوای پاسخ: {response.text[:100]}")
                        else:
                            print(f"❌ {endpoint}: {response.status_code}")
                    except Exception as e:
                        print(f"❌ {endpoint}: {e}")
            else:
                print("❌ خطا در ورود")
        else:
            print(f"❌ خطا در اتصال: {response.status_code}")
            
    except Exception as e:
        print(f"❌ خطا در اتصال: {e}")
    
    print("\n🎉 بررسی x-ui source code کامل شد!")

if __name__ == "__main__":
    check_xui_source() 