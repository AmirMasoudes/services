#!/usr/bin/env python3
import requests
import json
import random

def test_xui_inbound_creation():
    """تست ایجاد inbound در X-UI"""
    base_url = "http://127.0.0.1:44"
    
    # ورود
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json'
    })
    
    login_data = {
        "username": "ames",
        "password": "FJam@1610"
    }
    
    try:
        response = session.post(f"{base_url}/login", json=login_data)
        if response.status_code == 200:
            print("✅ ورود موفق")
        else:
            print(f"❌ ورود ناموفق: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ خطا در ورود: {e}")
        return
    
    # تست endpoint های مختلف برای ایجاد inbound
    endpoints = [
        "/api/inbounds/add",
        "/inbounds/add",
        "/panel/api/inbounds/add",
        "/panel/inbounds/add",
        "/xui/api/inbounds/add",
        "/xui/inbounds/add"
    ]
    
    # داده‌های inbound تستی
    inbound_data = {
        "remark": "Test Inbound",
        "port": random.randint(10000, 65000),
        "protocol": "vless",
        "settings": {
            "clients": [
                {
                    "id": "test-uuid-123",
                    "email": "test@example.com",
                    "totalGB": 1
                }
            ]
        },
        "streamSettings": {
            "network": "tcp",
            "security": "reality",
            "realitySettings": {
                "serverName": "www.google.com",
                "fingerprint": "chrome",
                "publicKey": "test-key",
                "shortId": "test-id",
                "spiderX": "/"
            }
        }
    }
    
    for endpoint in endpoints:
        try:
            print(f"\n🔍 تست {endpoint}...")
            response = session.post(f"{base_url}{endpoint}", json=inbound_data)
            print(f"کد پاسخ: {response.status_code}")
            print(f"محتوای پاسخ: {response.text[:200]}...")
            
            if response.status_code == 200:
                print(f"✅ {endpoint} کار می‌کند!")
                return endpoint
        except Exception as e:
            print(f"❌ خطا در {endpoint}: {e}")
    
    print("\n❌ هیچ endpoint صحیحی برای ایجاد inbound پیدا نشد")

if __name__ == "__main__":
    test_xui_inbound_creation() 