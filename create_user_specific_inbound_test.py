#!/usr/bin/env python3
import os
import sys
import django
import requests
import json
import uuid

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from xui_servers.models import XUIServer
from xui_servers.services import XUIService, UserConfigService
from accounts.models import UsersModel
from plan.models import ConfingPlansModel

def test_user_specific_inbound():
    """تست سیستم Inbound جداگانه برای هر کاربر"""
    print("🔧 تست سیستم Inbound جداگانه برای هر کاربر...")
    
    # دریافت سرور X-UI
    server = XUIServer.objects.filter(is_active=True).first()
    if not server:
        print("❌ سرور X-UI فعالی یافت نشد")
        return
    
    print(f"🖥️ سرور: {server.name}")
    print(f"   آدرس: {server.host}:{server.port}")
    
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
    
    # تست ایجاد Inbound برای کاربر 1
    print("\n👤 تست ایجاد Inbound برای کاربر 1...")
    inbound_id_1 = xui_service.get_or_create_inbound_for_user(1, "vless")
    if inbound_id_1:
        print(f"✅ Inbound برای کاربر 1 ایجاد شد (ID: {inbound_id_1})")
    else:
        print("❌ خطا در ایجاد Inbound برای کاربر 1")
        return
    
    # تست ایجاد Inbound برای کاربر 2
    print("\n👤 تست ایجاد Inbound برای کاربر 2...")
    inbound_id_2 = xui_service.get_or_create_inbound_for_user(2, "vless")
    if inbound_id_2:
        print(f"✅ Inbound برای کاربر 2 ایجاد شد (ID: {inbound_id_2})")
    else:
        print("❌ خطا در ایجاد Inbound برای کاربر 2")
        return
    
    # بررسی اینکه Inbound ها متفاوت هستند
    if inbound_id_1 != inbound_id_2:
        print("✅ Inbound های جداگانه برای کاربران ایجاد شد")
    else:
        print("❌ Inbound ها یکسان هستند!")
        return
    
    # دریافت مجدد inbound ها و نمایش
    inbounds_after = xui_service.get_inbounds()
    print(f"\n📊 تعداد inbound های موجود بعد از تست: {len(inbounds_after)}")
    
    print("\n📋 Inbound های ایجاد شده:")
    for inbound in inbounds_after:
        if inbound.get('remark', '').startswith('User-'):
            print(f"  - ID: {inbound.get('id')}, نام: {inbound.get('remark')}, پورت: {inbound.get('port')}")
    
    print("\n🎉 تست سیستم Inbound جداگانه موفق بود!")

def test_user_config_creation():
    """تست ایجاد کانفیگ برای کاربران مختلف"""
    print("\n🔧 تست ایجاد کانفیگ برای کاربران مختلف...")
    
    # دریافت سرور X-UI
    server = XUIServer.objects.filter(is_active=True).first()
    if not server:
        print("❌ سرور X-UI فعالی یافت نشد")
        return
    
    # ایجاد کاربر تستی 1
    test_user_1, created = UsersModel.objects.get_or_create(
        telegram_id=999001,
        defaults={
            'full_name': 'کاربر تست 1',
            'username': 'testuser1',
            'phone_number': '09120000001'
        }
    )
    
    # ایجاد کاربر تستی 2
    test_user_2, created = UsersModel.objects.get_or_create(
        telegram_id=999002,
        defaults={
            'full_name': 'کاربر تست 2',
            'username': 'testuser2',
            'phone_number': '09120000002'
        }
    )
    
    print(f"👤 کاربر تست 1: {test_user_1.full_name} (ID: {test_user_1.id})")
    print(f"👤 کاربر تست 2: {test_user_2.full_name} (ID: {test_user_2.id})")
    
    # ایجاد کانفیگ تستی برای کاربر 1
    print("\n🎁 ایجاد کانفیگ تستی برای کاربر 1...")
    config_1, message_1 = UserConfigService.create_trial_config(test_user_1, server, "vless")
    
    if config_1:
        print(f"✅ کانفیگ کاربر 1 ایجاد شد")
        print(f"   نام: {config_1.config_name}")
        print(f"   Inbound ID: {config_1.xui_inbound_id}")
    else:
        print(f"❌ خطا در ایجاد کانفیگ کاربر 1: {message_1}")
    
    # ایجاد کانفیگ تستی برای کاربر 2
    print("\n🎁 ایجاد کانفیگ تستی برای کاربر 2...")
    config_2, message_2 = UserConfigService.create_trial_config(test_user_2, server, "vless")
    
    if config_2:
        print(f"✅ کانفیگ کاربر 2 ایجاد شد")
        print(f"   نام: {config_2.config_name}")
        print(f"   Inbound ID: {config_2.xui_inbound_id}")
    else:
        print(f"❌ خطا در ایجاد کانفیگ کاربر 2: {message_2}")
    
    # بررسی اینکه Inbound ها متفاوت هستند
    if config_1 and config_2:
        if config_1.xui_inbound_id != config_2.xui_inbound_id:
            print("\n✅ کانفیگ‌های جداگانه برای کاربران ایجاد شد!")
        else:
            print("\n❌ کانفیگ‌ها از Inbound مشترک استفاده می‌کنند!")
    
    print("\n🎉 تست ایجاد کانفیگ کامل شد!")

if __name__ == "__main__":
    test_user_specific_inbound()
    test_user_config_creation() 