#!/usr/bin/env python3
"""
تست ایجاد inbound جدید
"""

import requests
import json
import random

# تنظیمات X-UI
XUI_URL = "http://38.54.105.124:54321/MsxZ4xuIy5xLfQtsSC"
LOGIN_DATA = {
    "username": "admin",
    "password": "YourSecurePassword123!@#"
}

def login_to_xui():
    """ورود به X-UI"""
    print("�� ورود به X-UI...")
    response = requests.post(f"{XUI_URL}/login", json=LOGIN_DATA)
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            print("✅ ورود موفق")
            return response.cookies
        else:
            print(f"❌ خطا در ورود: {data.get('msg')}")
            return None
    else:
        print(f"❌ خطا در اتصال: {response.status_code}")
        return None

def get_inbounds(cookies):
    """دریافت لیست inbound ها"""
    print("\n📋 دریافت لیست inbound ها...")
    response = requests.get(f"{XUI_URL}/panel/api/inbounds/list", cookies=cookies)
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            inbounds = data.get("obj", [])
            print(f"✅ تعداد inbound موجود: {len(inbounds)}")
            for inbound in inbounds:
                print(f"  - {inbound.get('remark')} (Port: {inbound.get('port')}, Protocol: {inbound.get('protocol')})")
            return inbounds
        else:
            print(f"❌ خطا: {data.get('msg')}")
            return []
    else:
        print(f"❌ خطا در اتصال: {response.status_code}")
        return []

def create_test_inbound(cookies):
    """ایجاد inbound تست"""
    print("\n🔧 ایجاد inbound تست...")
    
    # پورت تصادفی بین 20000-60000
    port = random.randint(20000, 60000)
    
    inbound_data = {
        "remark": f"Test-Inbound-{port}",
        "port": port,
        "protocol": "vless",
        "settings": json.dumps({
            "clients": [],
            "decryption": "none",
            "fallbacks": []
        }),
        "streamSettings": json.dumps({
            "network": "tcp",
            "security": "reality",
            "realitySettings": {
                "show": False,
                "dest": "www.aparat.com:443",
                "xver": 0,
                "serverNames": ["www.aparat.com"],
                "privateKey": "YFgo8YQUJmqhu2yXL8rd8D9gDgJ1H1XgfbYqMB6LmoM",
                "shortIds": [""]
            }
        }),
        "sniffing": json.dumps({
            "enabled": True,
            "destOverride": ["http", "tls"]
        }),
        "enable": True,
        "expiryTime": 0,
        "listen": "",
        "up": 0,
        "down": 0,
        "total": 0
    }
    
    print(f"📤 ارسال درخواست ایجاد inbound: {inbound_data['remark']}")
    print(f"📊 پورت: {port}")
    
    response = requests.post(f"{XUI_URL}/panel/api/inbounds/add", json=inbound_data, cookies=cookies)
    
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            inbound_id = data.get("obj", {}).get("id")
            print(f"✅ Inbound با موفقیت ایجاد شد - ID: {inbound_id}")
            return inbound_id
        else:
            print(f"❌ خطا در ایجاد: {data.get('msg')}")
            return None
    else:
        print(f"❌ خطا در اتصال: {response.status_code}")
        return None

def main():
    print("🚀 تست ایجاد inbound")
    print("=" * 40)
    
    # ورود به X-UI
    cookies = login_to_xui()
    if not cookies:
        return
    
    # دریافت لیست inbound ها
    inbounds = get_inbounds(cookies)
    
    # ایجاد inbound تست
    inbound_id = create_test_inbound(cookies)
    
    if inbound_id:
        print(f"\n🎉 تست موفق!")
        print(f"📋 Inbound ID: {inbound_id}")
        print(f"�� پورت: {port}")
    else:
        print("\n❌ تست ناموفق")

if __name__ == "__main__":
    main()
