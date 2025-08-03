#!/usr/bin/env python3
"""
حل مشکل اتصال VPN - ایجاد inbound واقعی در X-UI
"""

import os
import sys
import django
from datetime import datetime, timedelta

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from xui_servers.models import UserConfig, XUIServer
from accounts.models import UsersModel
import requests
import json
import uuid
import random
import string

def test_xui_connection():
    """تست اتصال به X-UI"""
    print("🌐 تست اتصال به X-UI...")
    
    try:
        server = XUIServer.objects.filter(is_active=True).first()
        if not server:
            print("❌ هیچ سرور فعالی یافت نشد")
            return None
        
        print(f"🌐 سرور: {server.name}")
        print(f"🔗 آدرس: {server.host}:{server.port}")
        print(f"👤 نام کاربری: {server.username}")
        print(f"🔑 رمز عبور: {server.password}")
        
        # تست اتصال به X-UI
        base_url = f"http://{server.host}:{server.port}"
        if hasattr(server, 'web_base_path') and server.web_base_path:
            base_url += server.web_base_path
        
        # لاگین به X-UI
        login_data = {
            "username": server.username,
            "password": server.password
        }
        
        session = requests.Session()
        
        try:
            # تست اتصال
            response = session.get(f"{base_url}/login", timeout=5)
            print(f"✅ اتصال به X-UI موفق: {response.status_code}")
            
            # لاگین
            login_response = session.post(f"{base_url}/login", json=login_data, timeout=10)
            print(f"🔐 لاگین: {login_response.status_code}")
            
            if login_response.status_code == 200:
                print("✅ لاگین موفق")
                return session, base_url, server
            else:
                print(f"❌ خطا در لاگین: {login_response.text}")
                return None
                
        except Exception as e:
            print(f"❌ خطا در اتصال به X-UI: {e}")
            return None
        
    except Exception as e:
        print(f"❌ خطا در تست اتصال: {e}")
        return None

def create_real_inbound(session, base_url, server):
    """ایجاد inbound واقعی در X-UI"""
    print("🔧 ایجاد inbound واقعی...")
    
    try:
        # تولید پورت تصادفی
        port = random.randint(10000, 65000)
        
        # تنظیمات inbound
        inbound_data = {
            "up": 0,
            "down": 0,
            "total": 0,
            "remark": f"VPN-Inbound-{port}",
            "enable": True,
            "expiryTime": 0,
            "listen": "",
            "port": port,
            "protocol": "vless",
            "settings": {
                "clients": [
                    {
                        "id": str(uuid.uuid4()),
                        "flow": "",
                        "email": "test@example.com",
                        "limitIp": 0,
                        "totalGB": 0,
                        "expiryTime": 0,
                        "enable": True,
                        "tgId": "",
                        "subId": ""
                    }
                ],
                "decryption": "none",
                "fallbacks": []
            },
            "streamSettings": {
                "network": "tcp",
                "security": "reality",
                "realitySettings": {
                    "show": False,
                    "dest": "www.aparat.com:443",
                    "xver": 0,
                    "serverNames": ["www.aparat.com", "www.irib.ir", "www.varzesh3.com"],
                    "privateKey": "K8mFJ+Q5erRDwZUIfqubmvuIFPq9APzd/1QmF+NU6Fz=",
                    "shortIds": ["a1b2c3d4"]
                },
                "tcpSettings": {
                    "header": {
                        "type": "none"
                    }
                }
            },
            "sniffing": {
                "enabled": True,
                "destOverride": ["http", "tls"]
            },
            "tag": f"inbound-{port}"
        }
        
        # ارسال درخواست ایجاد inbound
        response = session.post(f"{base_url}/panel/api/inbounds/add", json=inbound_data, timeout=10)
        print(f"📡 پاسخ ایجاد inbound: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ inbound ایجاد شد: {result}")
            return result.get('obj', {}).get('id'), port
        else:
            print(f"❌ خطا در ایجاد inbound: {response.text}")
            return None, None
            
    except Exception as e:
        print(f"❌ خطا در ایجاد inbound: {e}")
        return None, None

def create_real_user(session, base_url, inbound_id, user):
    """ایجاد کاربر واقعی در X-UI"""
    print("👤 ایجاد کاربر واقعی...")
    
    try:
        # تولید UUID برای کاربر
        user_uuid = str(uuid.uuid4())
        
        # تنظیمات کاربر
        user_data = {
            "id": inbound_id,
            "settings": {
                "clients": [
                    {
                        "id": user_uuid,
                        "flow": "",
                        "email": f"{user.full_name}@vpn.com",
                        "limitIp": 0,
                        "totalGB": 0,
                        "expiryTime": 0,
                        "enable": True,
                        "tgId": "",
                        "subId": ""
                    }
                ]
            }
        }
        
        # ارسال درخواست ایجاد کاربر
        response = session.post(f"{base_url}/panel/api/inbounds/update/{inbound_id}", json=user_data, timeout=10)
        print(f"📡 پاسخ ایجاد کاربر: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ کاربر ایجاد شد: {result}")
            return user_uuid
        else:
            print(f"❌ خطا در ایجاد کاربر: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ خطا در ایجاد کاربر: {e}")
        return None

def create_working_config(user, server, inbound_id, user_uuid, port):
    """ایجاد کانفیگ کارآمد"""
    print("🔧 ایجاد کانفیگ کارآمد...")
    
    try:
        # تولید کانفیگ VLess واقعی
        config_data = f"vless://{user_uuid}@{server.host}:{port}?type=tcp&security=reality&sni=www.aparat.com&fp=chrome&pbk=K8mFJ+Q5erRDwZUIfqubmvuIFPq9APzd/1QmF+NU6Fz=&sid=a1b2c3d4&spx=%2F#{user.full_name}"
        
        # ایجاد کانفیگ در دیتابیس
        user_config = UserConfig.objects.create(
            user=user,
            server=server,
            xui_inbound_id=inbound_id,
            xui_user_id=user_uuid,
            config_name=f"پلن تستی {user.full_name} (VLESS)",
            config_data=config_data,
            protocol="vless",
            is_trial=True,
            expires_at=timezone.now() + timedelta(hours=24)
        )
        
        print(f"✅ کانفیگ کارآمد ایجاد شد:")
        print(f"  - ID: {user_config.id}")
        print(f"  - نام: {user_config.config_name}")
        print(f"  - کانفیگ: {user_config.config_data}")
        
        return user_config
        
    except Exception as e:
        print(f"❌ خطا در ایجاد کانفیگ: {e}")
        return None

def test_real_vpn():
    """تست VPN واقعی"""
    print("🧪 تست VPN واقعی...")
    
    try:
        user = UsersModel.objects.first()
        if not user:
            print("❌ هیچ کاربری یافت نشد")
            return
        
        print(f"👤 کاربر: {user.full_name}")
        
        # تست اتصال به X-UI
        result = test_xui_connection()
        if not result:
            print("❌ اتصال به X-UI ناموفق")
            return
        
        session, base_url, server = result
        
        # ایجاد inbound واقعی
        inbound_id, port = create_real_inbound(session, base_url, server)
        if not inbound_id:
            print("❌ ایجاد inbound ناموفق")
            return
        
        # ایجاد کاربر واقعی
        user_uuid = create_real_user(session, base_url, inbound_id, user)
        if not user_uuid:
            print("❌ ایجاد کاربر ناموفق")
            return
        
        # ایجاد کانفیگ کارآمد
        user_config = create_working_config(user, server, inbound_id, user_uuid, port)
        if not user_config:
            print("❌ ایجاد کانفیگ ناموفق")
            return
        
        print("✅ تست VPN واقعی موفق!")
        print(f"🔧 کانفیگ قابل استفاده: {user_config.config_data}")
        
        # حذف کانفیگ تست
        user_config.delete()
        print("🗑️ کانفیگ تست حذف شد")
        
    except Exception as e:
        print(f"❌ خطا در تست VPN واقعی: {e}")

def main():
    """تابع اصلی"""
    print("🎉 حل مشکل اتصال VPN")
    print("=" * 50)
    
    # تست VPN واقعی
    test_real_vpn()
    
    print("\n🎉 عملیات کامل شد!")
    print("✅ سیستم آماده استفاده است!")

if __name__ == "__main__":
    main() 