#!/usr/bin/env python3
"""
سیستم کامل حل مشکلات VPN
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
import json

def get_xui_inbounds_with_details():
    """دریافت inbound ها با جزئیات کامل"""
    print("🌐 دریافت inbound ها با جزئیات...")
    
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
        
        # بررسی جزئیات هر inbound
        valid_inbounds = []
        for inbound in inbounds:
            print(f"\n🔍 بررسی inbound {inbound.get('id')}:")
            print(f"  - نام: {inbound.get('remark')}")
            print(f"  - پورت: {inbound.get('port')}")
            print(f"  - پروتکل: {inbound.get('protocol')}")
            
            # بررسی تنظیمات Reality
            stream_settings = inbound.get('streamSettings', {})
            security = stream_settings.get('security', '')
            
            if security == 'reality':
                reality_settings = stream_settings.get('realitySettings', {})
                print(f"  - Reality فعال")
                print(f"  - Dest: {reality_settings.get('dest')}")
                print(f"  - Server Names: {reality_settings.get('serverNames')}")
                print(f"  - Private Key: {reality_settings.get('privateKey')}")
                print(f"  - Short IDs: {reality_settings.get('shortIds')}")
                
                # بررسی کلید عمومی
                private_key = reality_settings.get('privateKey', '')
                if private_key:
                    print(f"  ✅ کلید خصوصی موجود")
                    valid_inbounds.append({
                        'inbound': inbound,
                        'session': session,
                        'base_url': base_url,
                        'private_key': private_key,
                        'dest': reality_settings.get('dest', 'www.aparat.com:443'),
                        'server_names': reality_settings.get('serverNames', ['www.aparat.com']),
                        'short_ids': reality_settings.get('shortIds', ['a1b2c3d4'])
                    })
                else:
                    print(f"  ❌ کلید خصوصی موجود نیست")
            else:
                print(f"  - Reality غیرفعال")
        
        return valid_inbounds
        
    except Exception as e:
        print(f"❌ خطا در دریافت inbound ها: {e}")
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
        
        # دریافت inbound های معتبر
        valid_inbounds = get_xui_inbounds_with_details()
        if not valid_inbounds:
            print("❌ هیچ inbound معتبری یافت نشد")
            return
        
        # انتخاب اولین inbound معتبر
        inbound_data = valid_inbounds[0]
        inbound = inbound_data['inbound']
        session = inbound_data['session']
        base_url = inbound_data['base_url']
        private_key = inbound_data['private_key']
        dest = inbound_data['dest']
        server_names = inbound_data['server_names']
        short_ids = inbound_data['short_ids']
        
        print(f"✅ inbound انتخاب شد:")
        print(f"  - نام: {inbound.get('remark')}")
        print(f"  - پورت: {inbound.get('port')}")
        print(f"  - کلید خصوصی: {private_key[:20]}...")
        print(f"  - Dest: {dest}")
        
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
        
        # تولید کانفیگ VLess با تنظیمات صحیح
        dest_host = dest.split(':')[0] if ':' in dest else dest
        sni = server_names[0] if server_names else dest_host
        short_id = short_ids[0] if short_ids else "a1b2c3d4"
        
        config_data = f"vless://{user_uuid}@{server.host}:{port}?type=tcp&security=reality&pbk={private_key}&fp=chrome&sni={sni}&sid={short_id}&spx=%2F#{user.full_name}"
        
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

def test_existing_configs():
    """تست کانفیگ‌های موجود"""
    print("\n🧪 تست کانفیگ‌های موجود...")
    
    try:
        configs = UserConfig.objects.filter(is_trial=True).order_by('-created_at')[:5]
        print(f"📊 {configs.count()} کانفیگ تستی یافت شد")
        
        for config in configs:
            print(f"\n🔧 کانفیگ {config.id}:")
            print(f"  - نام: {config.config_name}")
            print(f"  - کانفیگ: {config.config_data}")
            
            # بررسی مشکلات
            if 'pbk=' in config.config_data and 'pbk=&' in config.config_data:
                print(f"  ❌ مشکل: pbk خالی است")
            else:
                print(f"  ✅ pbk موجود است")
            
            if 'sni=www.aparat.com' in config.config_data:
                print(f"  ✅ sni صحیح است")
            else:
                print(f"  ❌ مشکل: sni نادرست است")
        
    except Exception as e:
        print(f"❌ خطا در تست کانفیگ‌ها: {e}")

def main():
    """تابع اصلی"""
    print("🎉 سیستم کامل حل مشکلات VPN")
    print("=" * 60)
    
    # تست کانفیگ‌های موجود
    test_existing_configs()
    
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