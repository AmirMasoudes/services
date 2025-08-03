#!/usr/bin/env python3
"""
راه حل استفاده از inbound واقعی در X-UI
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
import uuid
import random
import string
import requests

def get_existing_inbound():
    """دریافت inbound موجود از X-UI"""
    print("🌐 دریافت inbound موجود...")
    
    try:
        server = XUIServer.objects.filter(is_active=True).first()
        if not server:
            print("❌ هیچ سرور فعالی یافت نشد")
            return None
        
        print(f"🌐 سرور: {server.name}")
        print(f"🔗 آدرس: {server.host}:{server.port}")
        
        # اتصال به X-UI
        base_url = f"http://{server.host}:{server.port}"
        if hasattr(server, 'web_base_path') and server.web_base_path:
            base_url += server.web_base_path
        
        session = requests.Session()
        
        # لاگین
        login_data = {
            "username": server.username,
            "password": server.password
        }
        
        login_response = session.post(f"{base_url}/login", json=login_data, timeout=10)
        if login_response.status_code != 200:
            print(f"❌ خطا در لاگین: {login_response.status_code}")
            return None
        
        print("✅ لاگین موفق")
        
        # دریافت inbound ها
        inbounds_response = session.get(f"{base_url}/panel/api/inbounds", timeout=10)
        if inbounds_response.status_code != 200:
            print(f"❌ خطا در دریافت inbound ها: {inbounds_response.status_code}")
            return None
        
        inbounds = inbounds_response.json()
        print(f"✅ {len(inbounds)} inbound یافت شد")
        
        # انتخاب inbound مناسب (VLESS با Reality)
        for inbound in inbounds:
            if (inbound.get('protocol') == 'vless' and 
                'reality' in inbound.get('streamSettings', {}).get('security', '').lower()):
                print(f"✅ inbound مناسب یافت شد:")
                print(f"  - ID: {inbound.get('id')}")
                print(f"  - نام: {inbound.get('remark')}")
                print(f"  - پورت: {inbound.get('port')}")
                print(f"  - پروتکل: {inbound.get('protocol')}")
                return inbound, session, base_url
        
        print("❌ هیچ inbound مناسب یافت نشد")
        return None
        
    except Exception as e:
        print(f"❌ خطا در دریافت inbound: {e}")
        return None

def create_working_config_with_real_inbound():
    """ایجاد کانفیگ کارآمد با inbound واقعی"""
    print("🔧 ایجاد کانفیگ کارآمد با inbound واقعی...")
    
    try:
        user = UsersModel.objects.first()
        if not user:
            print("❌ هیچ کاربری یافت نشد")
            return
        
        print(f"👤 کاربر: {user.full_name}")
        
        # دریافت inbound موجود
        result = get_existing_inbound()
        if not result:
            print("❌ inbound مناسب یافت نشد")
            return
        
        inbound, session, base_url = result
        inbound_id = inbound.get('id')
        port = inbound.get('port', 443)
        
        # تولید UUID برای کاربر
        user_uuid = str(uuid.uuid4())
        
        # تنظیمات کاربر جدید
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
        
        # اضافه کردن کاربر به inbound
        response = session.post(f"{base_url}/panel/api/inbounds/update/{inbound_id}", json=user_data, timeout=10)
        if response.status_code != 200:
            print(f"❌ خطا در اضافه کردن کاربر: {response.status_code}")
            return None
        
        print("✅ کاربر به inbound اضافه شد")
        
        # تولید کانفیگ VLess
        config_data = f"vless://{user_uuid}@{inbound.get('listen', '0.0.0.0')}:{port}?type=tcp&security=reality&sni=www.aparat.com&fp=chrome&pbk=K8mFJ+Q5erRDwZUIfqubmvuIFPq9APzd/1QmF+NU6Fz=&sid=a1b2c3d4&spx=%2F#{user.full_name}"
        
        # ایجاد کانفیگ در دیتابیس
        user_config = UserConfig.objects.create(
            user=user,
            server=XUIServer.objects.filter(is_active=True).first(),
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

def main():
    """تابع اصلی"""
    print("🎉 راه حل استفاده از inbound واقعی")
    print("=" * 50)
    
    # ایجاد کانفیگ کارآمد با inbound واقعی
    user_config = create_working_config_with_real_inbound()
    
    if user_config:
        print("\n✅ کانفیگ VPN کارآمد ایجاد شد!")
        print(f"🔧 کانفیگ قابل استفاده: {user_config.config_data}")
        
        # حذف کانفیگ تست
        user_config.delete()
        print("🗑️ کانفیگ تست حذف شد")
    else:
        print("\n❌ خطا در ایجاد کانفیگ VPN")
    
    print("\n🎉 عملیات کامل شد!")

if __name__ == "__main__":
    main() 