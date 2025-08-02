#!/usr/bin/env python3
"""
تست API های X-UI
"""

import requests
import json

def test_xui_api():
    """تست API های X-UI"""
    
    # تنظیمات سرور
    base_url = "http://38.54.105.124:54321/MsxZ4xuIy5xLfQtsSC"
    
    # ایجاد session
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'User-Agent': 'Django-XUI-Bot/2.0'
    })
    
    print("🔍 تست API های X-UI...")
    print(f"🌐 URL پایه: {base_url}")
    
    # تست ورود
    print("\n🔐 تست ورود...")
    login_data = {
        "username": "admin",
        "password": "YourSecurePassword123!@#"
    }
    
    try:
        response = session.post(f"{base_url}/login", json=login_data, timeout=10)
        print(f"📊 وضعیت ورود: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📄 پاسخ ورود: {json.dumps(data, indent=2)}")
            
            if data.get('success'):
                print("✅ ورود موفق")
                
                # تست دریافت inbound ها
                print("\n📋 تست دریافت inbound ها...")
                list_endpoints = [
                    "/api/inbounds/list",
                    "/inbounds/list",
                    "/api/inbound/list",
                    "/inbound/list"
                ]
                
                for endpoint in list_endpoints:
                    try:
                        response = session.get(f"{base_url}{endpoint}", timeout=10)
                        print(f"  {endpoint}: {response.status_code}")
                        
                        if response.status_code == 200:
                            data = response.json()
                            print(f"    پاسخ: {json.dumps(data, indent=2)}")
                            break
                    except Exception as e:
                        print(f"  {endpoint}: خطا - {e}")
                
                # تست ایجاد inbound ساده
                print("\n🔧 تست ایجاد inbound...")
                test_inbound = {
                    "remark": "API-Test",
                    "port": 8445,
                    "protocol": "vmess",
                    "settings": {
                        "clients": []
                    },
                    "streamSettings": {
                        "network": "tcp",
                        "security": "none"
                    },
                    "sniffing": {
                        "enabled": True,
                        "destOverride": ["http", "tls"]
                    }
                }
                
                add_endpoints = [
                    "/api/inbounds/add",
                    "/inbounds/add",
                    "/api/inbound/add",
                    "/inbound/add"
                ]
                
                for endpoint in add_endpoints:
                    try:
                        print(f"  تست {endpoint}...")
                        response = session.post(f"{base_url}{endpoint}", json=test_inbound, timeout=10)
                        print(f"    وضعیت: {response.status_code}")
                        
                        if response.status_code == 200:
                            data = response.json()
                            print(f"    پاسخ: {json.dumps(data, indent=2)}")
                            
                            if data.get('success'):
                                print("✅ Inbound با موفقیت ایجاد شد!")
                                break
                            else:
                                print(f"❌ خطا: {data.get('msg', 'خطای نامشخص')}")
                        else:
                            print(f"    خطا: {response.text}")
                            
                    except Exception as e:
                        print(f"    خطا: {e}")
            else:
                print("❌ خطا در ورود")
        else:
            print(f"❌ خطای HTTP: {response.status_code}")
            print(f"📄 محتوای پاسخ: {response.text}")
            
    except Exception as e:
        print(f"❌ خطا در اتصال: {e}")

if __name__ == "__main__":
    test_xui_api() 