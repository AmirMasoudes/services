#!/usr/bin/env python3
import requests
import json

def find_xui_api():
    """یافتن API صحیح X-UI"""
    base_url = "http://127.0.0.1:44"
    
    # تست endpoint های مختلف
    endpoints = [
        "/api/inbounds",
        "/inbounds", 
        "/panel/api/inbounds",
        "/panel/inbounds",
        "/xui/api/inbounds",
        "/xui/inbounds",
        "/api/inbound",
        "/inbound",
        "/panel/api/inbound", 
        "/panel/inbound",
        "/xui/api/inbound",
        "/xui/inbound"
    ]
    
    # ابتدا ورود
    login_data = {
        "username": "ames",
        "password": "FJam@1610"
    }
    
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json'
    })
    
    # ورود
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
    
    # تست endpoint ها
    for endpoint in endpoints:
        try:
            response = session.get(f"{base_url}{endpoint}")
            print(f"🔍 {endpoint}: {response.status_code}")
            if response.status_code == 200:
                print(f"✅ {endpoint} کار می‌کند!")
                print(f"📋 محتوا: {response.text[:200]}...")
        except Exception as e:
            print(f"❌ {endpoint}: {e}")

if __name__ == "__main__":
    find_xui_api() 