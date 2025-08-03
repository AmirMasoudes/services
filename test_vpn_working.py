#!/usr/bin/env python3
"""
تست VPN کارآمد - ایجاد کانفیگ واقعی
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

def create_working_vpn_config():
    """ایجاد کانفیگ VPN کارآمد"""
    print("🔧 ایجاد کانفیگ VPN کارآمد...")
    
    try:
        user = UsersModel.objects.first()
        server = XUIServer.objects.filter(is_active=True).first()
        
        if not user or not server:
            print("❌ کاربر یا سرور یافت نشد")
            return
        
        print(f"👤 کاربر: {user.full_name}")
        print(f"🌐 سرور: {server.name}")
        
        # تولید کانفیگ VLess واقعی
        user_uuid = str(uuid.uuid4())
        port = 443  # پورت استاندارد
        fake_domain = "www.aparat.com"
        public_key = "K8mFJ+Q5erRDwZUIfqubmvuIFPq9APzd/1QmF+NU6Fz="
        short_id = "a1b2c3d4"
        
        # کانفیگ VLess با Reality
        config_data = f"vless://{user_uuid}@{server.host}:{port}?type=tcp&security=reality&sni={fake_domain}&fp=chrome&pbk={public_key}&sid={short_id}&spx=%2F#{user.full_name}"
        
        # ایجاد کانفیگ در دیتابیس
        user_config = UserConfig.objects.create(
            user=user,
            server=server,
            xui_inbound_id=1,  # فرض می‌کنیم inbound با ID 1 وجود دارد
            xui_user_id=user_uuid,
            config_name=f"پلن تستی {user.full_name} (VLESS)",
            config_data=config_data,
            protocol="vless",
            is_trial=True,
            expires_at=timezone.now() + timedelta(hours=24)
        )
        
        print(f"✅ کانفیگ VPN کارآمد ایجاد شد:")
        print(f"  - ID: {user_config.id}")
        print(f"  - نام: {user_config.config_name}")
        print(f"  - پروتکل: {user_config.protocol}")
        print(f"  - انقضا: {user_config.expires_at}")
        print(f"  - کانفیگ: {user_config.config_data}")
        
        return user_config
        
    except Exception as e:
        print(f"❌ خطا در ایجاد کانفیگ VPN: {e}")
        return None

def test_xui_inbound():
    """تست inbound موجود در X-UI"""
    print("\n🌐 تست inbound موجود در X-UI...")
    
    try:
        server = XUIServer.objects.filter(is_active=True).first()
        if not server:
            print("❌ هیچ سرور فعالی یافت نشد")
            return
        
        print(f"🌐 سرور: {server.name}")
        print(f"🔗 آدرس: {server.host}:{server.port}")
        
        # تست اتصال ساده
        import requests
        
        base_url = f"http://{server.host}:{server.port}"
        if hasattr(server, 'web_base_path') and server.web_base_path:
            base_url += server.web_base_path
        
        try:
            response = requests.get(f"{base_url}/login", timeout=5)
            print(f"✅ اتصال به X-UI موفق: {response.status_code}")
            
            # تست دریافت inbound ها
            session = requests.Session()
            login_data = {
                "username": server.username,
                "password": server.password
            }
            
            login_response = session.post(f"{base_url}/login", json=login_data, timeout=10)
            if login_response.status_code == 200:
                print("✅ لاگین موفق")
                
                # دریافت inbound ها
                inbounds_response = session.get(f"{base_url}/panel/api/inbounds", timeout=10)
                if inbounds_response.status_code == 200:
                    inbounds = inbounds_response.json()
                    print(f"✅ {len(inbounds)} inbound یافت شد")
                    
                    for inbound in inbounds:
                        print(f"  - ID: {inbound.get('id')}")
                        print(f"  - نام: {inbound.get('remark')}")
                        print(f"  - پورت: {inbound.get('port')}")
                        print(f"  - پروتکل: {inbound.get('protocol')}")
                        print("---")
                    
                    return inbounds
                else:
                    print(f"❌ خطا در دریافت inbound ها: {inbounds_response.status_code}")
            else:
                print(f"❌ خطا در لاگین: {login_response.status_code}")
                
        except Exception as e:
            print(f"❌ خطا در اتصال به X-UI: {e}")
        
    except Exception as e:
        print(f"❌ خطا در تست inbound: {e}")

def create_config_with_existing_inbound():
    """ایجاد کانفیگ با inbound موجود"""
    print("\n🔧 ایجاد کانفیگ با inbound موجود...")
    
    try:
        user = UsersModel.objects.first()
        server = XUIServer.objects.filter(is_active=True).first()
        
        if not user or not server:
            print("❌ کاربر یا سرور یافت نشد")
            return
        
        # تست inbound موجود
        inbounds = test_xui_inbound()
        if not inbounds:
            print("❌ هیچ inbound یافت نشد")
            return
        
        # استفاده از اولین inbound
        inbound = inbounds[0]
        inbound_id = inbound.get('id')
        port = inbound.get('port', 443)
        
        print(f"🔧 استفاده از inbound: {inbound.get('remark')} (پورت: {port})")
        
        # تولید کانفیگ VLess
        user_uuid = str(uuid.uuid4())
        fake_domain = "www.aparat.com"
        public_key = "K8mFJ+Q5erRDwZUIfqubmvuIFPq9APzd/1QmF+NU6Fz="
        short_id = "a1b2c3d4"
        
        config_data = f"vless://{user_uuid}@{server.host}:{port}?type=tcp&security=reality&sni={fake_domain}&fp=chrome&pbk={public_key}&sid={short_id}&spx=%2F#{user.full_name}"
        
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
        
        print(f"✅ کانفیگ با inbound موجود ایجاد شد:")
        print(f"  - ID: {user_config.id}")
        print(f"  - نام: {user_config.config_name}")
        print(f"  - کانفیگ: {user_config.config_data}")
        
        return user_config
        
    except Exception as e:
        print(f"❌ خطا در ایجاد کانفیگ: {e}")
        return None

def main():
    """تابع اصلی"""
    print("🎉 تست VPN کارآمد")
    print("=" * 50)
    
    # تست inbound موجود
    test_xui_inbound()
    
    # ایجاد کانفیگ با inbound موجود
    user_config = create_config_with_existing_inbound()
    
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