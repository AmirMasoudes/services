#!/usr/bin/env python3
import requests
import json

def debug_3xui_api():
    """دیباگ API 3X-UI"""
    base_url = "http://127.0.0.1:44/BerLdbHxpmtoT3xuzu"
    
    # اطلاعات ورود
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json'
    })
    
    print("�� دیباگ API 3X-UI...")
    print(f"🖥️ آدرس: {base_url}")
    
    # 1. ورود
    try:
        response = session.post(f"{base_url}/api/login", json=login_data)
        print(f"🔍 ورود: {response.status_code}")
        print(f"📋 پاسخ ورود: {response.text}")
        if response.status_code == 200:
            print("✅ ورود موفق")
        else:
            print(f"❌ ورود ناموفق")
            return
    except Exception as e:
        print(f"❌ خطا در ورود: {e}")
        return
    
    # 2. تست endpoint های مختلف
    endpoints = [
        "/api/v1/inbounds",
        "/api/inbounds",
        "/api/v1/inbound",
        "/api/inbound"
    ]
    
    for endpoint in endpoints:
        try:
            print(f"\n🔍 تست {endpoint}...")
            response = session.get(f"{base_url}{endpoint}")
            print(f"کد پاسخ: {response.status_code}")
            print(f"محتوای پاسخ: {response.text[:500]}...")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ JSON معتبر: {len(data.get('obj', []))} inbound")
                except json.JSONDecodeError as e:
                    print(f"❌ JSON نامعتبر: {e}")
            else:
                print(f"❌ خطا: {response.text}")
        except Exception as e:
            print(f"❌ خطا در {endpoint}: {e}")
    
    # 3. تست ایجاد inbound
    print(f"\n🔍 تست ایجاد inbound...")
    inbound_data = {
        "protocol": "vless",
        "port": 443,
        "stream": {
            "network": "tcp",
            "security": "reality",
            "realitySettings": {
                "serverName": "www.google.com",
                "fingerprint": "chrome",
                "publicKey": "test-key",
                "shortId": "test-id",
                "spiderX": "/"
            }
        },
        "clients": [
            {
                "id": "test-uuid-123",
                "email": "test@example.com",
                "totalGB": 1
            }
        ]
    }
    
    try:
        response = session.post(f"{base_url}/api/v1/inbounds", json=inbound_data)
        print(f"کد پاسخ ایجاد: {response.status_code}")
        print(f"محتوای پاسخ ایجاد: {response.text[:500]}...")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ inbound ایجاد شد: {data}")
            except json.JSONDecodeError as e:
                print(f"❌ JSON نامعتبر: {e}")
        else:
            print(f"❌ خطا در ایجاد inbound")
    except Exception as e:
        print(f"❌ خطا در ایجاد inbound: {e}")

if __name__ == "__main__":
    debug_3xui_api() 