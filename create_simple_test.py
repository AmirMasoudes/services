#!/usr/bin/env python3
import os
import sys
import django

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from xui_servers.models import XUIServer
from xui_servers.services import XUIService
from accounts.models import UsersModel
from plan.models import ConfingPlansModel

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
    
    if len(inbounds) == 0:
        print("❌ هیچ inbound موجود نیست. لطفاً از طریق X-UI Panel یک inbound ایجاد کنید.")
        print("   آدرس: http://38.54.105.181:44")
        return
    
    # نمایش inbound های موجود
    print("ℹ️ inbound های موجود:")
    for inbound in inbounds:
        print(f"  - ID: {inbound.get('id')}, نام: {inbound.get('remark', 'بدون نام')}")
    
    # انتخاب اولین inbound
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
