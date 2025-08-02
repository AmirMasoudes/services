#!/usr/bin/env python3
import requests
import json

def test_3xui_api_final():
    """تست نهایی API 3X-UI"""
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
    
    print("🔧 تست نهایی API 3X-UI...")
    print(f"🖥️ آدرس: {base_url}")
    
    # 1. ورود
    try:
        response = session.post(f"{base_url}/api/login", json=login_data)
        print(f"🔍 ورود: {response.status_code}")
        if response.status_code == 200:
            print("✅ ورود موفق")
            print(f"📋 پاسخ: {response.text[:200]}...")
        else:
            print(f"❌ ورود ناموفق: {response.text}")
            return
    except Exception as e:
        print(f"❌ خطا در ورود: {e}")
        return
    
    # 2. دریافت لیست inbound ها
    try:
        response = session.get(f"{base_url}/api/v1/inbounds")
        print(f"\n🔍 دریافت inbound ها: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {len(data.get('obj', []))} inbound یافت شد")
        else:
            print(f"❌ خطا: {response.text}")
    except Exception as e:
        print(f"❌ خطا در دریافت inbound ها: {e}")
    
    # 3. ایجاد inbound تستی
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
        print(f"\n🔍 ایجاد inbound: {response.status_code}")
        if response.status_code == 200:
            print("✅ inbound ایجاد شد")
        else:
            print(f"❌ خطا: {response.text}")
    except Exception as e:
        print(f"❌ خطا در ایجاد inbound: {e}")

if __name__ == "__main__":
    test_3xui_api_final() 