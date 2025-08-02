#!/usr/bin/env python3
"""
تست مستقیم endpoint های /panel/ برای X-UI
"""

import requests
import json

def test_direct_panel():
    """تست مستقیم endpoint های /panel/"""
    
    print("🔍 تست مستقیم endpoint های /panel/ برای X-UI")
    print("=" * 50)
    
    # تنظیمات سرور
    base_url = "http://38.54.105.124:54321/MsxZ4xuIy5xLfQtsSC"
    username = "admin"
    password = "YourSecurePassword123!@#"
    
    print(f"🌐 سرور: {base_url}")
    
    # ایجاد session
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'User-Agent': 'Django-XUI-Bot/2.0'
    })
    
    # ورود
    print("\n🔐 تست ورود...")
    login_data = {
        "username": username,
        "password": password
    }
    
    try:
        response = session.post(f"{base_url}/login", json=login_data, timeout=10)
        print(f"📊 وضعیت ورود: {response.status_code}")
        print(f"📄 پاسخ ورود: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ ورود موفق")
            else:
                print("❌ خطا در ورود")
                return
        else:
            print("❌ خطا در ورود")
            return
            
    except Exception as e:
        print(f"❌ خطا در ورود: {e}")
        return
    
    # تست دریافت inbound ها
    print("\n📋 تست دریافت inbound ها...")
    
    list_endpoints = [
        "/panel/api/inbounds/list",
        "/panel/inbounds/list",
        "/api/inbounds/list",
        "/inbounds/list"
    ]
    
    for endpoint in list_endpoints:
        try:
            response = session.get(f"{base_url}{endpoint}", timeout=10)
            print(f"📊 وضعیت {endpoint}: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    inbounds = data.get('obj', [])
                    print(f"✅ موفق با {endpoint} - تعداد inbound: {len(inbounds)}")
                    break
                except:
                    print(f"❌ پاسخ JSON نامعتبر {endpoint}")
            else:
                print(f"❌ خطای HTTP {endpoint}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ خطا {endpoint}: {e}")
    
    # تست ایجاد inbound
    print("\n🔧 تست ایجاد inbound...")
    
    test_inbound = {
        "remark": "Direct-Panel-Test",
        "port": 8449,
        "protocol": "vmess",
        "settings": json.dumps({"clients": []}),
        "streamSettings": json.dumps({"network": "tcp", "security": "none"}),
        "sniffing": "{\"enabled\":true,\"destOverride\":[\"http\",\"tls\"]}",
        "enable": True,
        "expiryTime": 0,
        "listen": "",
        "up": 0,
        "down": 0,
        "total": 0
    }
    
    add_endpoints = [
        "/panel/api/inbounds/add",
        "/panel/inbounds/add",
        "/api/inbounds/add",
        "/inbounds/add"
    ]
    
    for endpoint in add_endpoints:
        print(f"\n🔗 تست {endpoint}...")
        try:
            response = session.post(f"{base_url}{endpoint}", json=test_inbound, timeout=10)
            
            print(f"📊 وضعیت: {response.status_code}")
            print(f"📄 پاسخ: {response.text}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('success'):
                        print(f"✅ موفق با {endpoint}")
                        inbound_id = data.get('obj', {}).get('id')
                        if inbound_id:
                            print(f"📋 ID ایجاد شده: {inbound_id}")
                        break
                    else:
                        print(f"❌ خطا: {data.get('msg')}")
                except:
                    print("❌ پاسخ JSON نامعتبر")
            else:
                print(f"❌ خطای HTTP: {response.status_code}")
                
        except Exception as e:
            print(f"❌ خطا: {e}")
    
    print("\n🏁 تست کامل شد")

if __name__ == "__main__":
    test_direct_panel() 