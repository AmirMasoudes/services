#!/usr/bin/env python3
"""
تست ایجاد inbound ساده با فرمت صحیح
"""

import requests
import json

def test_simple_inbound():
    """تست ایجاد inbound ساده"""
    
    # تنظیمات سرور
    base_url = "http://38.54.105.124:54321/MsxZ4xuIy5xLfQtsSC"
    
    # ایجاد session
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'User-Agent': 'Django-XUI-Bot/2.0'
    })
    
    print("🔍 تست ایجاد inbound ساده...")
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
                
                # تست ایجاد inbound ساده
                print("\n🔧 تست ایجاد inbound ساده...")
                
                # فرمت صحیح برای VMess
                simple_inbound = {
                    "remark": "Simple-Test-VMess",
                    "port": 8446,
                    "protocol": "vmess",
                    "settings": json.dumps({
                        "clients": []
                    }),
                    "streamSettings": json.dumps({
                        "network": "tcp",
                        "security": "none"
                    }),
                    "sniffing": "{\"enabled\":true,\"destOverride\":[\"http\",\"tls\"]}",
                    "enable": True,
                    "expiryTime": 0,
                    "listen": "",
                    "up": [],
                    "down": [],
                    "total": 0
                }
                
                print(f"📤 داده ارسالی: {json.dumps(simple_inbound, indent=2)}")
                
                # تست endpoint اصلی
                try:
                    response = session.post(f"{base_url}/panel/api/inbounds/add", json=simple_inbound, timeout=10)
                    
                    print(f"📊 وضعیت پاسخ: {response.status_code}")
                    print(f"📄 محتوای پاسخ: {response.text}")
                    
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            print(f"✅ پاسخ JSON: {json.dumps(data, indent=2)}")
                            
                            if data.get('success'):
                                print("✅ Inbound با موفقیت ایجاد شد!")
                            else:
                                print(f"❌ خطا: {data.get('msg', 'خطای نامشخص')}")
                        except json.JSONDecodeError:
                            print("❌ پاسخ JSON نامعتبر")
                    else:
                        print("❌ خطا در ایجاد inbound")
                        
                except Exception as e:
                    print(f"❌ خطا در ارسال درخواست: {e}")
                
                # تست ایجاد inbound VLess
                print("\n🔧 تست ایجاد inbound VLess...")
                
                vless_inbound = {
                    "remark": "Simple-Test-VLess",
                    "port": 8447,
                    "protocol": "vless",
                    "settings": json.dumps({
                        "clients": []
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
                    "sniffing": "{\"enabled\":true,\"destOverride\":[\"http\",\"tls\"]}",
                    "enable": True,
                    "expiryTime": 0,
                    "listen": "",
                    "up": [],
                    "down": [],
                    "total": 0
                }
                
                print(f"📤 داده ارسالی VLess: {json.dumps(vless_inbound, indent=2)}")
                
                try:
                    response = session.post(f"{base_url}/panel/api/inbounds/add", json=vless_inbound, timeout=10)
                    
                    print(f"📊 وضعیت پاسخ VLess: {response.status_code}")
                    print(f"📄 محتوای پاسخ VLess: {response.text}")
                    
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            print(f"✅ پاسخ JSON VLess: {json.dumps(data, indent=2)}")
                            
                            if data.get('success'):
                                print("✅ Inbound VLess با موفقیت ایجاد شد!")
                            else:
                                print(f"❌ خطا VLess: {data.get('msg', 'خطای نامشخص')}")
                        except json.JSONDecodeError:
                            print("❌ پاسخ JSON نامعتبر VLess")
                    else:
                        print("❌ خطا در ایجاد inbound VLess")
                        
                except Exception as e:
                    print(f"❌ خطا در ارسال درخواست VLess: {e}")
                    
            else:
                print("❌ خطا در ورود")
        else:
            print(f"❌ خطای HTTP: {response.status_code}")
            print(f"📄 محتوای پاسخ: {response.text}")
            
    except Exception as e:
        print(f"❌ خطا در اتصال: {e}")

if __name__ == "__main__":
    test_simple_inbound() 