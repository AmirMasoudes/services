#!/usr/bin/env python3
import os
import sys
import django
import requests
import json
import uuid
import random

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from xui_servers.models import XUIServer
from xui_servers.services import XUIService
from accounts.models import UsersModel
from plan.models import ConfingPlansModel

def create_inbound_manually(xui_service, server):
    """ایجاد inbound به صورت دستی"""
    print("🔧 ایجاد inbound به صورت دستی...")
    
    try:
        # تنظیمات inbound
        inbound_data = {
            "up": [],
            "down": [],
            "total": 0,
            "remark": "AutoBot-VLESS-443",
            "enable": True,
            "expiryTime": 0,
            "listen": "",
            "port": 443,
            "protocol": "vless",
            "settings": {
                "clients": [],
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
                    "serverNames": ["www.aparat.com"],
                    "privateKey": "YFgo8YQUJmqhu2yXL8rd8D9gDgJ1H1XgfbYqMB6LmoM",
                    "shortIds": [""]
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
            }
        }
        
        # ارسال درخواست ایجاد inbound
        response = xui_service.session.post(
            f"{xui_service.base_url}/panel/api/inbounds/add",
            json=inbound_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                inbound_id = data.get('obj', {}).get('id')
                print(f"✅ inbound ایجاد شد (ID: {inbound_id})")
                return inbound_id
            else:
                print(f"❌ خطا در ایجاد inbound: {data.get('msg', 'خطای نامشخص')}")
        else:
            print(f"❌ خطا در اتصال: {response.status_code}")
            
    except Exception as e:
        print(f"❌ خطا در ایجاد inbound: {e}")
    
    return None

def create_test_user_and_config():
    """ایجاد کاربر تستی و کانفیگ"""
    print("   ایجاد کاربر تستی و کانفیگ...")
    
    # دریافت سرور X-UI
    server = XUIServer.objects.filter(is_active=True).first()
    if not server:
        print("❌ سرور X-UI فعالی یافت نشد")
        return
    
    print(f"🖥️ سرور: {server.name}")
    print(f" آدرس: {server.host}:{server.port}")
    
    # ایجاد سرویس X-UI
    xui_service = XUIService(server)
    
    # ورود به X-UI
    if not xui_service.login():
        print("❌ خطا در ورود به X-UI")
        return
    
    print("✅ ورود به X-UI موفق")
    
    # دریافت inbound های موجود
    inbounds = xui_service.get_inbounds()
    print(f"📊 تعداد inbound های موجود: {len(inbounds)}")
    
    # اگر inbound وجود نداشت، ایجاد کن
    if len(inbounds) == 0:
        print("🔄 هیچ inbound موجود نیست. در حال ایجاد...")
        inbound_id = create_inbound_manually(xui_service, server)
        if not inbound_id:
            print("❌ خطا در ایجاد inbound")
            return
    else:
        print("ℹ️ inbound های موجود:")
        for inbound in inbounds:
            print(f"  - ID: {inbound.get('id')}, نام: {inbound.get('remark', 'بدون نام')}")
        inbound_id = inbounds[0].get('id')
    
    print(f"✅ انتخاب inbound: {inbound_id}")
    
    # ایجاد کاربر تستی در Django
    print("\n👤 ایجاد کاربر تستی...")
    
    # ایجاد پلن تستی اگر وجود نداشته باشد
    trial_plan, created = ConfingPlansModel.objects.get_or_create(
        name="پلن تستی",
        defaults={
            "price": 0,
            "in_volume": 1,
            "traffic_mb": 1024,
            "description": "پلن تستی 24 ساعته - 1 گیگابایت"
        }
    )
    
    # ایجاد کاربر تستی
    test_user, created = UsersModel.objects.get_or_create(
        id_tel="test_user_001",
        defaults={
            "username_tel": "testuser",
            "full_name": "کاربر تستی",
            "telegram_id": "123456789",
            "username": "testuser",
            "is_active": True,
            "has_used_trial": False
        }
    )
    
    if created:
        print(f"✅ کاربر تستی ایجاد شد: {test_user.full_name}")
    else:
        print(f"ℹ️ کاربر تستی موجود است: {test_user.full_name}")
    
    # ایجاد کانفیگ تستی
    print("\n🔧 ایجاد کانفیگ تستی...")
    
    from xui_servers.services import UserConfigService
    
    config, error = UserConfigService.create_trial_config(test_user, server, "vless")
    
    if config:
        print("✅ کانفیگ تستی ایجاد شد")
        print(f"📋 کانفیگ: {config}")
    else:
        print(f"❌ خطا در ایجاد کانفیگ: {error}")
    
    print("\n✅ تست کامل شد!")
    print(f"👤 کاربر: {test_user.full_name}")
    print(f"🖥️ سرور: {server.name}")
    print(f"📊 inbound ID: {inbound_id}")

if __name__ == "__main__":
    create_test_user_and_config()
